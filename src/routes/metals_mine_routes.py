import logging
from flask import Blueprint, jsonify, request

from .common_helpers import (
    _resolve_helpers,
    _validate_date_params,
    _validate_paging_params,
)

logger = logging.getLogger(__name__)

metals_bp = Blueprint("metalsmine", __name__)


@metals_bp.route("/api/metalsmine/daily", methods=["GET"])
def metalsmine_daily():
    try:
        get_records, get_url = _resolve_helpers("src.scrapper.metalsMineScrapper")
    except Exception:
        logger.exception("Failed to resolve metalsmine scraper helpers")
        return jsonify({"error": "Server configuration error"}), 500

    # validate presence and parse
    day = request.args.get("day")
    month = request.args.get("month")
    year = request.args.get("year")
    date_err, day_i, month_i, year_i = _validate_date_params(day, month, year)

    if date_err:
        return jsonify({"error": date_err}), 400

    # Optional paging parameters
    limit_param = request.args.get("limit")
    offset_param = request.args.get("offset")

    limit, offset, paging_err = _validate_paging_params(limit_param, offset_param)
    if paging_err:
        return jsonify({"error": paging_err}), 400

    try:
        url = get_url(day_i, month_i, year_i, "day")
        record_json = get_records(url)
    except Exception:
        logger.exception("Failed to fetch or parse metalsmine records")
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
        logger.exception("Failed to apply paging to metalsmine records")
        return jsonify({"error": "Failed to process records"}), 500
