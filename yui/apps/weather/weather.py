from decimal import Decimal
from hashlib import md5
from typing import Optional
from urllib.parse import urlencode

import aiohttp
from aiohttp import client_exceptions

from attr import define

from ...box import box
from ...command import argument
from ...event import Message
from ...utils import json
from ...utils.datetime import now

box.assert_config_required("GOOGLE_API_KEY", str)
box.assert_config_required("OPENWEATHER_API_KEY", str)


class WeatherResponseError(RuntimeError):
    pass


EXCEPTIONS = (
    client_exceptions.ClientPayloadError,  # Bad HTTP Response
    ValueError,  # JSON Error
    client_exceptions.ClientConnectorCertificateError,  # TLS expired
    WeatherResponseError,  # Bad HTTP Response
)


@define
class WeatherRecord:
    # 위치에 대한 정보 (영어)
    location: str

    # 현재, 최고/최소 온도, 습도 및 기압, 가시거리
    current_temp: float
    min_temp: float
    max_temp: float
    feel_temp: float
    humidity: int
    pressure: float
    visibility: int

    # 바람의 세기와 각도
    wind_speed: float
    wind_degree: int

    # 구름 정도
    cloudiness: int

    # 강우 유무
    rain: bool
    rain_1h: Optional[float]
    rain_3h: Optional[float]

    # 강설 유무
    snow: bool
    snow_1h: Optional[float]
    snow_3h: Optional[float]

    # 날씨 설명 (영어)
    status: str
    description: str


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
        async with session.get(url) as resp:
            if resp.status != 200:
                raise WeatherResponseError(f"Bad HTTP Response: {resp.status}")

            data = await resp.json(loads=json.loads)

    full_address = data["results"][0]["formatted_address"]
    lat = data["results"][0]["geometry"]["location"]["lat"]
    lng = data["results"][0]["geometry"]["location"]["lng"]

    return full_address, lat, lng


async def get_weather_by_coordinate(
    lat: float,
    lng: float,
    api_key: str,
) -> WeatherRecord:
    url = "https://api.openweathermap.org/data/2.5/weather?" + urlencode(
        {
            "lat": lat,
            "lon": lng,
            "appid": api_key,
            "units": "metric",
        }
    )

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                raise WeatherResponseError(f"Bad HTTP Response: {resp.status}")

            data = await resp.json(loads=json.loads)

    is_rain = data.get("rain", None) is not None
    is_snow = data.get("snow", None) is not None

    return WeatherRecord(
        location=data["name"],
        current_temp=data["main"]["temp"],
        min_temp=data["main"]["temp_min"],
        max_temp=data["main"]["temp_max"],
        feel_temp=data["main"]["feels_like"],
        humidity=data["main"]["humidity"],
        pressure=data["main"]["pressure"],
        visibility=data["visibility"],
        wind_speed=data["wind"]["speed"],
        wind_degree=data["wind"]["deg"],
        cloudiness=data["clouds"]["all"],
        rain=is_rain,
        rain_1h=data["rain"].get("1h", None) if is_rain else None,
        rain_3h=data["rain"].get("3h", None) if is_rain else None,
        snow=is_snow,
        snow_1h=data["snow"].get("1h", None) if is_snow else None,
        snow_3h=data["snow"].get("3h", None) if is_snow else None,
        status=data["weather"][0]["main"],
        description=data["weather"][0]["description"],
    )


def degree_to_direction(degree: int) -> str:
    # 북에서 다시 북으로, 360으로 나누면서 index로 계산
    directions = [
        "N",
        "NNE",
        "NE",
        "ENE",
        "E",
        "ESE",
        "SE",
        "SSE",
        "S",
        "SSW",
        "SW",
        "WSW",
        "W",
        "WNW",
        "NW",
        "NNW",
        "N",
    ]
    return directions[round((degree % 360) / 22.5)]


def shorten(input_value) -> str:
    decimal_string = (
        str(Decimal(format(input_value, "f"))) if input_value else "0"
    )
    return (
        decimal_string.rstrip("0").rstrip(".")
        if "." in decimal_string
        else decimal_string
    )


def clothes_by_temperature(temperature: float) -> str:
    if temperature <= 5:
        return "패딩, 두꺼운 코트, 목도리, 기모제품"
    elif temperature <= 9:
        return "코트, 가죽재킷, 니트, 스카프, 두꺼운 바지"
    elif temperature <= 11:
        return "재킷, 트랜치코트, 니트, 면바지, 청바지, 검은색 스타킹"
    elif temperature <= 16:
        return "얇은 재킷, 가디건, 간절기 야상, 맨투맨, 니트, 살구색 스타킹"
    elif temperature <= 19:
        return "얇은 니트, 얇은 재킷, 가디건, 맨투맨, 면바지, 청바지"
    elif temperature <= 22:
        return "긴팔티, 얇은 가디건, 면바지, 청바지"
    elif temperature <= 26:
        return "반팔티, 얇은 셔츠, 반바지, 면바지"
    else:
        return "민소매티, 반바지, 반팔티, 치마"


@box.command("날씨", ["aws", "weather"])
@argument("address", nargs=-1, concat=True)
async def weather(
    bot,
    event: Message,
    address: str,
):
    """
    지역의 현재 기상상태를 조회합니다.

    `{PREFIX}날씨 부천` (부천으로 검색되는 주소의 현재 기상상태를 출력)
    """

    if len(address) < 2:
        await bot.say(
            event.channel,
            "검색어가 너무 짧아요! 2글자 이상의 검색어를 사용해주세요!",
        )
        return

    addr = md5(address.encode()).hexdigest()

    full_address_key = f"WEATHER_ADDRESS_{addr}_full_address"
    lat_key = f"WEATHER_ADDRESS_{addr}_lat"
    lng_key = f"WEATHER_ADDRESS_{addr}_lng"
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
        result = await get_weather_by_coordinate(
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

    rain = None
    if result.rain:
        rain = "예(1시간: {} / 3시간: {})".format(
            shorten(result.rain_1h),
            shorten(result.rain_3h),
        )

    snow = None
    if result.snow:
        snow = "예(1시간: {} / 3시간: {})".format(
            shorten(result.snow_1h),
            shorten(result.snow_3h),
        )

    temperature = "{}℃ / 체감: {}℃".format(
        shorten(result.current_temp), shorten(result.feel_temp)
    )

    wind = "{} {}㎧".format(
        degree_to_direction(result.wind_degree),
        shorten(result.wind_speed),
    )

    humidity = "{}%".format(shorten(result.humidity))

    atmospheric = "{}hPa".format(shorten(result.pressure))

    # full_address를 쓰는 이유는 result.location은 영어이기 때문입니다.
    res = "[{}] ".format(full_address)

    if result.rain:
        res += "강수 {} / ".format(rain)
        emoji = ":umbrella_with_rain_drops:"
    elif result.snow:
        res += "강설 {} / ".format(snow)
        emoji = ":snowflake:"
    else:
        if now().hour in [21, 22, 23, 0, 1, 2, 3, 4, 5, 6]:
            emoji = ":crescent_moon:"
        else:
            emoji = ":sunny:"

    res += temperature
    res += " / 바람: {}".format(wind)
    res += " / 습도: {}".format(humidity)
    res += " / 해면기압: {}".format(atmospheric)

    recommend = clothes_by_temperature(result.current_temp)
    res += f"\n\n추천 의상: {recommend}"

    await bot.api.chat.postMessage(
        channel=event.channel,
        text=res,
        username=f"{full_address} 날씨",
        icon_emoji=emoji,
        thread_ts=event.ts if result is not None else None,
    )
