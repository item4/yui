import datetime
import functools
from concurrent.futures import ProcessPoolExecutor
from typing import List, Optional

import aiohttp

import lxml.html

from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from ..box import box
from ..command import argument, option
from ..event import Message
from ..models.aws import AWS
from ..session import client_session
from ..transform import choice
from ..util import truncate_table


def parse(html: str) -> Optional[List[AWS]]:
    h = lxml.html.fromstring(html)
    try:
        observed_at = datetime.datetime.strptime(
            h.cssselect('span.ehead')[0].text_content().replace(
                '[ 매분관측자료 ] ',
                ''
            ),
            '%Y.%m.%d.%H:%M'
        )
    except IndexError:
        return None

    records: List[AWS] = []
    for tr in h.cssselect('table table tr')[1:]:
        record = AWS()
        record.id = int(tr[0].text_content())
        record.name = tr[1].text_content().replace('*', '').strip()
        try:
            record.height = int(tr[2].text_content()[:-1])
        except ValueError:
            record.height = -1

        record.is_raining = {'○': False, '●': True}.get(
            tr[3].text_content()
        )
        try:
            record.rain15 = float(tr[4].text_content())
        except ValueError:
            pass
        try:
            record.rain60 = float(tr[5].text_content())
        except ValueError:
            pass
        try:
            record.rain6h = float(tr[6].text_content())
        except ValueError:
            pass
        try:
            record.rain12h = float(tr[7].text_content())
        except ValueError:
            pass
        try:
            record.rainday = float(tr[8].text_content())
        except ValueError:
            pass

        try:
            record.temperature = float(tr[9].text_content())
        except ValueError:
            pass

        wind_direction1 = tr[11].text_content().strip()
        record.wind_direction1 = wind_direction1 if wind_direction1 else None
        try:
            record.wind_speed1 = float(tr[12].text_content())
        except ValueError:
            pass
        wind_d10 = tr[14].text_content().strip()
        record.wind_direction10 = wind_d10 if wind_d10 else None
        try:
            record.wind_speed10 = float(tr[15].text_content())
        except ValueError:
            pass

        try:
            record.humidity = int(tr[16].text_content())
        except ValueError:
            pass

        try:
            record.pressure = float(tr[17].text_content())
        except ValueError:
            pass

        record.location = tr[18].text_content()

        record.observed_at = observed_at

        records.append(record)
    return records


@box.crontab('*/3 * * * *')
async def crawl(bot, loop, sess):
    """Crawl from Korea Meteorological Administration AWS."""

    engine = bot.config.DATABASE_ENGINE

    html = ''
    url = 'http://www.kma.go.kr/cgi-bin/aws/nph-aws_txt_min'
    try:
        async with client_session() as session:
            async with session.get(url) as res:
                html = await res.text()
    except aiohttp.client_exceptions.ClientConnectorError:
        return
    except aiohttp.client_exceptions.ServerDisconnectedError:
        return

    ex = ProcessPoolExecutor()
    records = await loop.run_in_executor(ex, functools.partial(
        parse,
        html
    ))

    if records is None:
        return

    truncate_table(engine, AWS)

    with sess.begin():
        sess.add_all(records)


@box.command('날씨', ['aws', 'weather'])
@argument('keyword', nargs=-1, concat=True)
async def aws(bot, event: Message, sess, keyword: str):
    """
    지역의 현재 기상상태를 조회합니다.

    `날씨 부천` (부천지역의 현재 기상상태를 출력)

    이 명령어는 `aws`, `날씨`, `weather` 중 편한 이름으로 사용할 수 있습니다.

    """

    record = None
    try:
        record = sess.query(AWS).filter_by(name=keyword).one()
    except NoResultFound:
        await bot.say(
            event.channel,
            '검색 결과가 없어요!'
        )
        return
    except MultipleResultsFound:
        await bot.say(
            event.channel,
            '검색 결과가 여러가지 있어요! 시스템 관리자에게 문의해주세요!'
        )
        return

    rain = {
        True: '예(15min: {}/일일: {})'.format(
            record.rain15,
            record.rainday,
        ),
        False: '아니오',
        None: '모름',
    }.get(record.is_raining)

    temperature = None
    if record.temperature is not None:
        temperature = '{}℃'.format(record.temperature)

    wind = None
    if record.wind_speed1 is not None and record.wind_direction1 is not None:
        wind = '{} {}㎧'.format(
            record.wind_direction1
                  .replace('N', '북')
                  .replace('S', '남')
                  .replace('W', '서')
                  .replace('E', '동'),
            record.wind_speed1,
        )

    humidity = None
    if record.humidity is not None:
        humidity = '{}%'.format(record.humidity)

    pressure = None
    if record.pressure is not None:
        pressure = '{}hPa'.format(record.pressure)

    res = '[{}@{}/{}] 강수: {}'.format(
        record.observed_at.strftime('%Y년 %m월 %d일 %H시 %M분'),
        record.name,
        record.location,
        rain,
    )

    if temperature:
        res += ' / {}'.format(temperature)

    if wind:
        res += ' / 바람: {}'.format(wind)

    if humidity:
        res += ' / 습도: {}'.format(humidity)

    if pressure:
        res += ' / 해면기압: {}'.format(pressure)

    await bot.say(
        event.channel,
        res
    )


@box.command('날씨지역검색', ['search-aws-zone'])
@option('--by', transform_func=choice(['name', 'location']), default='name',
        type_error='`{name}`의 값으로는 `name` 이나 `location`만 가능합니다.')
@argument('keyword', nargs=-1, concat=True)
async def search_aws_zone(bot, event: Message, sess, by: str, keyword: str):
    """
    날씨 명령어에 사용되는 지역명 검색기능

    주어진 키워드를 기준으로 비슷한 지역명을 모두 출력합니다.
    해당 명령어는 DB에 `like '%keyword%'` 연산을 사용합니다.

    `날씨지역검색 부산` (이름에 `부산` 이 들어가는 모든 지역 검색)
    `날씨지역검색 --by location 서울` (관측기 위치 주소에 `서울`이 들어가는 모든 지역 검색)

    이 명령어는 `날씨지역검색`, `search-aws-zone` 중 편한 이름으로 사용할 수 있습니다.

    """

    q = sess.query(AWS)
    if by == 'location':
        q = q.filter(AWS.location.contains(keyword))
    else:
        q = q.filter(AWS.name.contains(keyword))

    result = q.all()

    if result:
        await bot.say(
            event.channel,
            '검색 결과는 다음과 같습니다.\n\n{}'.format(
                '\n'.join('{}({})'.format(x.name, x.location) for x in result)
            ),
            thread_ts=event.ts,
        )
    else:
        await bot.say(
            event.channel,
            '검색 결과가 없어요!',
            thread_ts=event.ts,
        )
