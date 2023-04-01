import contextlib
import re

import aiohttp
import aiohttp.client_exceptions
import tossi

from ...box import box
from ...event import Message
from ...transform import str_to_date
from ...utils.datetime import now
from .utils import APIDoesNotSupport
from .utils import get_holiday_names

box.assert_channel_required("general")

YEAR_PATTERN = re.compile(r"^(\d{4})년$")
YEAR_MONTH_PATTERN = re.compile(r"^(\d{4})년\s*(\d{1,2})월$")


@box.cron("0 0 * * 0,2,3,4,5,6")
async def holiday_message(bot):
    holidays = None
    today = now()
    with contextlib.suppress(aiohttp.client_exceptions.ClientOSError):
        holidays = await get_holiday_names(today)

    if holidays:
        await bot.say(
            bot.config.CHANNELS["general"],
            "오늘은 {}! 즐거운 휴일 되세요!".format(
                tossi.postfix(holidays[0], "(이)에요"),
            ),
        )


@box.command("공휴일", ["휴일", "holiday"])
async def holiday(bot, event: Message, raw: str):
    """
    공휴일 조회

    특정 날짜가 공휴일인지 조회합니다.

    `{PREFIX}공휴일` (오늘이 공휴일인지 조회)
    `{PREFIX}공휴일 2019년 1월 1일 (2019년 1월 1일이 공휴일인지 조회)

    """

    if raw:
        try:
            dt = str_to_date()(raw)
        except ValueError:
            await bot.say(
                event.channel,
                "인식할 수 없는 날짜 표현식이에요!",
            )
            return
    else:
        dt = now()

    try:
        holidays = await get_holiday_names(dt)
    except APIDoesNotSupport:
        await bot.say(
            event.channel,
            "API가 해당 년월일시의 자료를 제공하지 않아요!",
        )
        return

    if holidays:
        await bot.say(
            event.channel,
            "{}: {}".format(dt.strftime("%Y년 %m월 %d일"), ", ".join(holidays)),
        )
    else:
        await bot.say(
            event.channel,
            "{}: 평일".format(dt.strftime("%Y년 %m월 %d일")),
        )
