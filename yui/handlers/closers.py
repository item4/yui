import decimal

from ..box import box
from ..command import Cs, argument, only
from ..event import Message


@box.crontab('30 9,14,19,22 * * 0,2,4,6')
async def overflood_before_30m(bot):
    await bot.say(
        '#game',
        ':closers: 오염지옥 오버플루드 개장 30분 전입니다.'
    )


@box.crontab('0 10,15,20,23 * * 0,2,4,6')
async def overflood_start(bot):
    await bot.say(
        '#game',
        ':closers: 오염지옥 오버플루드 개장 시간입니다.'
    )


BASE = decimal.Decimal(3)
INCREASE = decimal.Decimal('0.5')
UNIT = decimal.Decimal(10_000_000)
MAX = decimal.Decimal(10)


@box.command('블마수수료', channels=only(Cs.game_and_test))
@argument('price', type_=decimal.Decimal)
async def black_market_charge(bot, event: Message, price: decimal.Decimal):
    """
    클로저스 온라인 블랙마켓 수수료 계산

    `{PREFIX}블마수수료 100000` (100,000 크레딧 상품의 수수료 계산)

    """

    charge_percent = min(
        BASE + INCREASE * decimal.Decimal(int(price / UNIT)),
        MAX
    ) / decimal.Decimal(100)
    charge = price * charge_percent
    net = price - charge

    await bot.say(
        event.channel,
        f':closers: {price:,.0f} 크레딧 상품의 수수료는 {charge_percent*100:.2f}%인 '
        f'{charge:,.0f} 크레딧 입니다. 순 이익은 {net:,.0f} 크레딧 입니다.'
    )
