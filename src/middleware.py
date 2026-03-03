from flask import g, request
from uuid import uuid4


def register_middleware(app):
    """Register request lifecycle middleware on the Flask app.

    Moves correlation-id handling out of error handlers so middleware sits
    in its own module and `app.py` stays minimal.
    """

    @app.before_request
    def set_correlation_id():
        cid = request.headers.get("X-Request-ID") or uuid4().hex
        g.correlation_id = cid

    @app.after_request
    def add_correlation_header(response):
        cid = getattr(g, "correlation_id", None)
        if cid:
            response.headers.setdefault("X-Request-ID", cid)
        return response
