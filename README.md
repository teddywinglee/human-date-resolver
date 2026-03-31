# Human Date Resolver

## Description
A set of Claude Code skills to resolve human-readable dates to machine-readable dates.
For example, "tomorrow" should be resolved to "2026-04-01" (if today is 2026-03-31) which translates to 1775001600000 in milliseconds since epoch.
Since humans read/write dates in many different habits and languages, we need a way to resolve them to machine-readable dates.

The pipeline separates NLP understanding (LLM) from date computation (code), as a learning exercise for building Claude Code skills:
1. **NLP → Structured Intent** (LLM): Parse natural language into a structured intent JSON
2. **Intent → Date + Timestamp** (Code): Compute the exact date deterministically
3. **Orchestrator** (Skill): Chains the above two steps into a single user-facing command

Timezone defaults to UTC when not specified, but can be provided as an input parameter.
A base date can be provided for reproducibility; defaults to today.

## Skills

### `/date-nlp-parser`
Parses natural language date expressions (in any language) into structured intent JSON.

```
/date-nlp-parser next Tuesday
```
```json
{"type": "weekday", "direction": "next", "value": "tuesday"}
```

### `/date-resolver`
User-facing orchestrator. Parses the expression, computes the date, and returns the full result.

```
/date-resolver next Tuesday UTC 2026-03-31
```
```json
{
    "input": "next Tuesday",
    "base": "2026-03-31",
    "timezone": "UTC",
    "intent": {"type": "weekday", "direction": "next", "value": "tuesday"},
    "date": "2026-04-07T00:00:00+00:00",
    "timestamp": 1775520000000
}
```

## Intent Types

| Type | Example | Intent |
|------|---------|--------|
| `relative_days` | "tomorrow" | `{"type": "relative_days", "value": 1}` |
| `weekday` | "next Tuesday" | `{"type": "weekday", "direction": "next", "value": "tuesday"}` |
| `relative_period` | "in 2 months" | `{"type": "relative_period", "unit": "month", "value": 2}` |
| `month_day` | "1st of next month" | `{"type": "month_day", "month_offset": 1, "day": 1}` |

## Lessons Learned

- **LLMs are bad at date math** — An initial single-skill design had the LLM resolve dates directly. It returned April 6 for "next Tuesday" (off by one) and inconsistent results across runs. Splitting NLP (LLM) from computation (code) solved this.
- **Splitting creates a testability boundary** — The compute layer has 29 deterministic tests. The LLM layer is non-deterministic by nature. The split makes it clear which parts are reliably testable.
- **Skill argument parsing is limited** — Multi-word inputs like "in 3 days" broke with positional args (`$0/$1/$2`). Using `$ARGUMENTS` and letting the LLM parse the full string was more robust.
- **LLMs don't reliably follow output format instructions** — Asking for "no markdown fences" still produced ` ```json ` wrapping. Consumers of skill output need to handle messy responses.
- **A base date parameter enables reproducibility** — Without it, tests break tomorrow. A small design choice that made the entire test suite possible.
- **Skills with code dependencies are not portable** — Pure-prompt skills (like `/date-nlp-parser`) can be copied anywhere. Skills that call code (like `/date-resolver`) are tied to the repo. The skill ecosystem doesn't yet have a standard for distributing hybrid skills.

## Development

```bash
uv sync              # Install dependencies
uv run pytest -v     # Run tests
```