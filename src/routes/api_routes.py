import logging
from flask import Blueprint, jsonify, request

logger = logging.getLogger(__name__)

api_bp = Blueprint("api", __name__)


@api_bp.route("/api/hello", methods=["GET"])
def hello():
    return jsonify({"message": "Hello, World!", "status": "success"}), 200


@api_bp.route("/api/health", methods=["GET"])
def health():
    """Health endpoint for quick liveness check."""
    return jsonify({"status": "ok"}), 200


@api_bp.route("/api/forex/daily", methods=["GET"])
def daily_data():
    # Import getRecords/getURL at runtime from src.app so tests can monkeypatch src.app.getRecords
    try:
        import src.app as src_app

        getRecords = getattr(src_app, "getRecords", None)
        getURL = getattr(src_app, "getURL", None)
    except Exception:
        getRecords = None
        getURL = None

    # Fallback to importing directly from the scraper module if not available
    if getRecords is None or getURL is None:
        try:
            from src.scrapper.forexFactoryScrapper import (
                getRecords as _gr,
                getURL as _gu,
            )

            getRecords = _gr
            getURL = _gu
        except Exception:
            logger.exception("Failed to import scraper helpers")
            return jsonify({"error": "Server configuration error"}), 500

    # validate presence
    day = request.args.get("day")
    month = request.args.get("month")
    year = request.args.get("year")
    if not (day and month and year):
        payload = {
            "error": ("Missing one or more required parameters: day, month, year")
        }
        return jsonify(payload), 400  # HTTP 400 Bad Request

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
        return (
            jsonify({"error": "Parameters out of reasonable range"}),
            400,
        )

    # Optional paging parameters: limit and offset
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
        url = getURL(day_i, month_i, year_i, "day")
        record_json = getRecords(url)
    except Exception:
        logger.exception("Failed to fetch or parse records")
        # Let centralized error handlers handle this (return 500) instead of returning 502 here
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
                "results": paged,
            }

            return jsonify(response_body), 200
        else:
            return jsonify(record_json), 200
    except Exception:
        logger.exception("Failed to apply paging to records")
        return jsonify({"error": "Failed to process records"}), 500


# --- New: cryptocraft daily endpoint (mirrors forex endpoint) ---
@api_bp.route("/api/cryptocraft/daily", methods=["GET"])
def cryptocraft_daily():
    # Import getRecords/getURL at runtime so tests can monkeypatch src.app.getRecords
    try:
        import src.app as src_app

        getRecords = getattr(src_app, "getRecords", None)
        getURL = getattr(src_app, "getURL", None)
    except Exception:
        getRecords = None
        getURL = None

    # Fallback to importing directly from the cryptocraft scrapper
    if getRecords is None or getURL is None:
        try:
            from src.scrapper.cryptoCraftScrapper import (
                getRecords as _gr,
                getURL as _gu,
            )

            getRecords = _gr
            getURL = _gu
        except Exception:
            logger.exception("Failed to import cryptocraft scraper helpers")
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
        return (
            jsonify({"error": "Parameters out of reasonable range"}),
            400,
        )

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
        url = getURL(day_i, month_i, year_i, "day")
        record_json = getRecords(url)
    except Exception:
        logger.exception("Failed to fetch or parse cryptocraft records")
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
        logger.exception("Failed to apply paging to cryptocraft records")
        return jsonify({"error": "Failed to process records"}), 500


# --- New: metalsmine daily endpoint (mirrors forex endpoint) ---
@api_bp.route("/api/metalsmine/daily", methods=["GET"])
def metalsmine_daily():
    # Import getRecords/getURL at runtime so tests can monkeypatch src.app.getRecords
    try:
        import src.app as src_app

        getRecords = getattr(src_app, "getRecords", None)
        getURL = getattr(src_app, "getURL", None)
    except Exception:
        getRecords = None
        getURL = None

    # Fallback to importing directly from the metalsmine scrapper
    if getRecords is None or getURL is None:
        try:
            from src.scrapper.metalsMineScrapper import (
                getRecords as _gr,
                getURL as _gu,
            )

            getRecords = _gr
            getURL = _gu
        except Exception:
            logger.exception("Failed to import metalsmine scraper helpers")
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
        url = getURL(day_i, month_i, year_i, "day")
        record_json = getRecords(url)
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
