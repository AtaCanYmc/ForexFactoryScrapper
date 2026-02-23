# ForexFactoryScrapper

[![CI](https://github.com/AtaCanYmc/ForexFactoryScrapper/actions/workflows/ci.yml/badge.svg)](https://github.com/AtaCanYmc/ForexFactoryScrapper/actions) [![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/AtaCanYmc/ForexFactoryScrapper/blob/main/LICENSE)

**ForexFactoryScrapper** is a Python-based web scraping tool designed to extract financial event data from the [ForexFactory](https://www.forexfactory.com/) website. This project provides a simple and effective way to scrape calendar events, forecast data, actual values, and other relevant information for forex trading analysis.

## Features

- Scrape calendar events, including date, time, currency, event name, forecast, actual, and previous values.
- Export or process extracted data in structured formats suitable for analysis.
- Simple and customizable scraping logic using `BeautifulSoup`.
- Includes examples for extracting data and creating basic reports.

## Requirements

- Python 3.9 or newer
- See `requirements.txt` for dependency versions used during development and testing.

## Installation

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Running locally

Start the application locally:

```bash
python main.py
```

By default this will start the app on 0.0.0.0:5000. Example endpoints you can call:

- GET /api/hello
- GET /api/health
- GET /api/forex/daily?day=1&month=1&year=2020

(Adjust host/port or endpoint parameters as needed in `main.py`.)

## Example requests

Below are simple example requests you can use to interact with the running application. Replace `localhost:5000` with the host/port where your app is listening if different.

### 1) Hello

Curl:

```bash
curl -sS http://localhost:5000/api/hello
```

Expected JSON response (HTTP 200):

```json
{
  "message": "Hello, World!",
  "status": "success"
}
```

### 2) Health

Curl:

```bash
curl -sS http://localhost:5000/api/health
```

Expected JSON response (HTTP 200):

```json
{
  "status": "ok"
}
```

### 3) Forex daily — missing or invalid parameters

- Missing parameters (HTTP 400):

```bash
curl -sS http://localhost:5000/api/forex/daily
```

Response body:

```json
{ "error": "Missing one or more required parameters: day, month, year" }
```

- Invalid (non-integer) parameters (HTTP 400):

```bash
curl -sS "http://localhost:5000/api/forex/daily?day=aa&month=bb&year=cc"
```

Response body:

```json
{ "error": "Parameters day, month and year must be integers" }
```

- Out-of-range parameters (HTTP 400):

```bash
curl -sS "http://localhost:5000/api/forex/daily?day=99&month=99&year=3000"
```

Response body:

```json
{ "error": "Parameters out of reasonable range" }
```

### 4) Forex daily — success

Curl (example):

```bash
curl -sS "http://localhost:5000/api/forex/daily?day=1&month=1&year=2020"
```

Expected JSON response (HTTP 200): a JSON array of records. Example record format:

```json
[
  {
    "Time": "01/01/2020 00:00",
    "Currency": "USD",
    "Event": "NFP",
    "Forecast": "100k",
    "Actual": "120k",
    "Previous": "90k"
  }
]
```

Python `requests` example:

```python
import requests

resp = requests.get(
    'http://localhost:5000/api/forex/daily',
    params={'day': 1, 'month': 1, 'year': 2020},
)
print(resp.status_code)
print(resp.json())
```

Notes:
- The exact fields and values depend on the parser and target site's HTML structure. When running the real scraper, values reflect what is parsed from ForexFactory for the given date.
- The examples above match the app behavior implemented in `main.py` and the test fixtures in `tests/test_app.py`.

## Tests

Run the test suite with pytest:

```bash
pytest -q
```

Unit tests are located in the `tests/` folder. Network calls and external dependencies are isolated using monkeypatching to keep tests deterministic.

## Notes and caveats

- The scraper depends on the target site's HTML structure. If ForexFactory changes its markup, the parsing code will need updating.
- `requirements.txt` pins versions that were used during development; consider updating or pinning further for deployments.
- Respect the target site's robots.txt and terms of service when scraping.

## Contributing

Contributions, bug reports, and feature requests are welcome. Please open an issue or a pull request.

## License

This project is licensed under the MIT License — see the [LICENSE](./LICENSE) file for details.
