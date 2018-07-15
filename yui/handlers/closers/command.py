from decimal import Decimal
from typing import List

from .base import get_next_overflood_info
from ...box import box
from ...command import Cs, argument, only
from ...event import Message
from ...util import now

BASE = Decimal(3)
INCREASE = Decimal(0.5)
UNIT = Decimal(10_000_000)
MAX = Decimal(10)


@box.command('오버플루드', ['overflood'])
async def overflood_info(bot, event: Message):
    """
    클로저스 오염지옥 오버플루드 정보

    `{PREFIX}오버플루드` (현재 시각의 오버플루드 정보 출력)

    """

    await bot.say(
        event.channel,
        f':closers: {get_next_overflood_info(now())}'
    )


@box.command('블마수수료', channels=only(Cs.game_and_test))
@argument('prices', nargs=-1, type_=Decimal)
async def black_market_charge(bot, event: Message, prices: List[Decimal]):
    """
    클로저스 온라인 블랙마켓 수수료 계산

    `{PREFIX}블마수수료 100000` (100,000 크레딧 상품의 수수료 계산)
    `{PREFIX}블마수수료 100000 200000` (100,000, 200,000 크레딧 상품의 순차적 수수료 계산)

    """

    count = len(prices)

    if count < 1 or count > 20:
        await bot.say(
            event.channel,
            '거래 건수는 1개 이상 20개 이하로 해주세요!'
        )
        return

    total_price = Decimal(0)
    total_charge = Decimal(0)
    total_net = Decimal(0)

    body = f':closers: 총 {count}개 거래건의 블랙마켓 수수료를 계산해드릴게요!\n\n'

    for i, price in enumerate(prices, 1):
        charge_percent = min(
            BASE + INCREASE * Decimal(
                int((total_price + price) / UNIT)
            ),
            MAX
        ) / Decimal(100)
        charge = price * charge_percent
        net = price - charge

        body += (
            f'{i}. {price:,.0f} 크레딧 상품의 수수료는 {charge_percent*100:.2f}%인 '
            f'{charge:,.0f} 크레딧 입니다. 순 이익은 {net:,.0f} 크레딧 입니다.\n'
        )

        total_price += price
        total_charge += charge
        total_net += net

    body += (
        f'\n총 판매액 {total_price:,.0f} 크레딧 중 수수료로 {total_charge:,.0f}'
        f' 크레잇이 빠져서 총 순 이익은 {total_net:,.0f} 크레딧 입니다.'
    )

    await bot.say(
        event.channel,
        body,
        thread_ts=event.ts,
    )
