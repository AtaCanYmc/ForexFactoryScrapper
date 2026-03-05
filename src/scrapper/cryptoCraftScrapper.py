import logging
from src.scrapper.common import (
    build_url,
    get_page_html,
    parse_calendar_from_html,
    to_24h,
)

logger = logging.getLogger(__name__)

BASE_URL = "https://www.cryptocraft.com/calendar"


def getURL(day=1, month=1, year=2020, timeline="day"):
    return build_url(BASE_URL, day=day, month=month, year=year, timeline=timeline)


def getPageHTML(url, timeout=10):
    return get_page_html(url, timeout=timeout)


def get24H(day, month, year, am_pm, last=None):
    return to_24h(day, month, year, am_pm, last)


def _normalize_impact_value(val):
    """Normalize a raw impact-like value into 'low'/'medium'/'high' or empty string.

    Accepts values like 'Low', 'LOW', 'l', 'H', 'High', etc.
    """
    if val is None:
        return ""
    v = str(val).strip().lower()
    if not v:
        return ""
    # direct mapping
    if v in ("low", "medium", "high"):
        return v
    # single-letter shortcuts
    if v in ("l", "m", "h"):
        return {"l": "low", "m": "medium", "h": "high"}[v]
    # sometimes there might be words like 'Low impact' or similar
    if "low" in v:
        return "low"
    if "medium" in v or "med" in v:
        return "medium"
    if "high" in v:
        return "high"
    # fallback: not recognized
    return ""


def getRecords(url):
    """Fetch calendar page, parse events and normalize to cryptorecord shape.

    Returns a list of records with keys: Impact, Event, Actual, Forecast, Previous, Time
    """
    pageHTML = getPageHTML(url)
    raw = parse_calendar_from_html(pageHTML, url)

    normalized = []
    for r in raw:
        if not isinstance(r, dict):
            # skip unexpected entries
            continue
        # only use explicit Impact; do NOT map Currency into Impact
        raw_impact = r.get("Impact")
        impact = _normalize_impact_value(raw_impact)
        normalized.append(
            {
                "Impact": impact,
                "Event": r.get("Event"),
                "Actual": r.get("Actual"),
                "Forecast": r.get("Forecast"),
                "Previous": r.get("Previous"),
                "Time": r.get("Time"),
            }
        )
    return normalized
