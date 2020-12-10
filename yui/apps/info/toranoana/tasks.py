import asyncio
import datetime
from collections import defaultdict
from typing import Union

import aiohttp

from lxml import html

from more_itertools import chunked

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import and_
from sqlalchemy.sql.expression import exists
from sqlalchemy.sql.expression import or_

from .commons import HEADERS
from .commons import get_urls
from .models import Author
from .models import Character
from .models import Circle
from .models import Coupling
from .models import Genre
from .models import Item
from .models import ItemAuthor
from .models import ItemCharacter
from .models import ItemCircle
from .models import ItemCoupling
from .models import ItemTag
from .models import STOCK_LABEL
from .models import Stock
from .models import Tag
from .models import Target
from .models import Watch
from ....box import box
from ....types.slack.attachment import Attachment
from ....types.slack.attachment import Field
from ....utils.datetime import now


box.assert_channel_required('toranoana')

GenreURLlist = dict[Genre, list[str]]


def process(
    *,
    sess,
    h,
    genre: Genre,
    dt: datetime.datetime,
    is_male: bool,
):
    rows = h.cssselect('#search-result-container li.product-list-item')
    for row in rows:
        with sess.no_autoflush:
            tags: list[tuple[Tag, bool]] = []
            authors: list[tuple[Author, bool]] = []
            circles: list[tuple[Circle, bool]] = []
            couplings: list[tuple[Coupling, bool]] = []
            characters: list[tuple[Character, bool]] = []
            code = row.cssselect('input#commodityCode')[0].get('value').strip()
            is_new = False
            is_adult = False
            try:
                item = sess.query(Item).filter_by(code=code).one()
            except NoResultFound:
                is_new = True
                item = Item()
                item.code = code
                item.genre = genre

            thumbnail_container = row.cssselect('.product-list-img a')[0]
            item.image_url = str(
                thumbnail_container[-1].get('data-src').strip()
            )
            item.title = str(
                row.cssselect('.product-list-title')[0].text_content().strip()
            )
            item.price = int(
                row.cssselect(
                    '.product-list-price .fs_L',
                )[0]
                .text_content()
                .strip()
                .replace(',', '')
            )
            item.stock = {
                'stock_sufficient': Stock.ok,
                'stock_little': Stock.few,
            }.get(
                row.cssselect('.product-list-basic')[0].get('class'),
                Stock.soldout,
            )

            name_els = row.cssselect('.product-list-name')
            for el in name_els:
                url = el.get('href', '').strip()
                name = el.text_content().strip()

                if '/circle/' in url:
                    code = url.split('/circle/', 1)[1].replace('/all/', '')
                    try:
                        circle = (
                            sess.query(Circle)
                            .filter_by(code=code, name=name)
                            .one()
                        )
                        circles.append((circle, True))
                    except NoResultFound:
                        circle = Circle(code=code, name=name)
                        circles.append((circle, False))
                elif 'actorKindId' in url:
                    code = 'ACTR' + url.split('ACTR', 1)[1]

                    try:
                        author = (
                            sess.query(Author)
                            .filter_by(code=code, name=name)
                            .one()
                        )
                        authors.append((author, True))
                    except NoResultFound:
                        author = Author(code=code, name=name)
                        authors.append((author, False))

            label_els = row.cssselect('.product-list-labels li a')
            for el in label_els:
                url = el.get('href', '').strip()
                name = el.text_content().strip()
                if '?coupling_facet=' in url:  # coupling
                    code = name
                    try:
                        coupling = (
                            sess.query(Coupling)
                            .filter_by(code=code, name=name)
                            .one()
                        )
                        couplings.append((coupling, True))
                    except NoResultFound:
                        coupling = Coupling(code=code, name=name)
                        couplings.append((coupling, False))
                elif '?charaId=' in url:  # character
                    code = url.split('?charaId=', 1)[1]
                    try:
                        character = (
                            sess.query(Character)
                            .filter_by(code=code, name=name)
                            .one()
                        )
                        characters.append((character, True))
                    except NoResultFound:
                        character = Character(code=code, name=name)
                        characters.append((character, False))

            tags_els = row.cssselect('.product-list-tags')
            for el in tags_els:
                code = (
                    el.get('class').split(' ')[-1].replace('catalogMark', '')
                )
                name = el.text_content().strip()
                if code == '18':
                    is_adult = True
                try:
                    tag = sess.query(Tag).filter_by(code=code, name=name).one()
                    tags.append((tag, True))
                except NoResultFound:
                    tag = Tag(code=code, name=name)
                    tags.append((tag, False))

            if is_male:
                if is_adult:
                    item.male_target = Target.adult
                else:
                    item.male_target = Target.common
            else:
                if is_adult:
                    item.female_target = Target.adult
                else:
                    item.female_target = Target.common

            queue: list[
                Union[Author, Circle, Tag, Coupling, Character, Item]
            ] = []

            old_tags: list[int] = []
            old_authors: list[int] = []
            old_circles: list[int] = []
            old_couplings: list[int] = []
            old_characters: list[int] = []
            if not is_new:
                old_tags = [
                    x.id
                    for x in sess.query(Tag).filter(
                        Tag.id == ItemTag.tag_id,
                        ItemTag.item == item,
                    )
                ]
                old_authors = [
                    x.id
                    for x in sess.query(Author).filter(
                        Author.id == ItemAuthor.author_id,
                        ItemAuthor.item == item,
                    )
                ]
                old_circles = [
                    x.id
                    for x in sess.query(Circle).filter(
                        Circle.id == ItemCircle.circle_id,
                        ItemCircle.item == item,
                    )
                ]
                old_couplings = [
                    x.id
                    for x in sess.query(Coupling).filter(
                        Coupling.id == ItemCoupling.coupling_id,
                        ItemCoupling.item == item,
                    )
                ]
                old_characters = [
                    x.id
                    for x in sess.query(Character).filter(
                        Character.id == ItemCharacter.character_id,
                        ItemCharacter.item == item,
                    )
                ]

            for tag, wrote in tags:
                if not wrote:
                    queue.append(tag)
                if (
                    is_new
                    or not item.id
                    or not tag.id
                    or not sess.query(
                        exists().where(
                            and_(
                                ItemTag.item_id == item.id,
                                ItemTag.tag_id == tag.id,
                            )
                        )
                    ).scalar()
                ):
                    item.tags.append(tag)
                if not is_new and tag.id in old_tags:
                    old_tags.remove(tag.id)

            for author, wrote in authors:
                if not wrote:
                    queue.append(author)
                if (
                    is_new
                    or not item.id
                    or not author.id
                    or not sess.query(
                        exists().where(
                            and_(
                                ItemAuthor.item_id == item.id,
                                ItemAuthor.author_id == author.id,
                            )
                        )
                    ).scalar()
                ):
                    item.authors.append(author)
                if not is_new and author.id in old_authors:
                    old_authors.remove(author.id)

            for circle, wrote in circles:
                if not wrote:
                    queue.append(circle)
                if (
                    is_new
                    or not item.id
                    or not circle.id
                    or not sess.query(
                        exists().where(
                            and_(
                                ItemCircle.item_id == item.id,
                                ItemCircle.circle_id == circle.id,
                            )
                        )
                    ).scalar()
                ):
                    item.circles.append(circle)
                if not is_new and circle.id in old_circles:
                    old_circles.remove(circle.id)

            for coupling, wrote in couplings:
                if not wrote:
                    queue.append(coupling)
                if (
                    is_new
                    or not item.id
                    or not coupling.id
                    or not sess.query(
                        exists().where(
                            and_(
                                ItemCoupling.item_id == item.id,
                                ItemCoupling.coupling_id == coupling.id,
                            )
                        )
                    ).scalar()
                ):
                    item.couplings.append(coupling)
                if not is_new and coupling.id in old_couplings:
                    old_couplings.remove(coupling.id)

            for character, wrote in characters:
                if not wrote:
                    queue.append(character)
                if (
                    is_new
                    or not item.id
                    or not character.id
                    or not sess.query(
                        exists().where(
                            and_(
                                ItemCharacter.item_id == item.id,
                                ItemCharacter.character_id == character.id,
                            )
                        )
                    ).scalar()
                ):
                    item.characters.append(character)
                if not is_new and character.id in old_characters:
                    old_characters.remove(character.id)

            if is_new or sess.is_modified(item):
                item.updated_at = dt

            item.checked_at = dt
            queue.append(item)

            with sess.begin():
                for record in queue:
                    sess.add(record)

                if not is_new:
                    sess.query(ItemTag).filter(
                        ItemTag.item == item,
                        ItemTag.tag_id.in_(old_tags),
                    ).delete(synchronize_session=False)
                    sess.query(ItemAuthor).filter(
                        ItemAuthor.item == item,
                        ItemAuthor.author_id.in_(old_authors),
                    ).delete(synchronize_session=False)
                    sess.query(ItemCircle).filter(
                        ItemCircle.item == item,
                        ItemCircle.circle_id.in_(old_circles),
                    ).delete(synchronize_session=False)
                    sess.query(ItemCoupling).filter(
                        ItemCoupling.item == item,
                        ItemCoupling.coupling_id.in_(old_couplings),
                    ).delete(synchronize_session=False)
                    sess.query(ItemCharacter).filter(
                        ItemCharacter.item == item,
                        ItemCharacter.character_id.in_(old_characters),
                    ).delete(synchronize_session=False)


