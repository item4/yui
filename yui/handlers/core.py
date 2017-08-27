from ..bot import BotReconnect
from ..box import box
from ..event import (ChannelArchive, ChannelCreated, ChannelDeleted,
                     ChannelRename, ChannelUnarchive, TeamMigrationStarted)


@box.on(ChannelCreated)
async def channel_created(bot, event: ChannelCreated):
    bot.channels[event.channel.id] = event.channel


@box.on(ChannelDeleted)
async def channel_deleted(bot, event: ChannelDeleted):
    del bot.channels[event.channel]


@box.on(ChannelArchive)
async def channel_archive(bot, event: ChannelArchive):
    res = await bot.api.channels.info(
        event.channel
    )
    bot.channels[event.channel] = res['channel']


@box.on(ChannelUnarchive)
async def channel_unarchive(bot, event: ChannelUnarchive):
    res = await bot.api.channels.info(
        event.channel
    )
    bot.channels[event.channel] = res['channel']


@box.on(ChannelRename)
async def channel_rename(bot, event: ChannelRename):
    res = await bot.api.channels.info(
        event.channel.id
    )
    bot.channels[event.channel.id] = res['channel']


@box.on(TeamMigrationStarted)
async def team_migration_started():
    raise BotReconnect()
