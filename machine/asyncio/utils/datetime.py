from datetime import datetime, tzinfo


def calculate_epoch(dt: datetime, tz: tzinfo) -> int:
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        dt = dt.replace(tzinfo=tz)
    ts = round(dt.timestamp())
    return ts
