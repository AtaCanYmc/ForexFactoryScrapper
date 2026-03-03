import os
from flask import Blueprint, jsonify, request

from ..openapi_spec import OPENAPI_SPEC

swagger_bp = Blueprint("swagger", __name__)


@swagger_bp.route("/openapi.json", methods=["GET"])
def openapi_json():
    """Return the shared OpenAPI JSON."""
    return jsonify(OPENAPI_SPEC)


@swagger_bp.route("/swagger", methods=["GET"])
def swagger_ui():
    """Serve the static swagger.html template (reads from src/templates)."""
    # Build absolute OpenAPI URL
    openapi_url = request.url_root.rstrip("/") + "/openapi.json"

    # Path to the template file (src/templates/swagger.html)
    template_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "templates", "swagger.html")
    )

    try:
        with open(template_path, "r", encoding="utf-8") as f:
            tpl = f.read()
    except OSError:
        # Fallback: small inline HTML if template missing
        tpl = (
            "<!doctype html><html><head><meta charset='utf-8'/><title>Swagger</title>"
            "<link rel='stylesheet' href='https://unpkg.com/swagger-ui-dist@4/swagger-ui.css'>"
            "</head><body><div id='swagger'></div>"
            "<script src='https://unpkg.com/swagger-ui-dist@4/swagger-ui-bundle.js'></script>"
            "<script>window.onload=function(){SwaggerUIBundle({url:\"%s\",dom_id:'#swagger',"
            "presets:[SwaggerUIBundle.presets.apis]});};</script></body></html>"
        )

    # Template uses %s placeholder for the OpenAPI URL
    try:
        html = tpl % (openapi_url)
    except Exception:
        html = tpl

    return html, 200
