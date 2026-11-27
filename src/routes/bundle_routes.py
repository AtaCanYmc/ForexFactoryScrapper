from flask import Blueprint, request, jsonify
import logging
import os

from forex_pytory.core.scraper import (
    forex_factory_scraper,
    crypto_craft_scraper,
    metals_mine_scraper,
    energy_exch_scraper,
)

from ..performance import cached_get_records
from .common_helpers import (
    _validate_date_range_params,
    _validate_paging_params,
)

logger = logging.getLogger(__name__)

bundle_bp = Blueprint("bundle", __name__)

MAX_BUNDLE_DAYS = int(os.getenv("MAX_BUNDLE_DAYS", "31"))


@bundle_bp.route("/api/bundle", methods=["GET"])
def get_economic_events_bundle():
    """Endpoint to scrape economic events from multiple sources within a date range."""
    # 1. Parse and validate query parameters
    supported_sources = {"forex", "crypto", "metal", "energy"}
    sources_raw = request.args.getlist("sources")

    if not sources_raw:
        sources = ["forex"]
    else:
        # Handle both comma-separated string and multiple query params
        sources = []
        for s in sources_raw:
            # Split by comma in case it's a single comma-separated string
            sources.extend([x.strip().lower() for x in s.split(",")])

    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")

    # Optional paging parameters
    limit_param = request.args.get("limit")
    offset_param = request.args.get("offset")

    # 2. Validate date range
    if not start_date_str or not end_date_str:
        return (
            jsonify(
                {
                    "error": "Missing required parameters",
                    "message": "Both 'start_date' and 'end_date' are required in YYYY-MM-DD format.",
                }
            ),
            400,
        )

    date_err, start_date, end_date = _validate_date_range_params(
        start_date_str, end_date_str, max_days=MAX_BUNDLE_DAYS
    )
    if date_err:
        return jsonify({"error": "Invalid date parameters", "message": date_err}), 400

    # 3. Validate sources
    invalid_sources = set(sources) - supported_sources
    if invalid_sources:
        return (
            jsonify(
                {
                    "error": "Unsupported source detected",
                    "message": (
                        f"Supported sources are {sorted(list(supported_sources))}. "
                        f"Invalid: {sorted(list(invalid_sources))}"
                    ),
                }
            ),
            400,
        )

    # 4. Validate paging parameters
    limit, offset, paging_err = _validate_paging_params(limit_param, offset_param)
    if paging_err:
        return (
            jsonify({"error": "Invalid paging parameters", "message": paging_err}),
            400,
        )

    logger.info(
        f"Bundle request | Sources: {sources} | Date range: {start_date} to {end_date}"
    )

    try:
        # 5. Fetch data from each source
        all_combined_events = []
        source_results = {}

        source_map = {
            "forex": forex_factory_scraper,
            "crypto": crypto_craft_scraper,
            "metal": metals_mine_scraper,
            "energy": energy_exch_scraper,
        }

        for source in sources:
            try:
                scraper_module = source_map.get(source)
                if not scraper_module:
                    continue

                source_events = _fetch_from_date_range(
                    scraper_module, start_date, end_date
                )

                # Add source tag to each event for tracking
                for event in source_events:
                    if isinstance(event, dict):
                        event["_source"] = source

                source_results[source] = source_events
                all_combined_events.extend(source_events)

                logger.info(f"Fetched {len(source_events)} events from {source}")

            except Exception as e:
                logger.warning(f"Failed to fetch from {source}: {e}")
                source_results[source] = []

        # 6. Apply paging to combined results
        total = len(all_combined_events)

        # Apply offset
        if offset and offset > 0:
            if offset >= total:
                paged = []
            else:
                paged = all_combined_events[offset:]
        else:
            paged = all_combined_events[:]

        # Apply limit
        if limit is not None:
            paged = paged[:limit]

        # Wrap results with pagination metadata
        response_body = {
            "total": total,
            "offset": offset,
            "limit": limit,
            "start_date": str(start_date),
            "end_date": str(end_date),
            "sources": sources,
            "source_breakdown": {
                source: len(source_results.get(source, [])) for source in sources
            },
            "results": paged,
        }

        return jsonify(response_body), 200

    except Exception as e:
        logger.exception(f"Bundle scraper error: {e}")
        return (
            jsonify(
                {
                    "error": "Internal server error",
                    "message": "An error occurred while scraping the target websites.",
                }
            ),
            500,
        )


def _fetch_from_date_range(scraper_module, start_date, end_date):
    """Fetch records from a scraper for each day in the date range.

    Args:
        scraper_module: The scraper module from forex_pytory (e.g., forex_factory_scraper)
        start_date: datetime.date object for start
        end_date: datetime.date object for end

    Returns:
        List of records from all days in the range
    """
    from datetime import timedelta

    all_records = []
    current_date = start_date

    while current_date <= end_date:
        try:
            day = current_date.day
            month = current_date.month
            year = current_date.year

            url = scraper_module.get_url(day, month, year, "day")
            records = cached_get_records(scraper_module, url)

            # Convert to dicts
            record_json = [r.model_dump(by_alias=True) for r in records]

            if isinstance(record_json, list):
                # Add date info to each record
                for record in record_json:
                    if isinstance(record, dict):
                        record["_date"] = str(current_date)
                all_records.extend(record_json)

        except Exception as e:
            logger.warning(
                f"Failed to fetch data for {current_date} from {scraper_module.__name__}: {e}"
            )

        current_date += timedelta(days=1)

    return all_records
