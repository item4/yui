import aiohttp

from .utils import get_holiday_names
from ...box import box
from ...command import C
from ...types.slack.attachment import Attachment
from ...utils.datetime import now

box.assert_channel_required('general')


async def say_raccoon_man(bot, holiday: str):
    await bot.api.chat.postMessage(
        channel=C.general.get(),
        text=f'오늘은 {holiday}! 출근하라는 상사는 이 너굴맨이 처리했으니 안심하라구!',
        as_user=False,
        icon_url='https://i.imgur.com/dG6wXTX.jpg',
        username='너굴맨',
    )


async def say_happy_cat(bot, holiday: str, hour: int):
    await bot.api.chat.postMessage(
        channel=C.general.get(),
        text=f'{holiday} 만세! {hour}시인데 집사 퇴근 안 기다려도 되니까 좋다냥!',
        as_user=False,
        icon_url='https://i.imgur.com/fuC7jv5.png',
        username='집사가 집에 있어서 기분 좋은 고양이',
    )


async def say_start_monday(bot):
    await bot.api.chat.postMessage(
        channel=C.general.get(),
        attachments=[
            Attachment(
                fallback='https://i.imgur.com/Gv9GJBK.jpg',
                image_url='https://i.imgur.com/Gv9GJBK.jpg',
            ),
        ],
        as_user=False,
        icon_url='https://i.imgur.com/yO4RWyZ.jpg',
        username='현실부정중인 직장인',
    )


async def say_start_work(bot):
    await bot.api.chat.postMessage(
        channel=C.general.get(),
        text='한국인들은 세계 누구보다 출근을 사랑하면서 왜 본심을 숨기는 걸까?',
        as_user=False,
        icon_url='https://i.imgur.com/EGIUpE1.jpg',
        username='노동자 핫산',
    )


async def say_knife(bot, hour: int):
    await bot.api.chat.postMessage(
        channel=C.general.get(),
        text=f'{hour}시가 되었습니다. {hour+3}시에 출근하신 분들은'
        f' 칼같이 퇴근하시길 바랍니다.',
        as_user=False,
        icon_url='https://i.imgur.com/9asRVeZ.png',
        username='칼퇴의 요정',
    )


@box.cron('0 9 * * 1-5')
async def work_start(bot):
    holidays = None
    today = now()
    try:
        holidays = await get_holiday_names(today)
    except aiohttp.client_exceptions.ClientOSError:
        pass

    if holidays:
        await say_raccoon_man(bot, holidays[0])
    else:
        if today.isoweekday() == 1:
            await say_start_monday(bot)
        else:
            await say_start_work(bot)


@box.cron('0 18,19 * * 1-5')
async def work_end(bot):
    holidays = None
    today = now()
    hour = today.hour - 12
    try:
        holidays = await get_holiday_names(today)
    except aiohttp.client_exceptions.ClientOSError:
        pass

    if holidays:
        await say_happy_cat(bot, holidays[0], hour)
    else:
        await say_knife(bot, hour)
