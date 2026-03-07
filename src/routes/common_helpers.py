import logging

logger = logging.getLogger(__name__)


def _resolve_helpers(site_module_path):
    """Return (get_records, get_url) functions resolved in this order:
    1) src.app module attributes (if callable)
    2) top-level main module attributes (if callable) -- tests may patch this
    3) site-specific scraper module (imported dynamically)

    Raises ImportError if site module cannot be imported when needed.
    """
    get_records_fn = None
    get_url_fn = None

    # 1) src.app
    try:
        import src.app as src_app

        if callable(getattr(src_app, "get_records", None)):
            get_records_fn = getattr(src_app, "get_records")
        if callable(getattr(src_app, "get_url", None)):
            get_url_fn = getattr(src_app, "get_url")
    except Exception:
        pass

    # 2) main module (tests sometimes monkeypatch main)
    try:
        import importlib

        main_mod = importlib.import_module("main")
        if get_records_fn is None and callable(getattr(main_mod, "get_records", None)):
            get_records_fn = getattr(main_mod, "get_records")
        if get_url_fn is None and callable(getattr(main_mod, "get_url", None)):
            get_url_fn = getattr(main_mod, "get_url")
    except Exception:
        pass

    # 3) fallback to site-specific scraper for missing functions
    if get_records_fn is None or get_url_fn is None:
        module = __import__(site_module_path, fromlist=["*"])
        if get_records_fn is None and hasattr(module, "get_records"):
            get_records_fn = getattr(module, "get_records")
        if get_url_fn is None and hasattr(module, "get_url"):
            get_url_fn = getattr(module, "get_url")

    return get_records_fn, get_url_fn


# Shared validation helpers
def _validate_date_params(day, month, year):
    """Validate and parse day/month/year. Returns tuple:
    (error_message_or_None, day_i, month_i, year_i)
    """
    if not (day and month and year):
        return (
            "Missing one or more required parameters: day, month, year",
            None,
            None,
            None,
        )

    try:
        day_i = int(day)
        month_i = int(month)
        year_i = int(year)
    except ValueError:
        return "Parameters day, month and year must be integers", None, None, None

    if not (1 <= day_i <= 31 and 1 <= month_i <= 12 and 1900 <= year_i <= 2100):
        return "Parameters out of reasonable range", None, None, None

    return None, day_i, month_i, year_i


def _validate_paging_params(limit_param, offset_param):
    """Validate limit/offset query params. Returns (limit, offset, error)
    On success: (limit_int_or_None, offset_int, None)
    On error: (None, None, error_message)
    """
    limit = None
    offset = 0

    if limit_param is not None:
        try:
            limit = int(limit_param)
        except ValueError:
            return None, None, "Parameter 'limit' must be an integer"
        if limit < 0:
            return None, None, "Parameter 'limit' must be >= 0"

    if offset_param is not None:
        try:
            offset = int(offset_param)
        except ValueError:
            return None, None, "Parameter 'offset' must be an integer"
        if offset < 0:
            return None, None, "Parameter 'offset' must be >= 0"

    return limit, offset, None
