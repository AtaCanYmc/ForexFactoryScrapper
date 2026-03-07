import logging
from src.scrapper.common import (
    build_url,
    get_page_html,
    parse_calendar_from_html,
    to_24h,
)

logger = logging.getLogger(__name__)

BASE_URL = "https://www.forexfactory.com/calendar"


def get_url(day=1, month=1, year=2020, timeline="day"):
    return build_url(BASE_URL, day=day, month=month, year=year, timeline=timeline)


def get_forex_page_html(url, timeout=10):
    return get_page_html(url, timeout=timeout)


def get_24h(day, month, year, am_pm, last=None):
    return to_24h(day, month, year, am_pm, last)


def get_records(url):
    """Fetch calendar page and parse events into records (delegates to common parser)."""
    page_html = get_forex_page_html(url)
    return parse_calendar_from_html(page_html, url)
