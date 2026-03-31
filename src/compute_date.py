"""
Compute a resolved date from a structured intent.

Intent schema:
  {"type": "relative_days", "value": int}
    e.g., tomorrow = {"type": "relative_days", "value": 1}
    e.g., 3 days ago = {"type": "relative_days", "value": -3}

  {"type": "weekday", "direction": "next"|"last"|"this", "value": "monday"|...|"sunday"}
    e.g., next Tuesday = {"type": "weekday", "direction": "next", "value": "tuesday"}

  {"type": "relative_period", "unit": "week"|"month"|"year", "value": int}
    e.g., in 2 months = {"type": "relative_period", "unit": "month", "value": 2}
    e.g., last year = {"type": "relative_period", "unit": "year", "value": -1}

  {"type": "month_day", "direction": "next"|"last"|"this", "month_offset": int, "day": int}
    e.g., first day of next month = {"type": "month_day", "month_offset": 1, "day": 1}

Usage:
  python compute_date.py '<intent_json>' [base_date] [timezone]

  base_date: ISO 8601 date string (default: today)
  timezone:  IANA timezone name (default: UTC)

Output:
  JSON with "date" (ISO 8601) and "timestamp" (ms since epoch)
"""

import json
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

WEEKDAYS = {
    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
    "friday": 4, "saturday": 5, "sunday": 6,
}


def compute_relative_days(base, value):
    return base + timedelta(days=value)


def compute_weekday(base, direction, day_name):
    target_weekday = WEEKDAYS[day_name.lower()]
    current_weekday = base.weekday()
    diff = target_weekday - current_weekday

    if direction == "next":
        # Always at least 1 week ahead if same day or past
        if diff <= 0:
            diff += 7
    elif direction == "last":
        # Always at least 1 day back
        if diff >= 0:
            diff -= 7
    elif direction == "this":
        # Same week: could be before or after today
        pass

    return base + timedelta(days=diff)


def compute_relative_period(base, unit, value):
    if unit == "week":
        return base + timedelta(weeks=value)
    elif unit == "month":
        month = base.month + value
        year = base.year + (month - 1) // 12
        month = (month - 1) % 12 + 1
        day = min(base.day, _days_in_month(year, month))
        return base.replace(year=year, month=month, day=day)
    elif unit == "year":
        year = base.year + value
        day = min(base.day, _days_in_month(year, base.month))
        return base.replace(year=year, day=day)


def compute_month_day(base, month_offset, day):
    month = base.month + month_offset
    year = base.year + (month - 1) // 12
    month = (month - 1) % 12 + 1
    day = min(day, _days_in_month(year, month))
    return base.replace(year=year, month=month, day=day)


def _days_in_month(year, month):
    if month == 12:
        return (datetime(year + 1, 1, 1) - datetime(year, 12, 1)).days
    return (datetime(year, month + 1, 1) - datetime(year, month, 1)).days


def compute(intent, base_date_str=None, timezone_str="UTC"):
    tz = ZoneInfo(timezone_str)

    if base_date_str:
        base = datetime.strptime(base_date_str, "%Y-%m-%d").replace(tzinfo=tz)
    else:
        base = datetime.now(tz).replace(hour=0, minute=0, second=0, microsecond=0)

    intent_type = intent["type"]

    if intent_type == "relative_days":
        result = compute_relative_days(base, intent["value"])
    elif intent_type == "weekday":
        result = compute_weekday(base, intent["direction"], intent["value"])
    elif intent_type == "relative_period":
        result = compute_relative_period(base, intent["unit"], intent["value"])
    elif intent_type == "month_day":
        result = compute_month_day(base, intent["month_offset"], intent["day"])
    else:
        raise ValueError(f"Unknown intent type: {intent_type}")

    result = result.replace(hour=0, minute=0, second=0, microsecond=0)
    timestamp_ms = int(result.timestamp() * 1000)

    return {
        "date": result.isoformat(),
        "timestamp": timestamp_ms,
    }


if __name__ == "__main__":
    intent = json.loads(sys.argv[1])
    base_date = sys.argv[2] if len(sys.argv) > 2 else None
    timezone = sys.argv[3] if len(sys.argv) > 3 else "UTC"

    result = compute(intent, base_date, timezone)
    print(json.dumps(result))
