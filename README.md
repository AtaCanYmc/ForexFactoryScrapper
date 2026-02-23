# ForexFactoryScrapper

**ForexFactoryScrapper** is a Python-based web scraping tool designed to extract financial event data from the [ForexFactory](https://www.forexfactory.com/) website. This project provides a simple and effective way to scrape calendar events, forecast data, actual values, and other relevant information for forex trading analysis.

## Features

- Scrape calendar events, including date, time, currency, event name, forecast, actual, and previous values.
- Extract data into structured formats for further processing or analysis.
- Simple and customizable scraping logic using `BeautifulSoup`.
- Includes examples for extracting data and creating simple reports.

## Installation

To use ForexFactoryScrapper, you need to have Python (3.9+) installed. Install project dependencies into a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage (local)

- Çalıştırmak için:

```bash
python main.py
```

Bu, uygulamayı yerel olarak 0.0.0.0:5000 üzerinde başlatır. Aşağıdaki örnek uç noktaları kullanabilirsiniz:

- GET /api/hello
- GET /api/health
- GET /api/forex/daily?day=1&month=1&year=2020

## Tests

Basit unit testleri çalıştırmak için:

```bash
pytest -q
```

Testler `tests/` klasöründe bulunur ve dış bağımlılıkları (ağ çağrılarını) monkeypatch ile izole eder.

## Notes

- Gerçek ağ çağrıları ve parsing, hedef sitenin HTML yapısına bağlıdır; HTML değişirse scraper güncelleme gerektirir.
- `requirements.txt` içindeki sürümler projenin yerelde kurulup test edilmesi için öneridir.
