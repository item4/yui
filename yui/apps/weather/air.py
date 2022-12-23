import aiohttp
from attrs import define

from ...utils import json
from .exceptions import WeatherResponseError
from .utils import shorten


def hpa_to_atm(hpa: float) -> float:
    return hpa / 1013.25


def cubic_to_ppm(
    value: float, weight: float, temperature: float, atm: float
) -> float:
    # https://www.breeze-technologies.de/blog/air-pollution-how-to-convert-between-mgm3-%C2%B5gm3-ppm-ppb/
    return value * (22.41 * (1 + temperature / 273.15) / atm) / weight / 1000


FIELDS: dict[str, tuple[str, float | None]] = {
    "pm25": ("PM2.5", None),
    "pm10": ("PM10", None),
    "o3": ("오존", 48.0),
    "no": ("일산화 질소", 30.01),
    "no2": ("이산화 질소", 46.01),
    "so2": ("이산화 황", 64.07),
    "co": ("일산화 탄소", 28.01),
    "nh3": ("암모니아", 17.03),
}


@define
class AirPollutionRecord:

    aqi: int  # 1~5까지의 AQI Index
    co: float | None = None  # 일산화 탄소 (Carbon Monoxide)
    no: float | None = None  # 일산화 질소
    no2: float | None = None  # 이산화 질소 (Nitrogen Dioxide)
    o3: float | None = None  # 오존(Ozone)
    so2: float | None = None  # 이산화 황 (Sulphur Dioxide)
    pm25: float | None = None  # PM2.5
    pm10: float | None = None  # PM10
    nh3: float | None = None  # 암모니아

    def to_display(
        self, temperature: float, pressure: float | None = None
    ) -> str:
        results = []
        for key, v in FIELDS.items():
            name, weight = v
            value = getattr(self, key)
            unit = "\u338d/\u33a5"  # ㎍/㎥
            if value is None:
                continue
            if weight is not None:
                atm = hpa_to_atm(pressure) if pressure is not None else 1
                value = cubic_to_ppm(value, weight, temperature, atm)
                unit = "ppm"  # unicode 문자는 가독성이 너무 낮음
            results.append(f"* {name}: {shorten(value)} {unit}")

        return "\n".join(results)


def get_emoji_by_aqi(aqi: int) -> str:
    return {
        1: ":smile:",
        2: ":smiley:",
        3: ":neutral_face:",
        4: ":mask:",
        5: ":skull_and_crossbones:",
    }.get(aqi, ":interrobang:")


def get_aqi_description(aqi_level: int) -> str:
    if aqi_level >= 5:
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


async def get_air_pollution_by_coordinate(
    lat: float,
    lng: float,
    api_key: str,
) -> AirPollutionRecord:
    params = {
        "lat": lat,
        "lon": lng,
        "appid": api_key,
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.openweathermap.org/data/2.5/air_pollution",
            params=params,
        ) as resp:
            if resp.status != 200:
                raise WeatherResponseError(f"Bad HTTP Response: {resp.status}")

            data = await resp.json(loads=json.loads)

    if not data["list"]:
        raise WeatherResponseError("No air pollution data")

    base = data["list"][0]
    components = base["components"]

    return AirPollutionRecord(
        aqi=base["main"]["aqi"],
        co=components.get("co"),
        no=components.get("no"),
        no2=components.get("no2"),
        o3=components.get("o3"),
        so2=components.get("so2"),
        pm25=components.get("pm2_5"),
        pm10=components.get("pm10"),
        nh3=components.get("nh3"),
    )
