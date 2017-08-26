from typing import List

from ..box import box
from ..command import argument, not_, only, option
from ..type import int_range


@box.command('test', channels=only('test'))
@option('--count', '-c', default=1,
        type_error='`{name}`의 값으로는 1개의 1~15 사이의 정수값만 지정해주세요.',
        count_error='`{name}`의 값으로는 1개의 1~15 사이의 정수만을 지정해주세요.')
@option('--lower/--upper', '-l/-u', default=True)
@option('--name', '-n', dest='names', multiple=True, required=True,
        count_error='`{name}`가 최소 1개 필요합니다.')
@option('--sep', '-s', dest='separator', default=', ')
@option('--end', '-e', default='!')
async def test(
    bot,
    message,
    count: int_range(1, 15),
    lower: bool,
    names: List[str],
    separator: str,
    end: str
):
    """
    봇 기능 테스트용 명령어

    `{PREFIX}test --name kirito`
    `{PREFIX}test --name kirito --name asuna`
    `{PREFIX}test --name kirito --count=15`

    """

    if lower:
        res = separator.join(
            name.lower() for _ in range(count) for name in names
        ) + end
    else:
        res = separator.join(
            name.lower() for _ in range(count) for name in names
        ) + end

    await bot.say(
        message['channel'],
        res[:300]
    )


@box.command('test2', channels=only('test'))
@argument('name', dest='names', nargs=-1,
          count_error='`{name}`가 최소 1개 필요합니다.')
@argument('count',
          type_error='`{name}`의 값으로는 1개의 1~15 사이의 정수값만 지정해주세요.',
          count_error='`{name}`의 값으로는 1개의 1~15 사이의 정수만을 지정해주세요.')
async def test2(
    bot,
    message,
    names: List[str],
    count: int_range(1, 15)
):
    """
    봇 기능 테스트용 명령어

    `{PREFIX}test2 kirito 3`
    `{PREFIX}test2 kirito asuna 3`

    """

    await bot.say(
        message['channel'],
        '//'.join(', '.join(names) for _ in range(count))
    )


@box.command('test3', channels=not_('_general', 'dev'))
@argument('number', nargs=-1)
async def test3(bot, message, number: List[int_range(1, 10)]):
    await bot.say(
        message['channel'],
        ','.join(map(str, number))
    )


@box.crontab('*/1 * * * *', start=False)
async def one(bot):
    await bot.say('test', '1분마다')


@box.crontab('*/3 * * * *', start=False)
async def three(bot):
    await bot.say('test', '3분마다')


@box.crontab('*/5 * * * *', start=False)
async def five(bot):
    await bot.say('test', '5분마다')


@box.crontab('*/7 * * * *', start=False)
async def seven(bot):
    await bot.say('test', '7분마다')


@box.command('cron-test-start', channels=only('test'))
async def start(bot, message):
    """crontab 테스트 시작"""

    one.start()
    three.start()
    five.start()
    seven.start()
    await bot.say(message['channel'], 'start')


@box.command('cron-test-stop', channels=only('test'))
async def stop(bot, message):
    """crontab 테스트 종료"""

    one.stop()
    three.stop()
    five.stop()
    seven.stop()
    await bot.say(message['channel'], 'stop')
