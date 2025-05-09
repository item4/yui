from datetime import datetime
from typing import Literal

import aiohttp
from aiohttp.client_exceptions import ClientConnectorCertificateError
from aiohttp.client_exceptions import ContentTypeError
from attrs import define

from ...utils import json
from ...utils.datetime import fromisoformat
from .exceptions import WeatherRequestError
from .exceptions import WeatherResponseError
from .sun import get_emoji_by_sun
from .temperature import clothes_by_temperature
from .utils import shorten

RainInfoType = Literal["Rain", "Clear", "Unavailable", "Unknown"]


@define
class WeatherRecord:
    # 관측소 이름, 주소
    name: str
    location: str

    # 현재 기온, 습도 및 기압
    temperature: float | None
    humidity: int | None
    atmospheric: float | None

    # 바람의 세기와 각도
    wind_velocity: float
    wind_direction: str

    # 강우 유무
    is_rain: RainInfoType
    rain_15: float | None
    rain_day: float | None

    # 관측 시간
    observed_at: datetime

    def format_rain(self) -> str:
        label = (
            "강설"
            if self.temperature is not None and self.temperature < 0
            else "강수"
        )
        if self.is_rain == "Rain":
            return f"{label}: 예(15분: {shorten(self.rain_15 or 0)}㎜ / 일일: {shorten(self.rain_day or 0)}㎜)"
        if self.is_rain == "Unavailable":
            return f"{label}: 확인 불가"
        if self.is_rain == "Unknown":
            return f"{label}: 알 수 없음"
        return ""

    def format_temperature(self) -> str:
        if self.temperature:
            return f"기온: {shorten(self.temperature)}℃"
        return "기온: 확인 불가"

    def format_wind(self) -> str:
        if self.wind_direction == "No":
            return "바람: 없음"
        if self.wind_direction == "Unavailable":
            return ""
        return f"바람: {self.wind_direction} {shorten(self.wind_velocity)}㎧"

    def format_humidity(self) -> str:
        if self.humidity is not None:
            return f"습도: {shorten(self.humidity)}%"
        return ""

    def format_atmospheric(self) -> str:
        if self.atmospheric is not None:
            return f"해면기압: {shorten(self.atmospheric)}㍱"
        return ""

    def as_str(self) -> str:
        desc = " / ".join(
            filter(
                bool,
                [
                    self.format_rain(),
                    self.format_temperature(),
                    self.format_wind(),
                    self.format_humidity(),
                    self.format_atmospheric(),
                ],
            ),
        )
        weather_text = f"[{self.location} / {self.observed_at.strftime('%H시 %M분 기준')}] {desc}"

        if self.temperature is not None:
            recommend = clothes_by_temperature(self.temperature)
            weather_text += f"\n\n추천 의상: {recommend}"

        return weather_text

    async def get_emoji_by_weather(self) -> str:
        if self.is_rain == "Rain":
            if self.temperature is not None and self.temperature < 0:
                return ":snowflake:"
            return ":umbrella_with_rain_drops:"
        return await get_emoji_by_sun(
            self.observed_at,
        )


async def get_weather_by_keyword(keyword: str) -> WeatherRecord:
    try:
        async with (
            aiohttp.ClientSession() as session,
            session.get(
                "https://item4.net/api/weather/",
            ) as resp,
        ):
            if resp.status != 200:
                error = f"Bad HTTP Response: {resp.status}"
                raise WeatherResponseError(error)

            data = await resp.json(loads=json.loads)
    except ClientConnectorCertificateError as e:
        error = "인증서 만료"
        raise WeatherResponseError(error) from e
    except (ContentTypeError, ValueError) as e:
        error = "JSON 파싱 실패"
        raise WeatherResponseError(error) from e

    matched = None
    for record in data["records"]:
        if record["name"] == keyword:
            matched = record
            break
    else:
        error = "해당 이름의 관측소는 존재하지 않아요!"
        raise WeatherRequestError(error)

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
