from dateutil.tz import UTC
from dateutil.tz import gettz

from yui.apps.info.rss.models import RSSFeedURL
from yui.utils.datetime import now


def test_rss_feed_sub_model(fx_sess):
    now_dt = now()

    record = RSSFeedURL()
    record.url = 'http://example.com'
    record.channel = 'C1'
    record.updated_at = now_dt

    with fx_sess.begin():
        fx_sess.add(record)

    assert record.updated_at == now_dt
    assert record.updated_datetime == now_dt.astimezone(UTC)
    assert record.updated_timezone == gettz('Asia/Seoul')
