import pytest

from yui.utils.datetime import datetime


@pytest.mark.asyncio
async def get_emoji_by_sun():
    lat = 37.566535
    lng = 126.9779692
    before_sunrise = datetime(2022, 11, 6, 2)
    after_sunrise = datetime(2022, 11, 6, 9)
    noon = datetime(2022, 11, 6, 13)  # Start of SAO Official Service
    after_sunset = datetime(2022, 11, 6, 22)
    moon = ":crescent_moon:"
    sun = ":sunny:"
    assert (await get_emoji_by_sun(before_sunrise, lat, lng)) == moon
    assert (await get_emoji_by_sun(after_sunrise, lat, lng)) == sun
    assert (await get_emoji_by_sun(noon, lat, lng)) == sun
    assert (await get_emoji_by_sun(after_sunset, lat, lng)) == moon
