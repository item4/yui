import inspect
import re

import aiohttp
import aiohttp.client_exceptions
import dateutil.parser
import fastfeedparser
from dateutil.tz import UTC
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select

from ....box import box
from ....box import route
from ....command import argument
from ....event import Message
from ....transform import extract_url
from ....types.slack.attachment import Attachment
from .models import RSSFeedURL

SPACE_RE = re.compile(r"\s{2,}")


class RSS(route.RouteApp):
    def __init__(self) -> None:
        self.name = "rss"
        self.route_list.extend(
            [
                route.Route(name="add", callback=self.add),
                route.Route(name="추가", callback=self.add),
                route.Route(name="list", callback=self.list),
                route.Route(name="목록", callback=self.list),
                route.Route(name="del", callback=self.delete),
                route.Route(name="delete", callback=self.delete),
                route.Route(name="삭제", callback=self.delete),
                route.Route(name="제거", callback=self.delete),
            ],
        )

    def get_short_help(self, prefix: str):
        return f"`{prefix}rss`: RSS Feed 구독"

    def get_full_help(self, prefix: str):
        return inspect.cleandoc(
            f"""
        *RSS Feed 구독*

        채널에서 RSS를 구독할 때 사용됩니다.
        구독하기로 한 주소에서 1분 간격으로 새 글을 찾습니다.

        `{prefix}rss add URL` (URL을 해당 채널에서 구독합니다)
        `{prefix}rss list` (해당 채널에서 구독중인 RSS Feed 목록을 가져옵니다)
        `{prefix}rss del ID` (고유번호가 ID인 RSS 구독을 중지합니다)

        `add` 대신 `추가` 를 사용할 수 있습니다.
        `list` 대신 `목록` 을 사용할 수 있습니다.
        `del` 대신 `delete`, `삭제`, `제거` 를 사용할 수 있습니다.""",
        )

    async def fallback(self, bot, event: Message):
        await bot.say(event.channel, f"Usage: `{bot.config.PREFIX}help rss`")

    @argument("url", nargs=-1, concat=True, transform_func=extract_url)
    async def add(self, bot, event: Message, sess: AsyncSession, url: str):
        try:
            async with (
                aiohttp.ClientSession() as session,
                session.get(
                    url,
                ) as resp,
            ):
                data: bytes = await resp.read()
        except aiohttp.client_exceptions.InvalidURL:
            await bot.say(
                event.channel,
                f"`{url}`은 올바른 URL이 아니에요!",
            )
            return
        except aiohttp.client_exceptions.ClientConnectorError:
            await bot.say(event.channel, f"`{url}`에 접속할 수 없어요!")
            return

        if not data:
            await bot.say(event.channel, f"`{url}`은 빈 웹페이지에요!")
            return

        try:
            f = fastfeedparser.parse(data)
        except ValueError:
            await bot.say(
                event.channel,
                f"`{url}`은 올바른 RSS 문서가 아니에요!",
            )
            return

        feed = RSSFeedURL()
        feed.channel = event.channel
        feed.url = url
        feed.updated_at = max(
            dateutil.parser.parse(entry.published).astimezone(UTC)
            for entry in f.entries
        )

        sess.add(feed)
        await sess.commit()

        await bot.say(
            event.channel,
            f"<#{event.channel}> 채널에서 `{url}`을 구독하기 시작했어요!",
        )

    async def list(self, bot, event: Message, sess: AsyncSession):
        feeds = (
            await sess.scalars(
                select(RSSFeedURL).where(RSSFeedURL.channel == event.channel),
            )
        ).all()

        if feeds:
            feed_list = "\n".join(f"{feed.id} - {feed.url}" for feed in feeds)

            await bot.say(
                event.channel,
                f"<#{event.channel}> 채널에서 구독중인"
                " RSS 목록은 다음과 같아요!"
                f"\n```\n{feed_list}\n```",
            )
        else:
            await bot.say(
                event.channel,
                f"<#{event.channel}> 채널에서 구독중인 RSS가 없어요!",
            )

    @argument("id")
    async def delete(self, bot, event: Message, sess: AsyncSession, id: int):
        feed = await sess.get(RSSFeedURL, id)

        if feed is None:
            await bot.say(
                event.channel,
                f"{id}번 RSS 구독 레코드는 존재하지 않아요!",
            )
            return

        await bot.say(
            event.channel,
            f"<#{feed.channel}>에서 구독하는 `{feed.url}` RSS 구독을 취소했어요!",
        )

        await sess.delete(feed)
        await sess.commit()


@box.cron("*/5 * * * *")
async def crawl(bot, sess: AsyncSession):
    feeds = (await sess.scalars(select(RSSFeedURL))).all()

    feed: RSSFeedURL
    for feed in feeds:
        data = b""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(feed.url) as res:
                    data = await res.read()
            except aiohttp.client_exceptions.ClientConnectorError:
                await bot.say(
                    feed.channel,
                    f"*Error*: `{feed.url}`에 접속할 수 없어요!",
                )
                continue

        if not data:
            await bot.say(
                feed.channel,
                f"*Error*: `{feed.url}`에 접속해도 자료를 가져올 수 없어요!",
            )
            continue

        try:
            f = fastfeedparser.parse(data)
        except ValueError:
            await bot.say(
                feed.channel,
                f"*Error*: `{feed.url}`는 올바른 RSS 문서가 아니에요!",
            )
            continue

        last_updated = feed.updated_at
        attachments = []

        for entry in reversed(f.entries):
            t = dateutil.parser.parse(entry.published).astimezone(UTC)
            if feed.updated_at < t:
                attachments.append(
                    Attachment(
                        fallback=(
                            "RSS Feed: "
                            f"{f.feed.title!s} - "
                            f"{entry.title!s} - "
                            f"{entry.links[0].href}"
                        ),
                        title=str(entry.title),
                        title_link=entry.links[0].href,
                        text=("\n".join(str(entry.summary).split("\n")[:3]))[
                            :100
                        ],
                        author_name=str(f.feed.title),
                    ),
                )
                last_updated = t

        feed.updated_at = last_updated

        if attachments:
            await bot.api.chat.postMessage(
                channel=feed.channel,
                attachments=attachments,
            )

            sess.add(feed)
            await sess.commit()


box.register(RSS())
