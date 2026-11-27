import json
import logging
import os
import resource
import sys
import threading
import time
from http.client import HTTPSConnection
from collections import defaultdict, deque

from flask import jsonify, request

from . import metrics

logger = logging.getLogger(__name__)

_cache = {}
_cache_lock = threading.Lock()
_hits = defaultdict(deque)
_hits_lock = threading.Lock()
_redis_client = None

UPSTREAM_PROBE_HOST = "www.forexfactory.com"


def _int_env(name, default):
    try:
        return max(0, int(os.getenv(name, default)))
    except ValueError:
        return default


class _Dumped:
    """Record rebuilt from Redis JSON; routes only call model_dump()."""

    def __init__(self, data):
        self._data = data

    def model_dump(self, **_):
        return dict(self._data)


def _redis():
    global _redis_client
    if _redis_client is None:
        import redis

        _redis_client = redis.Redis.from_url(
            os.getenv("REDIS_URL", "redis://localhost:6379/0")
        )
    return _redis_client


def _redis_get_records(scraper, url, ttl):
    key = f"ffs:{scraper.__name__}:{url}"
    try:
        raw = _redis().get(key)
    except Exception:
        logger.warning("Redis read failed; fetching upstream", exc_info=True)
        raw = None
    if raw is not None:
        metrics.inc("cache_hits")
        return [_Dumped(d) for d in json.loads(raw)]
    metrics.inc("cache_misses")
    records = scraper.get_records(url)
    try:
        payload = json.dumps(
            [r.model_dump(by_alias=True) for r in records], default=str
        )
        _redis().setex(key, ttl, payload)
    except Exception:
        logger.warning("Redis write failed; response not cached", exc_info=True)
    return records


def cached_get_records(scraper, url):
    """Return scraper.get_records(url), cached for CACHE_TTL_SECONDS (0 = off).

    CACHE_BACKEND=memory (default) is per process; CACHE_BACKEND=redis is shared.
    """
    ttl = _int_env("CACHE_TTL_SECONDS", 0)
    if not ttl:
        return scraper.get_records(url)
    if os.getenv("CACHE_BACKEND", "memory").lower() == "redis":
        return _redis_get_records(scraper, url, ttl)
    key = (scraper.__name__, url)
    now = time.monotonic()
    with _cache_lock:
        hit = _cache.get(key)
        if hit and hit[0] > now:
            metrics.inc("cache_hits")
            return hit[1]
    metrics.inc("cache_misses")
    records = scraper.get_records(url)
    with _cache_lock:
        if len(_cache) >= _int_env("CACHE_MAX_ENTRIES", 256):
            for k in [k for k, v in _cache.items() if v[0] <= now] or [
                next(iter(_cache))
            ]:
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
                metrics.inc("rate_limited")
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
        conn = HTTPSConnection(UPSTREAM_PROBE_HOST, timeout=5)
        try:
            conn.request("HEAD", "/")
            upstream = {"reachable": True, "status": conn.getresponse().status}
        finally:
            conn.close()
    except Exception as e:
        upstream = {"reachable": False, "error": type(e).__name__}
    upstream["latency_ms"] = round((time.monotonic() - start) * 1000, 1)
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    mb = rss / (1024 * 1024 if sys.platform == "darwin" else 1024)
    return {"upstream": upstream, "memory_mb": round(mb, 1)}
