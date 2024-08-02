import asyncio
import random

import aiohttp

from ....bot import Bot
from ....utils import json
from ....utils.datetime import fromtimestamp
from ....utils.datetime import now
from ....utils.http import USER_AGENT

HEADERS = {
    "User-Agent": USER_AGENT,
    "Referer": "https://www.d2tz.info/",
}

CODE_MAPPING = {
    "1-1": "핏빛 황무지, 악의 소굴",
    "1-2": "차가운 평야, 동굴",
    "1-3": "매장지, 묘실, 영묘",
    "1-4": "바위 벌판",
    "1-5": "트리스트럼",
    "1-6": "어둠숲, 지하 통로",
    "1-7": "검은 습지, 구렁",
    "1-8": "잊힌 탑",
    "1-9": "구덩이",
    "1-10": "감옥, 병영",
    "1-11": "대성당, 지하 묘지",
    "1-12": "음메음메 농장",
    "2-1": "루트 골레인 하수도",
    "2-2": "바위투성이 황무지, 바위 무덤",
    "2-3": "메마른 언덕, 망자의 전당",
    "2-4": "머나먼 오아시스",
    "2-5": "고대 토굴",
    "2-6": "잊힌 도시, 뱀의 골짜기, 발톱 독사 사원",
    "2-7": "비전의 성역",
    "2-8": "탈 라샤의 무덤, 탈 라샤의 방",
    "3-1": "거미 숲, 거미 동굴",
    "3-2": "약탈자 밀림, 약탈자 던전",
    "3-3": "거대 습지",
    "3-4": "쿠라스트 시장, 허물어진 사원, 버려진 교회당",
    "3-5": "트라빈칼",
    "3-6": "증오의 억류지",
    "4-1": "평원 외곽, 절망의 평원",
    "4-2": "저주받은 자들의 도시, 불길의 강",
    "4-3": "혼돈의 성역",
    "5-1": "핏빛 언덕, 혹한의 고산지, 나락",
    "5-2": "빙하의 길, 부랑자의 동굴",
    "5-3": "고대인의 길, 얼음 지하실",
    "5-4": "아리앗 고원, 아케론의 구덩이",
    "5-5": "수정 동굴, 얼어붙은 강",
    "5-6": "니흘라탁의 사원, 고뇌의 전당, 고통의 전당, 보트의 전당",
    "5-7": "세계석 성채, 파괴의 왕좌, 세계석 보관실",
}


async def get_d2r_terror_zone_info():
    async with aiohttp.ClientSession(headers=HEADERS) as session, session.get(
        "https://api.d2tz.info/terror_zone",
    ) as resp:
        blob = await resp.text()
        return json.loads(blob)


async def say_d2r_terror_zone_info(bot: Bot, channel):
    data = await get_d2r_terror_zone_info()

    results = []
    limit_dt = data["data"][1]["time"]
    for x in data["data"]:
        if x["time"] < limit_dt:
            break
        dt = fromtimestamp(x["time"])
        fallback_time = dt.strftime("%Y-%m-%d %H:%M")
        zone = CODE_MAPPING.get(x["zone"], x["zone"])
        results.append(
            f"[<!date^{x['time']}^{{date_num}} {{time}}|{fallback_time}>]"
            f" {zone}",
        )

    text = "\n".join(results)
    await bot.say(channel, text)


async def wait_next_d2r_terror_zone_info(bot: Bot, channel):
    data = await get_d2r_terror_zone_info()
    this_time = now().replace(minute=0, second=0, microsecond=0).timestamp()

    loop_count = 0
    while data["data"][1]["time"] < this_time:
        data = await get_d2r_terror_zone_info()
        await asyncio.sleep(
            random.randint(55 + loop_count * 2, 333 + loop_count * 2) / 100,
        )
        loop_count += 1
        if loop_count > 500:
            data = await get_d2r_terror_zone_info()
            break

    results = []
    limit_dt = data["data"][1]["time"]
    for x in data["data"]:
        if x["time"] < limit_dt:
            break
        dt = fromtimestamp(x["time"])
        fallback_time = dt.strftime("%Y-%m-%d %H:%M")
        zone = CODE_MAPPING.get(x["zone"], x["zone"])
        results.append(
            f"[<!date^{x['time']}^{{date_num}} {{time}}|{fallback_time}>]"
            f" {zone}",
        )

    text = "\n".join(results)
    await bot.say(channel, text)
