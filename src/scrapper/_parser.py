import logging
import re
from datetime import datetime
from bs4 import BeautifulSoup

from ._constants import BASE_MONTH_NUMBERS
from ._time import to_24h

logger = logging.getLogger(__name__)


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


def _extract_start_date(start_row, url, table):
    """Extract day, month, year from the start_row text or url.

    Returns (day, month, year) as ints or raises ValueError.
    """
    # Try to find a span.date or any span
    startDate = start_row.find_next("span", class_="date")
    if not startDate:
        startDate = start_row.find("span")
    # If still not found on the start_row, try anywhere in the table (some markup places date differently)
    if not startDate:
        start_span = table.select_one("span.date, .date")
        if start_span:
            startDate = start_span

    if not startDate or not getattr(startDate, "text", None):
        logger.error("Start date text not found")
        raise ValueError("Start date text not found")

    dt_text = startDate.text.strip()

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


def _detect_header_indices(table, rows):
    """Detect header and return column indices for known fields.

    Returns a dict with keys: time, currency, event, forecast, actual, previous (values may be None).
    """
    header_cells = []
    header_row = None
    thead = table.find("thead")
    if thead:
        header_row = thead.find("tr")
    if not header_row:
        for r in rows:
            if r.find("th"):
                header_row = r
                break
    if not header_row and rows:
        header_row = rows[0]

    if header_row:
        header_cells = header_row.find_all(["th", "td"])
    header_texts = [
        (c.get_text(strip=True) or "").strip().lower() for c in header_cells
    ]

    def find_idx(keys):
        for key in keys:
            for i, h in enumerate(header_texts):
                if key in h:
                    return i
        return None

    time_col = find_idx(["time"])
    currency_col = find_idx(["currency", "curr"])
    event_col = find_idx(["event", "description", "detail", "news"])
    forecast_col = find_idx(["forecast", "fcast"])
    actual_col = find_idx(["actual", "value"])
    previous_col = find_idx(["previous", "prev"])

    if time_col is None:
        for i, c in enumerate(header_cells):
            cls = c.get("class") or []
            if any("time" in cl for cl in cls):
                time_col = i
                break

    def default_index(base, offset):
        try:
            if base is not None:
                return base + offset
        except Exception:
            pass
        return None

    if currency_col is None:
        currency_col = default_index(time_col, 1)
    if event_col is None:
        event_col = default_index(time_col, 2)
    if forecast_col is None:
        forecast_col = default_index(time_col, 3)
    if actual_col is None:
        actual_col = default_index(time_col, 4)
    if previous_col is None:
        previous_col = default_index(time_col, 5)

    return {
        "time": time_col,
        "currency": currency_col,
        "event": event_col,
        "forecast": forecast_col,
        "actual": actual_col,
        "previous": previous_col,
    }


