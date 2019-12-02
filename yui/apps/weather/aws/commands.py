from datetime import timedelta
from decimal import Decimal
from typing import Dict, List, Tuple

from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from ...shared.cache import JSONCache
from ....box import box
from ....command import argument, option
from ....event import Message
from ....utils.datetime import fromisoformat, now
from ....utils.fuzz import match


def shorten(input) -> str:
    decimal_string = str(Decimal(format(input, 'f'))) if input else '0'
    return (
        decimal_string.rstrip('0').rstrip('.')
        if '.' in decimal_string else decimal_string
    )


def clothes_by_temperature(temperature: float) -> str:
    if temperature <= 5:
        return '패딩, 두꺼운 코트, 목도리, 기모제품'
    elif temperature <= 9:
        return '코트, 가죽재킷, 니트, 스카프, 두꺼운 바지'
    elif temperature <= 11:
        return (
            '재킷, 트랜치코트, 니트, 면바지, 청바지, 검은색 스타킹'
        )
    elif temperature <= 16:
        return (
            '얇은 재킷, 가디건, 간절기 야상, 맨투맨, 니트, 살구색 스타킹'
        )
    elif temperature <= 19:
        return '얇은 니트, 얇은 재킷, 가디건, 맨투맨, 면바지, 청바지'
    elif temperature <= 22:
        return '긴팔티, 얇은 가디건, 면바지, 청바지'
    elif temperature <= 26:
        return '반팔티, 얇은 셔츠, 반바지, 면바지'
    else:
        return '민소매티, 반바지, 반팔티, 치마'


@box.command('날씨', ['aws', 'weather'])
@option('--clothes', '-c', '--의상',  is_flag=True, default=False)
@argument('keyword', nargs=-1, concat=True)
async def aws(
    bot,
    event: Message,
    sess: Session,
    clothes: bool,
    keyword: str,
):
    """
    지역의 현재 기상상태를 조회합니다.

    `{PREFIX}날씨 부천` (부천 관측소의 현재 기상상태를 출력)

    """

    now_dt = now()
    if event.channel.id in aws.last_call:
        last_call = aws.last_call[event.channel.id]
        cooltime = timedelta(minutes=2)
        if last_call and now_dt - last_call < cooltime:
            fine = last_call + cooltime
            await bot.say(
                event.channel,
                '아직 쿨타임이에요! '
                f"{fine.strftime('%H시 %M분')} 이후로 다시 시도해주세요!"
            )
            return

    if len(keyword) < 2:
        await bot.say(
            event.channel,
            '검색어가 너무 짧아요! 2글자 이상의 검색어를 사용해주세요!',
        )
        return

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
            name_ratio = match(record['name'], keyword)
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

            if clothes:
                recommand = clothes_by_temperature(record['temperature'])
                res += f'\n\n추천 의상: {recommand}'

            await bot.api.chat.postMessage(
                channel=event.channel,
                text=res,
                username=f"{record['name']} 날씨",
                icon_emoji=emoji,
                thread_ts=event.ts if len(records) > 1 else None,
            )

        if event.channel.id:
            if len(records) > 5:
                aws.last_call[event.channel.id] = now_dt
            else:
                aws.last_call[event.channel.id] = None
    else:
        await bot.say(
            event.channel,
            '검색결과가 없어요! 한국 기상청 AWS가 설치되지 않은 장소 같아요!',
        )
