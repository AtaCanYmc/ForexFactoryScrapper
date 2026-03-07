# ForexFactoryScrapper

[![CI](https://github.com/AtaCanYmc/ForexFactoryScrapper/actions/workflows/ci.yml/badge.svg)](https://github.com/AtaCanYmc/ForexFactoryScrapper/actions) [![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/AtaCanYmc/ForexFactoryScrapper/blob/main/LICENSE)

ForexFactoryScrapper is a small Flask-based API that exposes scraping logic for several economic-calendar sources (ForexFactory, CryptoCraft, EnergyExch, MetalsMine).

What this repository provides:
- Flask HTTP API endpoints returning JSON (or HTML for the root page)
- Per-site scrapers under `src/scrapper/` (site-specific logic)
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
- GET `/api/cryptocraft/daily` — CryptoCraft daily events (same parameters)
- GET `/api/energyexch/daily` — EnergyExch daily events (same parameters)
- GET `/api/metalsmine/daily` — MetalsMine daily events (same parameters)

All `/.../daily` endpoints follow the same validation and paging semantics:
- Required query parameters: `day`, `month`, `year` (integers)
- Optional `limit` and `offset` (integers, >= 0)
- On success, list results are wrapped in a pagination object: `{ total, offset, limit, results }`.
- On parameter validation error, endpoints return HTTP 400 with JSON: `{ "error": "..." }`.

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

---

If you want, I can also generate a short `CONTRIBUTING.md` or add CI steps to run lint/tests automatically on PRs. Let me know what else to update.
