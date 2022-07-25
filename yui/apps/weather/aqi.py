from hashlib import md5
from typing import Optional
from urllib.parse import urlencode

import aiohttp
from aiohttp import client_exceptions

from attrs import define

from ...box import box
from ...command import argument
from ...event import Message
from ...utils import json


box.assert_config_required("GOOGLE_API_KEY", str)
box.assert_config_required("OPENWEATHER_API_KEY", str)


class AirPollutionResponseError(RuntimeError):
    pass


EXCEPTIONS = (
    client_exceptions.ClientPayloadError,  # Bad HTTP Response
    ValueError,  # JSON Error
    client_exceptions.ClientConnectorCertificateError,  # TLS expired
    AirPollutionResponseError,  # Bad HTTP Response
)

LABELS = {
    "pm25": "PM2.5",
    "pm10": "PM10",
    "o3": "오존",
    "no": "일산화 질소",
    "no2": "이산화 질소",
    "so2": "이산화 황",
    "co": "일산화 탄소",
    "nh3": "암모니아",
}


@define
class AirPollutionRecord:

    aqi: int  # 1~5까지의 AQI Index
    co: Optional[float] = None  # 일산화 탄소 (Carbon Monoxide)
    no: Optional[float] = None  # 일산화 질소
    no2: Optional[float] = None  # 이산화 질소 (Nitrogen Dioxide)
    o3: Optional[float] = None  # 오존(Ozone)
    so2: Optional[float] = None  # 이산화 황 (Sulphur Dioxide)
    pm25: Optional[float] = None  # PM2.5
    pm10: Optional[float] = None  # PM10
    nh3: Optional[float] = None  # 암모니아


async def get_geometric_info_by_address(
    address: str,
    api_key: str,
) -> tuple[str, float, float]:
    url = "https://maps.googleapis.com/maps/api/geocode/json?" + urlencode(
        {"region": "kr", "address": address, "key": api_key}
    )
    async with aiohttp.ClientSession(
        headers={"Accept-Language": "ko-KR"}
    ) as session:
        async with session.get(url) as res:
            data = await res.json(loads=json.loads)

    full_address = data["results"][0]["formatted_address"]
    lat = data["results"][0]["geometry"]["location"]["lat"]
    lng = data["results"][0]["geometry"]["location"]["lng"]

    return full_address, lat, lng


async def get_air_pollution_by_coordinate(
    lat: float,
    lng: float,
    api_key: str,
) -> AirPollutionRecord:
    url = "https://api.openweathermap.org/data/2.5/air_pollution?" + urlencode(
        {
            "lat": lat,
            "lon": lng,
            "appid": api_key,
        }
    )

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as res:
            if res.status != 200:
                raise AirPollutionResponseError(
                    f"Bad HTTP Response: {res.status}"
                )

            data = await res.json(loads=json.loads)

    return AirPollutionRecord(
        aqi=data["list"][0]["main"]["aqi"],
        co=data["list"][0]["components"].get("co", None),
        no=data["list"][0]["components"].get("no", None),
        no2=data["list"][0]["components"].get("no2", None),
        o3=data["list"][0]["components"].get("o3", None),
        so2=data["list"][0]["components"].get("so2", None),
        pm25=data["list"][0]["components"].get("pm2_5", None),
        pm10=data["list"][0]["components"].get("pm10", None),
        nh3=data["list"][0]["components"].get("nh3", None),
    )


def get_aqi_description(aqi_level: int) -> str:
    if aqi_level == 5:
        return "매우 나쁨(환자군 및 민감군에게 노출시 심각한 영향 유발, " "일반인도 유해한 영향이 유발될 수 있는 수준)"
    elif aqi_level == 4:
        return (
            "나쁨(환자군 및 민감군[어린이, 노약자 등]에게 유해한 영향 유발, "
            "일반인도 건강상 불쾌감을 경험할 수 있는 수준)"
        )
    elif aqi_level == 3:
        return "민감군 영향(환자군 및 민감군에게 유해한 영향이 유발될 수 있는 수준)"
    elif aqi_level == 2:
        return "보통(환자군에게 만성 노출시 경미한 영향이 유발될 수 있는 수준)"
    else:
        return "좋음(대기오염 관련 질환자군에서도 영향이 유발되지 않을 수준)"


@box.command("aqi", ["공기", "먼지", "미세먼지"])
@argument("address", nargs=-1, concat=True)
async def aqi(bot, event: Message, address: str):
    """
    AQI 지수 열람

    Air Quality Index(AQI) 지수를 열람합니다.
    주소를 입력하면 가장 가까운 계측기의 정보를 열람합니다.

    `{PREFIX}공기 부천` (경기도 부천시의 AQI 지수 열람)

    """

    addr = md5(address.encode()).hexdigest()

    full_address_key = f"AQI_ADDRESS_{addr}_full_address"
    lat_key = f"AQI_ADDRESS_{addr}_lat"
    lng_key = f"AQI_ADDRESS_{addr}_lng"
    cached = await bot.cache.get_many(
        full_address_key,
        lat_key,
        lng_key,
    )
    full_address = cached.get(full_address_key)
    lat = cached.get(lat_key)
    lng = cached.get(lng_key)
    if not all([full_address, lat, lng]):
        try:
            full_address, lat, lng = await get_geometric_info_by_address(
                address,
                bot.config.GOOGLE_API_KEY,
            )
            await bot.cache.set(
                full_address_key,
                full_address,
            )
            await bot.cache.set(
                lat_key,
                lat,
            )
            await bot.cache.set(
                lng_key,
                lng,
            )
        except IndexError:
            await bot.say(event.channel, "해당 주소는 찾을 수 없어요!")
            return

    try:
        result = await get_air_pollution_by_coordinate(
            lat, lng, bot.config.OPENWEATHER_API_KEY
        )
    except EXCEPTIONS:
        await bot.say(event.channel, "날씨 API 접근 중 에러가 발생했어요!")
        return

    if result is None:
        await bot.say(
            event.channel,
            "검색 결과가 없어요! OpenWeather로 검색할 수 없는 곳 같아요!",
        )
        return

    text = (
        f"{full_address} 기준으로 가장 근접한 위치의 최근 자료에요.\n\n"
        f"* 종합 AQI: {get_aqi_description(result.aqi)}\n"
    )

    for key, name in LABELS.items():
        f: Optional[float] = getattr(result, key)
        if f:
            text += f"* {name}: {f}μg/m3\n"

    text = text.strip()
    await bot.say(
        event.channel,
        text,
        thread_ts=event.ts,
    )
