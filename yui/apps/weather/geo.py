import aiohttp

from ...utils import json
from .exceptions import WeatherResponseError


async def get_geometric_info_by_address(
    address: str,
    api_key: str,
) -> tuple[str, float, float]:
    params = {
        "region": "kr",
        "address": address,
        "key": api_key,
    }

    async with aiohttp.ClientSession(
        headers={"Accept-Language": "ko-KR"},
    ) as session, session.get(
        "https://maps.googleapis.com/maps/api/geocode/json",
        params=params,
    ) as resp:
        if resp.status != 200:
            raise WeatherResponseError(f"Bad HTTP Response: {resp.status}")

        data = await resp.json(loads=json.loads)

    result = data["results"][0]
    full_address = result["formatted_address"]
    lat = result["geometry"]["location"]["lat"]
    lng = result["geometry"]["location"]["lng"]

    # 주소가 대한민국의 주소일 경우, 앞의 "대한민국 "을 자른다.
    # 캐시를 위해 함수의 반환 결과부터 미리 처리를 해놓는다.
    if full_address.startswith("대한민국 "):
        full_address = full_address[5:]

    return full_address, lat, lng
