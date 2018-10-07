import datetime

import pytz

from yui.apps.info.subscribe.models import RSSFeedURL
from yui.util import now


def test_rss_feed_sub_model_with_aware_dt(fx_sess):
    now_dt = now()

    record = RSSFeedURL()
    record.url = 'http://example.com'
    record.channel = 'C1'
    record.updated_at = now_dt

    with fx_sess.begin():
        fx_sess.add(record)

    assert record.updated_at == now_dt
    assert record.updated_datetime == now_dt.replace(tzinfo=None)
    assert record.updated_timezone is pytz.timezone('Asia/Seoul')


def test_rss_feed_sub_model_with_aware_utc_dt(fx_sess):
    dt = datetime.datetime(2018, 10, 7, 1, 2, 3, tzinfo=pytz.UTC)

    record = RSSFeedURL()
    record.url = 'http://example.com'
    record.channel = 'C1'
    record.updated_at = dt

    with fx_sess.begin():
        fx_sess.add(record)

    assert record.updated_at == dt
    assert record.updated_datetime == datetime.datetime(2018, 10, 7, 1, 2, 3)
    assert record.updated_timezone is pytz.UTC


def test_rss_feed_sub_model_with_naive_dt(fx_sess):
    dt = datetime.datetime(2018, 10, 7, 1, 2, 3)

    record = RSSFeedURL()
    record.url = 'http://example.com'
    record.channel = 'C1'
    record.updated_at = dt

    with fx_sess.begin():
        fx_sess.add(record)

    assert record.updated_at == dt
    assert record.updated_datetime == dt
    assert record.updated_timezone is None
