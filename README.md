

# ForexFactoryScrapper

[![CI](https://github.com/AtaCanYmc/ForexFactoryScrapper/actions/workflows/ci.yml/badge.svg)](https://github.com/AtaCanYmc/ForexFactoryScrapper/actions) [![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/AtaCanYmc/ForexFactoryScrapper/blob/main/LICENSE)

ForexFactoryScrapper is a small Flask-based HTTP API that exposes economic-calendar data (ForexFactory, CryptoCraft, EnergyExch, MetalsMine).

> **Important Architecture Note:**
> All web scraping logic has been decoupled and is now centrally managed by the [forex-pytory](https://github.com/AtaCanYmc/forex-pytory) package. This API project delegates data fetching entirely to that library and focuses solely on providing a clean, user-friendly REST API interface.

### Why this architecture?
- **Modularity:** The scraping engine and the web server (API) are independent.
- **Maintainability:** Any HTML DOM changes on target sites only require updates in `forex-pytory`, leaving the API project untouched.
- **Single Source of Truth:** Data typing and validation is handled strictly via Pydantic models at the library level.

What this repository provides:
- Flask HTTP API endpoints returning JSON (or HTML for the root page)
- Simple test-suite using `pytest` under `tests/`
- A minimal OpenAPI spec (served at `/openapi.json`) and a Swagger UI at `/swagger`

---

## Quick start

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
# Note: This will automatically install the scraping engine 'forex-pytory'
pip install -r requirements.txt
```

3. Run the app locally:

```bash
python main.py
# or
python src/app.py
```

By default the app listens on `0.0.0.0:5000`. You can configure `HOST`, `PORT` and `DEBUG` via environment variables or a `.env` file (the app uses `python-dotenv` if present).

Open the welcome page in your browser: `http://localhost:5000/`
Open API docs: `http://localhost:5000/swagger`
Open raw OpenAPI JSON: `http://localhost:5000/openapi.json`

---

## Available endpoints

- GET `/` — Welcome HTML page (quick links)
- GET `/api/hello` — simple hello response
- GET `/api/health` — quick health check
- GET `/api/forex/daily` — ForexFactory daily events (query params: `day`, `month`, `year`, optional `limit`, `offset`)
- GET `/api/forex/sitemaps` — ForexFactory sitemap URLs (optional `start_date`, `end_date`, `limit`, `offset`, `max_pages`)
- GET `/api/cryptocraft/daily` — CryptoCraft daily events (same parameters)
- GET `/api/energyexch/daily` — EnergyExch daily events (same parameters)
- GET `/api/metalsmine/daily` — MetalsMine daily events (same parameters)
- GET `/api/bundle` — Combined economic events from multiple sources within a date range (see below)

### Daily events endpoints (`/api/.../daily`)

All `/.../daily` endpoints follow the same validation and paging semantics:
- Required query parameters: `day`, `month`, `year` (integers)
- Optional `limit` and `offset` (integers, >= 0)
- On success, list results are wrapped in a pagination object: `{ total, offset, limit, results }`.
- On parameter validation error, endpoints return HTTP 400 with JSON: `{ "error": "..." }`.

### Sitemap endpoint (`/api/forex/sitemaps`)

Fetches ForexFactory sitemap-index and child sitemaps to retrieve a paginated list of URLs:
- Optional `start_date` and `end_date` (ISO format: `YYYY-MM-DD`) — filters results by sitemap lastmod date
- Optional `limit` and `offset` (integers, >= 0) — standard paging
- Optional `max_pages` (integer, >= 1, default 10) — limits number of child sitemaps to scan
- Returns: `{ total, offset, limit, results }` where each result is `{ url, lastmod: date_or_null }`
- Example: `GET /api/forex/sitemaps?start_date=2026-05-15&max_pages=5`

### Bundle endpoint (`/api/bundle`)

Fetches combined economic events from multiple sources within a date range:
- Required query parameters:
  - `start_date` (ISO format: `YYYY-MM-DD`) — Start date (inclusive)
  - `end_date` (ISO format: `YYYY-MM-DD`) — End date (inclusive)
- Optional query parameters:
  - `sources` (comma-separated string, default: `forex`) — Sources to include: `forex`, `crypto`, `metal`, `energy`
  - `limit` (integer, >= 0) — Max number of results to return
  - `offset` (integer, >= 0) — Number of records to skip
- Returns: `{ total, offset, limit, start_date, end_date, sources, source_breakdown, results }`
  - Each result includes `_source` (which source it came from) and `_date` (which date it was fetched for)
  - `source_breakdown` shows count of records per source
- Examples:
  - `GET /api/bundle?start_date=2026-05-20&end_date=2026-05-25` — forex events for May 20-25
  - `GET /api/bundle?sources=forex,crypto&start_date=2026-05-20&end_date=2026-05-21&limit=50` — forex and crypto events, max 50 results

---

## OpenAPI / Swagger

- The OpenAPI document is available at `/openapi.json` and is generated from `src/openapi_spec.py`.
- The interactive Swagger UI is served at `/swagger` and uses the OpenAPI JSON. If your environment blocks external CDN assets, the UI falls back to an inline minimal page.

If you update endpoints or schemas, please update `src/openapi_spec.py` accordingly so the docs stay accurate.

---

## Environment variables

- `HOST` — host to bind (default `0.0.0.0`)
- `PORT` — port to bind (default `5000`)
- `DEBUG` — debug mode (default `True`)
- `DOTENV_PATH` — optional path to a `.env` file

---

## Tests

Run tests with:

```bash
python -m pytest -q
```

Tests are under `tests/` and use `pytest` and the Flask test client. Many tests monkeypatch `src.app` and `main` to avoid network calls.

---

## Docker

A `Dockerfile` is provided for convenience; if you prefer to run inside Docker, build and run the image as usual (adjust ports as needed).

---

## Contributing

Contributions welcome. Suggested workflow:
1. Create a branch for your change
2. Add tests for any behavior you modify
3. Run the full test suite
4. Open a pull request describing the change

If you modify or add a new scraper under `src/scrapper/`, try to keep the `get_records(url)` and `get_url(day, month, year, timeline)` function signatures so the route helpers can call them interchangeably.

**Code of Conduct**: Please read `CODE_OF_CONDUCT.md` before contributing — it describes expected behaviour and reporting contacts.

---

## Contact

Maintainer: Ata Can — atacanymc@gmail.com
