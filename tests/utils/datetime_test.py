from datetime import timedelta
from datetime import timezone
from zoneinfo import ZoneInfo

from time_machine import travel

from yui.utils.datetime import datetime
from yui.utils.datetime import fromisoformat
from yui.utils.datetime import fromtimestamp
from yui.utils.datetime import fromtimestampoffset
from yui.utils.datetime import now


@travel(datetime(2018, 10, 7, 19, 20, 30), tick=False)
def test_now_kst():
    now_kst = now()
    assert now_kst.year == 2018
    assert now_kst.month == 10
    assert now_kst.day == 7
    assert now_kst.hour == 19
    assert now_kst.minute == 20
    assert now_kst.second == 30
    assert now_kst.tzname() == "KST"
    assert now_kst.tzinfo == ZoneInfo("Asia/Seoul")


@travel(datetime(2018, 10, 7, 19, 20, 30), tick=False)
def test_now_utc():
    now_utc = now("UTC")
    assert now_utc.year == 2018
    assert now_utc.month == 10
    assert now_utc.day == 7
    assert now_utc.hour == 10  # NOTE: KST to UTC
    assert now_utc.minute == 20
    assert now_utc.second == 30
    assert now_utc.tzname() == "UTC"
    assert now_utc.tzinfo == ZoneInfo("UTC")


def test_fromtimestamp_kst():
    dt = fromtimestamp(1234567890)
    assert dt.year == 2009
    assert dt.month == 2
    assert dt.day == 14
    assert dt.hour == 8
    assert dt.minute == 31
    assert dt.second == 30
    assert dt.tzname() == "KST"
    assert dt.tzinfo == ZoneInfo("Asia/Seoul")


def test_fromtimestamp_utc():
    dt = fromtimestamp(1234567890, tzname="UTC")
    assert dt.year == 2009
    assert dt.month == 2
    assert dt.day == 13
    assert dt.hour == 23
    assert dt.minute == 31
    assert dt.second == 30
    assert dt.tzname() == "UTC"
    assert dt.tzinfo == ZoneInfo("UTC")


def test_fromtimestampoffset_zero():
    dt = fromtimestampoffset(1234567890, 0)
    assert dt.year == 2009
    assert dt.month == 2
    assert dt.day == 13
    assert dt.hour == 23
    assert dt.minute == 31
    assert dt.second == 30
    assert dt.tzinfo == timezone(timedelta(seconds=0))


def test_fromtimestampoffset_kst():
    dt = fromtimestampoffset(1234567890, 9 * 60 * 60)
    assert dt.year == 2009
    assert dt.month == 2
    assert dt.day == 14
    assert dt.hour == 8
    assert dt.minute == 31
    assert dt.second == 30
    assert dt.tzinfo == timezone(timedelta(hours=9))


def test_fromisoformat_kst():
    dt = fromisoformat("2018-10-07T19:20:30")
    assert dt.year == 2018
    assert dt.month == 10
    assert dt.day == 7
    assert dt.hour == 19
    assert dt.minute == 20
    assert dt.second == 30
    assert dt.tzname() == "KST"
    assert dt.tzinfo == ZoneInfo("Asia/Seoul")


def test_fromisoformat_utc():
    dt = fromisoformat("2018-10-07T19:20:30", tzname="UTC")
    assert dt.year == 2018
    assert dt.month == 10
    assert dt.day == 7
    assert dt.hour == 19
    assert dt.minute == 20
    assert dt.second == 30
    assert dt.tzname() == "UTC"
    assert dt.tzinfo == ZoneInfo("UTC")
