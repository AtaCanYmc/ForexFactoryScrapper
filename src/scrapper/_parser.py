import logging
import re
from datetime import datetime
from bs4 import BeautifulSoup

from ._constants import BASE_MONTH_NUMBERS
from ._time import to_24h

logger = logging.getLogger(__name__)


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

    # Try a few selectors for the calendar table to support slightly different site markup
    table = None
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
            break

    if table is None:
        # Last resort: look for any table with a td that looks like a time cell
        for t in soup.find_all("table"):
            if t.find("td"):
                table = t
                break

    if table is None:
        logger.error("Calendar table not found in page")
        raise ValueError("Calendar table not found in page")

    # start date: try several strategies to locate the start row / date text
    start_row = None
    start_row = table.find_next("tr", class_="calendar__row--new-day")
    if not start_row:
        # try common alternative class names
        start_row = table.find_next(
            "tr", class_=re.compile(r"new[-_ ]?day|row--new-day")
        )
    if not start_row:
        # try to find a span.date anywhere in the table
        start_span = table.select_one("span.date, .date")
        if start_span:
            # use its parent row
            start_row = start_span.find_parent("tr")
    if not start_row:
        # As a last resort, use the first row of the table
        first_tr = table.find("tr")
        if first_tr:
            start_row = first_tr

    if not start_row:
        logger.error("Start date row not found")
        raise ValueError("Start date row not found")

    startDate = None
    # Try to find a date text in a span or the row text
    startDate = start_row.find_next("span", class_="date")
    if not startDate:
        startDate = start_row.find("span")
    if not startDate:
        # try to search within the row text for a date-like substring
        row_text = start_row.get_text(separator=" ") if start_row else ""

        # small wrapper creating a dummy object with .text
        class _D:
            def __init__(self, t):
                self.text = t

        startDate = _D(row_text)

    if not startDate or not getattr(startDate, "text", None):
        logger.error("Start date text not found")
        raise ValueError("Start date text not found")

    # Attempt flexible date parsing (supporting variants like 'Wed Jan 01', 'Jan 1, 2020', etc.)
    dt_text = startDate.text.strip()
    # patterns: capture month (short or long), day and optional year
    m = re.search(r"([A-Za-z]{3,9})\s+([0-9]{1,2})(?:,?\s*([0-9]{4}))?", dt_text)
    month = None
    day = None
    year = None
    if m:
        month_str = m.group(1)
        # normalize to first 3 letters
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

    # If we failed to parse month/day from the text, try to find a year in the URL or elsewhere
    if year is None:
        yr_match = re.search(r"(20[0-9]{2})", url)
        if yr_match:
            try:
                year = int(yr_match.group(1))
            except Exception:
                year = None

    # As a last resort, try to find any 4-digit year in the whole table
    if year is None:
        yr2 = re.search(r"(20[0-9]{2})", table.get_text())
        if yr2:
            try:
                year = int(yr2.group(1))
            except Exception:
                year = None

    # If still missing, default to current year
    if year is None:
        year = datetime.now().year

    if month is None or day is None:
        # Try alternative parsing like 'Jan 01 2020' or '01 Jan 2020'
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

    dt = datetime.now()

    # Prefer iterating rows (tbody) to avoid picking header cells from thead.
    tbody = table.find("tbody")
    rows = tbody.find_all("tr") if tbody else table.find_all("tr")

    # Detect header row to map column indices (helps when sites use different column orders)
    header_cells = []
    header_row = None
    thead = table.find("thead")
    if thead:
        header_row = thead.find("tr")
    if not header_row:
        # try first non-empty row that has th cells
        for r in rows:
            if r.find("th"):
                header_row = r
                break
    if not header_row and rows:
        # fallback to first row
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

    # Common column name candidates
    time_col = find_idx(["time"])
    currency_col = find_idx(["currency", "curr"])
    event_col = find_idx(["event", "description", "detail", "news"])
    forecast_col = find_idx(["forecast", "fcast"])
    actual_col = find_idx(["actual", "value"])
    previous_col = find_idx(["previous", "prev"])

    # If time_col not found try to detect via class or content in header_texts
    if time_col is None:
        for i, c in enumerate(header_cells):
            cls = c.get("class") or []
            if any("time" in cl for cl in cls):
                time_col = i
                break

    # default offsets relative to time_col if mapping incomplete
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

    for row in rows:
        try:
            # Skip header-like rows
            row_classes = " ".join(row.get("class") or [])
            if "head" in row_classes or "new-day" in row_classes and not row.find("td"):
                continue
            # Collect cells in this row to pick values by index (keeps siblings consistent)
            cells = row.find_all(["td", "th"])
            if not cells:
                continue

            # Try to find time cell index within the row if header mapping didn't provide one
            # Determine time index using header mapping where possible
            time_idx = time_col
            if time_idx is None:
                time_idx = None
                time_cell = None
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
                    continue
            else:
                # safe-guard: ensure time_idx within cells
                if time_idx < 0 or time_idx >= len(cells):
                    continue
                time_cell = cells[time_idx]

            time_text = time_cell.get_text(strip=True)
            dt = to_24h(int(day), int(month), int(year), time_text, dt)
            p_day = f"{dt.day:02d}"
            p_month = f"{dt.month:02d}"
            p_year = f"{dt.year:04d}"
            hour = f"{dt.hour:02d}"
            minute = f"{dt.minute:02d}"

            def cell_text(i):
                if 0 <= i < len(cells):
                    return cells[i].get_text(strip=True) or ""
                return ""

            # Use header-mapped columns where available
            curr = ""
            if currency_col is not None:
                curr = cell_text(currency_col).replace("\n", "").replace(" ", "")
            if not curr:
                # fallback offsets
                curr = cell_text(time_idx + 1).replace("\n", "").replace(" ", "")
                if not curr:
                    curr = cell_text(time_idx + 2).replace("\n", "").replace(" ", "")
            if not curr:
                continue

            # Event name and metrics using mapped indices or default offsets
            if event_col is not None:
                name = cell_text(event_col) or "unknown"
            else:
                name = cell_text(time_idx + 2) or "unknown"

            forecast = (
                cell_text(forecast_col)
                if forecast_col is not None
                else cell_text(time_idx + 3)
            ).replace("\n", "").replace(" ", "") or "unknown"
            actual = (
                cell_text(actual_col)
                if actual_col is not None
                else cell_text(time_idx + 4)
            ).replace("\n", "").replace(" ", "") or "unknown"
            previous = (
                cell_text(previous_col)
                if previous_col is not None
                else cell_text(time_idx + 5)
            ).replace("\n", "").replace(" ", "") or "unknown"

            forecast = forecast if len(forecast) > 1 else "unknown"
            actual = actual if len(actual) > 1 else "unknown"
            previous = previous if len(previous) > 1 else "unknown"

            c_time.append(f"{p_day}/{p_month}/{p_year} {hour}:{minute}")
            c_curr.append(curr)
            c_event.append(name)
            c_forecast.append(forecast)
            c_actual.append(actual)
            c_prev.append(previous)
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
