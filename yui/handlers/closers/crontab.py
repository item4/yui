from .base import get_next_overflood_info
from ...box import box
from ...util import now


@box.crontab('30 9,14,17,19,22 * * *')
async def overflood_before_30m(bot):
    info = get_next_overflood_info(now())
    if info != '오버플루드: 휴무':
        await bot.say(
            '#game',
            f':closers: {info}'
        )


@box.crontab('0 10,15,18,20,23 * * *')
async def overflood_start(bot):
    info = get_next_overflood_info(now())
    if info != '오버플루드: 휴무':
        await bot.say(
            '#game',
            f':closers: {info}'
        )


@box.crontab('0 0,1 * * *')
async def midnight_overflood_before_30m(bot):
    info = get_next_overflood_info(now())
    if info != '오버플루드: 휴무':
        await bot.say(
            '#game',
            f':closers: {info}'
        )


@box.crontab('30 0,1 * * *')
async def midnight_overflood_start(bot):
    info = get_next_overflood_info(now())
    if info != '오버플루드: 휴무':
        await bot.say(
            '#game',
            f':closers: {info}'
        )


@box.crontab('0 4 * * 0')
async def sunday_dungeon_info(bot):
    await bot.say(
        '#game',
        ':closers: 오늘의 대정화작전 보스 - 감시자 틴달로스 / 괴조 하르파스 / 오염위상 요드'
    )


@box.crontab('0 4 * * 1')
async def monday_dungeon_info(bot):
    await bot.say(
        '#game',
        ':closers: 오늘의 대정화작전 보스 - 괴조 하르파스 / 오염위상 요드'
    )


@box.crontab('0 4 * * 2')
async def tuesday_dungeon_info(bot):
    await bot.say(
        '#game',
        ':closers: 오늘의 대정화작전 보스 - 감시자 틴달로스 / 거울잡이 니토크리스'
    )


@box.crontab('0 4 * * 3')
async def wednesday_dungeon_info(bot):
    await bot.say(
        '#game',
        ':closers: 오늘의 대정화작전 보스 - 감시자 틴달로스 / 괴조 하르파스'
    )


@box.crontab('0 4 * * 4')
async def thursday_dungeon_info(bot):
    await bot.say(
        '#game',
        ':closers: 오늘의 대정화작전 보스 - 괴조 하르파스 / 거울잡이 니토크리스'
    )


@box.crontab('0 4 * * 5')
async def friday_dungeon_info(bot):
    await bot.say(
        '#game',
        ':closers: 오늘의 대정화작전 보스 - 감시자 틴달로스 / 오염위상 요드'
    )


@box.crontab('0 4 * * 6')
async def saturday_dungeon_info(bot):
    await bot.say(
        '#game',
        ':closers: 오늘의 대정화작전 보스 - 감시자 틴달로스 / 괴조 하르파스'
        ' / 거울잡이 니토크리스'
    )
