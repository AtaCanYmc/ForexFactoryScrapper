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
