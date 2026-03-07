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
    # Import get_records/get_url at runtime from src.app so tests can monkeypatch src.app.get_records
    try:
        import src.app as src_app

        get_records = getattr(src_app, "get_records", None)
        get_url = getattr(src_app, "get_url", None)
    except Exception:
        get_records = None
        get_url = None

    # Also allow top-level `main` module to provide overrides (tests monkeypatch `main`)
    try:
        import importlib

        main_mod = importlib.import_module("main")
        main_getRecords = getattr(main_mod, "get_records", None)
        main_getURL = getattr(main_mod, "get_url", None)
        if main_getRecords is not None:
            get_records = main_getRecords
        if main_getURL is not None:
            get_url = main_getURL
    except Exception:
        # ignore if main not available
        pass

    # Resolve helper functions (src.app, main overrides, fallback to site-specific)
    try:
        get_records, get_url = _resolve_helpers("src.scrapper.forexFactoryScrapper")
    except Exception:
        logger.exception("Failed to resolve scraper helpers")
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
        url = get_url(day_i, month_i, year_i, "day")
        record_json = get_records(url)
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

    # Also allow top-level `main` module to provide overrides (tests monkeypatch `main`)
    try:
        import importlib

        main_mod = importlib.import_module("main")
        main_getRecords = getattr(main_mod, "getRecords", None)
        main_getURL = getattr(main_mod, "getURL", None)
        if main_getRecords is not None:
            getRecords = main_getRecords
        if main_getURL is not None:
            getURL = main_getURL
    except Exception:
        pass

    # Fallback to importing directly from the cryptocraft scrapper
    if getRecords is None:
        try:
            from src.scrapper.cryptoCraftScrapper import (
                get_records as _gr,
                get_url as _gu,
            )

            getRecords = _gr
            getURL = _gu
        except Exception:
            logger.exception("Failed to import cryptocraft scraper helpers")
            return jsonify({"error": "Server configuration error"}), 500
    else:
        if getURL is None:
            try:
                from src.scrapper.cryptoCraftScrapper import get_url as _gu

                getURL = _gu
            except Exception:
                logger.exception("Failed to import cryptocraft getURL")
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

    # Normalize cryptocraft records to requested shape: Impact, Event, Actual, Forecast, Previous, Time
    try:
        if isinstance(record_json, list):
            normalized = []
            for r in record_json:
                # Impact must reflect severity (low/medium/high). Do not map Currency into Impact.
                impact = (
                    r.get("Impact") if isinstance(r, dict) and "Impact" in r else None
                )
                normalized.append(
                    {
                        "Impact": impact if impact is not None else "",
                        "Event": r.get("Event") if isinstance(r, dict) else None,
                        "Actual": r.get("Actual") if isinstance(r, dict) else None,
                        "Forecast": r.get("Forecast") if isinstance(r, dict) else None,
                        "Previous": r.get("Previous") if isinstance(r, dict) else None,
                        "Time": r.get("Time") if isinstance(r, dict) else None,
                    }
                )
            record_json = normalized

        # If records is a list apply paging (offset/limit); otherwise return as-is
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

    # Also allow top-level `main` module to provide overrides (tests monkeypatch `main`)
    try:
        import importlib

        main_mod = importlib.import_module("main")
        main_getRecords = getattr(main_mod, "getRecords", None)
        main_getURL = getattr(main_mod, "getURL", None)
        if main_getRecords is not None:
            getRecords = main_getRecords
        if main_getURL is not None:
            getURL = main_getURL
    except Exception:
        pass

    # Fallback to importing directly from the metalsmine scrapper
    if getRecords is None:
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
    else:
        if getURL is None:
            try:
                from src.scrapper.metalsMineScrapper import getURL as _gu

                getURL = _gu
            except Exception:
                logger.exception("Failed to import metalsmine getURL")
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


# --- New: energyexch daily endpoint (mirrors forex endpoint) ---
@api_bp.route("/api/energyexch/daily", methods=["GET"])
def energyexch_daily():
    # Import getRecords/getURL at runtime so tests can monkeypatch src.app.getRecords
    try:
        import src.app as src_app

        getRecords = getattr(src_app, "getRecords", None)
        getURL = getattr(src_app, "getURL", None)
    except Exception:
        getRecords = None
        getURL = None

    # Also allow top-level `main` module to provide overrides (tests monkeypatch `main`)
    try:
        import importlib

        main_mod = importlib.import_module("main")
        main_getRecords = getattr(main_mod, "getRecords", None)
        main_getURL = getattr(main_mod, "getURL", None)
        if main_getRecords is not None:
            getRecords = main_getRecords
        if main_getURL is not None:
            getURL = main_getURL
    except Exception:
        pass

    # Fallback to importing directly from the energyexch scrapper
    if getRecords is None:
        try:
            from src.scrapper.energyExchScrapper import (
                get_records as _gr,
                get_url as _gu,
            )

            getRecords = _gr
            getURL = _gu
        except Exception:
            logger.exception("Failed to import energyexch scraper helpers")
            return jsonify({"error": "Server configuration error"}), 500
    else:
        if getURL is None:
            try:
                from src.scrapper.energyExchScrapper import get_url as _gu

                getURL = _gu
            except Exception:
                logger.exception("Failed to import energyexch getURL")
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


def _resolve_helpers(site_module_path):
    """Return (getRecords, getURL) functions resolved in this order:
    1) src.app module attributes (if callable)
    2) top-level main module attributes (if callable) -- tests may patch this
    3) site-specific scraper module (imported dynamically)

    Raises ImportError if site module cannot be imported when needed.
    """
    getRecords_fn = None
    getURL_fn = None

    # 1) src.app
    try:
        import src.app as src_app

        if callable(getattr(src_app, "getRecords", None)):
            getRecords_fn = getattr(src_app, "getRecords")
        if callable(getattr(src_app, "getURL", None)):
            getURL_fn = getattr(src_app, "getURL")
    except Exception:
        pass

    # 2) main module (tests sometimes monkeypatch main)
    try:
        import importlib

        main_mod = importlib.import_module("main")
        if getRecords_fn is None and callable(getattr(main_mod, "getRecords", None)):
            getRecords_fn = getattr(main_mod, "getRecords")
        if getURL_fn is None and callable(getattr(main_mod, "getURL", None)):
            getURL_fn = getattr(main_mod, "getURL")
    except Exception:
        pass

    # 3) fallback to site-specific scraper for missing functions
    if getRecords_fn is None or getURL_fn is None:
        module = __import__(site_module_path, fromlist=["*"])
        if getRecords_fn is None and hasattr(module, "getRecords"):
            getRecords_fn = getattr(module, "getRecords")
        if getURL_fn is None and hasattr(module, "getURL"):
            getURL_fn = getattr(module, "getURL")

    return getRecords_fn, getURL_fn
