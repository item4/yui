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
from ..type import (
    DirectMessageChannel,
    PrivateChannel,
    PublicChannel,
    User,
)

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
    async def channel():
        cursor = None
        bot.channels.clear()
        while True:
            result = await retry(bot.api.channels.list, cursor)
            cursor = None
            if 'response_metadata' in result:
                cursor = result['response_metadata'].get('next_cursor')
            for c in result['channels']:
                res = await retry(bot.api.channels.info, c['id'])
                bot.channels.append(PublicChannel(**res['channel']))
            if not cursor:
                break

    async def im():
        bot.ims.clear()
        result = await retry(bot.api.im.list)
        for d in result['ims']:
            bot.ims.append(DirectMessageChannel(**d))

    async def groups():
        bot.groups.clear()
        result = await retry(bot.api.groups.list)
        for g in result['groups']:
            res = await retry(bot.api.groups.info, g['id'])
            bot.groups.append(PrivateChannel(**res['group']))

    async def users():
        bot.users.clear()
        result = await retry(bot.api.users.list, presence=False)
        for u in result['members']:
            bot.users[u['id']] = User(**u)

    await asyncio.wait(
        (
            channel(),
            im(),
            groups(),
            users(),
        ),
        return_when=asyncio.FIRST_EXCEPTION,
    )

    return True


@box.on(TeamJoin)
async def on_team_join(bot, event: TeamJoin):
    logger.info('on team join start')
    res = await retry(bot.api.users.info, event.user)
    bot.users[res['user']['id']] = User(**res['user'])
    logger.info('on team join end')

    return True


@box.on(UserChange)
async def on_user_change(bot, event: UserChange):
    logger.info('on user change start')
    res = await retry(bot.api.users.info, event.user)
    bot.users[res['user']['id']] = User(**res['user'])
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
        result = await retry(bot.api.channels.list, cursor)
        cursor = result.get('response_metadata', {}).get('next_cursor')
        for c in result['channels']:
            res = await retry(bot.api.channels.info, c['id'])
            new_channels.append(PublicChannel(**res['channel']))
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
    result = await retry(bot.api.groups.list)
    for g in result['groups']:
        res = await retry(bot.api.groups.info, g['id'])
        new_groups.append(PrivateChannel(**res['group']))

    bot.groups[:] = new_groups
    logger.info('private_channel_mutation_detected start')
    return True


@box.on(IMClose)
@box.on(IMCreated)
@box.on(IMHistoryChanged)
@box.on(IMMarked)
@box.on(IMOpen)
async def direct_message_channel_mutation_detected(bot):
    logger.info('direct_message_channel_mutation_detected start')
    new_ims = []
    result = await retry(bot.api.im.list)
    for d in result['ims']:
        new_ims.append(DirectMessageChannel(**d))

    bot.ims[:] = new_ims
    logger.info('direct_message_channel_mutation_detected end')
    return True


@box.on(TeamMigrationStarted)
async def team_migration_started():
    logger.info('Slack sent team_migration_started. restart bot')
    raise BotReconnect()
