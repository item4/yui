import datetime

import pytz

from yui.models.aws import AWS
from yui.util import now


def test_aws_model_with_aware_dt(fx_sess):
    now_dt = now()

    record = AWS()
    record.name = '인천'
    record.height = 1234
    record.is_raining = True
    record.rain15 = 111.111
    record.rain60 = 222.222
    record.rain6h = 333.333
    record.rain12h = 444.444
    record.rainday = 555.555
    record.temperature = 12.34
    record.wind_direction1 = 'SSW'
    record.wind_speed1 = 11.11
    record.wind_direction10 = 'NNE'
    record.wind_speed10 = 22.22
    record.humidity = 55
    record.pressure = 1234.56
    record.location = '인천광역시 중구 전동'
    record.observed_at = now_dt

    with fx_sess.begin():
        fx_sess.add(record)

    assert record.observed_at == now_dt
    assert record.observed_datetime == now_dt.replace(tzinfo=None)
    assert record.observed_timezone is pytz.timezone('Asia/Seoul')


def test_aws_model_with_aware_utc_dt(fx_sess):
    dt = datetime.datetime(2018, 10, 7, 1, 2, 3, tzinfo=pytz.UTC)

    record = AWS()
    record.name = '인천'
    record.height = 1234
    record.is_raining = True
    record.rain15 = 111.111
    record.rain60 = 222.222
    record.rain6h = 333.333
    record.rain12h = 444.444
    record.rainday = 555.555
    record.temperature = 12.34
    record.wind_direction1 = 'SSW'
    record.wind_speed1 = 11.11
    record.wind_direction10 = 'NNE'
    record.wind_speed10 = 22.22
    record.humidity = 55
    record.pressure = 1234.56
    record.location = '인천광역시 중구 전동'
    record.observed_at = dt

    with fx_sess.begin():
        fx_sess.add(record)

    assert record.observed_at == dt
    assert record.observed_datetime == datetime.datetime(2018, 10, 7, 1, 2, 3)
    assert record.observed_timezone is pytz.UTC


def test_aws_model_with_naive_dt(fx_sess):
    dt = datetime.datetime(2018, 10, 7, 1, 2, 3)

    record = AWS()
    record.name = '인천'
    record.height = 1234
    record.is_raining = True
    record.rain15 = 111.111
    record.rain60 = 222.222
    record.rain6h = 333.333
    record.rain12h = 444.444
    record.rainday = 555.555
    record.temperature = 12.34
    record.wind_direction1 = 'SSW'
    record.wind_speed1 = 11.11
    record.wind_direction10 = 'NNE'
    record.wind_speed10 = 22.22
    record.humidity = 55
    record.pressure = 1234.56
    record.location = '인천광역시 중구 전동'
    record.observed_at = dt

    with fx_sess.begin():
        fx_sess.add(record)

    assert record.observed_at == dt
    assert record.observed_datetime == dt
    assert record.observed_timezone is None
