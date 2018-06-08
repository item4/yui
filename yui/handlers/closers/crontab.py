from ...box import box


@box.crontab('30 9,14,17,19,22 * * 0,1,5')
async def overflood_front_before_30m(bot):
    await bot.say(
        '#game',
        ':closers: 오염지옥 오버플루드(표면) 개장 30분 전입니다.'
    )


@box.crontab('0 10,15,18,20,23 * * 0,1,5')
async def overflood_front_start(bot):
    await bot.say(
        '#game',
        ':closers: 오염지옥 오버플루드(표면) 개장 시간입니다.'
    )


@box.crontab('30 9,14,17,19,22 * * 2,4,6')
async def overflood_back_before_30m(bot):
    await bot.say(
        '#game',
        ':closers: 오염지옥 오버플루드(이면) 개장 30분 전입니다.'
    )


@box.crontab('0 10,15,18,20,23 * * 2,4,6')
async def overflood_back_start(bot):
    await bot.say(
        '#game',
        ':closers: 오염지옥 오버플루드(이면) 개장 시간입니다.'
    )


@box.crontab('0 0,1 * * 1,2,6')
async def midnight_overflood_front_before_30m(bot):
    await bot.say(
        '#game',
        ':closers: 오염지옥 오버플루드(표면) 개장 30분 전입니다.'
    )


@box.crontab('30 0,1 * * 1,2,6')
async def midnight_overflood_front_start(bot):
    await bot.say(
        '#game',
        ':closers: 오염지옥 오버플루드(표면) 개장 시간입니다.'
    )


@box.crontab('0 0,1 * * 0,3,5')
async def midnight_overflood_back_before_30m(bot):
    await bot.say(
        '#game',
        ':closers: 오염지옥 오버플루드(이면) 개장 30분 전입니다.'
    )


@box.crontab('30 0,1 * * 0,3,5')
async def midnight_overflood_back_start(bot):
    await bot.say(
        '#game',
        ':closers: 오염지옥 오버플루드(이면) 개장 시간입니다.'
    )
