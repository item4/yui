import datetime

import pytest

from yui.apps.date.utils import APIDoesNotSupport, get_holiday_names


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
