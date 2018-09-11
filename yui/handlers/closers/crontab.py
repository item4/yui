import datetime
import re
from typing import List
from urllib.parse import parse_qs, urlparse

from lxml.html import fromstring

from .base import get_next_overflood_info
from ...api import Attachment
from ...bot import Bot
from ...box import box
from ...command import C
from ...models.closers import Event, GMNote, Notice
from ...orm import Session
from ...session import client_session
from ...util import now

box.assert_channel_required('game')

MINUTE_PATTERN = re.compile('^(\d+)분 전$')
HOUR_PATTERN = re.compile('^(\d+)시간 전$')
HOUR_MINUTE_PATTERN = re.compile('^(\d+)시간 (\d+)분 전$')


def parse_date(input: str) -> datetime.date:
    if input == '방금전':
        return datetime.date.today()

    match = HOUR_MINUTE_PATTERN.match(input)
    if match:
        return (now() - datetime.timedelta(
            hours=int(match.group(1)),
            minutes=int(match.group(2)),
        )).date()

    match = HOUR_PATTERN.match(input)
    if match:
        return (now() - datetime.timedelta(
            hours=int(match.group(1)),
        )).date()

    match = MINUTE_PATTERN.match(input)
    if match:
        return (now() - datetime.timedelta(
            minutes=int(match.group(1)),
        )).date()

    return datetime.date(
        *map(int, input.split('.'))
    )


def make_notice_url(article_sn: int) -> str:
    return (
        'http://closers.nexon.com/news/notice/'
        f'View.aspx?noticearticlesn={article_sn}'
    )


def make_event_url(article_sn: int) -> str:
    return (
        'http://closers.nexon.com/news/events/'
        f'view.aspx?n4articlecategorysn=4&n4articlesn={article_sn}'
    )


def make_gm_note_url(article_sn: int) -> str:
    return (
        'http://closers.nexon.com/news/gmnote/'
        f'view.aspx?n4articlesn={article_sn}'
    )


def process_notice_list(html: str, sess: Session) -> List[Attachment]:
    h = fromstring(html)
    tds = h.cssselect('table.notice_list tr td')
    result: List[Attachment] = []
    for td in tds:
        a_tag = td[0][0]
        headline = a_tag.text_content()
        category = a_tag[0].text_content()
        title = headline.replace(category, '').strip()
        category = category.replace('[', '').replace(']', '').strip()
        article_sn = int(parse_qs(
            urlparse(a_tag.get('href')).query
        )['noticearticlesn'][0])
        posted_date = parse_date(td[1].text_content().strip())

        article: Notice = sess.query(Notice).get(article_sn)
        url = make_notice_url(article_sn)
        if article:
            if article.title != title:
                result.append(Attachment(
                    fallback='{}: {} -> {} / {}'.format(
                        category,
                        article.title,
                        title,
                        url,
                    ),
                    title='{}: {} -> {}'.format(
                        article.category,
                        article.title,
                        title,
                    ),
                    title_link=url,
                ))
                article.title = article.title
                article.updated_at = now()
                with sess.begin():
                    sess.add(article)
        else:
            article = Notice()
            article.article_sn = article_sn
            article.category = category
            article.title = title
            article.posted_date = posted_date
            article.updated_at = now()
            result.append(Attachment(
                fallback='{}: {} / {}'.format(
                    article.category,
                    article.title,
                    url,
                ),
                title='{}: {}'.format(
                    article.category,
                    article.title,
                ),
                title_link=url,
            ))
            with sess.begin():
                sess.add(article)

    return result


def process_event_list(html: str, sess: Session) -> List[Attachment]:
    h = fromstring(html)
    tds = h.cssselect('table.notice_list tr td')
    result: List[Attachment] = []
    for td in tds:
        a_tag = td[0][1]
        title = a_tag.text_content().strip()
        article_sn = int(parse_qs(
            urlparse(a_tag.get('href')).query
        )['n4articlesn'][0])
        posted_date = parse_date(td[1].text_content().strip())

        article: Event = sess.query(Event).get(article_sn)
        url = make_event_url(article_sn)
        if article is None:
            article = Event()
            article.article_sn = article_sn
            article.title = title
            article.posted_date = posted_date
            result.append(Attachment(
                fallback='이벤트: {} / {}'.format(
                    article.title,
                    url,
                ),
                title='이벤트: {}'.format(
                    article.title,
                ),
                title_link=url,
            ))
            with sess.begin():
                sess.add(article)

    return result


def process_gm_note_list(html: str, sess: Session) -> List[Attachment]:
    h = fromstring(html)
    tds = h.cssselect('table.gmnote_list tr td')
    result: List[Attachment] = []
    for td in tds:
        image_url = td[0][0].get('src')
        title = td[1][0].text_content().strip()
        text = td[2].text_content().strip()
        article_sn = int(parse_qs(
            urlparse(td[1][0].get('href')).query
        )['n4articlesn'][0])
        posted_date = parse_date(td[3][0].text_content().strip())
        article: GMNote = sess.query(GMNote).get(article_sn)
        url = make_gm_note_url(article_sn)
        if article is None:
            article = GMNote()
            article.article_sn = article_sn
            article.title = title
            article.text = text
            article.image_url = image_url
            article.posted_date = posted_date
            result.append(Attachment(
                fallback='GM노트: {} / {}'.format(
                    article.title,
                    url,
                ),
                title='GM노트: {}'.format(
                    article.title,
                ),
                image_url=article.image_url,
                title_link=url,
                text=article.text,
            ))
            with sess.begin():
                sess.add(article)

    return result


