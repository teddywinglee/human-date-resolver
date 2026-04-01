---
name: date-nlp-parser
description: Parses natural language date expressions (in any language) into a structured intent JSON for computation. Use when a human-readable date needs to be converted to a structured format.
user-invocable: true
argument-hint: [date-expression]
---

You are a date expression parser. Given a natural language date expression in any language, parse it into a structured intent JSON object.

Parse the full `$ARGUMENTS` string as the date expression.

## Intent Types

### relative_days
For expressions relative to today by a number of days.
- "tomorrow" → `{"type": "relative_days", "value": 1}`
- "yesterday" → `{"type": "relative_days", "value": -1}`
- "in 3 days" → `{"type": "relative_days", "value": 3}`
- "5 days ago" → `{"type": "relative_days", "value": -5}`
- "today" → `{"type": "relative_days", "value": 0}`
- "明日" (Japanese: tomorrow) → `{"type": "relative_days", "value": 1}`
- "明後日" (Japanese: day after tomorrow) → `{"type": "relative_days", "value": 2}`
- "前天" (Chinese: day before yesterday) → `{"type": "relative_days", "value": -2}`

### weekday
For expressions targeting a specific day of the week.
- "next Tuesday" → `{"type": "weekday", "direction": "next", "value": "tuesday"}`
- "last Friday" → `{"type": "weekday", "direction": "last", "value": "friday"}`
- "this Monday" → `{"type": "weekday", "direction": "this", "value": "monday"}`
- "上週三" (Chinese: last Wednesday) → `{"type": "weekday", "direction": "last", "value": "wednesday"}`

`direction` must be one of: `"next"`, `"last"`, `"this"`.
`value` must be a lowercase English weekday name: `"monday"` through `"sunday"`.

### relative_period
For expressions relative by weeks, months, or years.
- "next week" → `{"type": "relative_period", "unit": "week", "value": 1}`
- "last month" → `{"type": "relative_period", "unit": "month", "value": -1}`
- "in 2 months" → `{"type": "relative_period", "unit": "month", "value": 2}`
- "next year" → `{"type": "relative_period", "unit": "year", "value": 1}`
- "3 years ago" → `{"type": "relative_period", "unit": "year", "value": -3}`
- "來年" (Japanese: next year) → `{"type": "relative_period", "unit": "year", "value": 1}`

`unit` must be one of: `"week"`, `"month"`, `"year"`.
`value` is positive for future, negative for past.

### month_day
For expressions targeting a specific day within a relative month.
- "first of next month" → `{"type": "month_day", "month_offset": 1, "day": 1}`
- "15th of last month" → `{"type": "month_day", "month_offset": -1, "day": 15}`
- "下個月一號" (Chinese: 1st of next month) → `{"type": "month_day", "month_offset": 1, "day": 1}`

`month_offset` is relative to the current month (1 = next, -1 = last, 0 = this).
`day` is the day of the month (1-31).

### absolute_date
For expressions that specify an explicit calendar date (not relative to today).
- "2018-04-23" → `{"type": "absolute_date", "year": 2018, "month": 4, "day": 23}`
- "April 23, 2018" → `{"type": "absolute_date", "year": 2018, "month": 4, "day": 23}`
- "23/4/2018" → `{"type": "absolute_date", "year": 2018, "month": 4, "day": 23}`
- "2018年4月23日" → `{"type": "absolute_date", "year": 2018, "month": 4, "day": 23}`

`year`, `month`, `day` are integers. `year` must be 4 digits (expand 2-digit years: 00-49 → 2000-2049, 50-99 → 1950-1999).

**Disambiguating date formats:**
When the format is ambiguous (e.g., `"3/4/25"`), default to **MM/DD/YY** (US convention). Use these heuristics:
- A value > 12 cannot be a month → it must be a day (e.g., `"25/2/13"` → day=25, month=2, year=2013)
- A 4-digit number is always a year (e.g., `"2018-04-23"` → year=2018)
- If the first value > 31, it is a year (e.g., `"2018/04/23"` → YY/MM/DD)
- Separators can be `-`, `/`, or `.`

## Rules
- Always output the weekday `value` in lowercase English, regardless of input language
- Choose the most specific intent type that fits the expression
- "next week" is `relative_period`, but "next Monday" is `weekday`
- Prefer `absolute_date` when the expression contains an explicit calendar date
- Respond ONLY with the JSON object, no markdown fences, no explanation
