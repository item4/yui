import re

import aiohttp

from libearth.parser.autodiscovery import get_format

from ..api import Attachment
from ..box import box
from ..command import argument
from ..event import Message
from ..models.subscribe import RssFeedSub
from ..session import client_session
from ..transform import extract_url

SPACE_RE = re.compile('\s{2,}')


@box.crontab('*/1 * * * *')
async def crawl(bot, sess):
    feeds = sess.query(RssFeedSub).all()

    for feed in feeds:  # type: RssFeedSub
        data = ''
        async with client_session() as session:
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

    async with client_session() as session:
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
    feed.channel = event.channel.id
    feed.url = url
    feed.updated_at = f.updated_at

    with sess.begin():
        sess.add(feed)

    await bot.say(
        event.channel,
        f'<#{event.channel.id}> 채널에서 `{url}` 을 구독하기 시작했어요!'
    )


@box.command('rss-list')
async def rss_list(bot, event: Message, sess):
    """
    채널에서 구독중인 RSS 목록

    `{PREFIX}rss-list` (해당 채널에서 구독중인 RSS 목록)

    """

    feeds = sess.query(RssFeedSub).filter_by(channel=event.channel.id).all()

    if feeds:
        feed_list = '\n'.join(
            f'{feed.id} - {feed.url}' for feed in feeds
        )

        await bot.say(
            event.channel,
            f'<#{event.channel.id}> 채널에서 구독중인 RSS 목록은 다음과 같아요!'
            f'\n```\n{feed_list}\n```'
        )
    else:
        await bot.say(
            event.channel,
            f'<#{event.channel.id}> 채널에서 구독중인 RSS가 없어요!'
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
