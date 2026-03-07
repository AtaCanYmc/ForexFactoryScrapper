import logging
from flask import Blueprint, render_template

logger = logging.getLogger(__name__)

root_bp = Blueprint("root", __name__)


@root_bp.route("/", methods=["GET"])
def welcome():
    """Render a simple welcome page with quick links to the API."""
    try:
        return render_template("welcome.html"), 200
    except Exception:
        logger.exception("Failed to render welcome template")
        # Fallback: return plain text
        return ("<html><body><h1>Welcome</h1></body></html>"), 200
