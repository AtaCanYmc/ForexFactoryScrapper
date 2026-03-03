from flask import jsonify
from werkzeug.exceptions import HTTPException


def register_error_handlers(app):
    """Register JSON error handlers on the given Flask app.

    This keeps handlers in a separate module so `src/app.py` remains minimal.
    """

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        payload = {
            "error": e.name,
            "message": e.description,
            "status": "error",
            "code": e.code,
        }
        return jsonify(payload), e.code

    @app.errorhandler(Exception)
    def handle_exception(e):
        # Use app.logger so logs integrate with Flask logging configuration
        app.logger.exception("Unhandled exception occurred while processing request")
        payload = {
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "status": "error",
            "code": 500,
        }
        return jsonify(payload), 500
