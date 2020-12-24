import datetime
from hashlib import md5
from typing import Optional
from urllib.parse import urlencode

import aiohttp

import attr

from fake_useragent import UserAgent

import tzlocal

from ...box import box
from ...command import argument
from ...event import Message
from ...utils import json

box.assert_config_required('GOOGLE_API_KEY', str)
box.assert_config_required('AQI_API_TOKEN', str)


LABELS = {
    'pm25': 'PM2.5',
    'pm10': 'PM10',
    'o3': '오존',
    'no2': '이산화 질소',
    'so2': '이산화 황',
    'co': '일산화 탄소',
}


@attr.dataclass(slots=True)
class Field:

    current: int
    min: int
    max: int


@attr.dataclass(slots=True)
class AQIRecord:

    name: str
    aqi: int
    time: int
    pm25: Optional[Field] = None  # PM2.5
    pm10: Optional[Field] = None  # PM10
    o3: Optional[Field] = None  # 오존(Ozone)
    no2: Optional[Field] = None  # 이산화 질소 (Nitrogen Dioxide)
    so2: Optional[Field] = None  # 이산화 황 (Sulphur Dioxide)
    co: Optional[Field] = None  # 일산화 탄소 (Carbon Monoxide)


async def get_geometric_info_by_address(
    address: str,
    api_key: str,
) -> tuple[str, float, float]:
    url = 'https://maps.googleapis.com/maps/api/geocode/json?' + urlencode(
        {'region': 'kr', 'address': address, 'key': api_key}
    )
    async with aiohttp.ClientSession(
        headers={'Accept-Language': 'ko-KR'}
    ) as session:
        async with session.get(url) as res:
            data = await res.json(loads=json.loads)

    full_address = data['results'][0]['formatted_address']
    lat = data['results'][0]['geometry']['location']['lat']
    lng = data['results'][0]['geometry']['location']['lng']

    return full_address, lat, lng


async def get_aqi_idx(lat: float, lng: float, token: str) -> str:
    url = f'https://api.waqi.info/feed/geo:{lat};{lng}/?token={token}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as res:
            d1 = await res.json(loads=json.loads)
    try:
        return str(d1['data']['idx'])
    except (KeyError, TypeError):
        return 'wrong'


async def get_aqi_result(idx: str) -> Optional[AQIRecord]:
    url = f'https://api.waqi.info/api/feed/@{idx}/obs.en.json'
    headers = {
        'User-Agent': UserAgent().chrome,
        'accept-language': 'ko',
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers) as res:
            d2 = await res.json(loads=json.loads)

    if d2['rxs']['obs'][0]['status'] != 'ok':
        return None

    data = d2['rxs']['obs'][0]['msg']

    return AQIRecord(
        name=data['i18n']['name']['ko'],
        aqi=data['aqi'],
        time=data['time']['utc']['v'],
        **{
            x['p']: Field(*x['v'])
            for x in data['iaqi']
            if x['p'] in ['pm25', 'pm10', 'o3', 'no2', 'so2', 'co']
        },
    )


def get_aqi_description(aqi: int) -> str:
    if aqi > 300:
        return '위험(환자군 및 민감군에게 응급 조치가 발생되거나, ' '일반인에게 유해한 영향이 유발될 수 있는 수준)'
    elif aqi > 200:
        return (
            '매우 나쁨(환자군 및 민감군에게 급성 노출시 심각한 영향 유발, ' '일반인도 약한 영향이 유발될 수 있는 수준)'
        )
    elif aqi > 150:
        return (
            '나쁨(환자군 및 민감군[어린이, 노약자 등]에게 유해한 영향 유발, '
            '일반인도 건강상 불쾌감을 경험할 수 있는 수준)'
        )
    elif aqi > 100:
        return '민감군 영향(환자군 및 민감군에게 유해한 영향이 유발될 수 있는 수준)'
    elif aqi > 50:
        return '보통(환자군에게 만성 노출시 경미한 영향이 유발될 수 있는 수준)'
    else:
        return '좋음(대기오염 관련 질환자군에서도 영향이 유발되지 않을 수준)'


@box.command('aqi', ['공기', '먼지', '미세먼지'])
@argument('address', nargs=-1, concat=True)
async def aqi(bot, event: Message, address: str):
    """
    AQI 지수 열람

    Air Quality Index(AQI) 지수를 열람합니다.
    주소를 입력하면 가장 가까운 계측기의 정보를 열람합니다.

    `{PREFIX}공기 부천` (경기도 부천시의 AQI 지수 열람)

    """

    addr = md5(address.encode()).hexdigest()

    cached = await bot.cache.multi_get(
        f'AQI_ADDRESS_{addr}_full_address',
        f'AQI_ADDRESS_{addr}_lat',
        f'AQI_ADDRESS_{addr}_lng',
    )
    if cached[0] and cached[1] and cached[2]:
        full_address, lat, lng = cached
    else:
        try:
            full_address, lat, lng = await get_geometric_info_by_address(
                address,
                bot.config.GOOGLE_API_KEY,
            )
            await bot.cache.set(
                f'AQI_ADDRESS_{addr}_full_address',
                full_address,
            )
            await bot.cache.set(
                f'AQI_ADDRESS_{addr}_lat',
                lat,
            )
            await bot.cache.set(
                f'AQI_ADDRESS_{addr}_lng',
                lng,
            )
        except IndexError:
            await bot.say(event.channel, '해당 주소는 찾을 수 없어요!')
            return

    idx = await bot.cache.get(f'AQI_IDX_{lat}_{lng}')
    if not idx:
        idx = await get_aqi_idx(lat, lng, bot.config.AQI_API_TOKEN)
        await bot.cache.set(f'AQI_IDX_{lat}_{lng}', idx)

    if idx == 'wrong':
        await bot.say(event.channel, '해당 지역의 AQI 정보를 받아올 수 없어요!')
        return

    result = await get_aqi_result(idx)

    if result is None:
        await bot.say(event.channel, '현재 AQI 서버의 상태가 좋지 않아요! 나중에 다시 시도해주세요!')
        return

    time = datetime.datetime.fromtimestamp(result.time)
    offset = tzlocal.get_localzone().utcoffset(time)
    if offset:
        time -= offset

    ftime = time.strftime('%Y년 %m월 %d일 %H시')
    text = (
        f'{full_address} 기준으로 가장 근접한 관측소의 {ftime} 계측 자료에요.\n\n'
        f'* 종합 AQI: {result.aqi} - {get_aqi_description(result.aqi)}\n'
    )

    for key, name in LABELS.items():
        f: Field = getattr(result, key)
        if f:
            text += f'* {name}: {f.current} (최소 {f.min} / 최대 {f.max})\n'

    text = text.strip()
    await bot.say(
        event.channel,
        text,
        thread_ts=event.ts,
    )
