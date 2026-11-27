import logging
from flask import Blueprint, jsonify, request
from ..performance import probe_metrics

logger = logging.getLogger(__name__)

helper_bp = Blueprint("helper", __name__)


@helper_bp.route("/api/hello", methods=["GET"])
def hello():
    return jsonify({"message": "Hello, World!", "status": "success"}), 200


@helper_bp.route("/api/health", methods=["GET"])
def health():
    """Liveness check. Add ?probe=true for upstream latency and memory metrics."""
    body = {"status": "ok"}
    if request.args.get("probe", "").lower() in ("1", "true"):
        body.update(probe_metrics())
    return jsonify(body), 200