@box.crontab('*/1 * * * *')
async def crawl_notice(bot: Bot, sess):
    url = 'http://closers.nexon.com/news/notice/list.aspx'
    async with client_session() as session:
        async with session.get(url) as resp:
            html = await resp.text()

    attachments = await bot.run_in_other_process(
        process_notice_list,
        html,
        sess,
    )

    if attachments:
        await bot.api.chat.postMessage(
            channel=C.game.get(),
            text=':closers: 클로저스 공지사항 목록의 변동이 감지되었어요!.',
            attachments=attachments,
            as_user=True,
        )


@box.crontab('*/1 * * * *')
async def crawl_event(bot: Bot, sess):
    url = (
        'http://closers.nexon.com/news/events/list.aspx?n4ArticleCategorySN=4'
    )
    async with client_session() as session:
        async with session.get(url) as resp:
            html = await resp.text()

    attachments = await bot.run_in_other_process(
        process_event_list,
        html,
        sess,
    )

    if attachments:
        await bot.api.chat.postMessage(
            channel=C.game.get(),
            text=':closers: 클로저스 이벤트 당첨자 발표 목록의 변동이 감지되었어요!',
            attachments=attachments,
            as_user=True,
        )


@box.crontab('*/1 * * * *')
async def crawl_gm_note(bot: Bot, sess):
    url = 'http://closers.nexon.com/news/gmnote/list.aspx'
    async with client_session() as session:
        async with session.get(url) as resp:
            html = await resp.text()

    attachments = await bot.run_in_other_process(
        process_gm_note_list,
        html,
        sess,
    )

    if attachments:
        await bot.api.chat.postMessage(
            channel=C.game.get(),
            text=':closers: 클로저스 GM노트 목록의 변동이 감지되었어요!',
            attachments=attachments,
            as_user=True,
        )


@box.crontab('30 9,14,17,19,22 * * *')
async def overflood_before_30m(bot: Bot):
    info = get_next_overflood_info(now())
    if info != '오버플루드: 휴무':
        await bot.say(
            C.game.get(),
            f':closers: {info}'
        )


@box.crontab('0 10,15,18,20,23 * * *')
async def overflood_start(bot: Bot):
    info = get_next_overflood_info(now())
    if info != '오버플루드: 휴무':
        await bot.say(
            C.game.get(),
            f':closers: {info}'
        )


@box.crontab('0 0,1 * * *')
async def midnight_overflood_before_30m(bot: Bot):
    info = get_next_overflood_info(now())
    if info != '오버플루드: 휴무':
        await bot.say(
            C.game.get(),
            f':closers: {info}'
        )


@box.crontab('30 0,1 * * *')
async def midnight_overflood_start(bot: Bot):
    info = get_next_overflood_info(now())
    if info != '오버플루드: 휴무':
        await bot.say(
            C.game.get(),
            f':closers: {info}'
        )


@box.crontab('0 4 * * 0')
async def sunday_dungeon_info(bot: Bot):
    await bot.say(
        C.game.get(),
        ':closers: 오늘의 대정화작전 보스 - 감시자 틴달로스 / 괴조 하르파스 / 오염위상 요드'
    )


@box.crontab('0 4 * * 1')
async def monday_dungeon_info(bot: Bot):
    await bot.say(
        C.game.get(),
        ':closers: 오늘의 대정화작전 보스 - 괴조 하르파스 / 오염위상 요드'
    )


@box.crontab('0 4 * * 2')
async def tuesday_dungeon_info(bot: Bot):
    await bot.say(
        C.game.get(),
        ':closers: 오늘의 대정화작전 보스 - 감시자 틴달로스 / 거울잡이 니토크리스'
    )


@box.crontab('0 4 * * 3')
async def wednesday_dungeon_info(bot: Bot):
    await bot.say(
        C.game.get(),
        ':closers: 오늘의 대정화작전 보스 - 감시자 틴달로스 / 괴조 하르파스'
    )


@box.crontab('0 4 * * 4')
async def thursday_dungeon_info(bot: Bot):
    await bot.say(
        C.game.get(),
        ':closers: 오늘의 대정화작전 보스 - 괴조 하르파스 / 거울잡이 니토크리스'
    )


@box.crontab('0 4 * * 5')
async def friday_dungeon_info(bot: Bot):
    await bot.say(
        C.game.get(),
        ':closers: 오늘의 대정화작전 보스 - 감시자 틴달로스 / 오염위상 요드'
    )


@box.crontab('0 4 * * 6')
async def saturday_dungeon_info(bot: Bot):
    await bot.say(
        C.game.get(),
        ':closers: 오늘의 대정화작전 보스 - 감시자 틴달로스 / 괴조 하르파스'
        ' / 거울잡이 니토크리스'
    )
