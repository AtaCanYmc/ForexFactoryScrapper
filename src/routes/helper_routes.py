import logging
from flask import Blueprint, Response, jsonify, request

from .. import metrics
from ..performance import probe_metrics

logger = logging.getLogger(__name__)

helper_bp = Blueprint("helper", __name__)


@helper_bp.route("/api/hello", methods=["GET"])
def hello():
    return jsonify({"message": "Hello, World!", "status": "success"}), 200


@helper_bp.route("/metrics", methods=["GET"])
def prometheus_metrics():
    """Prometheus scrape target (text exposition format)."""
    return Response(metrics.render(), mimetype="text/plain; version=0.0.4")


@helper_bp.route("/api/health", methods=["GET"])
def health():
    """Liveness check. Add ?probe=true for upstream latency and memory metrics."""
    body = {"status": "ok"}
    if request.args.get("probe", "").lower() in ("1", "true"):
        body.update(probe_metrics())
    return jsonify(body), 200
