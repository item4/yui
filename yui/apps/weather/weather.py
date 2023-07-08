from datetime import datetime
from typing import Literal

import aiohttp
from aiohttp.client_exceptions import ClientConnectorCertificateError
from attrs import define

from ...utils import json
from ...utils.datetime import fromisoformat
from .exceptions import WeatherRequestError
from .exceptions import WeatherResponseError

RainInfoType = Literal["Rain", "Clear", "Unavailable", "Unknown"]


@define
class WeatherRecord:
    # 관측소 이름, 주소
    name: str
    location: str

    # 현재 기온, 습도 및 기압
    temperature: float
    humidity: int
    atmospheric: float

    # 바람의 세기와 각도
    wind_velocity: float
    wind_direction: str

    # 강우 유무
    is_rain: RainInfoType
    rain_15: float | None
    rain_day: float | None

    # 관측 시간
    observed_at: datetime


async def get_weather_by_keyword(keyword: str) -> WeatherRecord:
    try:
        async with aiohttp.ClientSession() as session, session.get(
            "https://item4.net/api/weather/",
        ) as resp:
            if resp.status != 200:
                raise WeatherResponseError(f"Bad HTTP Response: {resp.status}")

            data = await resp.json(loads=json.loads)
    except ClientConnectorCertificateError as e:
        raise WeatherResponseError("인증서 만료") from e
    except ValueError as e:
        raise WeatherResponseError("JSON 파싱 실패") from e

    matched = None
    for record in data["records"]:
        if record["name"] == keyword:
            matched = record
            break
    else:
        raise WeatherRequestError("해당 이름의 관측소는 존재하지 않아요!")

    observed_at = fromisoformat(data["observed_at"].split("+", 1)[0])
    rain = matched["rain"]
    wind = matched["wind1"]

    return WeatherRecord(
        name=matched["name"],
        location=matched["address"],
        temperature=matched["temperature"],
        humidity=matched["humidity"],
        atmospheric=matched["atmospheric"],
        wind_velocity=wind["velocity"],
        wind_direction=wind["direction_text"],
        is_rain=rain["is_raining"],
        rain_15=rain["rain15"],
        rain_day=rain["rainday"],
        observed_at=observed_at,
    )
