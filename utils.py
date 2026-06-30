from datetime import datetime
from zoneinfo import ZoneInfo

JST = ZoneInfo("Asia/Tokyo")


def now_jst():
    return datetime.now(JST)


def parse_time(text):

    h, m = map(
        int,
        text.split(":")
    )

    now = now_jst()

    return now.replace(
        hour=h,
        minute=m,
        second=0,
        microsecond=0
    )
