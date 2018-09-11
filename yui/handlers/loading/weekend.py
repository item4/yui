import datetime
from typing import List

from yui.box import box
from yui.command import C
from yui.event import Message
from yui.util import now

box.assert_config_required('WEEKEND_LOADING_TIME', List[int])
box.assert_channel_required('general')


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


@box.crontab('0 * * * 1-5')
async def auto_weekend_loading(bot):
    now_dt = now()
    if now_dt.hour in bot.config.WEEKEND_LOADING_TIME:
        percent = weekend_loading_percent(now_dt)
        await bot.say(
            C.general.get(),
            f'주말로딩… {percent:.2f}%'
        )


@box.crontab('0 0 * * 6')
async def auto_weekend_start(bot):
    await bot.say(
        C.general.get(),
        f'주말이에요! 즐거운 주말 되세요!'
    )


@box.command('주말로딩')
async def weekend_loading(bot, event: Message):
    """
    주말로딩

    주말까지 얼마나 남았는지 출력합니다.

    `{PREFIX}주말로딩`

    """

    now_dt = now()
    percent = weekend_loading_percent(now_dt)
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
