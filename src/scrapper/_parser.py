import logging
import re
import os
from datetime import datetime
from bs4 import BeautifulSoup
from pandas import DataFrame

from ._constants import BASE_MONTH_NUMBERS
from ._time import to_24h
from ._utils import date_to_string

logger = logging.getLogger(__name__)

# Read class selectors from environment (allows overriding via .env). Defaults kept as before.
TIME_CLASS = os.getenv("TIME", "calendar__time")
CURRENCY_CLASS = os.getenv("CURRENCY", "calendar__currency")
PREV_CLASS = os.getenv("PREVIOUS", "calendar__previous")
ACTUAL_CLASS = os.getenv("ACTUAL", "calendar__actual")
FORECAST_CLASS = os.getenv("FORECAST", "calendar__forecast")
IMPACT_CLASS = os.getenv("IMPACT", "calendar__impact")
EVENT_CLASS = os.getenv("EVENT", "calendar__event")
ROW_ID_ATTR = os.getenv("ROW_ID", "data-event-id")


def _find_table(soup):
    """Try a few selectors then fall back to any table with td."""
    selectors = [
        "table.calendar__table",
        "table.calendar",
        "table[class*='calendar']",
        "div.calendar__table",
        "div.calendar",
    ]
    for sel in selectors:
        table = soup.select_one(sel)
        if table:
            return table

    # Last resort: any table with a td
    for t in soup.find_all("table"):
        if t.find("td"):
            return t
    return None


def _find_start_row(table):
    """Locate the start row that contains the date text.

    Returns a Tag or raises ValueError if not found.
    """
    start_row = table.find_next("tr", class_="calendar__row--new-day")
    if not start_row:
        start_row = table.find_next(
            "tr", class_=re.compile(r"new[-_ ]?day|row--new-day")
        )
    if not start_row:
        start_span = table.select_one("span.date, .date")
        if start_span:
            start_row = start_span.find_parent("tr")
    if not start_row:
        first_tr = table.find("tr")
        if first_tr:
            start_row = first_tr
    if not start_row:
        logger.error("Start date row not found")
        raise ValueError("Start date row not found")
    return start_row


def _safe_cell_text(cell):
    """Safely extract text from a cell, returning '' if cell is None or has no text."""
    if cell is None:
        return ""
    return cell.get_text(strip=True) or "n/a"


def _find_date_node(start_row, table):
    """Return a Tag with date text or None.

    Tries row-local spans first, then a table-wide selector.
    """
    if start_row is None:
        return None
    # prefer explicit class
    node = start_row.find_next("span", class_="date")
    if node:
        return node
    node = start_row.find("span")
    if node and getattr(node, "text", None):
        return node
    # fallback to table-wide
    node = table.select_one("span.date, .date")
    if node:
        return node
    return None


def _extract_start_date(start_row, url, table):
    """Extract day, month, year from the start_row text or url.

    Returns (day, month, year) as ints or raises ValueError.
    """
    # Try to find a date node on the row first, then the table
    start_date = _find_date_node(start_row, table)

    if not start_date or not getattr(start_date, "text", None):
        logger.error("Start date text not found")
        raise ValueError("Start date text not found")

    dt_text = start_date.text.strip()

    # pattern: MonthName Day [Year]
    m = re.search(r"([A-Za-z]{3,9})\s+([0-9]{1,2})(?:,?\s*([0-9]{4}))?", dt_text)
    month = None
    day = None
    year = None
    if m:
        month_str = m.group(1)
        month_key = month_str[:3].title()
        month = BASE_MONTH_NUMBERS.get(month_key)
        try:
            day = int(m.group(2))
        except Exception:
            day = None
        if m.group(3):
            try:
                year = int(m.group(3))
            except Exception:
                year = None

    # Try to find year in url
    if year is None:
        yr_match = re.search(r"(20[0-9]{2})", url)
        if yr_match:
            try:
                year = int(yr_match.group(1))
            except Exception:
                year = None

    # Try any 4-digit year in table text
    if year is None:
        yr2 = re.search(r"(20[0-9]{2})", table.get_text())
        if yr2:
            try:
                year = int(yr2.group(1))
            except Exception:
                year = None

    if year is None:
        year = datetime.now().year

    # Alternative pattern like '01 Jan 2020' or 'Jan 01 2020'
    if month is None or day is None:
        m2 = re.search(r"([0-9]{1,2})[\-/ ]([A-Za-z]{3,9})[\-/ ]([0-9]{4})", dt_text)
        if m2:
            try:
                day = int(m2.group(1))
                month = BASE_MONTH_NUMBERS.get(m2.group(2)[:3].title())
                year = int(m2.group(3))
            except Exception:
                pass

    if month is None or day is None:
        logger.error("Failed to parse start date from text: %s", dt_text)
        raise ValueError("Failed to parse start date")

    return int(day), int(month), int(year)


def _find_cell_with_class(cells, class_name):
    """Helper to find a cell with a specific class in a list of cells.

    Behavior:
    - First, look for a td whose class list contains class_name.
    - Then, look for a descendant inside any td with that class and return the descendant.
    - Finally, fall back to a column index mapping (time=0, currency=1, event=2, forecast=3, actual=4, previous=5, impact=6)
    """
    # 1) direct td with class
    for cell in cells:
        if class_name in (cell.get("class") or []):
            return cell

    # 2) descendant element inside a td
    for cell in cells:
        descendant = cell.find(class_=class_name)
        if descendant:
            return descendant

    # 3) fallback by column index
    order = [
        TIME_CLASS,
        CURRENCY_CLASS,
        EVENT_CLASS,
        FORECAST_CLASS,
        ACTUAL_CLASS,
        PREV_CLASS,
        IMPACT_CLASS,
    ]
    try:
        idx = order.index(class_name)
        if idx < len(cells):
            return cells[idx]
    except ValueError:
        pass

    return None


