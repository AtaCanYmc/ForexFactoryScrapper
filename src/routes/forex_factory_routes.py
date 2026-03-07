import logging
from flask import Blueprint, jsonify, request

from .common_helpers import (
    _resolve_helpers,
    _validate_date_params,
    _validate_paging_params,
)

logger = logging.getLogger(__name__)

forex_bp = Blueprint("forex", __name__)


@forex_bp.route("/api/forex/daily", methods=["GET"])
def daily_data():
    try:
        get_records, get_url = _resolve_helpers("src.scrapper.forexFactoryScrapper")
    except Exception:
        logger.exception("Failed to resolve scraper helpers")
        return jsonify({"error": "Server configuration error"}), 500

    # validate presence and parse
    day = request.args.get("day")
    month = request.args.get("month")
    year = request.args.get("year")
    date_err, day_i, month_i, year_i = _validate_date_params(day, month, year)

    if date_err:
        return jsonify({"error": date_err}), 400

    # Optional paging parameters: limit and offset
    limit_param = request.args.get("limit")
    offset_param = request.args.get("offset")

    limit, offset, paging_err = _validate_paging_params(limit_param, offset_param)
    if paging_err:
        return jsonify({"error": paging_err}), 400

    try:
        url = get_url(day_i, month_i, year_i, "day")
        record_json = get_records(url)
    except Exception:
        logger.exception("Failed to fetch or parse records")
        raise

    # If records is a list apply paging (offset/limit); otherwise return as-is
    try:
        if isinstance(record_json, list):
            total = len(record_json)

            # apply offset
            if offset and offset > 0:
                if offset >= total:
                    paged = []
                else:
                    paged = record_json[offset:]
            else:
                paged = record_json[:]

            # apply limit
            if limit is not None:
                paged = paged[:limit]

            # Wrap results with pagination metadata
            response_body = {
                "total": total,
                "offset": offset,
                "limit": limit,
                "url": url,
                "results": paged,
            }

            return jsonify(response_body), 200
        else:
            return jsonify(record_json), 200
    except Exception:
        logger.exception("Failed to apply paging to records")
        return jsonify({"error": "Failed to process records"}), 500
