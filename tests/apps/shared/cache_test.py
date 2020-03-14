import datetime

from dateutil.tz import UTC
from dateutil.tz import gettz

from yui.apps.shared.cache import JSONCache
from yui.utils.datetime import now


def test_json_cache_model_with_aware_dt(fx_sess):
    now_dt = now()

    record = JSONCache()
    record.name = 'test'
    record.body = 'Hello!'
    record.created_at = now_dt

    with fx_sess.begin():
        fx_sess.add(record)

    assert record.created_at == now_dt
    assert record.created_datetime == now_dt.replace(tzinfo=None)
    assert record.created_timezone == gettz('Asia/Seoul')


def test_json_cache_model_with_aware_utc_dt(fx_sess):
    dt = datetime.datetime(2018, 10, 7, 1, 2, 3, tzinfo=UTC)

    record = JSONCache()
    record.name = 'test'
    record.body = 'Hello!'
    record.created_at = dt

    with fx_sess.begin():
        fx_sess.add(record)

    assert record.created_at == dt
    assert record.created_datetime == datetime.datetime(2018, 10, 7, 1, 2, 3)
    assert record.created_timezone == UTC


def test_json_cache_model_with_naive_dt(fx_sess):
    dt = datetime.datetime(2018, 10, 7, 1, 2, 3)

    record = JSONCache()
    record.name = 'test'
    record.body = 'Hello!'
    record.created_at = dt

    with fx_sess.begin():
        fx_sess.add(record)

    assert record.created_at == dt
    assert record.created_datetime == dt
    assert record.created_timezone is None
