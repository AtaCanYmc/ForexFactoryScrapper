import logging
import os

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

# Do not import a default scrapper here — importing forex scrapper at module import time
# caused all endpoints to use the forex implementation. Leave getRecords/getURL as
# None so routes can fall back to their site-specific scrapers.
get_records = None
get_url = None

# Load .env file if present. Use DOTENV_PATH to override if needed.
dotenv_path = os.getenv("DOTENV_PATH")
if dotenv_path:
    load_dotenv(dotenv_path)
else:
    load_dotenv()  # will search for a .env file in cwd or parent directories

# Ensure Flask uses the package's templates directory
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
app = Flask(__name__, template_folder=TEMPLATES_DIR)

# Configure CORS to allow all origins for all routes (explicit)
# This avoids cross-origin issues when Swagger UI issues requests from different
# hostnames (localhost vs 127.0.0.1). If you need to lock this down in prod,
# set a specific origin or use environment config.
CORS(app, resources={r"/*": {"origins": "*"}})

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Register blueprints: API routes and Swagger routes
# Import inside try/except to avoid hard failure if routes are missing during partial installs
try:
    from .routes import register_blueprints

    # try to import swagger if available
    from .routes.swagger_routes import swagger_bp
except Exception:
    register_blueprints = None
    swagger_bp = None

if register_blueprints is not None:
    try:
        register_blueprints(app, swagger_bp=swagger_bp)
    except Exception:
        logger.exception("Failed to register route blueprints")
else:
    logger.debug(
        "Route blueprints not available; app will run without registered routes"
    )

# Register middleware (e.g. correlation-id) from src.middleware
try:
    from .middleware import register_middleware

    register_middleware(app)
except Exception:
    logger.debug("Middleware module not available; skipping middleware registration")

# Register centralized error handlers from routes/error_handlers.py
try:
    from .routes.error_handlers import register_error_handlers

    register_error_handlers(app)
except Exception:
    logger.debug("Error handlers module not available; using default Flask handlers")


def run_app():
    """Start the Flask app using environment configuration (HOST/PORT/DEBUG).

    This function is safe to import and call from external wrappers.
    """
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
            logger.error("Example: PORT=5001 python app.py")
        else:
            logger.exception("Failed to start the Flask app")
        raise


if __name__ == "__main__":
    run_app()
