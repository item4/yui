from ..box import box


@box.on('channel_created')
async def channel_created(bot, message):
    bot.channels[message['channel']['id']] = message['channel']


@box.on('channel_deleted')
async def channel_deleted(bot, message):
    del bot.channels[message['channel']]


@box.on('channel_archive')
async def channel_archive(bot, message):
    res = await bot.api.channels.info(
        message['channel']
    )
    bot.channels[message['channel']] = res['channel']


@box.on('channel_unarchive')
async def channel_unarchive(bot, message):
    res = await bot.api.channels.info(
        message['channel']
    )
    bot.channels[message['channel']] = res['channel']


@box.on('channel_rename')
async def channel_rename(bot, message):
    res = await bot.api.channels.info(
        message['channel']['id']
    )
    bot.channels[message['channel']['id']] = res['channel']
