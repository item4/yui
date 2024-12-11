from ....box import box
from .commons import wait_next_d2r_terror_zone_info


@box.cron("1 * * * *")
async def auto_d2tz(bot):
    await wait_next_d2r_terror_zone_info(bot, bot.config.CHANNELS["d2r"])