def get_dedupe_genre_url_map(sess) -> GenreURLlist:
    result: defaultdict[Genre, set[str]] = defaultdict(set)
    for watch in sess.query(Watch):
        genre = watch.genre
        code = genre.code
        result[genre] |= set(get_urls(code, watch.male, watch.female))

    return {genre: list(urls) for genre, urls in result.items()}


async def scan_all_pages(
    *,
    bot,
    sess,
    session,
    genre: Genre,
    url: str,
    is_male: bool,
    dt: datetime.datetime,
):
    page = 1
    end_page = 1
    while page <= end_page:
        paginated_url = f'{url}&currentPage={page}'
        if page > 1:
            await asyncio.sleep(1)

        async with session.get(paginated_url) as resp:
            blob = await resp.text()
        h = html.fromstring(blob)

        if page == 1:
            pager = h.cssselect('#pager')
            if pager:
                end_page = int(pager[0].get('data-maxpage', 1))

        await bot.run_in_other_thread(
            process,
            sess=sess,
            h=h,
            genre=genre,
            dt=dt,
            is_male=is_male,
        )

        page += 1


def get_watches(*, sess, item: Item):
    return (
        sess.query(Watch)
        .join(Item, Item.genre_id == Watch.genre_id)
        .filter(
            Item.id == item.id,
            or_(
                and_(
                    Item.male_target == Target.common,
                    Watch.male.in_([Target.wildcard, Target.common]),
                ),
                and_(
                    Item.male_target == Target.adult,
                    Watch.male.in_([Target.wildcard, Target.adult]),
                ),
                and_(
                    Item.female_target == Target.common,
                    Watch.female.in_([Target.wildcard, Target.common]),
                ),
                and_(
                    Item.female_target == Target.adult,
                    Watch.female.in_([Target.wildcard, Target.adult]),
                ),
            ),
        )
    )


