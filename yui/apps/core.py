import asyncio
import logging

from ..bot import APICallError, BotReconnect
from ..box import box
from ..event import (
    ChannelArchive,
    ChannelCreated,
    ChannelDeleted,
    ChannelHistoryChanged,
    ChannelJoined,
    ChannelLeft,
    ChannelMarked,
    ChannelRename,
    ChannelUnarchive,
    ChatterboxSystemStart,
    GroupArchive,
    GroupClose,
    GroupHistoryChanged,
    GroupJoined,
    GroupLeft,
    GroupMarked,
    GroupOpen,
    GroupRename,
    GroupUnarchive,
    IMClose,
    IMCreated,
    IMHistoryChanged,
    IMMarked,
    IMOpen,
    TeamJoin,
    TeamMigrationStarted,
    UserChange,
)
from ..types.channel import (
    DirectMessageChannel,
    PrivateChannel,
    PublicChannel,
)
from ..types.user import User

logger = logging.getLogger(__name__)


async def retry(callback, *args, **kwargs):
    while True:
        try:
            return await callback(*args, **kwargs)
        except APICallError:
            await asyncio.sleep(0.5)
        except Exception:
            raise


@box.on(ChatterboxSystemStart)
async def on_start(bot):
    async def channels():
        cursor = None
        bot.channels.clear()
        while True:
            result = await bot.api.conversations.list(
                cursor=cursor,
                types='public_channel,private_channel,im',
            )
            cursor = None
            await asyncio.sleep(0.1)
            if 'response_metadata' in result.body:
                cursor = result.body['response_metadata'].get('next_cursor')
            for c in result.body['channels']:
                resp = await bot.api.conversations.info(c['id'])
                if not resp.body['ok']:
                    continue
                channel = resp.body['channel']
                if channel.get('is_channel'):
                    bot.channels.append(
                        PublicChannel(**channel)
                    )
                elif channel.get('is_im'):
                    bot.ims.append(
                        DirectMessageChannel(**channel)
                    )
                elif channel.get('is_group'):
                    bot.groups.append(
                        PrivateChannel(**channel)
                    )
                await asyncio.sleep(0.1)
            if not cursor:
                break

    async def users():
        bot.users.clear()
        result = await retry(bot.api.users.list, presence=False)
        for u in result.body['members']:
            bot.users.append(User(**u))

    bot.is_ready = False

    await asyncio.wait(
        (
            channels(),
            users(),
        ),
        return_when=asyncio.FIRST_EXCEPTION,
    )

    bot.is_ready = True

    return True


@box.on(TeamJoin)
async def on_team_join(bot, event: TeamJoin):
    logger.info('on team join start')
    res = await retry(bot.api.users.info, event.user)
    bot.users.append(User(**res.body['user']))  # type: ignore
    logger.info('on team join end')

    return True


@box.on(UserChange)
async def on_user_change(bot, event: UserChange):
    if not (event.user.id and event.user.team_id):
        return True

    logger.info('on user change start')
    res = await retry(bot.api.users.info, event.user)

    bot.users[:] = [
        u for u in bot.users if u.id != event.user.id
    ] + [User(**res.body['user'])]  # type: ignore
    logger.info('on user change end')

    return True


@box.on(ChannelArchive)
@box.on(ChannelCreated)
@box.on(ChannelDeleted)
@box.on(ChannelHistoryChanged)
@box.on(ChannelJoined)
@box.on(ChannelLeft)
@box.on(ChannelMarked)
@box.on(ChannelUnarchive)
@box.on(ChannelRename)
async def public_channel_mutation_detected(bot):
    logger.info('public_channel_mutation_detected start')
    cursor = None
    new_channels = []
    while True:
        result = await bot.api.conversations.list(
            cursor=cursor,
            types='public_channel',
        )
        await asyncio.sleep(0.1)
        cursor = result.body.get('response_metadata', {}).get('next_cursor')
        for c in result.body['channels']:
            res = await bot.api.conversations.info(c['id'])
            new_channels.append(
                PublicChannel(**res.body['channel'])
            )
            await asyncio.sleep(0.1)
        if not cursor:
            break

    bot.channels[:] = new_channels
    logger.info('public_channel_mutation_detected end')
    return True


@box.on(GroupArchive)
@box.on(GroupClose)
@box.on(GroupHistoryChanged)
@box.on(GroupJoined)
@box.on(GroupLeft)
@box.on(GroupMarked)
@box.on(GroupOpen)
@box.on(GroupRename)
@box.on(GroupUnarchive)
async def private_channel_mutation_detected(bot):
    logger.info('private_channel_mutation_detected start')
    new_groups = []
    cursor = None
    while True:
        result = await bot.api.conversations.list(
            cursor=cursor,
            types='private_channel',
        )
        await asyncio.sleep(0.1)
        cursor = result.body.get('response_metadata', {}).get('next_cursor')
        for c in result.body['channels']:
            res = await bot.api.conversations.info(c['id'])
            new_groups.append(
                PrivateChannel(**res.body['channel'])
            )
            await asyncio.sleep(0.1)
        if not cursor:
            break

    bot.groups[:] = new_groups
    logger.info('private_channel_mutation_detected end')
    return True


@box.on(IMClose)
@box.on(IMCreated)
@box.on(IMHistoryChanged)
@box.on(IMMarked)
@box.on(IMOpen)
async def direct_message_channel_mutation_detected(bot):
    logger.info('direct_message_channel_mutation_detected start')
    new_ims = []
    cursor = None
    while True:
        result = await bot.api.conversations.list(
            cursor=cursor,
            types='im',
        )
        await asyncio.sleep(0.1)
        cursor = result.body.get('response_metadata', {}).get('next_cursor')
        for c in result.body['channels']:
            res = await bot.api.conversations.info(c['id'])
            new_ims.append(
                DirectMessageChannel(**res.body['channel'])
            )
            await asyncio.sleep(0.1)
        if not cursor:
            break

    bot.ims[:] = new_ims
    logger.info('direct_message_channel_mutation_detected end')
    return True


@box.on(TeamMigrationStarted)
async def team_migration_started():
    logger.info('Slack sent team_migration_started. restart bot')
    raise BotReconnect()
