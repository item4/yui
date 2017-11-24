from difflib import Differ

import aiohttp

from ..box import box
from ..command import argument
from ..event import Message
from ..models.watch import SiteSub
from ..transform import extract_url
from ..util import get_count


@box.crontab('*/1 * * * *')
async def run(bot, sess):
    subs = sess.query(SiteSub).all()
    for sub in subs:  # type: SiteSub
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(sub.url) as res:
                    new_body = await res.text()
                    if sub.body != new_body:
                        old_body_lines = sub.body.splitlines(keepends=True)
                        new_body_lines = new_body.splitlines(keepends=True)
                        d = Differ()
                        diff = [
                            x for x in d.compare(
                                old_body_lines,
                                new_body_lines
                            )
                            if x[0] not in [' ', '?']
                        ]
                        await bot.say(
                            sub.user,
                            '`{}` 에서 변경이 발생했어요!\n```\n{}\n```'.format(
                                sub.url,
                                '\n'.join(diff),
                            )
                        )
                        sub.body = new_body
                        with sess.begin():
                            sess.add(sub)
            except aiohttp.client_exceptions.ClientConnectorError:
                await bot.say(
                    sub.user,
                    f'`{sub.url}` 에 접속할 수 없어요!'
                )


@box.command('watch')
@argument('url', transform_func=extract_url)
async def watch(bot, event: Message, sess, url: str):
    """
    Website diff 구독

    RSS등의 수단으로 구독할 수 없는 사이트를 접속하여 변경점이 발생하면 DM으로 알려줍니다.
    15분 간격으로 모니터링하며, 한사람당 최대 5개의 사이트를 등록할 수 있습니다.

    `{PREFIX}watch http://item4.net` (`http://item4.net` 을 모니터링)

    """

    count = get_count(sess.query(SiteSub).filter_by(user=event.user))
    if count >= 5:
        await bot.say(
            event.channel,
            '테러 방지를 위해 한 사람당 최대 5개의 구독만 가능해요!'
        )
        return

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as res:
                data = await res.text()
        except aiohttp.client_exceptions.InvalidURL:
            await bot.say(
                event.channel,
                f'`{url}`은 올바른 URL이 아니에요!'
            )
            return
        except aiohttp.client_exceptions.ClientConnectorError:
            await bot.say(
                event.channel,
                f'`{url}`에 접속할 수 없어요!'
            )
            return

    sub = SiteSub()
    sub.url = url
    sub.user = event.user
    sub.body = data
    with sess.begin():
        sess.add(sub)

    await bot.say(
        event.channel,
        '해당 주소에 접속해서 바뀌는게 있으면 바로 DM으로 알려드릴게요!'
    )


@box.command('watch-list')
async def watch_list(bot, event: Message, sess):
    """
    Website diff 구독 목록

    `.watch` 명령어로 구독중인 사이트 목록을 출력합니다.

    `.watch-list` (자신이 구독중인 전체 목록)

    """

    subs = sess.query(SiteSub).filter_by(user=event.user).all()

    await bot.say(
        event.channel,
        '<@{}> 사용자가 구독중인 사이트는 다음과 같아요!\n```\n{}\n```'.format(
            event.user,
            '\n'.join(
                f'{s.id} - {s.url}' for s in subs
            )
        )
    )


@box.command('watch-del')
@argument('id')
async def watch_del(bot, event: Message, sess, id: int):
    """
    Website diff 구독 취소

    `.watch` 명령어로 구독중인 사이트를 구독 취소합니다.
    구독 번호는 `.watch-list` 명령어로 확인 가능합니다.

    `.watch-del 1` (1번 구독을 취소)

    """

    sub = sess.query(SiteSub).get(id)

    if sub and sub.user == event.user:
        await bot.say(
            event.channel,
            f'{id}번 구독을 취소했어요!'
        )
        with sess.begin():
            sess.delete(sub)
    else:
        await bot.say(
            event.channel,
            f'{id}번 구독은 존재하지 않거나 자신의 구독이 아니에요!'
        )
