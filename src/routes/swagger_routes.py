from flask import Blueprint, jsonify, request, render_template
from jinja2 import TemplateNotFound

from ..openapi_spec import OPENAPI_SPEC

swagger_bp = Blueprint("swagger", __name__)


@swagger_bp.route("/openapi.json", methods=["GET"])
def openapi_json():
    """Return the shared OpenAPI JSON."""
    return jsonify(OPENAPI_SPEC)


@swagger_bp.route("/swagger", methods=["GET"])
def swagger_ui():
    """Serve the swagger.html Jinja2 template and inject the OpenAPI URL."""
    openapi_url = request.url_root.rstrip("/") + "/openapi.json"

    try:
        # Flask app template_folder points to src/templates, so render_template will find it
        return render_template("swagger.html", openapi_url=openapi_url), 200
    except TemplateNotFound:
        # Fallback inline HTML if template system isn't available
        tpl = (
            "<!doctype html><html><head><meta charset='utf-8'/><title>Swagger</title>"
            "<link rel='stylesheet' href='https://unpkg.com/swagger-ui-dist@4/swagger-ui.css'>"
            "</head><body><div id='swagger'></div>"
            "<script src='https://unpkg.com/swagger-ui-dist@4/swagger-ui-bundle.js'></script>"
            "<script>window.onload=function(){"
            'SwaggerUIBundle({url:"%s",'
            "dom_id:'#swagger',"
            "presets:[SwaggerUIBundle.presets.apis]});};</script>"
            "</body></html>"
        )
        try:
            return tpl % (openapi_url), 200
        except Exception:
            return tpl, 200
