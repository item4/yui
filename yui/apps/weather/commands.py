from __future__ import annotations

from ...box import box
from ...command import argument
from ...event import Message  # noqa: TC001
from .exceptions import WeatherRequestError
from .exceptions import WeatherResponseError
from .weather import get_weather_by_keyword


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
    weather_emoji = await result.get_emoji_by_weather()

    await bot.api.chat.postMessage(
        channel=event.channel,
        text=weather_text,
        username=f"{result.name} 날씨",
        icon_emoji=weather_emoji,
    )
