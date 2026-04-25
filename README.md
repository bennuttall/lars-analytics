# lars-analytics

Log processing and analytics site generator for file servers.

Processes Apache access logs into CSV, then generates a static HTML analytics
site with breakdowns by file, directory, extension, referrer, and user agent.

## Usage

### Process logs

```
lars-analytics logs <log-dir> --csv-dir <csv-dir> --pattern "<pattern>"
```

- `<log-dir>` — directory containing gzipped Apache access logs
- `--csv-dir` — where to write the processed CSV files
- `--pattern` — glob pattern to match log files (default: `*.gz`)

Already-processed files are skipped on subsequent runs.

### Generate analytics

```
lars-analytics analytics --csv-dir <csv-dir> --output-dir <output-dir> [--base-url <url>] [--title <title>]
```

- `--csv-dir` — directory of CSV files produced by the `logs` step
- `--output-dir` — where to write the HTML analytics site
- `--base-url` — base URL of the file server, used for links (optional)
- `--title` — page title (optional)

Generates a static site with summary, all-time, yearly, and monthly pages.
Pages that are up to date are skipped.

## What gets counted

Only HTTP 200, 206, and 304 responses are written to CSV. The following paths
are excluded from analytics:

- `/icons/` — typically server icon assets
- `/.well-known/` — ACME challenge and similar infrastructure paths

## Installation

```
pip install lars-analytics
```
