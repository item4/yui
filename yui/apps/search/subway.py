import asyncio
import datetime
import logging
import math
from typing import Dict, Tuple
from urllib.parse import urlencode

from sqlalchemy.orm.exc import NoResultFound

import tossi

import ujson

from ..shared.cache import JSONCache
from ...box import box
from ...command import argument, option
from ...event import ChatterboxSystemStart, Message
from ...session import client_session
from ...transform import choice
from ...util import fuzzy_korean_ratio, now

logger = logging.getLogger(__name__)

headers: Dict[str, str] = {
    'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:56.0)'
                   ' Gecko/20100101 Firefox/56.0')
}
TEMPLATE = '{}역에서 {} {}행 {}열차에 탑승해서 {} 정거장을 지나 {}역에서 내립니다.{}'
REGION_TABLE: Dict[str, Tuple[str, str]] = {
    '수도권': ('1000', '6.0'),
    '부산': ('7000', '4.5'),
    '대구': ('4000', '4.5'),
    '광주': ('5000', '3.8'),
    '대전': ('3000', '3.8'),
}


async def fetch_station_db(sess, service_region: str, api_version: str):
    name = f'subway-{service_region}-{api_version}'
    logger.info(f'fetch {name} start')
    try:
        db = sess.query(JSONCache).filter_by(name=name).one()
    except NoResultFound:
        db = JSONCache()
        db.name = name

    metadata_url = 'http://map.naver.com/external/SubwayProvide.xml?{}'.format(
        urlencode({
            'requestFile': 'metaData.json',
            'readPath': service_region,
            'version': api_version,

        })
    )

    async with client_session(headers=headers) as session:
        async with session.get(metadata_url) as res:
            db.body = await res.json(loads=ujson.loads)

    db.created_at = now()

    with sess.begin():
        sess.add(db)

    logger.info(f'fetch {name} end')


@box.on(ChatterboxSystemStart)
async def on_start(sess):
    logger.info('on_start subway')
    tasks = []
    for service_region, api_version in REGION_TABLE.values():
        tasks.append(fetch_station_db(sess, service_region, api_version))
    await asyncio.wait(tasks)
    return True


@box.crontab('0 3 * * *')
async def refresh_db(sess):
    logger.info('refresh subway')
    tasks = []
    for service_region, api_version in REGION_TABLE.values():
        tasks.append(fetch_station_db(sess, service_region, api_version))
    await asyncio.wait(tasks)


async def body(bot, event: Message, sess, region: str, start: str, end: str):
    service_region, api_version = REGION_TABLE[region]

    try:
        db = sess.query(JSONCache).filter_by(
            name=f'subway-{service_region}-{api_version}'
        ).one()
    except NoResultFound:
        await bot.say(
            event.channel,
            '아직 지하철 관련 명령어의 실행준비가 덜 되었어요. 잠시만 기다려주세요!'
        )
        return

    data = db.body

    timestamp_url = 'http://map.naver.com/pubtrans/getSubwayTimestamp.nhn'
    async with client_session(headers=headers) as session:
        async with session.get(timestamp_url) as res:
            timestamp = ujson.loads(await res.text())

    find_start = None
    find_start_ratio = -1
    find_end = None
    find_end_ratio = -1
    for x in data[0]['realInfo']:
        start_ratio = fuzzy_korean_ratio(x['name'], start)
        end_ratio = fuzzy_korean_ratio(x['name'], end)
        if find_start_ratio < start_ratio:
            find_start = x
            find_start_ratio = start_ratio
        if find_end_ratio < end_ratio:
            find_end = x
            find_end_ratio = end_ratio

    if find_start_ratio < 40:
        await bot.say(
            event.channel,
            '출발역으로 지정하신 역 이름을 찾지 못하겠어요'
        )
        return
    elif find_end_ratio < 40:
        await bot.say(
            event.channel,
            '도착역으로 지정하신 역 이름을 찾지 못하겠어요'
        )
        return
    elif find_start and find_end:
        if find_start['id'] == find_end['id']:
            await bot.say(
                event.channel,
                '출발역과 도착역이 동일한 역이에요!'
            )
            return

        ts = datetime.datetime.utcnow()
        url = 'http://map.naver.com/pubtrans/searchSubwayPath.nhn?{}'.format(
            urlencode({
                'serviceRegion': service_region,
                'fromStationID': find_start['id'],
                'toStationID': find_end['id'],
                'dayType': timestamp['result']['dateType'],
                'presetTime': '3',
                'departureDateTime': ts.strftime('%Y%m%d%H%M%S00'),
                'caller': 'naver_map',
                'output': 'json',
                'searchType': '1',
            })
        )

        async with client_session(headers=headers) as session:
            async with session.get(url) as res:
                result = ujson.loads(await res.text())

        text = ''

        subway_paths = result['result']['subwayPaths']

        if subway_paths:
            text += '{} {}에서 {} {} 가는 노선을 안내드릴게요!\n\n'.format(
                find_start['logicalLine']['name'],
                find_start['name'],
                find_end['logicalLine']['name'],
                tossi.postfix(find_end['name'], '(으)로'),
            )
            for subway_path in subway_paths:
                routes = subway_path['path']['routes']
                text += '\n'.join(
                    TEMPLATE.format(
                        x['stations'][0]['name'],
                        x['logicalLine']['name'],
                        x['logicalLine']['direction'],
                        '급행' if x['isExpress'] else '',
                        len(list(filter(
                            lambda s: s['isNonstop'] == 0, x['stations']
                        )))-1,
                        x['stations'][-1]['name'],
                        ' (빠른환승 {}-{})'.format(
                            x['transfer']['exitTrainNumber'],
                            x['transfer']['exitDoorNumber'],
                        ) if 'transfer' in x else '',
                        ) for x in routes
                )
                text += '\n\n'

            summary = subway_path['summary']
            fare = list(filter(
                lambda f: f['paymentMethod'] == 1,
                subway_path['fareInfos']
            ))[0]['fare']
            text += ('소요시간: {:,}분 / 거리: {:,.2f}㎞'
                     ' / 요금(카드 기준): {:,}원').format(
                math.ceil(summary['overallTravelTimeInSecondOnAverage']/60),
                summary['overallTravelDistanceInMeter']/1000,
                fare,
                )

            await bot.say(
                event.channel,
                text
            )


