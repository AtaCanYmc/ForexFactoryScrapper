from flask import jsonify, g
from werkzeug.exceptions import HTTPException


def register_error_handlers(app):
    """Register JSON error handlers on the given Flask app.

    Error handlers are kept separate so `src/app.py` remains minimal. Correlation-id
    middleware has been moved to `src/middleware.py`.
    """

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        payload = {
            "error": e.name,
            "message": e.description,
            "status": "error",
            "code": e.code,
            "correlation_id": getattr(g, "correlation_id", None),
        }
        return jsonify(payload), e.code

    @app.errorhandler(Exception)
    def handle_exception(e):
        # Use app.logger so logs integrate with Flask logging configuration
        app.logger.exception(
            "Unhandled exception occurred while processing request (cid=%s)",
            getattr(g, "correlation_id", None),
        )
        payload = {
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "status": "error",
            "code": 500,
            "correlation_id": getattr(g, "correlation_id", None),
        }
        return jsonify(payload), 500
