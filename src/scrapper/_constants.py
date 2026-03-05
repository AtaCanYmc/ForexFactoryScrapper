"""Shared constants for scrapers: month name/number mappings and small config values."""
BASE_MONTH_NAMES = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec",
}

BASE_MONTH_NUMBERS = {v: k for k, v in BASE_MONTH_NAMES.items()}

# default timezone/hour shift used by some scrapers; keep 0 by default but allow overrides
DEFAULT_HOUR_OFFSET = 0
