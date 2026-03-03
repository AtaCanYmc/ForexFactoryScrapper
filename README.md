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
python app.py
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

Expected JSON response (HTTP 200): a pagination wrapper containing metadata and a list of records. Example response format:

```json
{
  "total": 1,
  "offset": 0,
  "limit": null,
  "results": [
    {
      "Time": "01/01/2020 00:00",
      "Currency": "USD",
      "Event": "NFP",
      "Forecast": "100k",
      "Actual": "120k",
      "Previous": "90k"
    }
  ]
}
```

> Note: The `total`, `offset`, and `limit` fields in the response wrapper provide pagination metadata. The `results` field contains the list of records.

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

### 5) Forex daily — paging (limit & offset)

This project added optional paging support to the `/api/forex/daily` endpoint via two query parameters: `limit` and `offset`.

- `offset` (optional): integer >= 0, default 0. Skip this many records from the start.
- `limit` (optional): integer >= 0, default is unlimited. Return at most this many records after applying the offset.

Behavior and validation:

- Both `limit` and `offset` must be integers. Non-integer values return HTTP 400.
- Negative values return HTTP 400.
- If `offset` is greater than or equal to the number of available records, the endpoint returns an empty list and HTTP 200.
- `limit=0` returns an empty list (valid request).
- If the scraper returns a non-list structure, paging is not applied and the raw response is returned.

Examples:

- First 10 records:

```bash
curl -sS "http://localhost:5000/api/forex/daily?day=1&month=1&year=2020&limit=10"
```

- Start from the 5th record and return up to 3 records:

```bash
curl -sS "http://localhost:5000/api/forex/daily?day=1&month=1&year=2020&offset=4&limit=3"
```

- Non-integer or negative paging params (example, HTTP 400):

```bash
curl -sS "http://localhost:5000/api/forex/daily?day=1&month=1&year=2020&limit=abc"
curl -sS "http://localhost:5000/api/forex/daily?day=1&month=1&year=2020&offset=-1"
```

### 6) Cryptocraft daily — examples

The project also exposes a Cryptocraft-specific scraping endpoint that follows the same parameter and paging semantics as the Forex endpoint.

- Missing parameters (HTTP 400):

```bash
curl -sS http://localhost:5000/api/cryptocraft/daily
```

Response body:

```json
{ "error": "Missing one or more required parameters: day, month, year" }
```

- Invalid (non-integer) parameters (HTTP 400):

```bash
curl -sS "http://localhost:5000/api/cryptocraft/daily?day=aa&month=bb&year=cc"
```

Response body:

```json
{ "error": "Parameters day, month and year must be integers" }
```

- Success (pagination wrapper):

Curl example:

```bash
curl -sS "http://localhost:5000/api/cryptocraft/daily?day=1&month=1&year=2020"
```

Expected JSON response (HTTP 200): a pagination wrapper containing metadata and a list of records. Example response format:

```json
{
  "total": 1,
  "offset": 0,
  "limit": null,
  "results": [
    {
      "Time": "01/01/2020 00:00",
      "Currency": "BTC",
      "Event": "Protocol Upgrade",
      "Forecast": "n/a",
      "Actual": "n/a",
      "Previous": "n/a"
    }
  ]
}
```

- Paging examples (limit & offset):

First 10 records:

```bash
curl -sS "http://localhost:5000/api/cryptocraft/daily?day=1&month=1&year=2020&limit=10"
```

Start from the 5th record and return up to 3 records:

```bash
curl -sS "http://localhost:5000/api/cryptocraft/daily?day=1&month=1&year=2020&offset=4&limit=3"
```

Notes:

- Behavior and validation match the Forex endpoint: `limit` and `offset` must be integers and non-negative; `limit=0` is valid and returns an empty `results` array.
- Responses use the pagination wrapper `{ "total": N, "offset": X, "limit": Y, "results": [...] }` for list data.

### 7) MetalsMine daily — examples

The project also exposes a MetalsMine-specific scraping endpoint that follows the same parameter and paging semantics as the Forex and Cryptocraft endpoints.

- Missing parameters (HTTP 400):

```bash
curl -sS http://localhost:5000/api/metalsmine/daily
```

Response body:

```json
{ "error": "Missing one or more required parameters: day, month, year" }
```

- Invalid (non-integer) parameters (HTTP 400):

```bash
curl -sS "http://localhost:5000/api/metalsmine/daily?day=aa&month=bb&year=cc"
```

Response body:

