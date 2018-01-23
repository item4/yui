import asyncio
import logging
from typing import Dict, List, NamedTuple, Optional
from urllib.parse import parse_qs, urlparse

import aiohttp

from lxml.html import fromstring

from sqlalchemy.orm.exc import NoResultFound

from ..api import Attachment
from ..box import box
from ..models.saomd import (
    Notice,
    SERVER_LABEL,
    Server,
)

logger = logging.getLogger(__name__)

NOTICE_URLS: Dict[Server, str] = {
    Server.japan: ('https://api-defrag.wrightflyer.net/webview/announcement'
                   '?phone_type=2'),
    Server.worldwide: ('https://api-defrag-ap.wrightflyer.net/webview/'
                       'announcement?phone_type=2&lang=kr&user_id='),
}


class Weapon(NamedTuple):
    """NamedTuple to store saomd weapon"""

    name: str
    grade: str
    ratio: int
    category: str
    attribute: str
    attack: int
    critical: int
    battle_skills: Optional[List[str]]


@box.crontab('*/1 * * * *')
async def watch_notice(bot, sess):
    base = 'https://api-defrag-ap.wrightflyer.net'

    async def watch(server: Server):
        html = ''
        async with aiohttp.ClientSession() as session:
            async with session.get(NOTICE_URLS[server]) as resp:
                html = await resp.text()

        h = fromstring(html)
        dls = h.cssselect('dl')
        attachments: List[Attachment] = []

        notice_ids: List[int] = []

        for dl in dls:
            changes = []
            onclick: str = dl.get('onclick')
            detail_url = base + onclick\
                .replace("javascript:location.href='", '')\
                .replace("'", '')
            notice_id = int(parse_qs(urlparse(detail_url).query)['id'][0])
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

            notice_ids.append(notice_id)

            status = 'pass'
            try:
                notice: Notice = sess.query(Notice).filter_by(
                    notice_id=notice_id,
                    server=server,
                ).one()
            except NoResultFound:
                status = 'new'
                notice = Notice()
                notice.notice_id = notice_id
                notice.server = server
                notice.title = title
                notice.duration = duration
                notice.short_description = short_description

            if title != notice.title:
                status = 'change'
                changes.append('title')
            if duration != notice.duration:
                status = 'change'
                changes.append('duration')
            if short_description != notice.short_description:
                status = 'change'
                changes.append('short_description')

            if status == 'new':
                text = ''
                if duration:
                    text += f'기간: {duration}\n'
                if short_description:
                    text += f'{short_description}\n'
                attachments.append(Attachment(
                    fallback=f'{SERVER_LABEL[server]} 서버 새 공지 - '
                             f'{title} - {detail_url}',
                    pretext=f'{SERVER_LABEL[server]} 서버에 새 공지가 있어요!',
                    title=title,
                    title_link=detail_url,
                    image_url=image_url,
                    text=text,
                ))
                with sess.begin():
                    sess.add(notice)
            elif status == 'change':
                text = ''
                if 'title' in changes:
                    new_title = f'{notice.title} → {title}'
                    notice.title = title
                else:
                    new_title = title

                if 'duration' in changes:
                    text += f'기간: {notice.duration} → {duration}\n'
                    notice.duration = duration
                else:
                    if notice.duration:
                        text += f'기간: {notice.duration}\n'

                if 'short_description' in changes:
                    text += f'{notice.short_description} → ' \
                            f'{short_description}\n'
                    notice.short_description = short_description
                else:
                    if notice.short_description:
                        text += f'{notice.short_description}\n'

                attachments.append(Attachment(
                    fallback=f'{SERVER_LABEL[server]} 서버 변경된 공지 - '
                             f'{new_title} - {detail_url}',
                    pretext=f'{SERVER_LABEL[server]} 서버에 변경된 공지가 있어요!',
                    title=new_title,
                    title_link=detail_url,
                    image_url=image_url,
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
                channel='game',
                attachments=attachments,
                as_user=True,
            )

    await asyncio.wait([
        watch(Server.japan),
        watch(Server.worldwide),
    ])
