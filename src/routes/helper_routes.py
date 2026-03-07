import logging
from flask import Blueprint, jsonify

logger = logging.getLogger(__name__)

helper_bp = Blueprint("helper", __name__)


@helper_bp.route("/api/hello", methods=["GET"])
def hello():
    return jsonify({"message": "Hello, World!", "status": "success"}), 200


@helper_bp.route("/api/health", methods=["GET"])
def health():
    """Health endpoint for quick liveness check."""
    return jsonify({"status": "ok"}), 200
