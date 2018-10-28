import datetime
import functools
import os

import pytest

from yui.apps.date.utils import (
    get_event_days,
    get_holiday_name,
    weekend_loading_percent,
)


def test_weekend_loading_percent():
    kirito_birthday = datetime.datetime(2008, 10, 7)

    mon = kirito_birthday - datetime.timedelta(days=1)
    tue = kirito_birthday
    wed = kirito_birthday + datetime.timedelta(days=1)
    thu = kirito_birthday + datetime.timedelta(days=2)
    fri = kirito_birthday + datetime.timedelta(days=3)
    sat = kirito_birthday + datetime.timedelta(days=4)
    sun = kirito_birthday + datetime.timedelta(days=5)

    assert weekend_loading_percent(mon) == 0.0
    assert weekend_loading_percent(tue) == 20.0
    assert weekend_loading_percent(wed) == 40.0
    assert weekend_loading_percent(thu) == 60.0
    assert weekend_loading_percent(fri) == 80.0
    assert weekend_loading_percent(sat) == 100.0
    assert weekend_loading_percent(sun) == 100.0


@pytest.fixture()
def fx_tdcproject_key():
    key = os.getenv('TDCPROJECT_KEY')
    if not key:
        pytest.skip('Can not test this without TDCPROJECT_KEY envvar')
    return key


@pytest.mark.asyncio
async def test_get_event_days(fx_tdcproject_key):
    call = functools.partial(get_event_days, api_key=fx_tdcproject_key)

    data = await call(year='2017')
    assert len(data['results']) == 189
    assert data['results'][0] == {
        'year': '2017',
        'month': '01',
        'day': '01',
        'type': 'h',
        'name': '신정',
    }

    data = await call(year='2017', month='01')
    assert len(data['results']) == 8
    assert data['results'][0] == {
        'year': '2017',
        'month': '01',
        'day': '01',
        'type': 'h',
        'name': '신정',
    }

    data = await call(year='2017', month='01', day='02')
    assert data['results'] == []

    data = await call(year='2017', month='10', day='03')
    assert data['results'] == [
        {
            'year': '2017',
            'month': '10',
            'day': '03',
            'type': 'h,k',
            'name': '개천절',
        },
        {
            'year': '2017',
            'month': '10',
            'day': '03',
            'type': 'h',
            'name': '추석연휴',
        },
    ]

    data = await call(year='2017', month='10', day='03', type='k')
    assert data['results'] == [
        {
            'year': '2017',
            'month': '10',
            'day': '03',
            'type': 'k',
            'name': '개천절',
        },
    ]


@pytest.mark.asyncio
async def test_get_holiday_name(fx_tdcproject_key):
    jan_first = datetime.datetime(2018, 1, 1)
    jan_second = datetime.datetime(2018, 1, 2)
    armed_forces_day = datetime.datetime(2018, 10, 1)

    holiday = await get_holiday_name(fx_tdcproject_key, jan_first)
    assert holiday == '신정'

    holiday = await get_holiday_name(fx_tdcproject_key, jan_second)
    assert holiday is None

    holiday = await get_holiday_name(fx_tdcproject_key, armed_forces_day)
    assert holiday is None
