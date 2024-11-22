from datetime import datetime
from zoneinfo import ZoneInfo

from machine.utils.datetime import calculate_epoch


def test_calculate_epoch():
    utc_tz = ZoneInfo("UTC")
    ams_tz = ZoneInfo("Europe/Amsterdam")
    epoch = datetime(1970, 1, 1, tzinfo=utc_tz)
    naive_epoch = datetime(1970, 1, 1)

    # epoch == epoch
    assert calculate_epoch(epoch, utc_tz) == 0
    # If the datetime is non-naive, the passed-in TZ isn't used
    assert calculate_epoch(epoch, ams_tz) == 0
    # If the datetime is naive, the passed-in TZ kicks in
    assert calculate_epoch(naive_epoch, utc_tz) == 0
    assert calculate_epoch(naive_epoch, ams_tz) == -3600
