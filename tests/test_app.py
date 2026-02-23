import importlib
import os
import sys

# Add project src directory and project root to sys.path so tests can import
# the application module from src/ during test runs.
ROOT = os.path.dirname(os.path.dirname(__file__))
SRC = os.path.join(ROOT, "src")
for p in (SRC, ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

# Import the app module dynamically so linters don't complain about code
# executing before imports.
main = importlib.import_module("main")
# Import the actual application module implemented in src/app.py so tests
# can monkeypatch the functions the routes call.
src_app = importlib.import_module("src.app")
app = main.app

SAMPLE_RECORDS = [
    {
        "Time": "01/01/2020 00:00",
        "Currency": "USD",
        "Event": "NFP",
        "Forecast": "100k",
        "Actual": "120k",
        "Previous": "90k",
    }
]

# A larger list used for paging tests
SAMPLE_RECORDS_MULTI = [
    {**SAMPLE_RECORDS[0], "Time": f"01/01/2020 00:0{i}", "Currency": f"USD{i}"}
    for i in range(5)
]


def test_hello():
    client = app.test_client()
    resp = client.get("/api/hello")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "success"


def test_health():
    client = app.test_client()
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_forex_missing_params():
    client = app.test_client()
    resp = client.get("/api/forex/daily")
    assert resp.status_code == 400


def test_forex_invalid_params():
    client = app.test_client()
    resp = client.get("/api/forex/daily?day=aa&month=bb&year=cc")
    assert resp.status_code == 400


def test_forex_out_of_range():
    client = app.test_client()
    resp = client.get("/api/forex/daily?day=99&month=99&year=3000")
    assert resp.status_code == 400


def test_forex_success(monkeypatch):
    # Patch the functions used by the Flask routes to avoid network calls.
    monkeypatch.setattr(src_app, "getRecords", lambda url: SAMPLE_RECORDS)
    monkeypatch.setattr(
        src_app, "getURL", lambda day, month, year, timeline: "http://example"
    )

    # Also patch top-level main module references for completeness.
    monkeypatch.setattr(main, "getRecords", lambda url: SAMPLE_RECORDS)
    monkeypatch.setattr(
        main, "getURL", lambda day, month, year, timeline: "http://example"
    )

    client = app.test_client()
    resp = client.get("/api/forex/daily?day=1&month=1&year=2020")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert data == SAMPLE_RECORDS


# Paging tests


def test_forex_paging_limit(monkeypatch):
    monkeypatch.setattr(src_app, "getRecords", lambda url: SAMPLE_RECORDS_MULTI)
    monkeypatch.setattr(
        src_app, "getURL", lambda day, month, year, timeline: "http://example"
    )
    monkeypatch.setattr(main, "getRecords", lambda url: SAMPLE_RECORDS_MULTI)
    monkeypatch.setattr(
        main, "getURL", lambda day, month, year, timeline: "http://example"
    )

    client = app.test_client()
    resp = client.get("/api/forex/daily?day=1&month=1&year=2020&limit=2")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data == SAMPLE_RECORDS_MULTI[:2]


def test_forex_paging_offset(monkeypatch):
    monkeypatch.setattr(src_app, "getRecords", lambda url: SAMPLE_RECORDS_MULTI)
    monkeypatch.setattr(
        src_app, "getURL", lambda day, month, year, timeline: "http://example"
    )
    monkeypatch.setattr(main, "getRecords", lambda url: SAMPLE_RECORDS_MULTI)
    monkeypatch.setattr(
        main, "getURL", lambda day, month, year, timeline: "http://example"
    )

    client = app.test_client()
    resp = client.get("/api/forex/daily?day=1&month=1&year=2020&offset=2")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert data == SAMPLE_RECORDS_MULTI[2:]


def test_forex_paging_limit_offset(monkeypatch):
    monkeypatch.setattr(src_app, "getRecords", lambda url: SAMPLE_RECORDS_MULTI)
    monkeypatch.setattr(
        src_app, "getURL", lambda day, month, year, timeline: "http://example"
    )
    monkeypatch.setattr(main, "getRecords", lambda url: SAMPLE_RECORDS_MULTI)
    monkeypatch.setattr(
        main, "getURL", lambda day, month, year, timeline: "http://example"
    )

    client = app.test_client()
    resp = client.get("/api/forex/daily?day=1&month=1&year=2020&offset=1&limit=2")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert data == SAMPLE_RECORDS_MULTI[1:3]


def test_forex_paging_invalid_params(monkeypatch):
    monkeypatch.setattr(src_app, "getRecords", lambda url: SAMPLE_RECORDS_MULTI)
    monkeypatch.setattr(
        src_app, "getURL", lambda day, month, year, timeline: "http://example"
    )
    monkeypatch.setattr(main, "getRecords", lambda url: SAMPLE_RECORDS_MULTI)
    monkeypatch.setattr(
        main, "getURL", lambda day, month, year, timeline: "http://example"
    )

    client = app.test_client()
    # non-integer limit
    resp = client.get("/api/forex/daily?day=1&month=1&year=2020&limit=abc")
    assert resp.status_code == 400
    # negative offset
    resp = client.get("/api/forex/daily?day=1&month=1&year=2020&offset=-1")
    assert resp.status_code == 400
