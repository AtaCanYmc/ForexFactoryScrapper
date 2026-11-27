from flask import g, request
import logging
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

    @app.after_request
    def log_access(response):
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
