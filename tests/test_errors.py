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


def test_404_returns_json():
    client = app.test_client()
    resp = client.get("/no-such-endpoint")
    assert resp.status_code == 404
    data = resp.get_json()
    assert isinstance(data, dict)
    assert data.get("code") == 404
    assert data.get("status") == "error"
    assert "error" in data and "message" in data


def test_405_returns_json():
    client = app.test_client()
    # POST not allowed on /api/hello which only supports GET
    resp = client.post("/api/hello")
    assert resp.status_code == 405
    data = resp.get_json()
    assert isinstance(data, dict)
    assert data.get("code") == 405
    assert data.get("status") == "error"


def test_500_internal_error(monkeypatch):
    # Force the scraper to raise to simulate an internal error
    def _raise(url):
        raise RuntimeError("boom")

    monkeypatch.setattr(src_app, "get_records", _raise)
    # Also patch main.getRecords for completeness
    monkeypatch.setattr(main, "get_records", _raise)

    client = app.test_client()
    resp = client.get("/api/forex/daily?day=1&month=1&year=2020")
    assert resp.status_code == 500
    data = resp.get_json()
    assert isinstance(data, dict)
    assert data.get("code") == 500
    assert data.get("status") == "error"
    assert data.get("error") == "Internal Server Error"