```json
{ "error": "Parameters day, month and year must be integers" }
```

- Success (pagination wrapper):

Curl example:

```bash
curl -sS "http://localhost:5000/api/metalsmine/daily?day=1&month=1&year=2020"
```

Expected JSON response (HTTP 200): a pagination wrapper containing metadata and a list of records. Example response format:

```json
{
  "total": 1,
  "offset": 0,
  "limit": null,
  "results": [
    {
      "Time": "01/01/2020 00:00",
      "Currency": "XAU",
      "Event": "Gold Inventory Release",
      "Forecast": "n/a",
      "Actual": "n/a",
      "Previous": "n/a"
    }
  ]
}
```

- Paging examples (limit & offset):

First 10 records:

```bash
curl -sS "http://localhost:5000/api/metalsmine/daily?day=1&month=1&year=2020&limit=10"
```

Start from the 5th record and return up to 3 records:

```bash
curl -sS "http://localhost:5000/api/metalsmine/daily?day=1&month=1&year=2020&offset=4&limit=3"
```

### 8) EnergyExch daily — examples

The project also exposes an EnergyExch-specific scraping endpoint that follows the same parameter and paging semantics as the Forex, Cryptocraft, and MetalsMine endpoints.

- Missing parameters (HTTP 400):

```bash
curl -sS http://localhost:5000/api/energyexch/daily
```

Response body:

```json
{ "error": "Missing one or more required parameters: day, month, year" }
```

- Invalid (non-integer) parameters (HTTP 400):

```bash
curl -sS "http://localhost:5000/api/energyexch/daily?day=aa&month=bb&year=cc"
```

Response body:

```json
{ "error": "Parameters day, month and year must be integers" }
```

- Success (pagination wrapper):

Curl example:

```bash
curl -sS "http://localhost:5000/api/energyexch/daily?day=1&month=1&year=2020"
```

Expected JSON response (HTTP 200): a pagination wrapper containing metadata and a list of records. Example response format:

```json
{
  "total": 1,
  "offset": 0,
  "limit": null,
  "results": [
    {
      "Time": "01/01/2020 00:00",
      "Currency": "USD",
      "Event": "Energy Report",
      "Forecast": "n/a",
      "Actual": "n/a",
      "Previous": "n/a"
    }
  ]
}
```

- Paging examples (limit & offset):

First 10 records:

```bash
curl -sS "http://localhost:5000/api/energyexch/daily?day=1&month=1&year=2020&limit=10"
```

Start from the 5th record and return up to 3 records:

```bash
curl -sS "http://localhost:5000/api/energyexch/daily?day=1&month=1&year=2020&offset=4&limit=3"
```

Notes:

- Behavior and validation match the Forex endpoint: `limit` and `offset` must be integers and non-negative; `limit=0` is valid and returns an empty `results` array.
- Responses use the pagination wrapper `{ "total": N, "offset": X, "limit": Y, "results": [...] }` for list data.

Notes and suggestions:

- There is no enforced maximum `limit` in the current implementation. For production use you may want to cap `limit` (for example 500 or 1000) to avoid large responses or memory spikes.
- Consider returning a pagination wrapper like `{ "total": N, "offset": X, "limit": Y, "results": [...] }` if clients benefit from metadata. Current response remains a plain JSON array for backward compatibility.

Notes:
- The exact fields and values depend on the parser and target site's HTML structure. When running the real scraper, values reflect what is parsed from ForexFactory for the given date.
- The examples above match the app behavior implemented in `main.py` and the test fixtures in `tests/test_app.py`.

## API docs (OpenAPI / Swagger UI)

This project exposes a tiny OpenAPI JSON and a Swagger UI page to help explore the endpoints:

- GET /openapi.json — returns a minimal OpenAPI 3 JSON describing the API (used by the UI).
- GET /swagger — serves a lightweight Swagger UI that loads `/openapi.json` (served from a CDN; no new Python dependencies required).

Examples:

- Fetch the spec directly:

```bash
curl -sS http://localhost:5000/openapi.json | jq .
```

- Open the interactive docs in your browser:

Visit: http://localhost:5000/swagger

Notes:
- The Swagger UI is loaded from a CDN (unpkg). If you need an offline or self-hosted UI, consider adding `swagger-ui` as a static asset or installing a Python package like `flasgger`.
- The OpenAPI spec is intentionally minimal and kept in `src/app.py` as `OPENAPI_SPEC`. You can expand it with schemas and richer response descriptions if you need stronger client generation.

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
