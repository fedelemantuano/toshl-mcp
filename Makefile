.PHONY: help install lint lint-fix format test test-cov pre-commit clean dev

# Variables
PYTHON := uv run python
PYTEST := uv run pytest
RUFF := uv run ruff
PRE_COMMIT := uv run pre-commit

help:
	@echo "Commands:"
	@echo "  install      Install all dependencies"
	@echo "  lint         Run ruff linter"
	@echo "  lint-fix     Run ruff linter with auto-fix"
	@echo "  format       Run ruff formatter"
	@echo "  test         Run tests"
	@echo "  test-cov     Run tests with coverage report"
	@echo "  pre-commit   Run pre-commit on all files"
	@echo "  dev          Run MCP inspector (loads .env)"
	@echo "  clean        Remove build artifacts and caches"

install:
	uv sync

lint:
	$(RUFF) check .

lint-fix:
	$(RUFF) check --fix .

format:
	$(RUFF) format .

test:
	$(PYTEST) tests/

test-cov:
	$(PYTEST) tests/ --cov=toshl_mcp --cov-report=term-missing --cov-report=html

dev:
	uv run --env-file .env mcp dev src/toshl_mcp/server.py

pre-commit:
	$(PRE_COMMIT) run --all-files

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null; true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .ruff_cache dist build htmlcov
