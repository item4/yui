import aiohttp

from .utils import get_holiday_name
from ...api import Attachment
from ...box import box
from ...command import C
from ...utils.datetime import now

box.assert_config_required('TDCPROJECT_KEY', str)
box.assert_channel_required('general')


@box.cron('0 9 * * 1')
async def work_start_monday(bot):
    holiday = None
    today = now()
    try:
        holiday = await get_holiday_name(bot.config.TDCPROJECT_KEY, today)
    except aiohttp.client_exceptions.ClientOSError:
        pass

    if holiday:
        await bot.api.chat.postMessage(
            channel=C.general.get(),
            text=f'오늘은 {holiday}! 출근하라는 상사는 이 너굴맨이 처리했으니 안심하라구!',
            as_user=False,
            icon_url='https://i.imgur.com/dG6wXTX.jpg',
            username='너굴맨',
        )
    else:
        await bot.api.chat.postMessage(
            channel=C.general.get(),
            username='아니 이게 무슨 소리야',
            icon_emoji=':interrobang:',
            attachments=[
                Attachment(
                    fallback='https://i.imgur.com/Gv9GJBK.jpg',
                    image_url='https://i.imgur.com/Gv9GJBK.jpg',
                ),
            ],
        )


@box.cron('0 9 * * 2-5')
async def work_start(bot):
    holiday = None
    today = now()
    try:
        holiday = await get_holiday_name(bot.config.TDCPROJECT_KEY, today)
    except aiohttp.client_exceptions.ClientOSError:
        pass

    if holiday:
        await bot.api.chat.postMessage(
            channel=C.general.get(),
            text=f'오늘은 {holiday}! 출근하라는 상사는 이 너굴맨이 처리했으니 안심하라구!',
            as_user=False,
            icon_url='https://i.imgur.com/dG6wXTX.jpg',
            username='너굴맨',
        )
    else:
        await bot.api.chat.postMessage(
            channel=C.general.get(),
            username='자본주의가 낳은 괴물',
            icon_emoji=':money_mouth_face:',
            attachments=[
                Attachment(
                    fallback='https://i.imgur.com/lBqfaCO.jpg',
                    image_url='https://i.imgur.com/lBqfaCO.jpg',
                ),
            ],
        )


@box.cron('0 18 * * 1-5')
async def work_end_18h(bot):
    holiday = None
    today = now()
    try:
        holiday = await get_holiday_name(bot.config.TDCPROJECT_KEY, today)
    except aiohttp.client_exceptions.ClientOSError:
        pass

    if holiday:
        await bot.api.chat.postMessage(
            channel=C.general.get(),
            text=f'오늘은 {holiday}! 출근을 안 했으니 퇴근도 안 해도 된다냥!',
            as_user=False,
            icon_emoji=':smile_cat:',
            username='퇴근을 알리는 냥냥이',
        )
    else:
        await bot.api.chat.postMessage(
            channel=C.general.get(),
            text=f'6시 퇴근 시간이다냥!',
            as_user=False,
            icon_emoji=':smile_cat:',
            username='퇴근을 알리는 냥냥이',
        )


@box.cron('0 19 * * 1-5')
async def work_end_19h(bot):
    holiday = None
    today = now()
    try:
        holiday = await get_holiday_name(bot.config.TDCPROJECT_KEY, today)
    except aiohttp.client_exceptions.ClientOSError:
        pass

    if holiday:
        await bot.api.chat.postMessage(
            channel=C.general.get(),
            text=f'오늘은 {holiday}! 출근을 안 했으니 퇴근도 안 해도 된다냥!',
            as_user=False,
            icon_emoji=':smile_cat:',
            username='퇴근을 알리는 냥냥이',
        )
    else:
        await bot.api.chat.postMessage(
            channel=C.general.get(),
            text=f'7시 퇴근 시간이다냥!',
            as_user=False,
            icon_emoji=':smile_cat:',
            username='퇴근을 알리는 냥냥이',
        )
