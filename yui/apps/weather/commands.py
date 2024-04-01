from __future__ import annotations

from typing import TYPE_CHECKING

from ...box import box
from ...command import argument
from ...event import Message  # noqa: TCH001
from .exceptions import WeatherRequestError
from .exceptions import WeatherResponseError
from .sun import get_emoji_by_sun
from .weather import get_weather_by_keyword

if TYPE_CHECKING:
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

    weather_text = result.as_str()

    if result.is_rain:
        if result.temperature is not None and result.temperature > 0:
            weather_emoji = ":umbrella_with_rain_drops:"
        else:
            weather_emoji = ":snowflake:"
    else:
        weather_emoji = await get_emoji_by_sun(
            result.observed_at,
        )

    await bot.api.chat.postMessage(
        channel=event.channel,
        text=weather_text,
        username=f"{result.name} 날씨",
        icon_emoji=weather_emoji,
        thread_ts=event.ts,
    )
