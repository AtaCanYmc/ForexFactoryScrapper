from ._constants import BASE_MONTH_NAMES


def build_url(base_url, day=1, month=1, year=2020, timeline="day"):
    """Build a calendar URL for the target site.

    Keeps the same date format used across scrapers: "Mon{day}.{year}" (e.g. Jan1.2020)
    """
    date_str = f"{BASE_MONTH_NAMES.get(month, 'Jan')}{day}.{year}"
    return f"{base_url}?{timeline}={date_str}"
