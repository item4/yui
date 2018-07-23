import datetime
import functools
import re
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from typing import List, NamedTuple
from urllib.parse import parse_qs, urlparse

from lxml.html import fromstring

from .base import get_next_overflood_info
from ...api import Attachment
from ...box import box
from ...models.closers import Event, GMNote, Notice
from ...session import client_session
from ...util import now


MINUTE_PATTERN = re.compile('^(\d+)분 전$')
HOUR_PATTERN = re.compile('^(\d+)시간 전$')
HOUR_MINUTE_PATTERN = re.compile('^(\d+)시간 (\d+)분 전$')


class NoticeArticle(NamedTuple):

    article_sn: int
    category: str
    title: str
    posted_date: datetime.date


class EventArticle(NamedTuple):

    article_sn: int
    title: str
    posted_date: datetime.date


class GMNoteArticle(NamedTuple):

    article_sn: int
    title: str
    text: str
    image_url: str
    posted_date: datetime.date


def parse_date(input: str) -> datetime.date:
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


def parse_notice_list(html: str) -> List[NoticeArticle]:
    h = fromstring(html)
    tds = h.cssselect('table.notice_list tr td')
    result: List[NoticeArticle] = []
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
        result.append(NoticeArticle(
            article_sn=article_sn,
            category=category,
            title=title,
            posted_date=posted_date,
        ))
    return result


def make_notice_url(article_sn: int) -> str:
    return (
        'http://closers.nexon.com/news/notice/'
        f'View.aspx?noticearticlesn={article_sn}'
    )


def make_notice_attachments(sess, articles: List[NoticeArticle]) -> \
        List[Attachment]:
    result: List[Attachment] = []
    for article in articles:
        a: Notice = sess.query(Notice).get(article.article_sn)
        url = make_notice_url(article.article_sn)
        if a:
            if a.title != article.title:
                result.append(Attachment(
                    fallback='{}: {} -> {} / {}'.format(
                        article.category,
                        a.title,
                        article.title,
                        url,
                    ),
                    title='{}: {} -> {}'.format(
                        article.category,
                        a.title,
                        article.title,
                    ),
                    title_link=url,
                ))
                a.title = article.title
                a.updated_at = now()
                with sess.begin():
                    sess.add(a)
        else:
            a = Notice()
            a.article_sn = article.article_sn
            a.category = article.category
            a.title = article.title
            a.posted_date = article.posted_date
            a.updated_at = now()
            result.append(Attachment(
                fallback='{}: {} / {}'.format(
                    a.category,
                    a.title,
                    url,
                ),
                title='{}: {}'.format(
                    a.category,
                    a.title,
                ),
                title_link=url,
            ))
            with sess.begin():
                sess.add(a)

    return result


def parse_event_list(html: str) -> List[EventArticle]:
    h = fromstring(html)
    tds = h.cssselect('table.notice_list tr td')
    result: List[EventArticle] = []
    for td in tds:
        a_tag = td[0][1]
        title = a_tag.text_content().strip()
        article_sn = int(parse_qs(
            urlparse(a_tag.get('href')).query
        )['n4articlesn'][0])
        posted_date = parse_date(td[1].text_content().strip())
        result.append(EventArticle(
            article_sn=article_sn,
            title=title,
            posted_date=posted_date,
        ))
    return result


def make_event_url(article_sn: int) -> str:
    return (
        'http://closers.nexon.com/news/events/'
        f'view.aspx?n4articlecategorysn=4&n4articlesn={article_sn}'
    )


def make_event_attachments(sess, articles: List[EventArticle]) -> \
        List[Attachment]:
    result: List[Attachment] = []
    for article in articles:
        a: Event = sess.query(Event).get(article.article_sn)
        url = make_event_url(article.article_sn)
        if a is None:
            a = Event()
            a.article_sn = article.article_sn
            a.title = article.title
            a.posted_date = article.posted_date
            result.append(Attachment(
                fallback='이벤트: {} / {}'.format(
                    a.title,
                    url,
                ),
                title='이벤트: {}'.format(
                    a.title,
                ),
                title_link=url,
            ))
            with sess.begin():
                sess.add(a)

    return result


def parse_gm_note_list(html: str) -> List[GMNoteArticle]:
    h = fromstring(html)
    tds = h.cssselect('table.gmnote_list tr td')
    result: List[GMNoteArticle] = []
    for td in tds:
        image_url = td[0][0].get('src')
        title = td[1][0].text_content().strip()
        text = td[2].text_content().strip()
        article_sn = int(parse_qs(
            urlparse(td[1][0].get('href')).query
        )['n4articlesn'][0])
        posted_date = parse_date(td[3][0].text_content().strip())
        result.append(GMNoteArticle(
            article_sn=article_sn,
            title=title,
            text=text,
            image_url=image_url,
            posted_date=posted_date,
        ))
    return result


def make_gm_note_url(article_sn: int) -> str:
    return (
        'http://closers.nexon.com/news/gmnote/'
        f'view.aspx?n4articlesn={article_sn}'
    )


def make_gm_note_attachments(sess, articles: List[GMNoteArticle]) -> \
        List[Attachment]:
    result: List[Attachment] = []
    for article in articles:
        a: GMNote = sess.query(GMNote).get(article.article_sn)
        url = make_gm_note_url(article.article_sn)
        if a is None:
            a = GMNote()
            a.article_sn = article.article_sn
            a.title = article.title
            a.text = article.text
            a.image_url = article.image_url
            a.posted_date = article.posted_date
            result.append(Attachment(
                fallback='GM노트: {} / {}'.format(
                    a.title,
                    url,
                ),
                title='GM노트: {}'.format(
                    a.title,
                ),
                image_url=article.image_url,
                title_link=url,
                text=a.text,
            ))
            with sess.begin():
                sess.add(a)

    return result


