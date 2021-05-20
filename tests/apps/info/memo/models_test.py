from dateutil.tz import UTC
from dateutil.tz import gettz

from yui.apps.info.memo.models import Memo
from yui.utils.datetime import now


def test_memo_model(fx_sess):
    now_dt = now()

    record = Memo()
    record.keyword = 'test'
    record.text = 'test test'
    record.author = 'U1'
    record.created_at = now_dt

    with fx_sess.begin():
        fx_sess.add(record)

    assert record.created_at == now_dt
    assert record.created_datetime == now_dt.astimezone(UTC)
    assert record.created_timezone == gettz('Asia/Seoul')
