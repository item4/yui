import inspect
import re

import aiohttp

from libearth.parser.autodiscovery import get_format

import pytz

from .models import RSSFeedURL
from ....api import Attachment
from ....box import CommandMappingHandler, CommandMappingUnit, box
from ....command import argument
from ....event import Message
from ....session import client_session
from ....transform import extract_url

SPACE_RE = re.compile(r'\s{2,}')


class RSS(CommandMappingHandler):

    def __init__(self) -> None:
        self.name = 'rss'
        self.command_map = [
            CommandMappingUnit(name='add', callback=self.add),
            CommandMappingUnit(name='추가', callback=self.add),
            CommandMappingUnit(name='list', callback=self.list),
            CommandMappingUnit(name='목록', callback=self.list),
            CommandMappingUnit(name='del', callback=self.delete),
            CommandMappingUnit(name='delete', callback=self.delete),
            CommandMappingUnit(name='삭제', callback=self.delete),
            CommandMappingUnit(name='제거', callback=self.delete),
        ]

    def get_short_help(self, prefix: str):
        return f'`{prefix}rss`: RSS Feed 구독'

    def get_full_help(self, prefix: str):
        return inspect.cleandoc(f"""
        *RSS Feed 구독*

        채널에서 RSS를 구독할 때 사용됩니다.
        구독하기로 한 주소에서 1분 간격으로 새 글을 찾습니다.

        `{prefix}rss add URL` (URL을 해당 채널에서 구독합니다)
        `{prefix}rss list` (해당 채널에서 구독중인 RSS Feed 목록을 가져옵니다)
        `{prefix}rss del ID` (고유번호가 ID인 RSS 구독을 중지합니다)

        `add` 대신 `추가` 를 사용할 수 있습니다.
        `list` 대신 `목록` 을 사용할 수 있습니다.
        `del` 대신 `delete`, `삭제`, `제거` 를 사용할 수 있습니다.""")

    async def fallback(self, bot, event: Message):
        await bot.say(
            event.channel,
            f'Usage: `{bot.config.PREFIX}help rss`'
        )

    @argument('url', nargs=-1, concat=True, transform_func=extract_url)
    async def add(self, bot, event: Message, sess, url: str):
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

        feed = RSSFeedURL()
        feed.channel = event.channel.id
        feed.url = url
        feed.updated_at = f.updated_at.astimezone(pytz.UTC)

        with sess.begin():
            sess.add(feed)

        await bot.say(
            event.channel,
            f'<#{event.channel.id}> 채널에서 `{url}`을 구독하기 시작했어요!'
        )

    async def list(self, bot, event: Message, sess):
        feeds = sess.query(RSSFeedURL).filter_by(
            channel=event.channel.id,
        ).all()

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

    @argument('id')
    async def delete(self, bot, event: Message, sess, id: int):
        feed = sess.query(RSSFeedURL).get(id)

        if feed is None:
            await bot.say(
                event.channel,
                f'{id}번 RSS 구독 레코드는 존재하지 않아요!'
            )
            return

        await bot.say(
            event.channel,
            f'<#{feed.channel}>에서 구독하는 `{feed.url}` RSS 구독을 취소했어요!'
        )

        with sess.begin():
            sess.delete(feed)


@box.crontab('*/1 * * * *')
async def crawl(bot, sess):
    feeds = sess.query(RSSFeedURL).all()

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
            if feed.updated_at < entry.updated_at.astimezone(pytz.UTC):
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
                feed.updated_at = entry.updated_at.astimezone(pytz.UTC)

        if attachments:
            await bot.api.chat.postMessage(
                channel=feed.channel,
                attachments=attachments,
                as_user=True,
            )

            with sess.begin():
                sess.add(feed)


box.register(RSS())
