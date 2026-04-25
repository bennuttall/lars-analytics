import calendar
import json
import os
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

from chameleon import PageTemplateLoader

from . import build_analytics, load_all_csvs


def _rel(from_page: str, to_page: str) -> str:
    """Relative URL from one page path to another (both relative to output_dir root)."""
    return os.path.relpath(to_page, Path(from_page).parent).replace(os.sep, "/")


def run(
    csv_dir: Path,
    output_dir: Path,
    base_url: str,
    title: str,
):
    templates_dir = Path(__file__).parent.parent / "templates"
    all_rows = load_all_csvs(csv_dir)

    by_year: dict[int, list] = defaultdict(list)
    by_month: dict[tuple, list] = defaultdict(list)
    for row in all_rows:
        t = datetime.fromisoformat(row["time"])
        by_year[t.year].append(row)
        by_month[(t.year, t.month)].append(row)

    all_months = sorted(by_month.keys())
    site = base_url.replace("https://", "").replace("http://", "").rstrip("/") or "Analytics"
    templates = PageTemplateLoader(search_path=[str(templates_dir)], default_extension=".pt")

    csv_files = sorted(csv_dir.rglob("*.csv"))
    latest_csv_mtime = max((f.stat().st_mtime for f in csv_files), default=0)
    template_mtime = (templates_dir / "analytics.pt").stat().st_mtime
    latest_source_mtime = max(latest_csv_mtime, template_mtime)

    def write_page(page_path: str, rows: list, nav: dict, period_label: str, always: bool = False):
        out = output_dir / page_path
        if not always and out.exists() and out.stat().st_mtime >= latest_source_mtime:
            return
        report = build_analytics(rows, base_url=base_url)
        page_title = title or f"{site} — {period_label}"
        html = templates["analytics"](
            report=report, title=page_title, json=json, datetime=datetime, nav=nav
        )
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html)
        print(out)

    all_years = sorted(by_year.keys(), reverse=True)
    year_buttons = [{"label": "All time", "url": "all/"}] + [
        {"label": str(y), "url": f"{y}/"} for y in all_years
    ]

    # Summary — last 30 days
    cutoff = datetime.now() - timedelta(days=30)
    summary_rows = [r for r in all_rows if datetime.fromisoformat(r["time"]) >= cutoff]
    summary_nav = {
        "type": "summary",
        "breadcrumbs": [],
        "years": year_buttons,
    }
    write_page("index.html", summary_rows, summary_nav, "Last 30 days", always=True)

    # All-time page
    all_time_nav = {
        "type": "all-time",
        "breadcrumbs": [{"label": "Summary", "url": "../"}],
        "years": [{"label": str(y), "url": f"../{y}/"} for y in all_years],
    }
    write_page("all/index.html", all_rows, all_time_nav, "All time")

    # Year pages
    for year in sorted(by_year.keys()):
        months_in_year = [(y, m) for y, m in all_months if y == year]
        year_nav = {
            "type": "year",
            "breadcrumbs": [{"label": "Summary", "url": "../"}],
            "years": [
                {"label": str(y), "url": f"../{y}/", "current": y == year} for y in all_years
            ],
            "months": [
                {"label": calendar.month_name[m], "url": f"{m:02d}/"}
                for _, m in sorted(months_in_year, reverse=True)
            ],
        }
        write_page(f"{year}/index.html", by_year[year], year_nav, str(year))

    # Month pages
    for year, month in all_months:
        page = f"{year}/{month:02d}/index.html"
        months_in_year = [(y, m) for y, m in all_months if y == year]
        month_nav = {
            "type": "month",
            "breadcrumbs": [
                {"label": "Summary", "url": _rel(page, "index.html")},
                {"label": str(year), "url": _rel(page, f"{year}/index.html")},
            ],
            "months": [
                {
                    "label": calendar.month_name[m],
                    "url": _rel(page, f"{y}/{m:02d}/index.html"),
                    "current": m == month,
                }
                for y, m in sorted(months_in_year, reverse=True)
            ],
        }
        write_page(page, by_month[(year, month)], month_nav, f"{calendar.month_name[month]} {year}")
