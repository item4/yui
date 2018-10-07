import datetime

import pytz

from yui.apps.info.memo.models import Memo
from yui.util import now


def test_memo_model_with_aware_dt(fx_sess):
    now_dt = now()

    record = Memo()
    record.keyword = 'test'
    record.text = 'test test'
    record.author = 'U1'
    record.created_at = now_dt

    with fx_sess.begin():
        fx_sess.add(record)

    assert record.created_at == now_dt
    assert record.created_datetime == now_dt.replace(tzinfo=None)
    assert record.created_timezone is pytz.timezone('Asia/Seoul')


def test_memo_model_with_aware_utc_dt(fx_sess):
    dt = datetime.datetime(2018, 10, 7, 1, 2, 3, tzinfo=pytz.UTC)

    record = Memo()
    record.keyword = 'test'
    record.text = 'test test'
    record.author = 'U1'
    record.created_at = dt

    with fx_sess.begin():
        fx_sess.add(record)

    assert record.created_at == dt
    assert record.created_datetime == datetime.datetime(2018, 10, 7, 1, 2, 3)
    assert record.created_timezone is pytz.UTC


def test_memo_model_with_naive_dt(fx_sess):
    dt = datetime.datetime(2018, 10, 7, 1, 2, 3)

    record = Memo()
    record.keyword = 'test'
    record.text = 'test test'
    record.author = 'U1'
    record.created_at = dt

    with fx_sess.begin():
        fx_sess.add(record)

    assert record.created_at == dt
    assert record.created_datetime == dt
    assert record.created_timezone is None
