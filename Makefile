PIP := pip
POETRY := poetry
PYTHON := python
LOGS_DIR := apache2
LOGS_PATTERN := files.bennuttall.com-access*
CSV_DIR := csv
OUTPUT_DIR := www
BASE_URL := https://files.bennuttall.com
TITLE := files.bennuttall.com

develop:
	$(PIP) install -U pip
	$(PIP) install "poetry>2"
	$(POETRY) install --all-extras --with dev

logs:
	$(PYTHON) -m lars_analytics.cli logs $(LOGS_DIR) --csv-dir $(CSV_DIR) --pattern "$(LOGS_PATTERN)"

analytics:
	$(PYTHON) -m lars_analytics.cli analytics --csv-dir $(CSV_DIR) --output-dir $(OUTPUT_DIR) --base-url $(BASE_URL) --title "$(TITLE)"

lint:
	$(POETRY) run isort . --check-only
	$(POETRY) run black . --check

format:
	$(POETRY) run isort .
	$(POETRY) run black .

.PHONY: develop logs analytics lint format