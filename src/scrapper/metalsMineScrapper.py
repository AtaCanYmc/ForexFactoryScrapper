import logging
from src.scrapper.common import (
    build_url,
    get_page_html,
    parse_calendar_from_html,
    to_24h,
)

logger = logging.getLogger(__name__)

BASE_URL = "https://www.metalsmine.com/calendar"


def getURL(day=1, month=1, year=2020, timeline="day"):
    return build_url(BASE_URL, day=day, month=month, year=year, timeline=timeline)


def getPageHTML(url, timeout=10):
    return get_page_html(url, timeout=timeout)


def get24H(day, month, year, am_pm, last=None):
    return to_24h(day, month, year, am_pm, last)


def getRecords(url):
    """Fetch calendar page and parse events into records (delegates to common parser)."""
    pageHTML = getPageHTML(url)
    return parse_calendar_from_html(pageHTML, url)
