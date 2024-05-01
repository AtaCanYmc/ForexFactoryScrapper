import cloudscraper
from bs4 import BeautifulSoup
from datetime import date, timedelta, datetime
import re
import time
import calendar
import pandas as pd
import json
import http.client

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
    12: "Dec"
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
    "Dec": 12
}


def getURL(day=1, month=1, year=2020, timeline='day'):
    date = f'{month_names.get(month, "Jan")}{day}.{year}'
    url = f'https://www.forexfactory.com/calendar?{timeline}={date}'
    return url

def getPageHTML(url):  # gets url and returns source html
    scraper = cloudscraper.create_scraper()
    page = scraper.get(url).text
    return page

def get24H(day, month, year, am_pm, last=datetime.now()):
    if 'day' in am_pm.lower():
        return datetime(year, month, day, 0, 0)

    addH = 7

    if 'pm' in am_pm:
        pm = am_pm.replace('pm', '')
        h = (int(pm.split(':')[0]) + 12)
        if h >= 24:
            h = h % 24
            #addH += 24
        m = int(pm.split(':')[1])
    elif 'am' in am_pm:
        am = am_pm.replace('am', '')
        h = int(am.split(':')[0])
        m = int(am.split(':')[1])
    else:
        return last

    evnt_date = datetime(year, month, day, h, m) + timedelta(hours=addH)

    return evnt_date

def getRecords(url):
    # columns
    c_time = []
    c_curr = []
    c_event = []
    c_forecast = []
    c_actual = []
    c_prev = []

    # page source
    pageHTML = getPageHTML(url)
    soup = BeautifulSoup(pageHTML, 'html.parser')
    table = soup.find('table', class_='calendar__table')
    events = table.find_all('td', class_='calendar__time')
    print(events)
    # start date
    startDate = table.find_next('tr', class_='calendar__row--new-day').find_next('span', class_='date')
    matchObj = re.search('([a-zA-Z]{3}) ([a-zA-Z]{3}) ([0-9]{1,2})', startDate.text)
    month = month_numbers.get(matchObj.group(2), None)
    day = matchObj.group(3)
    day = int(format(int(day), "02"))
    year = int(url[-4:])
    dt = datetime.now()

    # get event rows
    for event in events:
        # time
        time = event.text.strip()
        dt = get24H(int(day), int(month), int(year), time, dt)
        p_day = format(int(dt.day), "02")
        p_month = format(int(dt.month), "02")
        p_year = format(int(dt.year), "0002")
        hour = format(int(dt.hour), "02")
        minute = format(int(dt.minute), "02")

        # currency
        curr = (event.find_next_sibling('td', class_='calendar__currency').text.strip()).replace('\n', '').replace(' ', '')
        if len(curr) == 0:
            continue

        # event name
        name = event.find_next_sibling('td', class_='calendar__event').find_next('span').text.strip()

        # previous
        previous = (event.find_next_sibling('td', class_='calendar__previous').text).replace('\n', '').replace(' ', '')
        previous = previous if len(previous) > 1 else 'unknown'

        # forecast
        forecast = (event.find_next_sibling('td', class_='calendar__forecast').text).replace('\n', '').replace(' ', '')
        forecast = forecast if len(forecast) > 1 else 'unknown'

        # actual
        actual = (event.find_next_sibling('td', class_='calendar__actual').text).replace('\n', '').replace(' ', '')
        actual = actual if len(actual) > 1 else 'unknown'

        # save row
        c_time.append(f'{p_day}/{p_month}/{p_year} {hour}:{minute}')
        c_curr.append(curr)
        c_event.append(name)
        c_forecast.append(forecast)
        c_actual.append(actual)
        c_prev.append(previous)

    # create table
    data = {
        'Time': c_time,
        'Currency': c_curr,
        'Event': c_event,
        'Forecast': c_forecast,
        'Actual': c_actual,
        'Previous': c_prev
    }
    data_table = pd.DataFrame(data)
    return data_table.to_dict(orient='records')

