# CLAUDE.md

## Engineering Principles

- **DRY** — extract repeated logic; no copy-paste code.
- **KISS** — simplest solution that works; no clever tricks.
- **YAGNI** — no code for hypothetical future needs.
- **SRP** — one function/class, one responsibility.
- **Fail fast** — validate at boundaries; trust internal code.
- No dead code, commented-out blocks, or unused imports.

## Python style

- Follow PEP 8 by default.
- Use 4 spaces, never tabs.
- Keep lines short: 79 chars for code, 72 for comments/docstrings.
- Use snake_case for functions/variables, CapWords for classes, UPPER_CASE for constants.
- Put spaces around operators and after commas; avoid extra spaces inside brackets/parentheses.
- Separate top-level defs/classes with 2 blank lines.
- Organize imports: stdlib, third-party, local.
- Avoid trailing whitespace and ensure UTF-8 files with a final newline.
- Prefer readable code, clear comments, and informative docstrings.
- Use parentheses for wrapping long lines; avoid backslashes when possible.
- Respect repo-specific formatter/linter rules if they exist.

## Workflow

- Stage with `git add` before `make pre-commit` — unstaged files ignored.
- Run `make pre-commit` after every code change.

## Libraries

- HTTP retries via **tenacity** — no manual retry loops.

## Testing

- `tests/unittests/` mirrors `src/toshl_mcp/` structure.

## Documentation

- New feature or changed behavior → update `README.md`.
