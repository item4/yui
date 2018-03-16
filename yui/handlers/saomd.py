import asyncio
import functools
import logging
from concurrent.futures import ProcessPoolExecutor
from typing import Dict, List, NamedTuple, Optional
from urllib.parse import parse_qs, urlparse

from lxml.html import fromstring

from sqlalchemy.orm.exc import NoResultFound

from ..api import Attachment
from ..box import box
from ..command import C
from ..models.saomd import (
    Notice,
    SERVER_LABEL,
    Server,
)
from ..session import client_session

logger = logging.getLogger(__name__)

NOTICE_URLS: Dict[Server, str] = {
    Server.japan: ('https://api-defrag.wrightflyer.net/webview/announcement'
                   '?phone_type=2'),
    Server.worldwide: ('https://api-defrag-ap.wrightflyer.net/webview/'
                       'announcement?phone_type=2&lang=kr&user_id='),
}


class NoticeItem(NamedTuple):
    """Notice item from notice page"""

    detail_url: str
    id: int
    title: str
    duration: Optional[str]
    short_description: Optional[str]
    image_url: Optional[str]


def parse(html: str) -> List[NoticeItem]:
    base = 'https://api-defrag-ap.wrightflyer.net'

    h = fromstring(html)
    dls = h.cssselect('dl')

    result: List[NoticeItem] = []

    for dl in dls:
        onclick: str = dl.get('onclick')
        detail_url = base + onclick \
            .replace("javascript:location.href='", '') \
            .replace("'", '')
        id = int(parse_qs(urlparse(detail_url).query)['id'][0])
        title = dl.cssselect('h2')[0].text_content().strip()

        duration_els = dl.cssselect('h3')
        if duration_els:
            duration = duration_els[0].text_content().strip()
        else:
            duration = None

        p_els = dl.cssselect('p')
        if p_els:
            short_description = p_els[0].text_content().strip()
        else:
            short_description = None

        image_els = dl.cssselect('img')
        if image_els:
            image_url = image_els[0].get('src')
        else:
            image_url = None

        result.append(NoticeItem(
            detail_url=detail_url,
            id=id,
            title=title,
            duration=duration,
            short_description=short_description,
            image_url=image_url,
        ))

    return result


@box.crontab('*/1 * * * *')
async def watch_notice(bot, loop, sess):
    async def watch(server: Server):
        html = ''
        async with client_session() as session:
            async with session.get(NOTICE_URLS[server]) as resp:
                html = await resp.text()

        ex = ProcessPoolExecutor()
        notice_items = await loop.run_in_executor(ex, functools.partial(
            parse,
            html,
        ))

        attachments: List[Attachment] = []

        notice_ids: List[int] = []

        for item in notice_items:
            changes = []
            notice_ids.append(item.id)

            status = 'pass'
            try:
                notice: Notice = sess.query(Notice).filter_by(
                    notice_id=item.id,
                    server=server,
                ).one()
            except NoResultFound:
                status = 'new'
                notice = Notice()
                notice.notice_id = item.id
                notice.server = server
                notice.title = item.title
                notice.duration = item.duration
                notice.short_description = item.short_description

            if item.title != notice.title:
                status = 'change'
                changes.append('title')
            if item.duration != notice.duration:
                status = 'change'
                changes.append('duration')
            if item.short_description != notice.short_description:
                status = 'change'
                changes.append('short_description')

            if status == 'new':
                text = ''
                if item.duration:
                    text += f'기간: {item.duration}\n'
                if item.short_description:
                    text += f'{item.short_description}\n'
                attachments.append(Attachment(
                    fallback=f'{SERVER_LABEL[server]} 서버 새 공지 - '
                             f'{item.title} - {item.detail_url}',
                    pretext=f'{SERVER_LABEL[server]} 서버에 새 공지가 있어요!',
                    title=item.title,
                    title_link=item.detail_url,
                    image_url=item.image_url,
                    text=text,
                ))
                with sess.begin():
                    sess.add(notice)
            elif status == 'change':
                text = ''
                if 'title' in changes:
                    new_title = f'{notice.title} → {item.title}'
                    notice.title = item.title
                else:
                    new_title = notice.title

                if 'duration' in changes:
                    text += (
                        f'기간: {notice.duration} → {item.duration}\n'
                    )
                    notice.duration = item.duration
                else:
                    if notice.duration:
                        text += f'기간: {notice.duration}\n'

                if 'short_description' in changes:
                    text += f'{notice.short_description} → ' \
                            f'{item.short_description}\n'
                    notice.short_description = item.short_description
                else:
                    if notice.short_description:
                        text += f'{notice.short_description}\n'

                attachments.append(Attachment(
                    fallback=f'{SERVER_LABEL[server]} 서버 변경된 공지 - '
                             f'{new_title} - {item.detail_url}',
                    pretext=f'{SERVER_LABEL[server]} 서버에 변경된 공지가 있어요!',
                    title=new_title,
                    title_link=item.detail_url,
                    image_url=item.image_url,
                    text=text.strip(),
                ))
                with sess.begin():
                    sess.add(notice)

        deleted_notices = sess.query(Notice).filter(
            Notice.server == server,
            ~Notice.notice_id.in_(notice_ids),
        ).all()
        for notice in deleted_notices:
            attachments.append(Attachment(
                fallback=f'{SERVER_LABEL[server]} 서버 삭제된 공지',
                pretext=f'{SERVER_LABEL[server]} 서버에 삭제된 공지가 있어요!',
                title=notice.title,
            ))
            with sess.begin():
                sess.delete(notice)

        if attachments:
            await bot.api.chat.postMessage(
                channel=C.game.get(),
                attachments=attachments,
                as_user=True,
            )

    await asyncio.wait([
        watch(Server.japan),
        watch(Server.worldwide),
    ])
