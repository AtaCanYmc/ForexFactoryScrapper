import logging
from datetime import datetime, timedelta

from ._constants import DEFAULT_HOUR_OFFSET

logger = logging.getLogger(__name__)


def to_24h(day, month, year, am_pm, last=None):
    """Convert an am/pm string to a datetime in 24-hour format with configurable hour offset.

    Keeps behaviour compatible with previous implementations but uses the shared DEFAULT_HOUR_OFFSET.
    """
    if last is None:
        last = datetime.now()

    if "day" in am_pm.lower():
        return datetime(year, month, day, 0, 0)

    add_h = DEFAULT_HOUR_OFFSET

    if "pm" in am_pm:
        pm = am_pm.replace("pm", "")
        parts = pm.split(":")
        try:
            h = (int(parts[0].strip()) + 12) % 24
            m = int(parts[1].strip())
        except Exception:
            return last
    elif "am" in am_pm:
        am = am_pm.replace("am", "")
        parts = am.split(":")
        try:
            h = int(parts[0].strip())
            m = int(parts[1].strip())
        except Exception:
            return last
    else:
        return last

    evnt_date = datetime(year, month, day, h, m) + timedelta(hours=add_h)
    return evnt_date
