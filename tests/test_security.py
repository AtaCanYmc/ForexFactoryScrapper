import pytest
from src.app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_security_headers_present(client):
    """Verify defensive HTTP security headers are set on API responses."""
    response = client.get("/api/hello")
    assert response.status_code == 200
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "SAMEORIGIN"
    assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert "geolocation=()" in response.headers.get("Permissions-Policy", "")
    assert "X-Request-ID" in response.headers


def test_custom_correlation_id_passthrough(client):
    """Verify client-supplied X-Request-ID is preserved in response headers."""
    response = client.get("/api/health", headers={"X-Request-ID": "test-uuid-1234"})
    assert response.status_code == 200
    assert response.headers.get("X-Request-ID") == "test-uuid-1234"


def test_invalid_calendar_date(client):
    """Verify semantic date validation rejects non-existent dates (e.g. Feb 31)."""
    response = client.get("/api/forex/daily?day=31&month=2&year=2024")
    assert response.status_code == 400
    data = response.get_json()
    assert "Invalid calendar date" in data.get("error", "")


def test_paging_limit_upper_bound(client):
    """Verify pagination limit rejects excessively large values to prevent memory exhaustion."""
    response = client.get("/api/forex/daily?day=1&month=1&year=2024&limit=999999")
    assert response.status_code == 400
    data = response.get_json()
    assert "exceeds maximum allowed limit" in data.get("error", "")


def test_bundle_date_range_span_limit(client):
    """Verify bundle endpoint rejects date spans exceeding MAX_BUNDLE_DAYS."""
    response = client.get(
        "/api/bundle?sources=forex&start_date=2024-01-01&end_date=2025-01-01"
    )
    assert response.status_code == 400
    data = response.get_json()
    assert "exceeds maximum allowed span" in data.get("message", "")


def test_sitemap_max_pages_bounds(client):
    """Verify sitemaps endpoint enforces bounds on max_pages."""
    # Negative / zero
    res_zero = client.get("/api/forex/sitemaps?max_pages=0")
    assert res_zero.status_code == 400

    # Excessively large
    res_large = client.get("/api/forex/sitemaps?max_pages=99999")
    assert res_large.status_code == 400


def test_rate_limit_returns_429(client, monkeypatch):
    from src import performance

    performance._hits.clear()
    monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", "2")
    codes = [client.get("/api/hello").status_code for _ in range(3)]
    assert codes == [200, 200, 429]
    assert client.get("/api/health").status_code == 200
    performance._hits.clear()


def test_cache_reuses_upstream_call(monkeypatch):
    from src import performance

    class Fake:
        calls = 0

        @staticmethod
        def get_records(url):
            Fake.calls += 1
            return [url]

    performance._cache.clear()
    monkeypatch.setenv("CACHE_TTL_SECONDS", "60")
    performance.cached_get_records(Fake, "u")
    performance.cached_get_records(Fake, "u")
    assert Fake.calls == 1
    monkeypatch.setenv("CACHE_TTL_SECONDS", "0")
    performance.cached_get_records(Fake, "u")
    assert Fake.calls == 2
    performance._cache.clear()


def test_health_probe_metrics(client, monkeypatch):
    from src import performance

    monkeypatch.setattr(
        performance, "probe_metrics", lambda: {"upstream": {}, "memory_mb": 1.0}
    )
    import src.routes.helper_routes as h

    monkeypatch.setattr(h, "probe_metrics", performance.probe_metrics)
    data = client.get("/api/health?probe=true").get_json()
    assert data["status"] == "ok" and "memory_mb" in data


def test_probe_metrics_upstream_unreachable(monkeypatch):
    from src import performance

    def boom(*a, **k):
        raise OSError("offline")

    monkeypatch.setattr(performance, "HTTPSConnection", boom)
    out = performance.probe_metrics()
    assert out["upstream"]["reachable"] is False
    assert out["upstream"]["error"] == "OSError"
    assert out["memory_mb"] > 0


def test_json_logging_format(client, caplog):
    import json
    import logging

    from src.logging_config import JsonFormatter

    with caplog.at_level(logging.INFO, logger="access"):
        client.get("/api/hello", headers={"X-Request-ID": "rid-1"})
    rec = next(r for r in caplog.records if r.name == "access")
    line = json.loads(JsonFormatter().format(rec))
    assert line["message"] == "request"
    assert line["path"] == "/api/hello" and line["status"] == 200
    assert line["request_id"] == "rid-1" and "duration_ms" in line
