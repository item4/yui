import datetime

from ..box import box
from ..event import Message


def weekend_loading_percent(now: datetime.datetime) -> float:
    weekday = now.weekday()
    if weekday in [5, 6]:
        return 100.0
    monday = (now - datetime.timedelta(days=weekday)).replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )
    delta = now - monday
    return delta.total_seconds() / (5*24*60*60) * 100


@box.crontab('0 8,18 * * 1-5')
async def auto_weekend_loading(bot):
    now = datetime.datetime.now()
    percent = weekend_loading_percent(now)
    await bot.say(
        '_general',
        f'주말로딩… {percent:.2f}%'
    )


@box.crontab('0 0 * * 6')
async def auto_weekend_start(bot):
    await bot.say(
        '_general',
        f'주말이에요! 즐거운 주말 되세요!'
    )


@box.crontab('0 0 * * 1')
async def auto_weekend_end(bot):
    await bot.say(
        '_general',
        f'월월월월! 월요일이에요!'
    )


@box.command('주말로딩')
async def weekend_loading(bot, event: Message):
    """
    주말로딩

    주말까지 얼마나 남았는지 출력합니다.

    `{PREFIX}주말로딩`

    """

    now = datetime.datetime.now()
    percent = weekend_loading_percent(now)
    if percent == 100.0:
        await bot.say(
            event.channel,
            '주말이에요! 즐거운 주말 되세요!'
        )
    else:
        await bot.say(
            event.channel,
            f'주말로딩… {percent:.2f}%'
        )
