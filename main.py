# Thin top-level wrapper for backward compatibility
from src.app import app, run_app  # noqa: F401

# Do not import a default scraper here. Expose placeholders so tests or
# callers can monkeypatch or assign site-specific implementations without
# causing all endpoints to default to one scraper.
get_records = None
get_url = None


if __name__ == "__main__":
    run_app()
