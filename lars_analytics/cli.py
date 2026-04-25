import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(prog="lars-analytics")
    subparsers = parser.add_subparsers(dest="command", required=True)

    logs_p = subparsers.add_parser("logs", help="Process Apache log gz files into CSV")
    logs_p.add_argument("input", type=Path, help="gz file or directory of gz files")
    logs_p.add_argument("--csv-dir", type=Path, required=True)
    logs_p.add_argument("--pattern", default="*.gz")

    ana_p = subparsers.add_parser("analytics", help="Generate HTML analytics site from log CSVs")
    ana_p.add_argument("--csv-dir", type=Path, required=True)
    ana_p.add_argument("--output-dir", type=Path, required=True)
    ana_p.add_argument("--base-url", default="")
    ana_p.add_argument("--title", default="")

    args = parser.parse_args()

    if args.command == "logs":
        from .logs.cli import run
        run(args.input, args.csv_dir, args.pattern)

    elif args.command == "analytics":
        from .analytics.cli import run
        run(args.csv_dir, args.output_dir, args.base_url, args.title)


if __name__ == "__main__":
    main()
