import asyncio
import logging
from typing import Dict, List
from urllib.parse import parse_qs, urlparse

from lxml.html import fromstring

from sqlalchemy.orm.exc import NoResultFound

from .models import (
    Notice,
    SERVER_LABEL,
    Server,
)
from ....api import Attachment
from ....bot import Bot
from ....box import box
from ....command import C
from ....orm import EngineConfig, subprocess_session_manager
from ....session import client_session
from ....utils.api import retry

box.assert_channel_required('sao')

logger = logging.getLogger(__name__)

NOTICE_URLS: Dict[Server, str] = {
    Server.japan: ('https://api-defrag.wrightflyer.net/webview/announcement'
                   '?phone_type=2'),
    Server.worldwide: ('https://api-defrag-ap.wrightflyer.net/webview/'
                       'announcement?phone_type=2&lang=kr&user_id='),
}


def process(
    server: Server,
    html: str,
    engine_config: EngineConfig,
) -> List[Attachment]:

    base = '{u.scheme}://{u.netloc}'.format(u=urlparse(NOTICE_URLS[server]))
    h = fromstring(html)
    dls = h.cssselect('dl')

    attachments: List[Attachment] = []

    notice_ids: List[int] = []

    with subprocess_session_manager(engine_config) as sess:
        for dl in dls:
            onclick: str = dl.get('onclick')
            detail_url = base + onclick \
                .replace("javascript:location.href='", '') \
                .replace("'", '')

            id = int(parse_qs(urlparse(detail_url).query)['id'][0])

            title_els = dl.cssselect('h2')
            if title_els:
                title = title_els[0].text_content().strip()
            else:
                title_els = dl.cssselect('dd')
                if title_els:
                    dd = title_els[0]
                    if dd.get('class') == 'm_announcement_summary':
                        title = title_els[0].text_content().strip()
                    else:
                        title = 'No title'
                else:
                    title = 'No title'

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

            changes = []
            notice_ids.append(id)

            status = 'pass'
            try:
                notice: Notice = sess.query(Notice).filter_by(
                    notice_id=id,
                    server=server,
                ).one()
            except NoResultFound:
                status = 'new'
                notice = Notice()
                notice.notice_id = id
                notice.server = server
                notice.title = title
                notice.duration = duration
                notice.short_description = short_description

            if notice.is_deleted:
                status = 'change'
                changes.append('is_deleted')
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
                    new_title = notice.title

                if 'is_deleted' in changes:
                    new_title = f'[삭제 후 재생성] {new_title}'
                    notice.is_deleted = False

                if 'duration' in changes:
                    text += (
                        f'기간: {notice.duration} → {duration}\n'
                    )
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
            Notice.is_deleted == False,  # noqa
            Notice.server == server,
            ~Notice.notice_id.in_(notice_ids),
        ).all()
        for notice in deleted_notices:
            attachments.append(Attachment(
                fallback=f'{SERVER_LABEL[server]} 서버 삭제된 공지',
                pretext=f'{SERVER_LABEL[server]} 서버에 삭제된 공지가 있어요!',
                title=notice.title,
            ))
            notice.is_deleted = True
            with sess.begin():
                sess.add(notice)

    return attachments


@box.cron('*/1 * * * *')
async def watch_notice(bot: Bot, engine_config: EngineConfig):
    async def watch(server: Server):
        html = ''
        async with client_session() as session:
            async with session.get(NOTICE_URLS[server]) as resp:
                html = await resp.text()

        attachments = await bot.run_in_other_process(
            process,
            server,
            html,
            engine_config,
        )
        if attachments:
            await retry(bot.api.chat.postMessage(
                channel=C.sao.get(),
                attachments=attachments,
                as_user=True,
            ))

    await asyncio.wait([
        watch(Server.japan),
        watch(Server.worldwide),
    ])
