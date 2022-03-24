import asyncio
import logging

from ..bot import BotReconnect
from ..box import box
from ..event import TeamJoin
from ..event import TeamMigrationStarted
from ..event import YuiSystemStart
from ..types.channel import DirectMessageChannel
from ..types.channel import PrivateChannel
from ..types.channel import PublicChannel
from ..types.user import User

logger = logging.getLogger(__name__)


@box.on(YuiSystemStart)
async def on_start(bot):
    async def channels():
        logger.info('on yui system start - channels start')
        cursor = None
        bot.channels.clear()
        while True:
            result = await bot.api.conversations.list(
                cursor=cursor,
                types='public_channel,private_channel,im',
            )
            cursor = None
            if 'response_metadata' in result.body:
                cursor = result.body['response_metadata'].get('next_cursor')
            for c in result.body['channels']:
                resp = await bot.api.conversations.info(c['id'])
                if not resp.body['ok']:
                    continue
                channel = resp.body['channel']
                if channel.get('is_channel'):
                    bot.channels.append(PublicChannel(**channel))
                elif channel.get('is_im'):
                    bot.ims.append(DirectMessageChannel(**channel))
                elif channel.get('is_group'):
                    bot.groups.append(PrivateChannel(**channel))
            if not cursor:
                break
        logger.info('on yui system start - channels end')

    async def users():
        logger.info('on yui system start - users start')
        bot.users.clear()
        result = await bot.api.users.list(presence=False)
        for u in result.body['members']:
            bot.users.append(User(**u))
        logger.info('on yui system start - users end')

    logger.info('on yui system start start')

    bot.is_ready = False

    await asyncio.wait(
        (
            channels(),
            users(),
        ),
        return_when=asyncio.FIRST_EXCEPTION,
    )

    bot.is_ready = True

    logger.info('on yui system start end')

    return True


@box.on(TeamJoin)
async def on_team_join(bot, event: TeamJoin):
    logger.info('on team join start')
    res = await bot.api.users.info(event.user)
    bot.users.append(User(**res.body['user']))
    logger.info('on team join end')

    return True


@box.on(TeamMigrationStarted)
async def team_migration_started():
    logger.info('Slack sent team_migration_started. restart bot')
    raise BotReconnect()
