from ...box import box


@box.cron("55 8-20 * * *")
async def alert_lifestyle(bot):
    await bot.say(bot.config.CHANNELS["memo"], "메모할 시간이에요!")
