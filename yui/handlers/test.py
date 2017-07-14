from ..box import box
from ..command import argument, option


@box.command('test')
@option('--count', '-c', default=1, type_=int,
        type_error='`{name}`의 값으로는 1개의 정수값만 지정해주세요.',
        count_error='`{name}`의 값으로는 1개의 정수만을 지정해주세요.')
@option('--lower/--upper', '-l/-u', default=True)
@option('--name', '-n', dest='names', multiple=True, required=True,
        count_error='`{name}`가 최소 1개 필요합니다.')
@option('--sep', '-s', dest='separator', default=', ')
@option('--end', '-e', default='!')
async def test(bot, message, count, lower, names, separator, end):
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


@box.command('test2')
@argument('name', dest='names', nargs=-1,
          count_error='`{name}`가 최소 1개 필요합니다.')
@argument('count', type_=int,
          type_error='`{name}`의 값으로는 1개의 정수값만 지정해주세요.',
          count_error='`{name}`의 값으로는 1개의 정수만을 지정해주세요.')
async def test2(bot, message, names, count):
    await bot.say(
        message['channel'],
        '//'.join(', '.join(names) for _ in range(count))
    )
