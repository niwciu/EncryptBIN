# Development helper — Linux / macOS only.
# Windows: run the individual commands in the venv manually.

VENV  := .venv
BIN   := $(VENV)/bin
SRC   := src
TESTS := tests

.PHONY: install lint format format-check type-check security test check clean help

help:
	@echo "Available targets:"
	@echo "  install       Create venv and install all dev dependencies"
	@echo "  lint          Run ruff + flake8"
	@echo "  format        Auto-format with black"
	@echo "  format-check  Check formatting without modifying files"
	@echo "  type-check    Run mypy"
	@echo "  security      Run bandit + pip-audit"
	@echo "  test          Run pytest with coverage"
	@echo "  check         Run all of the above (lint, format-check, type-check, security, test)"
	@echo "  clean         Remove venv, build artefacts, and caches"

install:
	python -m venv $(VENV)
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -e ".[gui,dev]"

lint:
	$(BIN)/ruff check $(SRC)/ $(TESTS)/
	$(BIN)/flake8 $(SRC) $(TESTS)

format:
	$(BIN)/black $(SRC) $(TESTS)

format-check:
	$(BIN)/black --check $(SRC) $(TESTS)

type-check:
	$(BIN)/mypy $(SRC)

security:
	$(BIN)/bandit -r $(SRC)/ -ll -x $(SRC)/encrypt_bin/gui/resources
	$(BIN)/pip-audit --skip-editable

test:
	QT_QPA_PLATFORM=offscreen $(BIN)/pytest

check: lint format-check type-check security test
	@echo "All checks passed."

clean:
	rm -rf $(VENV) dist build __pycache__ .pytest_cache .mypy_cache .ruff_cache *.spec
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
