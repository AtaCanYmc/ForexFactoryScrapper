"""
Package-level exports for route blueprints.
Importing `src.routes` will expose the common blueprint objects so callers
can register them easily or use the convenience `register_blueprints` helper.
"""

from .helper_routes import helper_bp
from .forex_factory_routes import forex_bp
from .crypto_craft_routes import crypto_bp
from .energy_exch_routes import energy_bp
from .metals_mine_routes import metals_bp
from .root_routes import root_bp

__all__ = [
    "helper_bp",
    "forex_bp",
    "crypto_bp",
    "energy_bp",
    "metals_bp",
    "root_bp",
]


def register_blueprints(app, swagger_bp=None):
    """Register all route blueprints on the provided Flask app.

    Arguments:
        app: Flask application instance
        swagger_bp: optional blueprint for swagger routes to register as well
    """
    app.register_blueprint(root_bp)
    app.register_blueprint(helper_bp)
    app.register_blueprint(forex_bp)
    app.register_blueprint(crypto_bp)
    app.register_blueprint(energy_bp)
    app.register_blueprint(metals_bp)
    if swagger_bp:
        app.register_blueprint(swagger_bp)
