# ForexFactoryScrapper

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

This project does not include a license file by default. Add a `LICENSE` if you plan to open-source the project.
