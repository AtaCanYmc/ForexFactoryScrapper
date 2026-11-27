import os
import resource
import sys
import threading
import time
import urllib.request
from collections import defaultdict, deque

from flask import jsonify, request

_cache = {}
_cache_lock = threading.Lock()
_hits = defaultdict(deque)
_hits_lock = threading.Lock()

UPSTREAM_PROBE_URL = "https://www.forexfactory.com/"


def _int_env(name, default):
    try:
        return max(0, int(os.getenv(name, default)))
    except ValueError:
        return default


def cached_get_records(scraper, url):
    """Return scraper.get_records(url), cached for CACHE_TTL_SECONDS (0 = off)."""
    ttl = _int_env("CACHE_TTL_SECONDS", 0)
    if not ttl:
        return scraper.get_records(url)
    key = (scraper.__name__, url)
    now = time.monotonic()
    with _cache_lock:
        hit = _cache.get(key)
        if hit and hit[0] > now:
            return hit[1]
    records = scraper.get_records(url)
    with _cache_lock:
        if len(_cache) >= _int_env("CACHE_MAX_ENTRIES", 256):
            for k in [k for k, v in _cache.items() if v[0] <= now] or [next(iter(_cache))]:
                _cache.pop(k, None)
        _cache[key] = (now + ttl, records)
    return records


def register_rate_limit(app):
    """Per-client sliding-window limit on /api/* (RATE_LIMIT_PER_MINUTE, 0 = off)."""

    @app.before_request
    def rate_limit():
        limit = _int_env("RATE_LIMIT_PER_MINUTE", 0)
        if not limit or not request.path.startswith("/api/"):
            return None
        if request.path == "/api/health":
            return None
        now = time.monotonic()
        with _hits_lock:
            q = _hits[request.remote_addr]
            while q and q[0] <= now - 60:
                q.popleft()
            if len(q) >= limit:
                retry = max(1, int(60 - (now - q[0])))
                resp = jsonify({"error": "Rate limit exceeded"})
                resp.status_code = 429
                resp.headers["Retry-After"] = str(retry)
                return resp
            q.append(now)
        return None


def probe_metrics():
    """Upstream reachability latency (ms) and peak process memory (MB)."""
    start = time.monotonic()
    try:
        req = urllib.request.Request(UPSTREAM_PROBE_URL, method="HEAD")
        with urllib.request.urlopen(req, timeout=5) as r:
            upstream = {"reachable": True, "status": r.status}
    except Exception as e:
        upstream = {"reachable": False, "error": type(e).__name__}
    upstream["latency_ms"] = round((time.monotonic() - start) * 1000, 1)
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    mb = rss / (1024 * 1024 if sys.platform == "darwin" else 1024)
    return {"upstream": upstream, "memory_mb": round(mb, 1)}
