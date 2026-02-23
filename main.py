# Thin top-level wrapper for backward compatibility
from src.app import app, run_app  # noqa: F401
from src.forexFactoryScrapper import getRecords, getURL  # noqa: F401

if __name__ == "__main__":
    run_app()
