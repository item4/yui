from ....box import box
from .commons import say_d2r_terror_zone_info


@box.cron("1 * * * *")
async def auto_d2tz(bot):
    await say_d2r_terror_zone_info(bot, bot.config.CHANNELS["d2r"])
