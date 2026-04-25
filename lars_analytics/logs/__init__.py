import csv
import gzip
import io
import warnings
from pathlib import Path

from lars.apache import ApacheSource, ApacheWarning

from .ua import parse_ua


# Workaround: lars bug; User-Agent instead of User-agent
COMBINED = '%h %l %u %t "%r" %>s %b "%{Referer}i" "%{User-Agent}i"'

warnings.filterwarnings("ignore", category=ApacheWarning)


def get_csv_path(gz_file: Path, csv_dir: Path) -> Path:
    return csv_dir / (gz_file.name + ".csv")


def normalise_path(path: str) -> str:
    while "//" in path:
        path = path.replace("//", "/")
    p = path.lower()
    if p.endswith("/index.html") or p.endswith("/index.htm"):
        return path[: path.rfind("/") + 1]
    return path


def referer_domain(referer_url) -> str:
    if not referer_url or not referer_url.netloc:
        return ""
    domain = referer_url.netloc.lstrip("www.").lower().split(":")[0]
    # Reject anything that isn't a valid hostname (blocks XSS/spam probes)
    if not all(c.isalnum() or c in "-." for c in domain):
        return ""
    return domain


def is_processed(gz_file: Path, csv_dir: Path) -> bool:
    return get_csv_path(gz_file, csv_dir).exists()


def process_log_file(gz_file: Path, csv_dir: Path) -> int:
    csv_path = get_csv_path(gz_file, csv_dir)
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    with io.TextIOWrapper(gzip.open(gz_file, "rb"), encoding="ascii") as logf:
        with ApacheSource(logf, COMBINED) as src:
            for row in src:
                if (
                    row.status in (200, 206, 304)
                    and row.request is not None
                    and row.request.url is not None
                ):
                    ua_name, is_bot = parse_ua(row.req_User_Agent)
                    rows.append(
                        [
                            row.time,
                            row.remote_host,
                            normalise_path(row.request.url.path_str),
                            ua_name,
                            is_bot,
                            referer_domain(row.req_Referer),
                            row.status,
                        ]
                    )

    with open(csv_path, "w", newline="") as csvf:
        writer = csv.writer(csvf)
        writer.writerow(["time", "remote_host", "path", "ua", "is_bot", "referer", "status"])
        writer.writerows(rows)

    return len(rows)
