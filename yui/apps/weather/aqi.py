import datetime
from typing import NamedTuple, Optional, Tuple
from urllib.parse import urlencode

import tzlocal

import ujson

from ...box import box
from ...command import argument
from ...event import Message
from ...session import client_session

box.assert_config_required('GOOGLE_API_KEY', str)
box.assert_config_required('AQI_API_TOKEN', str)


class AQIRecord(NamedTuple):

    aqi: int
    pm25: Optional[int]  # PM2.5
    pm10: Optional[int]  # PM10
    o3: Optional[float]  # 오존(Ozone)
    no2: Optional[float]  # 이산화 질소 (Nitrogen Dioxide)
    so2: Optional[float]  # 이산화 황 (Sulphur Dioxide)
    co: Optional[float]  # 일산화 탄소 (Carbon Monoxide)
    time: int


async def get_geometric_info_by_address(
    address: str,
    api_key: str,
) -> Tuple[str, float, float]:
    url = 'https://maps.googleapis.com/maps/api/geocode/json?' + urlencode({
        'address': address,
        'key': api_key,
    })
    async with client_session(headers={
        'Accept-Language': 'ko-KR',
    }) as session:
        async with session.get(url) as res:
            data = await res.json(loads=ujson.loads)
    full_address = ' '.join(
        x['long_name'] for x in reversed(
            data['results'][0]['address_components']
        )
    )
    lat = data['results'][0]['geometry']['location']['lat']
    lng = data['results'][0]['geometry']['location']['lng']

    return full_address, lat, lng


async def get_aqi(lat: float, lng: float, token: str) -> Optional[AQIRecord]:
    url = f'https://api.waqi.info/feed/geo:{lat};{lng}/?token={token}'
    async with client_session() as session:
        async with session.get(url) as res:
            data = await res.json(loads=ujson.loads)
    try:
        return AQIRecord(
            aqi=data['data']['aqi'],
            pm10=data['data']['iaqi'].get('pm10', {'v': None})['v'],
            pm25=data['data']['iaqi'].get('pm25', {'v': None})['v'],
            o3=data['data']['iaqi'].get('o3', {'v': None})['v'],
            no2=data['data']['iaqi'].get('no2', {'v': None})['v'],
            so2=data['data']['iaqi'].get('so2', {'v': None})['v'],
            co=data['data']['iaqi'].get('co', {'v': None})['v'],
            time=data['data']['time']['v'],
        )
    except TypeError:
        return None


def get_aqi_description(aqi: int) -> str:
    if aqi > 300:
        return (
            "위험(환자군 및 민감군에게 응급 조치가 발생되거나, "
            "일반인에게 유해한 영향이 유발될 수 있는 수준)"
        )
    elif aqi > 200:
        return (
            "매우 나쁨(환자군 및 민감군에게 급성 노출시 심각한 영향 유발, "
            "일반인도 약한 영향이 유발될 수 있는 수준)"
        )
    elif aqi > 150:
        return (
            "나쁨(환자군 및 민감군[어린이, 노약자 등]에게 유해한 영향 유발, "
            "일반인도 건강상 불쾌감을 경험할 수 있는 수준)"
        )
    elif aqi > 100:
        return "민감군 영향(환자군 및 민감군에게 유해한 영향이 유발될 수 있는 수준)"
    elif aqi > 50:
        return "보통(환자군에게 만성 노출시 경미한 영향이 유발될 수 있는 수준)"
    else:
        return "좋음(대기오염 관련 질환자군에서도 영향이 유발되지 않을 수준)"


@box.command('aqi', ['공기'])
@argument('address', nargs=-1, concat=True)
async def aqi(bot, event: Message, address: str):
    """
    AQI 지수 열람

    Air Quality Index(AQI) 지수를 열람합니다.
    주소를 입력하면 가장 가까운 계측기의 정보를 열람합니다.

    `{PREFIX}공기 부천` (경기도 부천시의 AQI 지수 열람)

    """

    try:
        full_address, lat, lng = await get_geometric_info_by_address(
            address,
            bot.config.GOOGLE_API_KEY,
        )
    except IndexError:
        await bot.say(
            event.channel,
            '해당 주소는 찾을 수 없어요!'
        )
        return

    result = await get_aqi(lat, lng, bot.config.AQI_API_TOKEN)

    if result is None:
        await bot.say(
            event.channel,
            '현재 AQI 서버의 상태가 좋지 않아요! 나중에 다시 시도해주세요!'
        )
        return

    time = datetime.datetime.fromtimestamp(result.time)
    time -= tzlocal.get_localzone().utcoffset(time)

    ftime = time.strftime('%Y년 %m월 %d일 %H시')
    text = (
        f'{ftime} 계측 자료에요. {full_address}를 기준으로 AQI에 정보를 요청했어요!\n\n'
        f'* 종합 AQI: {result.aqi} - {get_aqi_description(result.aqi)}\n'
    )
    if result.pm25:
        text += f'* PM2.5: {result.pm25}\n'
    if result.pm10:
        text += f'* PM10: {result.pm10}\n'
    if result.o3:
        text += f'* 오존: {result.o3}\n'
    if result.no2:
        text += f'* 이산화 질소: {result.no2}\n'
    if result.so2:
        text += f'* 이산화 황: {result.so2}\n'
    if result.co:
        text += f'* 일산화 탄소: {result.co}\n'
    text = text.strip()
    await bot.say(
        event.channel,
        text,
        thread_ts=event.ts,
    )
