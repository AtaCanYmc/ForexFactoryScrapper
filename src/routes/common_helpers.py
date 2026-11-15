import logging

logger = logging.getLogger(__name__)


# Shared validation helpers
def _validate_date_params(day, month, year):
    """Validate and parse day/month/year. Returns tuple:
    (error_message_or_None, day_i, month_i, year_i)
    """
    if not (day and month and year):
        return (
            "Missing one or more required parameters: day, month, year",
            None,
            None,
            None,
        )

    try:
        day_i = int(day)
        month_i = int(month)
        year_i = int(year)
    except ValueError:
        return "Parameters day, month and year must be integers", None, None, None

    if not (1 <= day_i <= 31 and 1 <= month_i <= 12 and 1900 <= year_i <= 2100):
        return "Parameters out of reasonable range", None, None, None

    from datetime import date

    try:
        date(year_i, month_i, day_i)
    except ValueError:
        return (
            f"Invalid calendar date for day={day_i}, month={month_i}, year={year_i}",
            None,
            None,
            None,
        )

    return None, day_i, month_i, year_i


def _validate_paging_params(limit_param, offset_param):
    """Validate limit/offset query params. Returns (limit, offset, error)
    On success: (limit_int_or_None, offset_int, None)
    On error: (None, None, error_message)
    """
    MAX_PAGE_LIMIT = 500
    MAX_PAGE_OFFSET = 100000

    limit = None
    offset = 0

    if limit_param is not None:
        try:
            limit = int(limit_param)
        except ValueError:
            return None, None, "Parameter 'limit' must be an integer"
        if limit < 0:
            return None, None, "Parameter 'limit' must be >= 0"
        if limit > MAX_PAGE_LIMIT:
            return (
                None,
                None,
                f"Parameter 'limit' exceeds maximum allowed limit of {MAX_PAGE_LIMIT}",
            )

    if offset_param is not None:
        try:
            offset = int(offset_param)
        except ValueError:
            return None, None, "Parameter 'offset' must be an integer"
        if offset < 0:
            return None, None, "Parameter 'offset' must be >= 0"
        if offset > MAX_PAGE_OFFSET:
            return (
                None,
                None,
                f"Parameter 'offset' exceeds maximum allowed offset of {MAX_PAGE_OFFSET}",
            )

    return limit, offset, None


def _validate_date_range_params(start_date_str, end_date_str, max_days=None):
    """Validate optional ISO start_date and end_date strings.

    Returns tuple: (error_or_None, start_date_or_None, end_date_or_None)
    Dates are returned as datetime.date objects.
    """
    if not start_date_str and not end_date_str:
        return None, None, None

    from datetime import date

    def _parse(s):
        try:
            # Accept YYYY-MM-DD or full ISO datetime
            from datetime import datetime

            try:
                return datetime.fromisoformat(s).date()
            except Exception as e:
                logger.info(f"Failed to parse date ({s}): {e}")
                return date.fromisoformat(s[:10])
        except Exception as e:
            logger.info(f"Failed to parse date (return None): {e}")
            return None

    start_date = None
    end_date = None

    if start_date_str:
        start_date = _parse(start_date_str)
        if start_date is None:
            return "Parameter 'start_date' must be ISO format YYYY-MM-DD", None, None

    if end_date_str:
        end_date = _parse(end_date_str)
        if end_date is None:
            return "Parameter 'end_date' must be ISO format YYYY-MM-DD", None, None

    if start_date and end_date and start_date > end_date:
        return "Parameter 'start_date' must be <= 'end_date'", None, None

    if max_days is not None and start_date and end_date:
        if (end_date - start_date).days > max_days:
            return (
                f"Date range exceeds maximum allowed span of {max_days} days",
                None,
                None,
            )

    return None, start_date, end_date
