import logging
from datetime import datetime, timedelta

from ._constants import DEFAULT_HOUR_OFFSET

logger = logging.getLogger(__name__)


def to_24h(day, month, year, am_pm, last=None):
    """Convert an am/pm string or 24h string to a datetime in 24-hour format with configurable hour offset.

    Keeps behaviour compatible with previous implementations but uses the shared DEFAULT_HOUR_OFFSET.
    Supports formats like:
      - '3:30pm', '3pm', '03:30 pm'
      - '3:30am', 'day'
      - '00:00' (24-hour format)

    If parsing fails, returns `last`.
    """
    if last is None:
        last = datetime.now()

    s = (am_pm or "").strip().lower()

    if "day" in s:
        return datetime(year, month, day, 0, 0)

    add_h = DEFAULT_HOUR_OFFSET

    # am/pm handling
    if "pm" in s or "am" in s:
        try:
            # remove am/pm and whitespace
            core = s.replace("pm", "").replace("am", "").strip()
            parts = core.split(":")
            if len(parts) == 1:
                h = int(parts[0].strip())
                m = 0
            else:
                h = int(parts[0].strip())
                m = int(parts[1].strip())
            if "pm" in s:
                h = (h % 12) + 12
            else:
                h = h % 12
        except Exception:
            return last
    else:
        # try 24-hour style like '00:00' or '9:05'
        if ":" in s:
            try:
                parts = s.split(":")
                h = int(parts[0].strip())
                m = int(parts[1].strip())
                # normalize hour range
                if not (0 <= h < 24 and 0 <= m < 60):
                    return last
            except Exception:
                return last
        else:
            return last

    try:
        evnt_date = datetime(year, month, day, h, m) + timedelta(hours=add_h)
    except Exception:
        return last
    return evnt_date
