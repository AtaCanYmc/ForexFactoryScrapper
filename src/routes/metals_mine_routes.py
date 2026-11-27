import logging
from flask import Blueprint, jsonify, request

from forex_pytory.core.scraper import metals_mine_scraper

from ..performance import cached_get_records
from .common_helpers import (
    _validate_date_params,
    _validate_paging_params,
)

logger = logging.getLogger(__name__)

metals_bp = Blueprint("metalsmine", __name__)


@metals_bp.route("/api/metalsmine/daily", methods=["GET"])
def metalsmine_daily():
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
        url = metals_mine_scraper.get_url(
            day=day_i, month=month_i, year=year_i, timeline="day"
        )
        records = cached_get_records(metals_mine_scraper, url)
    except Exception as e:
        logger.exception(f"Failed to fetch or parse metalsmine records: {e}")
        return jsonify({"error": "Failed to fetch data"}), 500

    try:
        # Convert Pydantic models to dicts
        record_json = [r.model_dump(by_alias=True) for r in records]

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
            "results": paged,
        }

        return jsonify(response_body), 200
    except Exception as e:
        logger.exception(f"Failed to process records: {e}")
        return jsonify({"error": "Failed to process records"}), 500
