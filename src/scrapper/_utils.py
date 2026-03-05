from ._constants import BASE_MONTH_NAMES
import re


def build_url(base_url, day=1, month=1, year=2020, timeline="day"):
    """Build a calendar URL for the target site.

    Keeps the same date format used across scrapers: "Mon{day}.{year}" (e.g. Jan1.2020)
    """
    date_str = f"{BASE_MONTH_NAMES.get(month, 'Jan')}{day}.{year}"
    return f"{base_url}?{timeline}={date_str}"


def is_valid_calendar_time(time_str):
    """Check if a time string is in a valid format (e.g. '12:30pm', '9:00am')."""
    # Match formats like "12:30pm", "9:00am"
    pattern = r"^\s*(1[0-2]|0?[1-9])(:[0-5][0-9])?\s*(am|pm)\s*$"
    return re.match(pattern, time_str.strip(), re.IGNORECASE) is not None
