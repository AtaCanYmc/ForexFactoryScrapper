from flask import g, jsonify, request

from . import metrics
import hmac
import logging
import os
import time
from uuid import uuid4

access_log = logging.getLogger("access")


def register_middleware(app):
    """Register request lifecycle middleware on the Flask app.

    Moves correlation-id handling out of error handlers so middleware sits
    in its own module and `app.py` stays minimal.
    """

    @app.before_request
    def set_correlation_id():
        cid = request.headers.get("X-Request-ID") or uuid4().hex
        g.correlation_id = cid
        g.start = time.monotonic()

    @app.before_request
    def require_api_key():
        """API_KEYS (comma-separated) protects /api/*; /api/health stays open for probes."""
        keys = [k.strip() for k in os.getenv("API_KEYS", "").split(",") if k.strip()]
        if not keys or not request.path.startswith("/api/"):
            return None
        if request.path == "/api/health":
            return None
        supplied = request.headers.get("X-API-Key") or request.headers.get(
            "Authorization", ""
        ).removeprefix("Bearer ")
        if any(hmac.compare_digest(supplied, k) for k in keys):
            return None
        resp = jsonify({"error": "Missing or invalid API key"})
        resp.status_code = 401
        resp.headers["WWW-Authenticate"] = "Bearer"
        return resp

    @app.after_request
    def log_access(response):
        elapsed = time.monotonic() - getattr(g, "start", time.monotonic())
        route = request.url_rule.rule if request.url_rule else "unmatched"
        metrics.observe(request.method, route, response.status_code, elapsed)
        access_log.info(
            "request",
            extra={
                "method": request.method,
                "path": request.path,
                "status": response.status_code,
                "duration_ms": round(
                    (time.monotonic() - getattr(g, "start", time.monotonic())) * 1000, 1
                ),
                "request_id": getattr(g, "correlation_id", None),
                "client": request.remote_addr,
            },
        )
        return response

    @app.after_request
    def add_security_headers(response):
        cid = getattr(g, "correlation_id", None)
        if cid:
            response.headers.setdefault("X-Request-ID", cid)
        # Defensive HTTP security headers
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        response.headers.setdefault(
            "Referrer-Policy", "strict-origin-when-cross-origin"
        )
        response.headers.setdefault(
            "Permissions-Policy", "geolocation=(), microphone=(), camera=()"
        )
        return response

    from .performance import register_rate_limit

    register_rate_limit(app)
