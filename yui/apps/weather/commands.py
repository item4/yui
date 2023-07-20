from __future__ import annotations

from typing import TYPE_CHECKING

from ...box import box
from ...command import argument
from .exceptions import WeatherRequestError
from .exceptions import WeatherResponseError
from .sun import get_emoji_by_sun
from .temperature import clothes_by_temperature
from .utils import shorten
from .weather import get_weather_by_keyword

if TYPE_CHECKING:
    from ...event import Message
    from .air import AirPollutionRecord  # noqa: F401
    from .weather import WeatherRecord  # noqa: F401


@box.command("날씨", ["aws", "weather"])
@argument("keyword", nargs=-1, concat=True)
async def weather(
    bot,
    event: Message,
    keyword: str,
):
    """
    지역의 현재 기상상태를 조회합니다.

    `{PREFIX}날씨 부천` (한국 기상청 부천 관측소의 현재 계측값을 출력)
    """

    if len(keyword) < 2:
        await bot.say(
            event.channel,
            "검색어가 너무 짧아요! 2글자 이상의 검색어를 사용해주세요!",
        )
        return

    try:
        result = await get_weather_by_keyword(keyword)
    except WeatherRequestError as e:
        await bot.say(
            event.channel,
            str(e),
        )
        return
    except WeatherResponseError as e:
        await bot.say(
            event.channel,
            f"날씨 조회중 에러가 발생했어요! ({e!s})",
        )
        return

    rain = None
    match result.is_rain:
        case "Rain":
            rain = (
                f"예(15분: {shorten(result.rain_15 or 0)}㎜ / 일일:"
                f" {shorten(result.rain_day or 0)}㎜)"
            )
        case "Unavailable":
            rain = "확인 불가"
        case "Unknown":
            rain = "알 수 없음"

    temperature = (
        "기온: 알 수 없음"
        if result.temperature is None
        else f"기온: {shorten(result.temperature)}℃"
    )

    wind = f"{result.wind_direction} {shorten(result.wind_velocity)}㎧"

    humidity = (
        None if result.humidity is None else f"{shorten(result.humidity)}%"
    )

    atmospheric = (
        None
        if result.atmospheric is None
        else f"{shorten(result.atmospheric)}㍱"
    )

    weather_text = "[{} / {}] ".format(
        result.location,
        result.observed_at.strftime("%H시 %M분 기준"),
    )

    if result.is_rain and rain:
        if result.temperature is not None and result.temperature > 0:
            weather_text += f"강수 {rain} / "
            weather_emoji = ":umbrella_with_rain_drops:"
        else:
            weather_text += f"강설 {rain} / "
            weather_emoji = ":snowflake:"
    else:
        weather_emoji = await get_emoji_by_sun(
            result.observed_at,
        )

    weather_text += temperature
    weather_text += f" / 바람: {wind}"
    if humidity:
        weather_text += f" / 습도: {humidity}"
    if atmospheric:
        weather_text += f" / 해면기압: {atmospheric}"

    if result.temperature is not None:
        recommend = clothes_by_temperature(result.temperature)
        weather_text += f"\n\n추천 의상: {recommend}"

    await bot.api.chat.postMessage(
        channel=event.channel,
        text=weather_text,
        username=f"{result.name} 날씨",
        icon_emoji=weather_emoji,
        thread_ts=event.ts,
    )
