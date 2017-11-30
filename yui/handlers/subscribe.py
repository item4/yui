import re
from difflib import Differ

import aiohttp

from libearth.parser.autodiscovery import get_format

from ..api import Attachment
from ..box import box
from ..command import argument
from ..event import Message
from ..models.subscribe import RssFeedSub, SiteSub
from ..transform import extract_url
from ..util import get_count

SPACE_RE = re.compile('\s{2,}')


@box.crontab('*/1 * * * *')
async def crawl(bot, sess):
    feeds = sess.query(RssFeedSub).all()

    for feed in feeds:  # type: RssFeedSub
        data = ''
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(feed.url) as res:
                    data = await res.read()
            except aiohttp.client_exceptions.ClientConnectorError:
                await bot.say(
                    feed.channel,
                    f'*Error*: `{feed.url}`에 접속할 수 없어요!'
                )
                continue

        if not data:
            await bot.say(
                feed.channel,
                f'*Error*: `{feed.url}`에 접속해도 자료를 가져올 수 없어요!'
            )
            continue

        parser = get_format(data)

        if parser is None:
            await bot.say(
                feed.channel,
                f'*Error*: `{feed.url}`는 올바른 RSS 문서가 아니에요!'
            )
            continue
        f, _ = parser(data, feed.url)

        attachments = []

        for entry in reversed(f.entries):
            feed_updated_at = feed.updated_at.astimezone(
                entry.updated_at.tzinfo
            )
            if feed_updated_at < entry.updated_at:
                attachments.append(Attachment(
                    fallback=(
                        'RSS Feed: '
                        f'{str(f.title)} - '
                        f'{str(entry.title)} - '
                        f'{entry.links[0].uri}'
                    ),
                    title=str(entry.title),
                    title_link=entry.links[0].uri,
                    text=('\n'.join(str(entry.content).split('\n')[:3]))[:100],
                    author_name=str(f.title),
                ))
                feed.updated_at = entry.updated_at

        if attachments:
            await bot.api.chat.postMessage(
                channel=feed.channel,
                attachments=attachments,
                as_user=True,
            )

            with sess.begin():
                sess.add(feed)


@box.command('rss-add')
@argument('url', nargs=-1, concat=True, transform_func=extract_url)
async def rss_add(bot, event: Message, sess, url: str):
    """
    채널에서 RSS 구독

    `{PREFIX}rss-add https://item4.github.io/feed.xml` (해당 주소를 구독합니다)

    """

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as res:
                data: bytes = await res.read()
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

    if not data:
        await bot.say(
            event.channel,
            f'`{url}`은 빈 웹페이지에요!'
        )
        return

    parser = get_format(data)

    if parser is None:
        await bot.say(
            event.channel,
            f'`{url}`은 올바른 RSS 문서가 아니에요!'
        )
        return

    f, _ = parser(data, url)

    feed = RssFeedSub()
    feed.channel = event.channel
    feed.url = url
    feed.updated_at = f.updated_at

    with sess.begin():
        sess.add(feed)

    await bot.say(
        event.channel,
        f'<#{event.channel}> 채널에서 `{url}` 을 구독하기 시작했어요!'
    )


@box.command('rss-list')
async def rss_list(bot, event: Message, sess):
    """
    채널에서 구독중인 RSS 목록

    `{PREFIX}rss-list` (해당 채널에서 구독중인 RSS 목록)

    """

    feeds = sess.query(RssFeedSub).filter_by(channel=event.channel).all()

    if feeds:
        feed_list = '\n'.join(
            f'{feed.id} - {feed.url}' for feed in feeds
        )

        await bot.say(
            event.channel,
            f'<#{event.channel}> 채널에서 구독중인 RSS 목록은 다음과 같아요!'
            f'\n```\n{feed_list}\n```'
        )
    else:
        await bot.say(
            event.channel,
            '<#{event.channel}> 채널에서 구독중인 RSS가 없어요!'
        )


@box.command('rss-del')
@argument('id')
async def rss_del(bot, event: Message, sess, id: int):
    """
    RSS 구독 취소

    `{PREFIX}rss-del 123` (123번 RSS 구독 취소)

    RSS 고유 번호는 `{PREFIX}rss-list` 명령어를 통해 확인할 수 있습니다.

    """

    feed = sess.query(RssFeedSub).get(id)

    if feed is None:
        await bot.say(
            event.channel,
            f'{id}번 RSS 구독 레코드는 존재하지 않아요!'
        )
        return

    await bot.say(
        event.channel,
        f'<#{feed.channel}> 에서 구독하는 `{feed.url}` RSS 구독을 취소했어요!'
    )

    with sess.begin():
        sess.delete(feed)


@box.crontab('*/1 * * * *')
async def run(bot, sess):
    subs = sess.query(SiteSub).all()
    for sub in subs:  # type: SiteSub
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(sub.url) as res:
                    new_body: str = await res.text()
                    if sub.body != new_body:
                        old_body_lines = sub.body.splitlines(keepends=True)
                        new_body_lines = new_body.splitlines(keepends=True)
                        d = Differ()
                        diff = [
                            SPACE_RE.sub(' ', x).rstrip() for x in d.compare(
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
    1분 간격으로 모니터링하며, 한사람당 최대 5개의 사이트를 등록할 수 있습니다.

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
                data: str = await res.text()
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
        f'<@{event.user}>, 해당 주소에 접속해서 바뀌는게 있으면 바로 DM으로 알려드릴게요!'
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
        ),
        thread_ts=event.ts,
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
            f'{id}번 구독을 취소했어요! 더 이상 `{sub.url}` 에 대한 알림이 가지 않을거에요!'
        )
        with sess.begin():
            sess.delete(sub)
    else:
        await bot.say(
            event.channel,
            f'{id}번 구독은 존재하지 않거나 자신의 구독이 아니에요!'
        )
