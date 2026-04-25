from pathlib import Path

from . import is_processed, process_log_file


def run(input: Path, csv_dir: Path, pattern: str):
    gz_files = sorted(input.rglob(pattern)) if input.is_dir() else [input]
    for f in gz_files:
        if not is_processed(f, csv_dir):
            print(f"Processing {f}")
            n = process_log_file(f, csv_dir)
            print(f"  {n:,} rows -> {csv_dir / (f.name + '.csv')}")
