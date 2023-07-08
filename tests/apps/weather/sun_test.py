import pytest

from yui.apps.weather.sun import get_emoji_by_sun
from yui.utils.datetime import datetime


@pytest.mark.asyncio()
async def test_get_emoji_by_sun():
    before_sunrise = datetime(2022, 11, 6, 2)
    after_sunrise = datetime(2022, 11, 6, 9)
    noon = datetime(2022, 11, 6, 13)  # Start of SAO Official Service
    after_sunset = datetime(2022, 11, 6, 22)
    moon = ":crescent_moon:"
    sun = ":sunny:"
    assert (await get_emoji_by_sun(before_sunrise)) == moon
    assert (await get_emoji_by_sun(after_sunrise)) == sun
    assert (await get_emoji_by_sun(noon)) == sun
    assert (await get_emoji_by_sun(after_sunset)) == moon
