import datetime

import pytest

from yui.apps.date.utils import APIDoesNotSupport
from yui.apps.date.utils import get_holiday_names
from yui.apps.date.utils import weekend_loading_box
from yui.apps.date.utils import weekend_loading_percent


@pytest.mark.asyncio
async def test_get_holiday_names():
    jan_first = datetime.datetime(2018, 1, 1)
    jan_second = datetime.datetime(2018, 1, 2)
    armed_forces_day = datetime.datetime(2018, 10, 1)
    unsupported = datetime.datetime(2000, 1, 1)

    holidays = await get_holiday_names(jan_first)
    assert holidays == ['신정']

    holidays = await get_holiday_names(jan_second)
    assert holidays == []

    holidays = await get_holiday_names(armed_forces_day)
    assert holidays == []

    with pytest.raises(APIDoesNotSupport):
        await get_holiday_names(unsupported)


def test_weekend_loading_percent():
    assert weekend_loading_percent(datetime.datetime(2020, 6, 1)) == 0.0
    assert weekend_loading_percent(datetime.datetime(2020, 6, 2)) == 20.0
    assert weekend_loading_percent(datetime.datetime(2020, 6, 3)) == 40.0
    assert weekend_loading_percent(datetime.datetime(2020, 6, 4)) == 60.0
    assert weekend_loading_percent(datetime.datetime(2020, 6, 5)) == 80.0
    assert weekend_loading_percent(datetime.datetime(2020, 6, 6)) == 100.0
    assert weekend_loading_percent(datetime.datetime(2020, 6, 7)) == 100.0


def test_weekend_loading_box():
    assert weekend_loading_box(0.0) == ('[□□□□□□□□□□□□□□□□□□□□]')
    assert weekend_loading_box(5.0) == ('[■□□□□□□□□□□□□□□□□□□□]')
    assert weekend_loading_box(10.0) == ('[■■□□□□□□□□□□□□□□□□□□]')
    assert weekend_loading_box(15.0) == ('[■■■□□□□□□□□□□□□□□□□□]')
    assert weekend_loading_box(20.0) == ('[■■■■□□□□□□□□□□□□□□□□]')
    assert weekend_loading_box(25.0) == ('[■■■■■□□□□□□□□□□□□□□□]')
    assert weekend_loading_box(30.0) == ('[■■■■■■□□□□□□□□□□□□□□]')
    assert weekend_loading_box(35.0) == ('[■■■■■■■□□□□□□□□□□□□□]')
    assert weekend_loading_box(40.0) == ('[■■■■■■■■□□□□□□□□□□□□]')
    assert weekend_loading_box(45.0) == ('[■■■■■■■■■□□□□□□□□□□□]')
    assert weekend_loading_box(50.0) == ('[■■■■■■■■■■□□□□□□□□□□]')
    assert weekend_loading_box(55.0) == ('[■■■■■■■■■■■□□□□□□□□□]')
    assert weekend_loading_box(60.0) == ('[■■■■■■■■■■■■□□□□□□□□]')
    assert weekend_loading_box(65.0) == ('[■■■■■■■■■■■■■□□□□□□□]')
    assert weekend_loading_box(70.0) == ('[■■■■■■■■■■■■■■□□□□□□]')
    assert weekend_loading_box(75.0) == ('[■■■■■■■■■■■■■■■□□□□□]')
    assert weekend_loading_box(80.0) == ('[■■■■■■■■■■■■■■■■□□□□]')
    assert weekend_loading_box(85.0) == ('[■■■■■■■■■■■■■■■■■□□□]')
    assert weekend_loading_box(90.0) == ('[■■■■■■■■■■■■■■■■■■□□]')
    assert weekend_loading_box(95.0) == ('[■■■■■■■■■■■■■■■■■■■□]')
    assert weekend_loading_box(100.0) == ('[■■■■■■■■■■■■■■■■■■■■]')
