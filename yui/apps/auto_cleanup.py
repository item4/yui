import asyncio
import datetime
import logging
import time

from ..bot import APICallError
from ..box import box
from ..command import Cs, option
from ..event import Message
from ..utils.datetime import now

box.assert_config_required('OWNER_USER_TOKEN', str)
box.assert_channels_required('auto_cleanup_targets')

COOLTIME = datetime.timedelta(minutes=5)

logger = logging.getLogger(__name__)


@box.cron('*/10 * * * *')
async def cleanup_channels(bot):
    try:
        channels = Cs.auto_cleanup_targets.gets()
    except KeyError:
        return

    naive_now = datetime.datetime.now()
    time_limit = naive_now - datetime.timedelta(hours=5)

    latest_ts = str(time.mktime(time_limit.timetuple()))
    logger.debug(f'latest_ts: {latest_ts}')

    for channel in channels:
        logger.debug(f'channel {channel.name} start')
        history = await bot.api.channels.history(
            channel,
            count=100,
            latest=latest_ts,
            unreads=True,
        )

        if history['ok']:
            logger.debug(f'channel history: {len(history["messages"])}')
            for message in history['messages']:
                try:
                    r = await bot.api.chat.delete(
                        channel,
                        message['ts'],
                        token=bot.config.OWNER_USER_TOKEN,
                    )
                    logger.debug(f'message {message["ts"]} delete: {r}')
                except APICallError:
                    logger.debug(f'message {message} fail to delete')
                    break
        logger.debug(f'channel {channel.name} end')

        await asyncio.sleep(1)


@box.command('청소')
@option('--count', '-c', default=100)
async def cleanup(bot, event: Message, count: int):
    """
    채널 청소

    해당 채널의 메시지 최근 100개를 즉각적으로 삭제합니다.
    채널당 5분의 쿨타임을 가지며, 자동 청소 채널 이외의 채널은 관리자만 사용 가능합니다.

    """

    try:
        channels = Cs.auto_cleanup_targets.gets()
    except KeyError:
        await bot.say(
            event.channel,
            '권한 검사 도중 에러가 발생했어요! 잠시 후에 다시 시도해주세요!',
        )
        return

    if event.user.id != bot.config.OWNER_ID:
        if event.channel not in channels:
            await bot.say(
                event.channel,
                '본 채널에서 이 명령어를 사용할 수 있는 권한이 없어요!',
            )
            return
        count = 100

        now_dt = now()
        if event.channel.id in cleanup.last_call:
            last_call = cleanup.last_call[event.channel.id]
            if now_dt - last_call < COOLTIME:
                fine = last_call + COOLTIME
                await bot.say(
                    text=(
                        "아직 쿨타임이에요! "
                        f"{fine.strftime('%H시 %M분')} 이후로 다시 시도해주세요!"
                    )
                )
                return

    history = await bot.api.channels.history(
        event.channel,
        count=count,
        latest=event.ts,
        unreads=True,
    )

    delete_count = 0
    if history['ok']:
        for message in history['messages']:
            try:
                await bot.api.chat.delete(
                    event.channel,
                    message['ts'],
                    token=bot.config.OWNER_USER_TOKEN,
                )
                delete_count += 1
            except APICallError:
                break
    await bot.say(
        event.channel,
        f'본 채널에서 최근 {delete_count:,}개의 메시지를 삭제했어요!',
    )