def _parse_row_to_record(row, indices, base_day, base_month, base_year, dt):
    """Parse a single table row into a record dict or return None to skip.

    indices: dict from _detect_header_indices
    dt: current rolling datetime used by to_24h
    Returns tuple (record_dict, updated_dt) or (None, dt) on skip.
    """
    row_classes = " ".join(row.get("class") or [])
    if "head" in row_classes or ("new-day" in row_classes and not row.find("td")):
        return None, dt

    cells = row.find_all(["td", "th"])
    if not cells:
        return None, dt

    time_idx = indices.get("time")
    time_cell = None
    if time_idx is None:
        for idx, cell in enumerate(cells):
            txt = (cell.get_text() or "").strip().lower()
            cls = cell.get("class") or []
            if (
                any("time" in c for c in cls)
                or (":" in txt)
                or ("am" in txt)
                or ("pm" in txt)
                or ("day" in txt)
            ):
                time_idx = idx
                time_cell = cell
                break
        if time_idx is None:
            return None, dt
    else:
        if time_idx < 0 or time_idx >= len(cells):
            return None, dt
        time_cell = cells[time_idx]

    time_text = time_cell.get_text(strip=True)
    try:
        local_dt = to_24h(int(base_day), int(base_month), int(base_year), time_text, dt)
    except Exception:
        logger.exception("Failed to parse time for row")
        return None, dt

    p_day = f"{local_dt.day:02d}"
    p_month = f"{local_dt.month:02d}"
    p_year = f"{local_dt.year:04d}"
    hour = f"{local_dt.hour:02d}"
    minute = f"{local_dt.minute:02d}"

    def cell_text(i):
        if 0 <= i < len(cells):
            return cells[i].get_text(strip=True) or ""
        return ""

    def _extract_event_name_from_cell_by_index(i):
        # helper to extract event text from a cell index using robust selectors
        if not (0 <= i < len(cells)):
            return None
        cell = cells[i]
        # prefer explicit event title elements commonly used on sites
        selectors = [
            ".calendar__event-title",
            ".event-title",
            ".calendar__event",
            ".title",
        ]
        for sel in selectors:
            el = cell.select_one(sel)
            if el:
                txt = el.get_text(strip=True)
                if txt:
                    return txt
        # fallback to anchor text inside cell
        a = cell.find("a")
        if a:
            txt = a.get_text(strip=True)
            if txt:
                return txt
        # last resort: the whole cell text
        txt = cell.get_text(strip=True) or None
        return txt

    def _find_event_in_row():
        # Search the entire row first for common event title selectors
        selectors = [
            ".calendar__event-title",
            ".event-title",
            ".calendar__event",
            ".title",
            "[data-event-title]",
        ]
        for sel in selectors:
            el = row.select_one(sel)
            if el:
                txt = el.get_text(strip=True)
                if txt:
                    return txt

        # Look for anchors with meaningful text in the row
        for a in row.find_all("a"):
            txt = a.get_text(strip=True)
            if txt and not re.match(r"^[0-9:\s-]+$", txt):
                return txt

        return None

    # Currency
    curr = ""
    cur_idx = indices.get("currency")
    if cur_idx is not None:
        curr = cell_text(cur_idx).replace("\n", "").replace(" ", "")
    if not curr:
        curr = cell_text(time_idx + 1).replace("\n", "").replace(" ", "")
        if not curr:
            curr = cell_text(time_idx + 2).replace("\n", "").replace(" ", "")
    if not curr:
        return None, local_dt

    # Event
    # Prefer finding event inside the whole row (robust to column layout changes)
    name = _find_event_in_row()
    if not name:
        ev_idx = indices.get("event")
        if ev_idx is not None:
            name = _extract_event_name_from_cell_by_index(ev_idx)
        if not name:
            name = _extract_event_name_from_cell_by_index(time_idx + 2)
    if not name:
        name = "unknown"

    def clean_or_unknown(s):
        s2 = (s or "").replace("\n", "").replace(" ", "")
        return s2 if len(s2) > 1 else "unknown"

    forecast = clean_or_unknown(
        cell_text(
            indices.get("forecast")
            if indices.get("forecast") is not None
            else time_idx + 3
        )
    )
    actual = clean_or_unknown(
        cell_text(
            indices.get("actual") if indices.get("actual") is not None else time_idx + 4
        )
    )
    previous = clean_or_unknown(
        cell_text(
            indices.get("previous")
            if indices.get("previous") is not None
            else time_idx + 5
        )
    )

    record = {
        "Time": f"{p_day}/{p_month}/{p_year} {hour}:{minute}",
        "Currency": curr,
        "Event": name,
        "Forecast": forecast,
        "Actual": actual,
        "Previous": previous,
    }

    return record, local_dt


def parse_calendar_from_html(html, url):
    """Parse a calendar page HTML and return a list of record dicts.

    Raises ValueError for parse problems (consistent with existing scrapers).
    """
    from pandas import DataFrame  # imported lazily to keep module import lightweight

    c_time = []
    c_curr = []
    c_event = []
    c_forecast = []
    c_actual = []
    c_prev = []

    soup = BeautifulSoup(html, "html.parser")

    table = _find_table(soup)
    if table is None:
        logger.error("Calendar table not found in page")
        raise ValueError("Calendar table not found in page")

    start_row = _find_start_row(table)
    day, month, year = _extract_start_date(start_row, url, table)

    dt = datetime.now()

    tbody = table.find("tbody")
    rows = tbody.find_all("tr") if tbody else table.find_all("tr")

    indices = _detect_header_indices(table, rows)

    for row in rows:
        try:
            rec, dt = _parse_row_to_record(row, indices, day, month, year, dt)
            if not rec:
                continue
            c_time.append(rec["Time"])
            c_curr.append(rec["Currency"])
            c_event.append(rec["Event"])
            c_forecast.append(rec["Forecast"])
            c_actual.append(rec["Actual"])
            c_prev.append(rec["Previous"])
        except Exception:
            logger.exception("Failed to parse one event row, skipping")
            continue

    data = {
        "Time": c_time,
        "Currency": c_curr,
        "Event": c_event,
        "Forecast": c_forecast,
        "Actual": c_actual,
        "Previous": c_prev,
    }

    try:
        df = DataFrame(data)
        return df.to_dict(orient="records")
    except Exception:
        records = []
        for i in range(len(c_time)):
            records.append(
                {
                    "Time": c_time[i],
                    "Currency": c_curr[i],
                    "Event": c_event[i],
                    "Forecast": c_forecast[i],
                    "Actual": c_actual[i],
                    "Previous": c_prev[i],
                }
            )
        return records
