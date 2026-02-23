import pytest
from main import app
import main

SAMPLE_RECORDS = [
    {'Time': '01/01/2020 00:00', 'Currency': 'USD', 'Event': 'NFP', 'Forecast': '100k', 'Actual': '120k', 'Previous': '90k'}
]


def test_hello():
    client = app.test_client()
    resp = client.get('/api/hello')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['status'] == 'success'


def test_health():
    client = app.test_client()
    resp = client.get('/api/health')
    assert resp.status_code == 200
    assert resp.get_json()['status'] == 'ok'


def test_forex_missing_params():
    client = app.test_client()
    resp = client.get('/api/forex/daily')
    assert resp.status_code == 400


def test_forex_invalid_params():
    client = app.test_client()
    resp = client.get('/api/forex/daily?day=aa&month=bb&year=cc')
    assert resp.status_code == 400


def test_forex_out_of_range():
    client = app.test_client()
    resp = client.get('/api/forex/daily?day=99&month=99&year=3000')
    assert resp.status_code == 400


def test_forex_success(monkeypatch):
    # Patch main.getRecords and main.getURL to avoid network calls
    monkeypatch.setattr(main, 'getRecords', lambda url: SAMPLE_RECORDS)
    monkeypatch.setattr(main, 'getURL', lambda day, month, year, timeline: 'http://example')

    client = app.test_client()
    resp = client.get('/api/forex/daily?day=1&month=1&year=2020')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert data == SAMPLE_RECORDS

