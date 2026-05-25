"""
MCP server exposing the date resolver as a tool.

The LLM constructs a structured intent (same schema as date-nlp-parser skill),
then calls this tool to compute the ISO 8601 date and Unix timestamp.

Run via: uv run python src/mcp_server.py
"""

from mcp.server.fastmcp import FastMCP
from src.compute_date import compute

mcp = FastMCP("human-date-resolver")


@mcp.tool()
def resolve_date(
    intent: dict,
    timezone: str = "UTC",
    base_date: str | None = None,
) -> dict:
    """Compute an ISO 8601 date and Unix timestamp (ms) from a structured date intent.

    intent must be one of:
      {"type": "relative_days", "value": <int>}
        e.g. tomorrow = {"type": "relative_days", "value": 1}
      {"type": "weekday", "direction": "next"|"last"|"this", "value": "<weekday>"}
        e.g. {"type": "weekday", "direction": "next", "value": "tuesday"}
      {"type": "relative_period", "unit": "week"|"month"|"year", "value": <int>}
        e.g. {"type": "relative_period", "unit": "month", "value": 2}
      {"type": "month_day", "month_offset": <int>, "day": <int>}
        e.g. {"type": "month_day", "month_offset": 1, "day": 1}
      {"type": "absolute_date", "year": <int>, "month": <int>, "day": <int>}
        e.g. {"type": "absolute_date", "year": 2018, "month": 4, "day": 23}

    timezone: IANA timezone name (default: UTC)
    base_date: ISO 8601 date string used as "today" (default: actual today)
    """
    return compute(intent, base_date, timezone)


if __name__ == "__main__":
    mcp.run()
