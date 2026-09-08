"""
Turns a UTC timestamp into (shift_number, shift_business_date) in the
configured local timezone.

Shift 1: [shift1_start, shift2_start)          -- does not cross midnight
Shift 2: [shift2_start, shift1_start next day)  -- crosses midnight

`shift_business_date` is the date the shift is reported under. For Shift 2,
that's the calendar date the shift *started* on (e.g. a part counted at
1am on 03 Jun belongs to the Shift 2 that started 02 Jun 19:00, so it is
reported under 02 Jun -- matching the "Shift 2 (07:00 PM - 07:00 AM)" column
next to each date row in the Date Wise report).
"""
import datetime as dt
from zoneinfo import ZoneInfo

from config import settings

_TZ = ZoneInfo(settings.timezone)


def _parse_hhmm(value: str) -> dt.time:
    h, m = value.split(":")
    return dt.time(int(h), int(m))


SHIFT1_START = _parse_hhmm(settings.shift1_start)
SHIFT2_START = _parse_hhmm(settings.shift2_start)


def compute_shift(ts_utc: dt.datetime) -> tuple[int, dt.date]:
    if ts_utc.tzinfo is None:
        ts_utc = ts_utc.replace(tzinfo=dt.timezone.utc)
    local = ts_utc.astimezone(_TZ)
    t = local.time()

    if SHIFT1_START <= t < SHIFT2_START:
        return 1, local.date()

    # Shift 2: either after shift2_start today, or before shift1_start
    # today (i.e. the tail end of yesterday's Shift 2).
    if t >= SHIFT2_START:
        return 2, local.date()
    else:
        return 2, (local - dt.timedelta(days=1)).date()
