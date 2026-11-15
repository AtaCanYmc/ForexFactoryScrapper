import logging
import os
from flask import Blueprint, jsonify, request

from .common_helpers import _validate_paging_params, _validate_date_range_params

logger = logging.getLogger(__name__)

sitemap_bp = Blueprint("sitemap", __name__)

MAX_SITEMAP_PAGES = int(os.getenv("MAX_SITEMAP_PAGES", "100"))


@sitemap_bp.route("/api/forex/sitemaps", methods=["GET"])
def sitemap_urls():
    try:
        # import here to avoid import-time network activity
        from forex_pytory.core.scraper import forexfactory_sitemap as sitemap_scraper
    except Exception as e:
        logger.exception(f"Failed to import sitemap scraper module: {e}")
        return jsonify({"error": "Server configuration error"}), 500

    # validate date range params
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")
    date_err, start_date, end_date = _validate_date_range_params(
        start_date_str, end_date_str
    )
    if date_err:
        return jsonify({"error": date_err}), 400

    # paging
    limit_param = request.args.get("limit")
    offset_param = request.args.get("offset")
    limit, offset, paging_err = _validate_paging_params(limit_param, offset_param)
    if paging_err:
        return jsonify({"error": paging_err}), 400

    # max_pages
    max_pages_param = request.args.get("max_pages")
    try:
        max_pages = int(max_pages_param) if max_pages_param is not None else 10
        if max_pages < 1 or max_pages > MAX_SITEMAP_PAGES:
            raise ValueError()
    except ValueError:
        return (
            jsonify(
                {
                    "error": (
                        f"Parameter 'max_pages' must be a positive integer between 1 and {MAX_SITEMAP_PAGES}"
                    )
                }
            ),
            400,
        )

    try:
        result = sitemap_scraper.get_sitemap_urls(
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
            max_pages=max_pages,
        )
    except Exception as e:
        logger.exception(f"Failed to fetch sitemap URLs: {e}")
        return jsonify({"error": "Failed to fetch sitemap URLs"}), 500

    return jsonify(result), 200
