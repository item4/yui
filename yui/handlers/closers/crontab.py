from ...box import box


@box.crontab('30 9,14,19,22 * * 0,2,4,6')
async def overflood_before_30m(bot):
    await bot.say(
        '#game',
        ':closers: 오염지옥 오버플루드 개장 30분 전입니다.'
    )


@box.crontab('0 10,15,20,23 * * 0,2,4,6')
async def overflood_start(bot):
    await bot.say(
        '#game',
        ':closers: 오염지옥 오버플루드 개장 시간입니다.'
    )
