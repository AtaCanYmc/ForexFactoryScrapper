import logging
from src.scrapper.common import (
    build_url,
    get_page_html,
    parse_calendar_from_html,
    to_24h,
)

logger = logging.getLogger(__name__)

BASE_URL = "https://www.cryptocraft.com/calendar"


def get_url(day=1, month=1, year=2020, timeline="day"):
    return build_url(BASE_URL, day=day, month=month, year=year, timeline=timeline)


def get_crypto_page_html(url, timeout=10):
    return get_page_html(url, timeout=timeout)


def get_24h(day, month, year, am_pm, last=None):
    return to_24h(day, month, year, am_pm, last)


def _get_crypto_object(raw, url):
    """Convert a raw event dict to the normalized record shape."""
    return {
        "Impact": raw.get("Impact", "n/a"),
        "Event": raw.get("Event", "n/a"),
        "Actual": raw.get("Actual", "n/a"),
        "Forecast": raw.get("Forecast", "n/a"),
        "Previous": raw.get("Previous", "n/a"),
        "Time": raw.get("Time", "n/a"),
        "Page": url,
    }


def get_records(url):
    """Fetch calendar page, parse events and normalize to cryptorecord shape.

    Returns a list of records with keys: Impact, Event, Actual, Forecast, Previous, Time
    """
    page_html = get_page_html(url)
    raw = parse_calendar_from_html(page_html, url)

    normalized = []
    for r in raw:
        if not isinstance(r, dict):
            continue  # skip unexpected entries
        obj = _get_crypto_object(r, url)
        normalized.append(obj)
    return normalized
