from datetime import timedelta

import aiohttp

from ...bot import Bot
from ...box import box
from ...event import Message
from ...types.slack.attachment import Attachment
from ...utils import json
from ...utils.datetime import now

box.assert_channel_required('general')

PACKTPUB_URL = 'https://www.packtpub.com/packt/offers/free-learning'


async def say_packtpub_dotd(bot: Bot, channel):
    attachments: list[Attachment] = []
    now_dt = now()
    start = now_dt.strftime('%Y-%m-%d')
    end = (now_dt + timedelta(days=1)).strftime('%Y-%m-%d')
    list_endpoint = (
        'https://services.packtpub.com/free-learning-v1/offers'
        f'?dateFrom={start}T00:00:00.000Z&dateTo={end}T00:00:00.000Z'
    )
    async with aiohttp.ClientSession() as session:
        async with session.get(list_endpoint) as resp:
            list_data = await resp.json(loads=json.loads)

    for item in list_data['data']:
        product_id = item['productId']
        info_endpoint = (
            f'https://static.packt-cdn.com/products/{product_id}/summary'
        )
        async with aiohttp.ClientSession() as session:
            async with session.get(info_endpoint) as resp:
                data = await resp.json(loads=json.loads)

        title = data['title']
        image_url = data['coverImage']
        attachments.append(
            Attachment(
                fallback=f'{title} - {PACKTPUB_URL}',
                title=title,
                title_link=PACKTPUB_URL,
                text='오늘의 Packt Book Deal of The Day:'
                f' {title} - {PACKTPUB_URL}',
                image_url=image_url,
            )
        )

    if attachments:
        await bot.api.chat.postMessage(
            channel=channel,
            text='오늘자 PACKT Book의 무료책이에요!',
            attachments=attachments,
            as_user=True,
        )
    else:
        await bot.say(channel, '오늘은 PACKT Book의 무료책이 없는 것 같아요')


@box.command('무료책', ['freebook'])
async def packtpub_dotd(bot, event: Message):
    """
    PACKT Book 무료책 안내

    PACKT Book에서 날마다 무료로 배부하는 Deal of The Day를 조회합니다.

    `{PREFIX}무료책` (오늘의 무료책)

    """

    await say_packtpub_dotd(bot, event.channel)


@box.cron('5 9 * * *')
async def auto_packtpub_dotd(bot):
    await say_packtpub_dotd(bot, bot.config.CHANNELS['general'])
