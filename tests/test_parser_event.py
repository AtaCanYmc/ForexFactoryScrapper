import os
import sys
from src.scrapper._parser import parse_calendar_from_html

# ensure src is importable
ROOT = os.path.dirname(os.path.dirname(__file__))
SRC = os.path.join(ROOT, "src")
for p in (SRC, ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

SAMPLE_HTML = """
<table class="calendar calendar__table">
  <tr class="calendar__row--new-day">
    <td colspan="6"><span class="date">Jan 1, 2020</span></td>
  </tr>
  <tbody>
    <tr>
      <td>00:00</td>
      <td>BTC</td>
      <td>
        <div class="calendar__event">
          <div class="calendar__event-title">Protocol Upgrade</div>
        </div>
      </td>
      <td>n/a</td>
      <td>n/a</td>
      <td>n/a</td>
    </tr>
  </tbody>
</table>
"""


def test_event_extraction_from_calendar_title():
    recs = parse_calendar_from_html(SAMPLE_HTML, "http://example.com/2020")
    assert isinstance(recs, list)
    assert len(recs) == 1
    rec = recs[0]
    assert rec.get("Event") == "Protocol Upgrade"
    assert rec.get("Time").startswith("01/01/2020")
