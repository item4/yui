from typing import List

from .utils import weekend_loading_box
from .utils import weekend_loading_percent
from ...box import box
from ...command import C
from ...event import Message
from ...utils.datetime import now

box.assert_config_required('WEEKEND_LOADING_TIME', List[int])
box.assert_channel_required('general')


@box.cron('0 * * * 1-5')
async def auto_weekend_loading(bot):
    now_dt = now()
    if now_dt.hour in bot.config.WEEKEND_LOADING_TIME:
        percent = weekend_loading_percent(now_dt)
        blocks = weekend_loading_box(percent)
        await bot.say(C.general.get(), f'주말로딩… {blocks} {percent:.2f}%')


@box.cron('0 0 * * 6')
async def auto_weekend_start(bot):
    await bot.say(C.general.get(), f'주말이에요! 즐거운 주말 되세요!')


@box.command('주말로딩')
async def weekend_loading(bot, event: Message):
    """
    주말로딩

    주말까지 얼마나 남았는지 출력합니다.

    `{PREFIX}주말로딩`

    """

    now_dt = now()
    percent = weekend_loading_percent(now_dt)
    blocks = weekend_loading_box(percent)
    if percent == 100.0:
        await bot.say(event.channel, '주말이에요! 즐거운 주말 되세요!')
    else:
        await bot.say(event.channel, f'주말로딩… {blocks} {percent:.2f}%')
