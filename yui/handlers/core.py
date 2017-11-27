from ..bot import BotReconnect
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
    GroupArchive,
    GroupClose,
    GroupHistoryChanged,
    GroupJoined,
    GroupLeft,
    GroupMarked,
    GroupOpen,
    GroupRename,
    GroupUnarchive,
    Hello,
    TeamMigrationStarted,
)
from ..type import DirectMessageChannel, PrivateChannel, PublicChannel


@box.on(Hello)
async def on_start(bot):
    cursor = None
    while True:
        result = await bot.api.channels.list(cursor)
        cursor = None
        if 'response_metadata' in result:
            cursor = result['response_metadata'].get('next_cursor')
        for c in result['channels']:
            res = await bot.api.channels.info(c['id'])
            bot.channels.append(PublicChannel(**res['channel']))
        if not cursor:
            break

    result = await bot.api.im.list()
    for d in result['ims']:
        bot.ims.append(DirectMessageChannel(**d))

    result = await bot.api.groups.list()
    for g in result['groups']:
        res = await bot.api.groups.info(g['id'])
        bot.groups.append(PrivateChannel(**res['group']))
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
    cursor = None
    new_channels = []
    while True:
        result = await bot.api.channels.list(cursor)
        cursor = result['response_metadata'].get('next_cursor')
        for c in result['channels']:
            res = await bot.api.channels.info(c['id'])
            new_channels.append(PublicChannel(**res['channel']))
        if not cursor:
            break

    bot.channels[:] = new_channels


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
    new_groups = []
    result = await bot.api.groups.list()
    for g in result['groups']:
        res = await bot.api.groups.info(g['id'])
        new_groups.append(PrivateChannel(**res['group']))

    bot.groups[:] = new_groups


@box.on(TeamMigrationStarted)
async def team_migration_started():
    raise BotReconnect()
