# Human Date Resolver

A learning project for building Claude Code skills that resolve human-readable dates to machine-readable formats.

## Project Structure
- `.claude/skills/` — Claude Code skill definitions
- `src/` — Python source code
- `tests/` — Test cases and runners

## Tooling
- Python 3.14+, managed with `uv`
- Run code via `uv run python ...`
- Install deps: `uv sync`

## Pipeline
1. **date-nlp-parser** (skill, LLM) — natural language → structured intent JSON
2. **compute_date.py** (code) — intent + base date + timezone → ISO 8601 + timestamp
3. **date-resolver** (skill, orchestrator) — user-facing, chains parser → compute

## Conventions
- Default timezone is UTC when not specified
- Timestamps are in milliseconds since epoch
- ISO 8601 dates include time and timezone (e.g., `2026-04-07T00:00:00Z`)
