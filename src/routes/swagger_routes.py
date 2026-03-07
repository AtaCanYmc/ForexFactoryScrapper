from flask import Blueprint, jsonify, request, render_template
from jinja2 import TemplateNotFound
import json
import copy

from ..openapi_spec import OPENAPI_SPEC

swagger_bp = Blueprint("swagger", __name__)


@swagger_bp.route("/openapi.json", methods=["GET"])
def openapi_json():
    """Return the shared OpenAPI JSON."""
    return jsonify(OPENAPI_SPEC)


@swagger_bp.route("/swagger", methods=["GET"])
def swagger_ui():
    """Serve the swagger.html Jinja2 template and inject the OpenAPI spec.

    Providing the spec inline avoids a separate client-side fetch which can
    fail in some environments (CORS, file:// usage, etc.). The template will
    use `openapi_spec` if present; otherwise it falls back to fetching the
    spec via `openapi_url`.
    """
    openapi_url = request.url_root.rstrip("/") + "/openapi.json"

    # Use a copy of the spec and set servers to the current request host so
    # Swagger UI's "Try it out" uses the same origin as the UI (avoids CORS).
    spec_for_template = copy.deepcopy(OPENAPI_SPEC)
    try:
        spec_for_template["servers"] = [
            {"url": request.url_root.rstrip("/"), "description": "Server (auto)"}
        ]
    except Exception:
        # if request.url_root is not available, leave spec as-is
        pass

    try:
        # Try to render the template and pass the spec for inline initialization
        return (
            render_template(
                "swagger.html", openapi_url=openapi_url, openapi_spec=spec_for_template
            ),
            200,
        )
    except TemplateNotFound:
        # Fallback inline HTML if template system isn't available. Embed the spec JSON.
        spec_json = json.dumps(spec_for_template)
        tpl = (
            "<!doctype html><html><head><meta charset='utf-8'/><title>Swagger</title>"
            "<link rel='stylesheet' href='https://unpkg.com/swagger-ui-dist@4/swagger-ui.css'>"
            "</head><body><div id='swagger'></div>"
            "<script src='https://unpkg.com/swagger-ui-dist@4/swagger-ui-bundle.js'></script>"
            "<script>window.onload=function(){"
            "var spec = %s;"
            "SwaggerUIBundle({spec: spec,dom_id:'#swagger',presets:[SwaggerUIBundle.presets.apis]});};</script>"
            "</body></html>"
        )
        try:
            return tpl % (spec_json), 200
        except Exception:
            return tpl, 200
