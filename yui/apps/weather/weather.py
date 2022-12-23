import aiohttp
from attrs import define

from ...utils import json
from .exceptions import WeatherResponseError


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
    rain_1h: float | None
    rain_3h: float | None

    # 강설 유무
    snow: bool
    snow_1h: float | None
    snow_3h: float | None

    # 날씨 설명 (영어)
    status: str
    description: str

    # 시간 관련
    # 현재 UTC 단위의 timestamp
    timestamp: int
    # UTC 기준에서 얼마나 시간 차가 나는지 초 단위로 제공됨
    timezone: int


async def get_weather_by_coordinate(
    lat: float,
    lng: float,
    api_key: str,
) -> WeatherRecord:
    params = {
        "lat": lat,
        "lon": lng,
        "appid": api_key,
        "units": "metric",
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.openweathermap.org/data/2.5/weather", params=params
        ) as resp:
            if resp.status != 200:
                raise WeatherResponseError(f"Bad HTTP Response: {resp.status}")

            data = await resp.json(loads=json.loads)

    is_rain = data.get("rain") is not None
    is_snow = data.get("snow") is not None

    main = data["main"]

    return WeatherRecord(
        location=data["name"],
        current_temp=main["temp"],
        min_temp=main["temp_min"],
        max_temp=main["temp_max"],
        feel_temp=main["feels_like"],
        humidity=main["humidity"],
        pressure=main["pressure"],
        visibility=data["visibility"],
        wind_speed=data["wind"]["speed"],
        wind_degree=data["wind"]["deg"],
        cloudiness=data["clouds"]["all"],
        rain=is_rain,
        rain_1h=data["rain"].get("1h") if is_rain else None,
        rain_3h=data["rain"].get("3h") if is_rain else None,
        snow=is_snow,
        snow_1h=data["snow"].get("1h") if is_snow else None,
        snow_3h=data["snow"].get("3h") if is_snow else None,
        status=data["weather"][0]["main"],
        description=data["weather"][0]["description"],
        timestamp=data["dt"],
        timezone=data["timezone"],
    )