@box.crontab('*/1 * * * *')
async def crawl_notice(bot, sess, loop):
    url = 'http://closers.nexon.com/news/notice/list.aspx'
    async with client_session() as session:
        async with session.get(url) as resp:
            html = await resp.text()

    with ProcessPoolExecutor() as ex:
        articles = await loop.run_in_executor(
            ex,
            functools.partial(parse_notice_list, html),
        )

    with ThreadPoolExecutor() as ex:
        attachments = await loop.run_in_executor(
            ex,
            functools.partial(make_notice_attachments, sess, articles),
        )

    if attachments:
        await bot.api.chat.postMessage(
            channel='#game',
            text=':closers: 클로저스 공지사항 목록의 변동이 감지되었어요!.',
            attachments=attachments,
            as_user=True,
        )


@box.crontab('*/1 * * * *')
async def crawl_event(bot, sess, loop):
    url = (
        'http://closers.nexon.com/news/events/list.aspx?n4ArticleCategorySN=4'
    )
    async with client_session() as session:
        async with session.get(url) as resp:
            html = await resp.text()

    with ProcessPoolExecutor() as ex:
        articles = await loop.run_in_executor(
            ex,
            functools.partial(parse_event_list, html),
        )

    with ThreadPoolExecutor() as ex:
        attachments = await loop.run_in_executor(
            ex,
            functools.partial(make_event_attachments, sess, articles),
        )

    if attachments:
        await bot.api.chat.postMessage(
            channel='#game',
            text=':closers: 클로저스 이벤트 당첨자 발표 목록의 변동이 감지되었어요!',
            attachments=attachments,
            as_user=True,
        )


@box.crontab('*/1 * * * *')
async def crawl_gm_note(bot, sess, loop):
    url = 'http://closers.nexon.com/news/gmnote/list.aspx'
    async with client_session() as session:
        async with session.get(url) as resp:
            html = await resp.text()

    with ProcessPoolExecutor() as ex:
        articles = await loop.run_in_executor(
            ex,
            functools.partial(parse_gm_note_list, html),
        )

    with ThreadPoolExecutor() as ex:
        attachments = await loop.run_in_executor(
            ex,
            functools.partial(make_gm_note_attachments, sess, articles),
        )

    if attachments:
        await bot.api.chat.postMessage(
            channel='#game',
            text=':closers: 클로저스 GM노트 목록의 변동이 감지되었어요!',
            attachments=attachments,
            as_user=True,
        )


@box.crontab('30 9,14,17,19,22 * * *')
async def overflood_before_30m(bot):
    info = get_next_overflood_info(now())
    if info != '오버플루드: 휴무':
        await bot.say(
            '#game',
            f':closers: {info}'
        )


@box.crontab('0 10,15,18,20,23 * * *')
async def overflood_start(bot):
    info = get_next_overflood_info(now())
    if info != '오버플루드: 휴무':
        await bot.say(
            '#game',
            f':closers: {info}'
        )


@box.crontab('0 0,1 * * *')
async def midnight_overflood_before_30m(bot):
    info = get_next_overflood_info(now())
    if info != '오버플루드: 휴무':
        await bot.say(
            '#game',
            f':closers: {info}'
        )


@box.crontab('30 0,1 * * *')
async def midnight_overflood_start(bot):
    info = get_next_overflood_info(now())
    if info != '오버플루드: 휴무':
        await bot.say(
            '#game',
            f':closers: {info}'
        )


@box.crontab('0 4 * * 0')
async def sunday_dungeon_info(bot):
    await bot.say(
        '#game',
        ':closers: 오늘의 대정화작전 보스 - 감시자 틴달로스 / 괴조 하르파스 / 오염위상 요드'
    )


@box.crontab('0 4 * * 1')
async def monday_dungeon_info(bot):
    await bot.say(
        '#game',
        ':closers: 오늘의 대정화작전 보스 - 괴조 하르파스 / 오염위상 요드'
    )


@box.crontab('0 4 * * 2')
async def tuesday_dungeon_info(bot):
    await bot.say(
        '#game',
        ':closers: 오늘의 대정화작전 보스 - 감시자 틴달로스 / 거울잡이 니토크리스'
    )


@box.crontab('0 4 * * 3')
async def wednesday_dungeon_info(bot):
    await bot.say(
        '#game',
        ':closers: 오늘의 대정화작전 보스 - 감시자 틴달로스 / 괴조 하르파스'
    )


@box.crontab('0 4 * * 4')
async def thursday_dungeon_info(bot):
    await bot.say(
        '#game',
        ':closers: 오늘의 대정화작전 보스 - 괴조 하르파스 / 거울잡이 니토크리스'
    )


@box.crontab('0 4 * * 5')
async def friday_dungeon_info(bot):
    await bot.say(
        '#game',
        ':closers: 오늘의 대정화작전 보스 - 감시자 틴달로스 / 오염위상 요드'
    )


@box.crontab('0 4 * * 6')
async def saturday_dungeon_info(bot):
    await bot.say(
        '#game',
        ':closers: 오늘의 대정화작전 보스 - 감시자 틴달로스 / 괴조 하르파스'
        ' / 거울잡이 니토크리스'
    )
