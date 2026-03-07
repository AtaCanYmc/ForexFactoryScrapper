from ._constants import BASE_MONTH_NAMES


def build_url(base_url, day=1, month=1, year=2020, timeline="day"):
    """Build a calendar URL for the target site.

    Keeps the same date format used across scrapers: "Mon{day}.{year}" (e.g. Jan1.2020)
    """
    date_str = f"{BASE_MONTH_NAMES.get(month, 'Jan')}{day}.{year}"
    return f"{base_url}?{timeline}={date_str}"


def date_to_string(local_dt):
    """Convert a datetime object to the string format used in URLs (e.g. Jan1.2020)."""
    p_day = f"{local_dt.day:02d}"
    p_month = f"{local_dt.month:02d}"
    p_year = f"{local_dt.year:04d}"
    hour = f"{local_dt.hour:02d}"
    minute = f"{local_dt.minute:02d}"

    return f"{p_day}/{p_month}/{p_year} {hour}:{minute}"
