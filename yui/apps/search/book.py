from decimal import Decimal

import aiohttp
import tossi

from ...box import box
from ...command import argument
from ...event import Message
from ...types.slack.attachment import Attachment
from ...utils import json
from ...utils.html import strip_tags

box.assert_config_required("NAVER_CLIENT_ID", str)
box.assert_config_required("NAVER_CLIENT_SECRET", str)


@box.command("책", ["book"])
@argument("keyword", nargs=-1, concat=True)
async def book(bot, event: Message, keyword: str):
    """
    책 검색

    책 제목으로 네이버 책 DB에서 검색합니다.

    `{PREFIX}책 소드 아트 온라인` (`소드 아트 온라인`으로 책 검색)

    """

    url = "https://openapi.naver.com/v1/search/book.json"
    params = {
        "query": keyword,
    }
    headers = {
        "X-Naver-Client-Id": bot.config.NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": bot.config.NAVER_CLIENT_SECRET,
    }

    async with aiohttp.ClientSession() as session, session.get(
        url,
        params=params,
        headers=headers,
    ) as resp:
        data = await resp.json(loads=json.loads)

    attachments: list[Attachment] = []

    count = min(5, len(data["items"]))

    for i in range(count):
        book = data["items"][i]
        title = strip_tags(book["title"])
        text = "저자: {} / 출판사: {}".format(
            strip_tags(book["author"]),
            strip_tags(book["publisher"]),
        )
        if "price" in book:
            text += " / 가격: {}".format(Decimal(book["price"]))
        attachments.append(
            Attachment(
                fallback="{} - {}".format(title, book["link"]),
                title=title,
                title_link=book["link"],
                thumb_url=book["image"],
                text=text,
            ),
        )

    if attachments:
        await bot.api.chat.postMessage(
            channel=event.channel,
            text=(
                "키워드 *{}* {} 네이버 책 DB 검색 결과,"
                " 총 {:,}개의 결과가 나왔어요."
                " 그 중 상위 {}개를 보여드릴게요!"
            ).format(
                keyword,
                tossi.pick(keyword, "(으)로"),
                data["total"],
                count,
            ),
            attachments=attachments,
            thread_ts=event.ts,
        )
    else:
        await bot.say(event.channel, "검색 결과가 없어요!")
