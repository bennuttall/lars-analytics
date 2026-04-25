import csv
from collections import Counter
from datetime import datetime
from pathlib import Path


_DOUBLE_EXTS = (".tar.gz", ".tar.bz2", ".tar.xz", ".tar.zst", ".tar.lz4")


def file_ext(path: str) -> str:
    name = path.rstrip("/").rsplit("/", 1)[-1]
    if not name or "." not in name:
        return "/"
    lower = name.lower()
    for double in _DOUBLE_EXTS:
        if lower.endswith(double):
            return double
    return "." + name.rsplit(".", 1)[-1].lower()


def first_dir(path: str) -> str:
    stripped = path.strip("/")
    if not stripped:
        return "/"
    parts = stripped.split("/")
    # A single component without trailing slash is a root-level file; group it under /
    if len(parts) == 1 and not path.endswith("/"):
        return "/"
    return "/" + parts[0] + "/"


def load_csv(csv_path: Path) -> list[dict]:
    with open(csv_path) as f:
        return list(csv.DictReader(f))


def load_all_csvs(csv_dir: Path) -> list[dict]:
    rows = []
    for f in sorted(csv_dir.rglob("*.csv")):
        rows.extend(load_csv(f))
    return rows


_EXCLUDED_PREFIXES = ("/icons", "/.well-known")


def _is_counted(r: dict) -> bool:
    if any(r["path"].startswith(p) for p in _EXCLUDED_PREFIXES):
        return False
    if r.get("status") == "404":
        return False
    return True


def build_analytics(rows: list[dict], base_url: str = "") -> dict:
    rows = [r for r in rows if _is_counted(r)]
    human_rows = [r for r in rows if r.get("is_bot", "False") not in ("True", True)]
    bot_rows = [r for r in rows if r.get("is_bot", "False") in ("True", True)]

    times = [datetime.fromisoformat(r["time"]) for r in human_rows]
    dates = sorted(set(t.date() for t in times))
    hits_by_day = [sum(1 for t in times if t.date() == d) for d in dates]

    month_counts = Counter(t.strftime("%Y-%m") for t in times)
    months_iso = sorted(month_counts)
    hits_by_month = [month_counts[m] for m in months_iso]

    path_counts = Counter(r["path"] for r in human_rows)

    top_files = [
        {"path": path, "hits": n, "ext": file_ext(path)}
        for path, n in path_counts.most_common(30)
    ]

    root_files = [
        {"path": path, "hits": n, "ext": file_ext(path)}
        for path, n in path_counts.most_common()
        if path.count("/") == 1 and not path.endswith("/")
    ][:20]

    ext_counts = [
        {"ext": ext, "hits": n}
        for ext, n in Counter(file_ext(r["path"]) for r in human_rows).most_common(15)
    ]

    dir_counts = [
        {"dir": d, "hits": n}
        for d, n in Counter(first_dir(r["path"]) for r in human_rows).most_common(15)
    ]

    ua_all = Counter(r["ua"] for r in rows)
    ua_bot = Counter(r["ua"] for r in bot_rows)
    ua_counts = [
        {"ua": ua, "hits": n, "is_bot": ua_bot[ua] > n / 2} for ua, n in ua_all.most_common(15)
    ]

    unique_ips = len(set(r["remote_host"] for r in human_rows))

    base_domain = (
        base_url.replace("https://", "").replace("http://", "").rstrip("/") if base_url else ""
    )
    referer_counts = Counter(
        r["referer"] for r in human_rows if r.get("referer") and r["referer"] != base_domain
    ).most_common(20)

    total = len(rows)
    bot_pct = round(100 * len(bot_rows) / total, 1) if total else 0.0

    return {
        "date_from": dates[0].isoformat() if dates else "",
        "date_to": dates[-1].isoformat() if dates else "",
        "total_hits": total,
        "bot_hits": bot_pct,
        "unique_ips": unique_ips,
        "dates": [d.isoformat() for d in dates],
        "hits_by_day": hits_by_day,
        "months": months_iso,
        "hits_by_month": hits_by_month,
        "top_files": top_files,
        "root_files": root_files,
        "ext_counts": ext_counts,
        "dir_counts": dir_counts,
        "ua_counts": ua_counts,
        "referer_counts": referer_counts,
        "base_url": base_url,
    }
