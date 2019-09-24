from decimal import Decimal
from typing import Dict, List, Tuple

from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from ...shared.cache import JSONCache
from ....box import box
from ....command import argument
from ....event import Message
from ....utils.datetime import fromisoformat
from ....utils.fuzz import fuzzy_korean_partial_ratio


def shorten(input) -> str:
    decimal_string = str(Decimal(format(input, 'f'))) if input else '0'
    return (
        decimal_string.rstrip('0').rstrip('.')
        if '.' in decimal_string else decimal_string
    )


@box.command('날씨', ['aws', 'weather'])
@argument('keyword', nargs=-1, concat=True)
async def aws(
    bot,
    event: Message,
    sess: Session,
    keyword: str,
):
    """
    지역의 현재 기상상태를 조회합니다.

    `{PREFIX}날씨 부천` (부천 관측소의 현재 기상상태를 출력)

    """

    try:
        cache = sess.query(JSONCache).filter_by(name='aws').one()
    except NoResultFound:
        await bot.say(
            event.channel,
            '날씨 정보 검색 준비가 진행중이에요. 잠시만 기다려주세요!',
        )
        return

    records: List[Tuple[int, Dict]] = []
    observed_at = fromisoformat(cache.body['observed_at'].split('+', 1)[0])

    for record in cache.body['records']:
        if record['name'] == keyword:
            records.append((10000, record))
        else:
            name_ratio = fuzzy_korean_partial_ratio(record['name'], keyword)
            address_score = 50 if keyword in record['address'] else 0
            score = name_ratio + address_score
            if score >= 90:
                records.append(
                    (score, record)
                )

    if records:
        for ratio, record in sorted(records, key=lambda x: -x[0]):
            rain = {
                'Rain': '예(15min: {}/일일: {})'.format(
                    shorten(record['rain']['rain15']),
                    shorten(record['rain']['rainday']),
                ),
                'Clear': '아니오',
                'Unavailable': '확인 불가',
                'Unknown': '모름',
            }.get(record['rain']['is_raining'])

            temperature = None
            if record['temperature'] is not None:
                temperature = '{}℃'.format(shorten(record['temperature']))

            wind = None
            if record['wind1']['direction_text'] not in ('No', 'Unavailable'):
                wind = '{} {}㎧'.format(
                    record['wind1']['direction_text']
                    .replace('N', '북')
                    .replace('S', '남')
                    .replace('W', '서')
                    .replace('E', '동'),
                    shorten(record['wind1']['velocity']),
                )

            humidity = None
            if record['humidity'] is not None:
                humidity = '{}%'.format(shorten(record['humidity']))

            atmospheric = None
            if record['atmospheric'] is not None:
                atmospheric = '{}hPa'.format(shorten(record['atmospheric']))

            res = '[{}@{}/{}] 강수: {}'.format(
                observed_at.strftime('%Y년 %m월 %d일 %H시 %M분'),
                record['name'],
                record['address'],
                rain,
            )

            if temperature:
                res += ' / {}'.format(temperature)

            if wind:
                res += ' / 바람: {}'.format(wind)

            if humidity:
                res += ' / 습도: {}'.format(humidity)

            if atmospheric:
                res += ' / 해면기압: {}'.format(atmospheric)

            if record['rain']['is_raining'] == 'Rain':
                if record['temperature'] < 0:
                    emoji = ':snowflake:'
                else:
                    emoji = ':umbrella_with_rain_drops:'
            else:
                if observed_at.hour in [21, 22, 23, 0, 1, 2, 3, 4, 5, 6]:
                    emoji = ':crescent_moon:'
                else:
                    emoji = ':sunny:'

            await bot.api.chat.postMessage(
                channel=event.channel,
                text=res,
                username=f"{record['name']} 날씨",
                icon_emoji=emoji,
                thread_ts=event.ts if len(records) > 1 else None,
            )
    else:
        await bot.say(
            event.channel,
            '검색결과가 없어요!',
        )
