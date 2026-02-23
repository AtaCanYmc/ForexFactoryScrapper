import logging
import re
from datetime import datetime, timedelta

import cloudscraper
import pandas as pd
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

month_names = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec",
}

month_numbers = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12,
}


def getURL(day=1, month=1, year=2020, timeline="day"):
    date_str = f"{month_names.get(month, 'Jan')}{day}.{year}"
    url = f"https://www.forexfactory.com/calendar?{timeline}={date_str}"
    return url


def getPageHTML(url, timeout=10):  # gets url and returns source html
    scraper = cloudscraper.create_scraper()
    try:
        resp = scraper.get(url, timeout=timeout)
        resp.raise_for_status()
    except Exception as e:
        logger.exception("Failed to fetch page HTML")
        raise RuntimeError(f"Failed to get URL {url}: {e}")

    return resp.text


def get24H(day, month, year, am_pm, last=None):
    # Use sentinel for last to avoid B008.
    if last is None:
        last = datetime.now()

    # If event row says 'All Day' or similar, return midnight
    if "day" in am_pm.lower():
        return datetime(year, month, day, 0, 0)

    addH = 7

    if "pm" in am_pm:
        pm = am_pm.replace("pm", "")
        parts = pm.split(":")
        try:
            h = (int(parts[0].strip()) + 12) % 24
            m = int(parts[1].strip())
        except Exception:
            return last
    elif "am" in am_pm:
        am = am_pm.replace("am", "")
        parts = am.split(":")
        try:
            h = int(parts[0].strip())
            m = int(parts[1].strip())
        except Exception:
            return last
    else:
        return last

    evnt_date = datetime(year, month, day, h, m) + timedelta(hours=addH)

    return evnt_date


def getRecords(url):
    """Fetch calendar page and parse events into a list of dictionaries.

    Raises RuntimeError on network errors or ValueError on parse errors.
    """
    c_time = []
    c_curr = []
    c_event = []
    c_forecast = []
    c_actual = []
    c_prev = []

    pageHTML = getPageHTML(url)
    soup = BeautifulSoup(pageHTML, "html.parser")

    table = soup.find("table", class_="calendar__table")
    if table is None:
        logger.error("Calendar table not found in page")
        raise ValueError("Calendar table not found in page")

    events = table.find_all("td", class_="calendar__time")
    if not events:
        logger.info("No events found for url: %s", url)
        return []

    # start date
    start_row = table.find_next("tr", class_="calendar__row--new-day")
    if not start_row:
        logger.error("Start date row not found")
        raise ValueError("Start date row not found")

    startDate = start_row.find_next("span", class_="date")
    if not startDate or not startDate.text:
        logger.error("Start date text not found")
        raise ValueError("Start date text not found")

    matchObj = re.search("([a-zA-Z]{3}) ([a-zA-Z]{3}) ([0-9]{1,2})", startDate.text)
    if not matchObj:
        logger.error("Failed to parse start date from text: %s", startDate.text)
        raise ValueError("Failed to parse start date")

    month = month_numbers.get(matchObj.group(2), None)
    day = int(matchObj.group(3))
    year = int(url[-4:])
    dt = datetime.now()

    for event in events:
        try:
            time_text = event.text.strip()
            dt = get24H(int(day), int(month), int(year), time_text, dt)
            p_day = f"{dt.day:02d}"
            p_month = f"{dt.month:02d}"
            p_year = f"{dt.year:04d}"
            hour = f"{dt.hour:02d}"
            minute = f"{dt.minute:02d}"

            curr_td = event.find_next_sibling("td", class_="calendar__currency")
            if not curr_td:
                continue
            curr = curr_td.text.strip().replace("\n", "").replace(" ", "")
            if len(curr) == 0:
                continue

            ev_td = event.find_next_sibling("td", class_="calendar__event")
            name_span = ev_td.find_next("span") if ev_td else None
            name = name_span.text.strip() if name_span and name_span.text else "unknown"

            prev_td = event.find_next_sibling("td", class_="calendar__previous")
            previous = (
                (prev_td.text if prev_td else "").replace("\n", "").replace(" ", "")
            )
            previous = previous if len(previous) > 1 else "unknown"

            fcast_td = event.find_next_sibling("td", class_="calendar__forecast")
            forecast = (
                (fcast_td.text if fcast_td else "").replace("\n", "").replace(" ", "")
            )
            forecast = forecast if len(forecast) > 1 else "unknown"

            actual_td = event.find_next_sibling("td", class_="calendar__actual")
            actual = (
                (actual_td.text if actual_td else "").replace("\n", "").replace(" ", "")
            )
            actual = actual if len(actual) > 1 else "unknown"

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
        df = pd.DataFrame(data)
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
