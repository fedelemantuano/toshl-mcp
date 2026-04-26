.PHONY: help install lint lint-fix format test pre-commit clean

help:
	@echo "Commands:"
	@echo "  install      Install all dependencies"
	@echo "  lint         Run ruff linter"
	@echo "  lint-fix     Run ruff linter with auto-fix"
	@echo "  format       Run ruff formatter"
	@echo "  test         Run tests"
	@echo "  pre-commit   Run pre-commit on all files"
	@echo "  clean        Remove build artifacts and caches"

install:
	uv sync

lint:
	uv run ruff check .

lint-fix:
	uv run ruff check --fix .

format:
	uv run ruff format .

test:
	uv run pytest

pre-commit:
	pre-commit run --all-files

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null; true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .ruff_cache dist build
