import logging
import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

from forexFactoryScrapper import getRecords, getURL

# Load .env file if present. Use DOTENV_PATH to override if needed.
dotenv_path = os.getenv("DOTENV_PATH")
if dotenv_path:
    load_dotenv(dotenv_path)
else:
    load_dotenv()  # will search for a .env file in cwd or parent directories

app = Flask(__name__)
CORS(app)

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route("/api/hello", methods=["GET"])
def hello():
    response_data = {"message": "Hello, World!", "status": "success"}
    return jsonify(response_data), 200


@app.route("/api/health", methods=["GET"])
def health():
    """Health endpoint for quick liveness check."""
    return jsonify({"status": "ok"}), 200


@app.route("/api/forex/daily", methods=["GET"])
def daily_data():
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

    try:
        url = getURL(day_i, month_i, year_i, "day")
        record_json = getRecords(url)
    except Exception as e:
        logger.exception("Failed to fetch or parse records")
        return (
            jsonify({"error": "Failed to fetch records", "detail": str(e)}),
            502,
        )

    return jsonify(record_json), 200


if __name__ == "__main__":
    # Allow configuration via environment variables or .env file.
    # Defaults keep previous behavior.
    host = os.getenv("HOST", "0.0.0.0")
    try:
        port = int(os.getenv("PORT", "5000"))
    except ValueError:
        logger.warning("PORT env var is not an integer; falling back to 5000")
        port = 5000

    debug_env = os.getenv("DEBUG", "True").lower()
    debug = debug_env in ("1", "true", "yes", "on")

    try:
        app.run(host=host, port=port, debug=debug)
    except OSError as e:
        # Common case: address already in use
        if (
            "address already in use" in str(e).lower()
            or getattr(e, "errno", None) == 98
        ):
            logger.error("Port %s is already in use.", port)
            logger.error("Option 1: stop the process using the port.")
            logger.error("Example: lsof -i tcp:%s", port)
            logger.error("Option 2: run this app on a different port.")
            logger.error("Example: PORT=5001 python main.py")
        else:
            logger.exception("Failed to start the Flask app")
        raise
