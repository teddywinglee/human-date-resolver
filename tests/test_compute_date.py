import pytest
from src.compute_date import compute

BASE = "2026-03-31"  # A Tuesday


class TestRelativeDays:
    def test_tomorrow(self):
        result = compute({"type": "relative_days", "value": 1}, BASE, "UTC")
        assert result["date"] == "2026-04-01T00:00:00+00:00"

    def test_yesterday(self):
        result = compute({"type": "relative_days", "value": -1}, BASE, "UTC")
        assert result["date"] == "2026-03-30T00:00:00+00:00"

    def test_in_3_days(self):
        result = compute({"type": "relative_days", "value": 3}, BASE, "UTC")
        assert result["date"] == "2026-04-03T00:00:00+00:00"

    def test_5_days_ago(self):
        result = compute({"type": "relative_days", "value": -5}, BASE, "UTC")
        assert result["date"] == "2026-03-26T00:00:00+00:00"

    def test_today(self):
        result = compute({"type": "relative_days", "value": 0}, BASE, "UTC")
        assert result["date"] == "2026-03-31T00:00:00+00:00"


class TestWeekday:
    def test_next_tuesday_on_tuesday(self):
        """'next Tuesday' when today is Tuesday should be next week's Tuesday."""
        result = compute({"type": "weekday", "direction": "next", "value": "tuesday"}, BASE, "UTC")
        assert result["date"] == "2026-04-07T00:00:00+00:00"

    def test_next_friday(self):
        result = compute({"type": "weekday", "direction": "next", "value": "friday"}, BASE, "UTC")
        assert result["date"] == "2026-04-03T00:00:00+00:00"

    def test_next_monday(self):
        """Monday is the day before Tuesday, so 'next Monday' = 6 days later."""
        result = compute({"type": "weekday", "direction": "next", "value": "monday"}, BASE, "UTC")
        assert result["date"] == "2026-04-06T00:00:00+00:00"

    def test_last_monday(self):
        """Monday before Tuesday March 31 = March 30."""
        result = compute({"type": "weekday", "direction": "last", "value": "monday"}, BASE, "UTC")
        assert result["date"] == "2026-03-30T00:00:00+00:00"

    def test_last_tuesday_on_tuesday(self):
        """'last Tuesday' when today is Tuesday should be last week's Tuesday."""
        result = compute({"type": "weekday", "direction": "last", "value": "tuesday"}, BASE, "UTC")
        assert result["date"] == "2026-03-24T00:00:00+00:00"

    def test_last_friday(self):
        result = compute({"type": "weekday", "direction": "last", "value": "friday"}, BASE, "UTC")
        assert result["date"] == "2026-03-27T00:00:00+00:00"

    def test_this_friday(self):
        """'this Friday' on a Tuesday = same week Friday."""
        result = compute({"type": "weekday", "direction": "this", "value": "friday"}, BASE, "UTC")
        assert result["date"] == "2026-04-03T00:00:00+00:00"

    def test_this_monday(self):
        """'this Monday' on a Tuesday = yesterday (same week Monday)."""
        result = compute({"type": "weekday", "direction": "this", "value": "monday"}, BASE, "UTC")
        assert result["date"] == "2026-03-30T00:00:00+00:00"


class TestRelativePeriod:
    def test_next_week(self):
        result = compute({"type": "relative_period", "unit": "week", "value": 1}, BASE, "UTC")
        assert result["date"] == "2026-04-07T00:00:00+00:00"

    def test_last_week(self):
        result = compute({"type": "relative_period", "unit": "week", "value": -1}, BASE, "UTC")
        assert result["date"] == "2026-03-24T00:00:00+00:00"

    def test_next_month(self):
        result = compute({"type": "relative_period", "unit": "month", "value": 1}, BASE, "UTC")
        assert result["date"] == "2026-04-30T00:00:00+00:00"

    def test_last_month(self):
        result = compute({"type": "relative_period", "unit": "month", "value": -1}, BASE, "UTC")
        assert result["date"] == "2026-02-28T00:00:00+00:00"

    def test_next_year(self):
        result = compute({"type": "relative_period", "unit": "year", "value": 1}, BASE, "UTC")
        assert result["date"] == "2027-03-31T00:00:00+00:00"

    def test_month_end_clamping(self):
        """March 31 + 1 month = April 30 (clamped, April has no 31st)."""
        result = compute({"type": "relative_period", "unit": "month", "value": 1}, "2026-03-31", "UTC")
        assert result["date"] == "2026-04-30T00:00:00+00:00"

    def test_leap_year_clamping(self):
        """Feb 29 in leap year + 1 year = Feb 28 in non-leap year."""
        result = compute({"type": "relative_period", "unit": "year", "value": 1}, "2028-02-29", "UTC")
        assert result["date"] == "2029-02-28T00:00:00+00:00"


class TestMonthDay:
    def test_first_of_next_month(self):
        result = compute({"type": "month_day", "month_offset": 1, "day": 1}, BASE, "UTC")
        assert result["date"] == "2026-04-01T00:00:00+00:00"

    def test_15th_of_next_month(self):
        result = compute({"type": "month_day", "month_offset": 1, "day": 15}, BASE, "UTC")
        assert result["date"] == "2026-04-15T00:00:00+00:00"

    def test_last_month_day(self):
        result = compute({"type": "month_day", "month_offset": -1, "day": 1}, BASE, "UTC")
        assert result["date"] == "2026-02-01T00:00:00+00:00"

    def test_day_clamping(self):
        """Requesting day 31 of April (which has 30 days) should clamp to 30."""
        result = compute({"type": "month_day", "month_offset": 1, "day": 31}, BASE, "UTC")
        assert result["date"] == "2026-04-30T00:00:00+00:00"


class TestTimezone:
    def test_new_york(self):
        result = compute({"type": "relative_days", "value": 1}, BASE, "America/New_York")
        assert result["date"] == "2026-04-01T00:00:00-04:00"

    def test_tokyo(self):
        result = compute({"type": "relative_days", "value": 1}, BASE, "Asia/Tokyo")
        assert result["date"] == "2026-04-01T00:00:00+09:00"

    def test_different_tz_different_timestamp(self):
        """Same date in different timezones should produce different timestamps."""
        utc = compute({"type": "relative_days", "value": 1}, BASE, "UTC")
        tokyo = compute({"type": "relative_days", "value": 1}, BASE, "Asia/Tokyo")
        assert utc["timestamp"] != tokyo["timestamp"]


class TestTimestamp:
    def test_epoch_ms(self):
        """2026-04-01 UTC = 1775001600 seconds = 1775001600000 ms."""
        result = compute({"type": "relative_days", "value": 1}, BASE, "UTC")
        assert result["timestamp"] == 1775001600000

    def test_timestamp_is_int(self):
        result = compute({"type": "relative_days", "value": 0}, BASE, "UTC")
        assert isinstance(result["timestamp"], int)
