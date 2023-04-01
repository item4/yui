import re
from decimal import Decimal

import aiohttp

from ...box import box
from ...command import argument
from ...event import Message
from ...utils import json

SHORTCUT_TABLE: dict[str, str] = {
    "$": "USD",
    "달러": "USD",
    "\\": "KRW",
    "원": "KRW",
    "엔": "JPY",
    "유로": "EUR",
}
CURRENCY = r"|".join(re.escape(key) for key in SHORTCUT_TABLE) + r"|[a-z]+"
BASE = r"(?P<base>" + CURRENCY + r")"
QUANTITY = r"(?P<quantity>\d+(?:\.\d+)?)"
TO = r"(?P<to>" + CURRENCY + r")"
QUERY_PATTERN1 = re.compile(
    r"^" + QUANTITY + r"\s*" + BASE + r"(?:\s+(?:to|->|=)\s+" + TO + r")?$",
    re.IGNORECASE,
)
QUERY_PATTERN2 = re.compile(
    r"^" + BASE + r"\s*" + QUANTITY + r"(?:\s+(?:to|->|=)\s+" + TO + r")?$",
    re.IGNORECASE,
)


class ExchangeError(Exception):
    """Exception for exchange."""


class SameBaseAndTo(ExchangeError):
    """Base and to symbol is same."""


class WrongUnit(ExchangeError):
    """Wrong unit."""


async def get_exchange_rate(base: str, to: str) -> dict:
    """Get exchange rate."""

    if base == to:
        raise SameBaseAndTo

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.manana.kr/exchange/rate.json",
            params={"base": to, "code": base},
        ) as resp:
            data = await resp.json(loads=json.loads)
            if isinstance(data, list):
                return data[0]
            raise WrongUnit


@box.command("환율", ["exchange"])
@argument("query", nargs=-1, concat=True)
async def exchange(bot, event: Message, query: str):
    """
    환전시 얼마가 되는지 계산.

    `{PREFIX}환율 100엔` (100 JPY가 KRW로 얼마인지 계산)
    `{PREFIX}환율 100 JPY to USD` (100 JPY가 USD로 얼마인지 계산)

    """
    match = QUERY_PATTERN1.match(query)
    if not match:
        match = QUERY_PATTERN2.match(query)

    if match:
        quantity = Decimal(match.group("quantity"))
        base = SHORTCUT_TABLE.get(match.group("base"), match.group("base"))
        to = SHORTCUT_TABLE.get(match.group("to"), match.group("to")) or "KRW"

        data = None
        error = None
        try:
            data = await get_exchange_rate(base, to)
        except SameBaseAndTo:
            error = "변환하려는 두 화폐가 같은 단위에요!"
        except WrongUnit:
            error = "지원되는 통화기호가 아니에요!"

        if error:
            await bot.say(event.channel, error)
            return

        if data:
            date = data["date"]
            rate = Decimal(data["rate"])

            result = quantity * rate

            await bot.say(
                event.channel,
                f"{quantity} {base} == {result:.2f} {to} ({date})",
            )
        else:
            await bot.say(
                event.channel,
                "알 수 없는 에러가 발생했어요! 아빠에게 문의해주세요!",
            )
    else:
        await bot.say(event.channel, "주문을 이해하는데에 실패했어요!")
