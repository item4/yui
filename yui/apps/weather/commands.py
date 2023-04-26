from __future__ import annotations

import asyncio
from hashlib import md5
from typing import TYPE_CHECKING

from ...box import box
from ...command import argument
from ...command import option
from ...utils.datetime import fromtimestampoffset
from .air import get_air_pollution_by_coordinate
from .air import get_aqi_description
from .air import get_emoji_by_aqi
from .exceptions import EXCEPTIONS
from .geo import get_geometric_info_by_address
from .sun import get_emoji_by_sun
from .temperature import clothes_by_temperature
from .utils import shorten
from .weather import get_weather_by_coordinate
from .wind import degree_to_direction

if TYPE_CHECKING:
    from ...event import Message
    from .air import AirPollutionRecord  # noqa: F401
    from .weather import WeatherRecord  # noqa: F401


box.assert_config_required("GOOGLE_API_KEY", str)
box.assert_config_required("OPENWEATHER_API_KEY", str)


@box.command("날씨", ["aws", "weather", "aqi", "공기", "먼지", "미세먼지"])
@option("--debug", default=False, is_flag=True)
@argument("address", nargs=-1, concat=True)
async def weather(
    bot,
    event: Message,
    address: str,
    debug: bool = False,
):
    """
    지역의 현재 기상상태를 조회합니다.

    `{PREFIX}날씨 부천` (부천으로 검색되는 주소의 현재 기상상태를 출력)
    """

    if len(address) < 2:
        await bot.say(
            event.channel,
            "검색어가 너무 짧아요! 2글자 이상의 검색어를 사용해주세요!",
        )
        return

    addr = md5(address.encode()).hexdigest()  # noqa: S324

    full_address_key = f"WEATHER_ADDRESS_{addr}_full_address"
    lat_key = f"WEATHER_ADDRESS_{addr}_lat"
    lng_key = f"WEATHER_ADDRESS_{addr}_lng"
    cached = await bot.cache.get_many(
        full_address_key,
        lat_key,
        lng_key,
    )

    full_address = cached.get(full_address_key)
    lat = cached.get(lat_key)
    lng = cached.get(lng_key)

    if not all([full_address, lat, lng]):
        try:
            full_address, lat, lng = await get_geometric_info_by_address(
                address,
                bot.config.GOOGLE_API_KEY,
            )

            await asyncio.gather(
                bot.cache.set(full_address_key, full_address),
                bot.cache.set(lat_key, lat),
                bot.cache.set(lng_key, lng),
            )
        except IndexError:
            await bot.say(event.channel, "해당 주소는 찾을 수 없어요!")
            return

    try:
        result = await asyncio.gather(
            get_weather_by_coordinate(lat, lng, bot.config.OPENWEATHER_API_KEY),
            get_air_pollution_by_coordinate(
                lat, lng, bot.config.OPENWEATHER_API_KEY
            ),
        )

        weather_result, air_pollution_result = (
            result
        )  # type: WeatherRecord, AirPollutionRecord
    except EXCEPTIONS:
        await bot.say(event.channel, "날씨 API 접근 중 에러가 발생했어요!")
        return

    if weather_result is None or air_pollution_result is None:
        await bot.say(
            event.channel,
            "검색 결과가 없어요! OpenWeather로 검색할 수 없는 곳 같아요!",
        )
        return

    rain = None
    if weather_result.rain:
        rain = "예(1시간: {}㎜ / 3시간: {}㎜)".format(
            shorten(weather_result.rain_1h or 0),
            shorten(weather_result.rain_3h or 0),
        )

    snow = None
    if weather_result.snow:
        snow = "예(1시간: {}㎜ / 3시간: {}㎜)".format(
            shorten(weather_result.snow_1h or 0),
            shorten(weather_result.snow_3h or 0),
        )

    temperature = "기온: {}℃ (체감 {}℃)".format(
        shorten(weather_result.current_temp),
        shorten(weather_result.feel_temp),
    )

    wind = "{} {}㎧".format(
        degree_to_direction(weather_result.wind_degree),
        shorten(weather_result.wind_speed),
    )

    humidity = f"{shorten(weather_result.humidity)}%"

    atmospheric = f"{shorten(weather_result.pressure)}㍱"

    current_dt = fromtimestampoffset(
        # timestamp는 UTC 기준이므로 offset 값을 미리 더해줘야합니다.
        timestamp=weather_result.timestamp,
        offset=weather_result.timezone,
    )

    # full_address를 쓰는 이유는 result.location은 영어이기 때문입니다.
    weather_text = "[{} / {}] ".format(
        full_address,
        current_dt.strftime("%H시 %M분 기준"),
    )

    if weather_result.rain:
        weather_text += f"강수 {rain} / "
        weather_emoji = ":umbrella_with_rain_drops:"
    elif weather_result.snow:
        weather_text += f"강설 {snow} / "
        weather_emoji = ":snowflake:"
    else:
        weather_emoji = await get_emoji_by_sun(
            current_dt,
            weather_result.timezone,
            lat,
            lng,
        )

    weather_text += temperature
    weather_text += f" / 바람: {wind}"
    weather_text += f" / 습도: {humidity}"
    weather_text += f" / 해면기압: {atmospheric}"

    recommend = clothes_by_temperature(weather_result.current_temp)
    weather_text += f"\n\n추천 의상: {recommend}"

    if debug:  # pragma: no cover
        weather_text += f"\n\n* URL: {weather_result.url}"

    await bot.api.chat.postMessage(
        channel=event.channel,
        text=weather_text,
        username=f"{full_address} 날씨",
        icon_emoji=weather_emoji,
        thread_ts=event.ts,
    )

    air_pollution_text = (
        f"{full_address} 기준으로 가장 근접한 관측소의 최근 자료에요.\n\n"
        f"* 종합 AQI: {get_aqi_description(air_pollution_result.aqi)}\n"
        + air_pollution_result.to_display(
            weather_result.current_temp,
            weather_result.pressure,
            debug=debug,
        )
    )

    text = air_pollution_text.strip()
    air_pollution_emoji = get_emoji_by_aqi(air_pollution_result.aqi)

    await bot.api.chat.postMessage(
        channel=event.channel,
        text=text,
        username=f"{full_address} 대기질",
        icon_emoji=air_pollution_emoji,
        thread_ts=event.ts,
    )
