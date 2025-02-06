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

    def as_str(self) -> str:
        rain = None
        match self.is_rain:
            case "Rain":
                rain = (
                    f"예(15분: {shorten(self.rain_15 or 0)}㎜ / 일일:"
                    f" {shorten(self.rain_day or 0)}㎜)"
                )
            case "Unavailable":
                rain = "확인 불가"
            case "Unknown":
                rain = "알 수 없음"

        temperature = (
            "기온: 알 수 없음"
            if self.temperature is None
            else f"기온: {shorten(self.temperature)}℃"
        )

        wind = f"{self.wind_direction} {shorten(self.wind_velocity)}㎧"

        humidity = (
            None if self.humidity is None else f"{shorten(self.humidity)}%"
        )

        atmospheric = (
            None
            if self.atmospheric is None
            else f"{shorten(self.atmospheric)}㍱"
        )

        weather_text = "[{} / {}] ".format(
            self.location,
            self.observed_at.strftime("%H시 %M분 기준"),
        )

        if self.is_rain != "Clear" and rain:
            if self.temperature is not None and self.temperature > 0:
                weather_text += f"강수 {rain} / "
            else:
                weather_text += f"강설 {rain} / "

        weather_text += temperature
        weather_text += f" / 바람: {wind}"
        if humidity:
            weather_text += f" / 습도: {humidity}"
        if atmospheric:
            weather_text += f" / 해면기압: {atmospheric}"

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
                raise WeatherResponseError(f"Bad HTTP Response: {resp.status}")

            data = await resp.json(loads=json.loads)
    except ClientConnectorCertificateError as e:
        raise WeatherResponseError("인증서 만료") from e
    except (ContentTypeError, ValueError) as e:
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