@box.cron('0,30 * * * *')
async def crawl(bot, sess):
    dt = now()
    url_map = await bot.run_in_other_thread(get_dedupe_genre_url_map, sess)
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        loop1_first = True
        for genre, urls in url_map.items():
            if loop1_first:
                loop1_first = False
            else:
                await asyncio.sleep(5)

            loop2_first = True
            for url in urls:
                if loop2_first:
                    loop2_first = False
                else:
                    await asyncio.sleep(1)

                is_male = 'joshi' not in url
                await scan_all_pages(
                    bot=bot,
                    sess=sess,
                    session=session,
                    genre=genre,
                    url=url,
                    is_male=is_male,
                    dt=dt,
                )

    data: defaultdict[str, list[Attachment]] = defaultdict(list)
    for item in sess.query(Item).filter_by(updated_at=dt):
        author_name = ', '.join(author.name for author in item.authors)
        circle_name = ', '.join(circle.name for circle in item.circles)
        author_line = f'{author_name} ({circle_name})'

        targets = []
        color = '3399ff'

        if Target.adult == item.male_target:
            color = 'ff0000'
            targets.append('남성향 성인물')
        elif item.male_target == Target.common:
            targets.append('남성향 일반물')

        if item.female_target == Target.adult:
            color = 'ff0000'
            targets.append('여성향 성인물')
        elif item.female_target == Target.common:
            targets.append('여성향 일반물')

        attachment = Attachment(
            color=color,
            title=item.title,
            title_link=item.url,
            author_name=author_line,
            image_url=item.image_url,
            fields=[
                Field(
                    title='장르',
                    value=item.genre.name_ko or item.genre.name,
                    short=True,
                ),
                Field(
                    title='카테고리',
                    value='\n'.join(targets),
                    short=True,
                ),
                Field(
                    title='가격',
                    value=f'{item.price} JPY',
                    short=True,
                ),
                Field(title='재고', value=STOCK_LABEL[item.stock], short=True),
            ],
        )

        if item.couplings:
            attachment.fields.append(
                Field(
                    title='커플링',
                    value=', '.join(
                        coupling.name_ko or coupling.name
                        for coupling in item.couplings
                    ),
                    short=True,
                )
            )
        if item.characters:
            attachment.fields.append(
                Field(
                    title='등장인물',
                    value=', '.join(
                        character.name_ko or character.name
                        for character in item.characters
                    ),
                    short=True,
                )
            )

        watches = await bot.run_in_other_thread(
            get_watches,
            sess=sess,
            item=item,
        )

        for watch in watches:
            data[watch.print_target_id].append(attachment)

    for target, attachments in data.items():
        if target.startswith('U'):
            resp = await bot.api.conversations.open(users=[target])
            channel_id = resp.body['channel']['id']
        else:
            channel_id = target
        for a in chunked(attachments, 20):
            await bot.say(
                channel_id,
                '토라노아나 변경항목을 전달해드릴게요!',
                attachments=a,
            )
