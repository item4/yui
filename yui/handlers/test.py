from ..box import box
from ..command import argument, option


@box.command('test')
@option('--count', '-c', default=1, type_=int)
@option('--lower/--upper', '-l/-u', default=True)
@option('--name', '-n', dest='names', multiple=True, required=True)
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
@argument('name', dest='names', nargs=-1)
@argument('count', type_=int)
async def test2(bot, message, names, count):
    await bot.say(
        message['channel'],
        '//'.join(', '.join(names) for _ in range(count))
    )