def _find_impact_node(cell):
    """Locate the most likely node inside impact cell that indicates impact.

    Tries elements with known icon classes, then img, then span/div.
    """
    if cell is None:
        return None

    # 1) any element whose classes contain icon-like indicators
    for tag in cell.find_all(True):
        classes = tag.get("class") or []
        if any(
            re.search(r"icon|impact|calendar__impact-icon|icon--ff-impact", c)
            for c in classes
        ):
            return tag

    # 2) any img element (src often contains 'impact-yel' etc)
    img = cell.find("img")
    if img:
        return img

    # 3) fallback to span or div
    sp = cell.find("span")
    if sp:
        return sp
    dv = cell.find("div")
    if dv:
        return dv

    return None


def _normalize_impact_value(node):
    """Normalize the impact value from a node element using classes/src/alt/title.

    Returns one of: 'low', 'medium', 'high', or 'n/a'.
    """
    if node is None:
        return "n/a"

    # Collect candidate strings from classes, src, alt, title and text
    classes = " ".join(node.get("class") or [])
    src = node.get("src") or ""
    alt = node.get("alt") or ""
    title = node.get("title") or ""
    text = getattr(node, "text", "") or ""

    combined = " ".join([classes, src, alt, title, text]).lower()

    # Look for known markers
    if re.search(
        r"\b(yel|yellow|impact.*yel|impact.*yellow|impact-yel|ee-impact-yel)\b",
        combined,
    ):
        return "low"
    if re.search(r"\b(ora|orange|impact.*ora|impact.*orange|impact-ora)\b", combined):
        return "medium"
    if re.search(r"\b(red|impact.*red|impact-red)\b", combined):
        return "high"

    # Legacy class names used by previous parser
    if "icon--ff-impact-yel" in classes:
        return "low"
    if "icon--ff-impact-ora" in classes:
        return "medium"
    if "icon--ff-impact-red" in classes:
        return "high"

    return "n/a"


def _parse_row_to_record(row, base_day, base_month, base_year, dt):
    """Parse a single table row into a record dict or return None to skip.
    Args:
    dt: current rolling datetime used by to_24h
    Returns tuple (record_dict, updated_dt) or (None, dt) on skip.
    """
    row_class_arr = row.get("class") or []
    row_classes = " ".join(row_class_arr)
    if "head" in row_classes or ("new-day" in row_classes and not row.find("td")):
        return None, dt

    cells = row.find_all(["td"])
    if not cells:
        return None, dt

    # --------------- Data Event ID ---------------
    row_id = row.get(f"{ROW_ID_ATTR}", None)

    # --------------- Time ---------------
    time_cell = _find_cell_with_class(cells, TIME_CLASS)
    time_text = _safe_cell_text(time_cell)

    try:
        local_dt = to_24h(int(base_day), int(base_month), int(base_year), time_text, dt)
    except Exception:
        logger.exception("Failed to parse time for row")
        return None, dt

    # --------------- [Currency] ---------------
    curr_cell = _find_cell_with_class(cells, CURRENCY_CLASS)
    curr = _safe_cell_text(curr_cell)

    # --------------- Event ---------------
    event_cell = _find_cell_with_class(cells, EVENT_CLASS)
    name = _safe_cell_text(event_cell)
    if not name or name.lower() in ("n/a", "tbd", "tba"):
        return None, local_dt

    # --------------- Forecast ---------------
    forecast_cell = _find_cell_with_class(cells, FORECAST_CLASS)
    forecast = _safe_cell_text(forecast_cell)

    # --------------- Actual ---------------
    actual_cell = _find_cell_with_class(cells, ACTUAL_CLASS)
    actual = _safe_cell_text(actual_cell)

    # --------------- Previous ---------------
    prev_cell = _find_cell_with_class(cells, PREV_CLASS)
    previous = _safe_cell_text(prev_cell)

    # --------------- Impact ---------------
    impact_cell = _find_cell_with_class(cells, IMPACT_CLASS)
    impact_node = _find_impact_node(impact_cell)
    impact = _normalize_impact_value(impact_node)

    record = {
        "ID": row_id,
        "Time": date_to_string(local_dt),
        "Currency": curr,
        "Event": name,
        "Forecast": forecast,
        "Actual": actual,
        "Previous": previous,
        "Impact": impact,
    }

    return record, local_dt


def parse_calendar_from_html(html, url):
    """Parse a calendar page HTML and return a list of record dicts.

    Raises ValueError for parse problems (consistent with existing scrapers).
    """

    soup = BeautifulSoup(html, "html.parser")

    table = _find_table(soup)
    if table is None:
        logger.error("Calendar table not found in page")
        raise ValueError("Calendar table not found in page")

    start_row = _find_start_row(table)
    day, month, year = _extract_start_date(start_row, url, table)
    dt = datetime.now()

    table_body = table.find("tbody")
    rows = table_body.find_all("tr") if table_body else table.find_all("tr")
    recs = []
    for row in rows:
        try:
            rec, dt = _parse_row_to_record(row, day, month, year, dt)
            if not rec:
                continue
            recs.append(rec)
        except Exception:
            logger.exception("Failed to parse one event row, skipping")
            continue

    try:
        df = DataFrame(recs)
        return df.to_dict(orient="records")
    except Exception:
        logger.exception("Failed to convert records to DataFrame")
        raise ValueError("Failed to convert records to DataFrame")