@box.command('지하철', ['전철', 'subway'])
@option('--region', '-r', '--지역', default='수도권',
        transform_func=choice(list(REGION_TABLE.keys())),
        transform_error='지원되는 지역이 아니에요')
@argument('start', count_error='출발역을 입력해주세요')
@argument('end', count_error='도착역을 입력해주세요')
async def subway(bot, event: Message, sess, region: str, start: str, end: str):
    """
    전철/지하철의 예상 소요시간 및 탑승 루트 안내

    `{PREFIX}지하철 부천 선릉` (수도권 전철 부천역에서 선릉역까지 가는 가장 빠른 방법 안내)
    `{PREFIX}지하철 --region 부산 가야대 노포` (부산 전철 가야대역 출발 노포역 도착으로 조회)

    """

    await body(bot, event, sess, region, start, end)


@box.command('부산지하철', ['부산전철'])
@argument('start', count_error='출발역을 입력해주세요')
@argument('end', count_error='도착역을 입력해주세요')
async def busan_subway(bot, event: Message, sess, start: str, end: str):
    """
    부산 전철/지하철의 예상 소요시간 및 탑승 루트 안내

    `{PREFIX}지하철 --region 부산` 의 단축 명령어입니다.
    자세한 도움말은 `{PREFIX}help 지하철` 을 참조해주세요.

    """

    await body(bot, event, sess, '부산', start, end)


@box.command('대구지하철', ['대구전철'])
@argument('start', count_error='출발역을 입력해주세요')
@argument('end', count_error='도착역을 입력해주세요')
async def daegu_subway(bot, event: Message, sess, start: str, end: str):
    """
    대구 전철/지하철의 예상 소요시간 및 탑승 루트 안내

    `{PREFIX}지하철 --region 대구` 의 단축 명령어입니다.
    자세한 도움말은 `{PREFIX}help 지하철` 을 참조해주세요.

    """

    await body(bot, event, sess, '대구', start, end)


@box.command('광주지하철', ['광주전철'])
@argument('start', count_error='출발역을 입력해주세요')
@argument('end', count_error='도착역을 입력해주세요')
async def gwangju_subway(bot, event: Message, sess, start: str, end: str):
    """
    광주 전철/지하철의 예상 소요시간 및 탑승 루트 안내

    `{PREFIX}지하철 --region 광주` 의 단축 명령어입니다.
    자세한 도움말은 `{PREFIX}help 지하철` 을 참조해주세요.

    """

    await body(bot, event, sess, '광주', start, end)


@box.command('대전지하철', ['대전전철'])
@argument('start', count_error='출발역을 입력해주세요')
@argument('end', count_error='도착역을 입력해주세요')
async def daejeon_subway(bot, event: Message, sess, start: str, end: str):
    """
    대전 전철/지하철의 예상 소요시간 및 탑승 루트 안내

    `{PREFIX}지하철 --region 대전` 의 단축 명령어입니다.
    자세한 도움말은 `{PREFIX}help 지하철` 을 참조해주세요.

    """

    await body(bot, event, sess, '대전', start, end)
