# CLAUDE.md

## Engineering Principles

- **DRY** — extract repeated logic; no copy-paste code.
- **KISS** — simplest solution that works; no clever tricks.
- **YAGNI** — no code for hypothetical future needs.
- **SRP** — one function/class, one responsibility.
- **Fail fast** — validate at boundaries; trust internal code.
- No dead code, commented-out blocks, or unused imports.

## Python Style

Follow PEP8 standards.

## Workflow

- Stage with `git add` before `make pre-commit` — unstaged files ignored.

## Libraries

- HTTP retries via **tenacity** — no manual retry loops.

## Testing

- `tests/unittests/` mirrors `src/toshl_mcp/` structure.

## Documentation

- New feature or changed behavior → update `README.md`.
