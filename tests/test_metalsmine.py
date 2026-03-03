import importlib
import os
import sys

# ensure src is importable
ROOT = os.path.dirname(os.path.dirname(__file__))
SRC = os.path.join(ROOT, "src")
for p in (SRC, ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

main = importlib.import_module("main")
src_app = importlib.import_module("src.app")
app = main.app

SAMPLE_RECORD = {
    "Time": "01/01/2020 00:00",
    "Currency": "XAU",
    "Event": "Gold Inventory Release",
    "Forecast": "n/a",
    "Actual": "n/a",
    "Previous": "n/a",
}

SAMPLE_RECORDS_MULTI = [
    {**SAMPLE_RECORD, "Time": f"01/01/2020 00:0{i}", "Currency": f"XAU{i}"}
    for i in range(5)
]


def test_metalsmine_missing_params():
    client = app.test_client()
    resp = client.get("/api/metalsmine/daily")
    assert resp.status_code == 400


def test_metalsmine_invalid_params():
    client = app.test_client()
    resp = client.get("/api/metalsmine/daily?day=aa&month=bb&year=cc")
    assert resp.status_code == 400


def test_metalsmine_success(monkeypatch):
    monkeypatch.setattr(src_app, "getRecords", lambda url: [SAMPLE_RECORD])
    monkeypatch.setattr(
        src_app, "getURL", lambda day, month, year, timeline: "http://example"
    )
    monkeypatch.setattr(main, "getRecords", lambda url: [SAMPLE_RECORD])
    monkeypatch.setattr(
        main, "getURL", lambda day, month, year, timeline: "http://example"
    )

    client = app.test_client()
    resp = client.get("/api/metalsmine/daily?day=1&month=1&year=2020")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, dict)
    assert data["total"] == 1
    assert data["offset"] == 0
    assert data["limit"] is None
    assert data["results"] == [SAMPLE_RECORD]


def test_metalsmine_paging_limit(monkeypatch):
    monkeypatch.setattr(src_app, "getRecords", lambda url: SAMPLE_RECORDS_MULTI)
    monkeypatch.setattr(
        src_app, "getURL", lambda day, month, year, timeline: "http://example"
    )
    monkeypatch.setattr(main, "getRecords", lambda url: SAMPLE_RECORDS_MULTI)
    monkeypatch.setattr(
        main, "getURL", lambda day, month, year, timeline: "http://example"
    )

    client = app.test_client()
    resp = client.get("/api/metalsmine/daily?day=1&month=1&year=2020&limit=2")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["total"] == len(SAMPLE_RECORDS_MULTI)
    assert data["offset"] == 0
    assert data["limit"] == 2
    assert data["results"] == SAMPLE_RECORDS_MULTI[:2]


def test_metalsmine_paging_offset(monkeypatch):
    monkeypatch.setattr(src_app, "getRecords", lambda url: SAMPLE_RECORDS_MULTI)
    monkeypatch.setattr(
        src_app, "getURL", lambda day, month, year, timeline: "http://example"
    )
    monkeypatch.setattr(main, "getRecords", lambda url: SAMPLE_RECORDS_MULTI)
    monkeypatch.setattr(
        main, "getURL", lambda day, month, year, timeline: "http://example"
    )

    client = app.test_client()
    resp = client.get("/api/metalsmine/daily?day=1&month=1&year=2020&offset=2")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["total"] == len(SAMPLE_RECORDS_MULTI)
    assert data["offset"] == 2
    assert data["limit"] is None
    assert data["results"] == SAMPLE_RECORDS_MULTI[2:]


def test_metalsmine_paging_limit_offset(monkeypatch):
    monkeypatch.setattr(src_app, "getRecords", lambda url: SAMPLE_RECORDS_MULTI)
    monkeypatch.setattr(
        src_app, "getURL", lambda day, month, year, timeline: "http://example"
    )
    monkeypatch.setattr(main, "getRecords", lambda url: SAMPLE_RECORDS_MULTI)
    monkeypatch.setattr(
        main, "getURL", lambda day, month, year, timeline: "http://example"
    )

    client = app.test_client()
    resp = client.get("/api/metalsmine/daily?day=1&month=1&year=2020&offset=1&limit=2")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["total"] == len(SAMPLE_RECORDS_MULTI)
    assert data["offset"] == 1
    assert data["limit"] == 2
    assert data["results"] == SAMPLE_RECORDS_MULTI[1:3]


def test_metalsmine_paging_invalid_params(monkeypatch):
    monkeypatch.setattr(src_app, "getRecords", lambda url: SAMPLE_RECORDS_MULTI)
    monkeypatch.setattr(
        src_app, "getURL", lambda day, month, year, timeline: "http://example"
    )
    monkeypatch.setattr(main, "getRecords", lambda url: SAMPLE_RECORDS_MULTI)
    monkeypatch.setattr(
        main, "getURL", lambda day, month, year, timeline: "http://example"
    )

    client = app.test_client()
    resp = client.get("/api/metalsmine/daily?day=1&month=1&year=2020&limit=abc")
    assert resp.status_code == 400
    resp = client.get("/api/metalsmine/daily?day=1&month=1&year=2020&offset=-1")
    assert resp.status_code == 400
