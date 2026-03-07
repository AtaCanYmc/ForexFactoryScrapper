import logging
from flask import Blueprint, jsonify, request

from .common_helpers import _resolve_helpers

logger = logging.getLogger(__name__)

energy_bp = Blueprint("energyexch", __name__)


@energy_bp.route("/api/energyexch/daily", methods=["GET"])
def energyexch_daily():
    try:
        get_records, get_url = _resolve_helpers("src.scrapper.energyExchScrapper")
    except Exception:
        logger.exception("Failed to resolve energyexch helpers")
        return jsonify({"error": "Server configuration error"}), 500

    # validate presence
    day = request.args.get("day")
    month = request.args.get("month")
    year = request.args.get("year")

    if not (day and month and year):
        payload = {
            "error": ("Missing one or more required parameters: day, month, year")
        }
        return jsonify(payload), 400

    # validate types
    try:
        day_i = int(day)
        month_i = int(month)
        year_i = int(year)
    except ValueError:
        return (
            jsonify({"error": ("Parameters day, month and year must be integers")}),
            400,
        )

    # simple range checks
    if not (1 <= day_i <= 31 and 1 <= month_i <= 12 and 1900 <= year_i <= 2100):
        return (jsonify({"error": "Parameters out of reasonable range"}), 400)

    # Optional paging parameters
    limit_param = request.args.get("limit")
    offset_param = request.args.get("offset")

    limit = None
    offset = 0

    if limit_param is not None:
        try:
            limit = int(limit_param)
        except ValueError:
            return jsonify({"error": "Parameter 'limit' must be an integer"}), 400
        if limit < 0:
            return jsonify({"error": "Parameter 'limit' must be >= 0"}), 400

    if offset_param is not None:
        try:
            offset = int(offset_param)
        except ValueError:
            return jsonify({"error": "Parameter 'offset' must be an integer"}), 400
        if offset < 0:
            return jsonify({"error": "Parameter 'offset' must be >= 0"}), 400

    try:
        url = get_url(day_i, month_i, year_i, "day")
        record_json = get_records(url)
    except Exception:
        logger.exception("Failed to fetch or parse energyexch records")
        raise

    # Apply paging if list
    try:
        if isinstance(record_json, list):
            total = len(record_json)

            if offset and offset > 0:
                if offset >= total:
                    paged = []
                else:
                    paged = record_json[offset:]
            else:
                paged = record_json[:]

            if limit is not None:
                paged = paged[:limit]

            response_body = {
                "total": total,
                "offset": offset,
                "limit": limit,
                "results": paged,
            }

            return jsonify(response_body), 200
        else:
            return jsonify(record_json), 200
    except Exception:
        logger.exception("Failed to apply paging to energyexch records")
        return jsonify({"error": "Failed to process records"}), 500
