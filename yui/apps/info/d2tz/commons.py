import asyncio

import aiohttp
from discord_webhook import AsyncDiscordWebhook

from ....bot import Bot
from ....utils import json
from ....utils.datetime import fromtimestamp
from ....utils.datetime import now


def tz_id_to_names(ids: list[str]) -> list[str]:
    results = []
    if "1" in ids:
        results.append("자매단 야영지")
    if "2" in ids:
        results.append("핏빛 황무지")
    if "3" in ids:
        results.append("차가운 평야")
    if "4" in ids:
        results.append("바위 벌판")
    if "5" in ids:
        results.append("어둠숲")
    if "6" in ids:
        results.append("검은 습지")
    if "7" in ids:
        results.append("타모 고원")
    if "8" in ids:
        results.append("악의 소굴")
    if "9" in ids and "13" in ids:
        results.append("동굴")
        ids.remove("9")
        ids.remove("13")
    if "10" in ids and "14" in ids:
        results.append("지하 통로")
        ids.remove("10")
        ids.remove("14")
    if "11" in ids and "15" in ids:
        results.append("구렁")
        ids.remove("11")
        ids.remove("15")
    if "12" in ids and "16" in ids:
        results.append("구덩이")
        ids.remove("12")
        ids.remove("16")
    if "9" in ids:
        results.append("동굴 1층")
    if "10" in ids:
        results.append("지하 통로 1층")
    if "11" in ids:
        results.append("구렁 1층")
    if "12" in ids:
        results.append("구덩이 1층")
    if "13" in ids:
        results.append("동굴 2층")
    if "14" in ids:
        results.append("지하 통로 2층")
    if "15" in ids:
        results.append("구렁 2층")
    if "16" in ids:
        results.append("구덩이 2층")
    if "17" in ids:
        results.append("매장지")
    if "18" in ids:
        results.append("묘실")
    if "19" in ids:
        results.append("영묘")
    if (
        "20" in ids
        and "21" in ids
        and "22" in ids
        and "23" in ids
        and "24" in ids
        and "25" in ids
    ):
        results.append("잊힌 탑")
        ids.remove("20")
        ids.remove("21")
        ids.remove("22")
        ids.remove("23")
        ids.remove("24")
        ids.remove("25")
    if "20" in ids:
        results.append("잊힌 탑")
    if "21" in ids:
        results.append("탑 지하 1층")
    if "22" in ids:
        results.append("탑 지하 2층")
    if "23" in ids:
        results.append("탑 지하 3층")
    if "24" in ids:
        results.append("탑 지하 4층")
    if "25" in ids:
        results.append("탑 지하 5층")
    if "26" in ids:
        results.append("수도원 정문")
    if "27" in ids:
        results.append("외부 회랑")
    if "28" in ids:
        results.append("병영")
    if "29" in ids and "30" in ids and "31" in ids:
        results.append("감옥")
        ids.remove("29")
        ids.remove("30")
        ids.remove("31")
    if "29" in ids:
        results.append("감옥 1층")
    if "30" in ids:
        results.append("감옥 2층")
    if "31" in ids:
        results.append("감옥 3층")
    if "32" in ids:
        results.append("내부 회랑")
    if "33" in ids:
        results.append("대성당")
    if "34" in ids and "35" in ids and "36" in ids and "37" in ids:
        results.append("지하 묘지")
        ids.remove("34")
        ids.remove("35")
        ids.remove("36")
        ids.remove("37")
    if "34" in ids:
        results.append("지하 묘지 1층")
    if "35" in ids:
        results.append("지하 묘지 2층")
    if "36" in ids:
        results.append("지하 묘지 3층")
    if "37" in ids:
        results.append("지하 묘지 4층")
    if "38" in ids:
        results.append("트리스트럼")
    if "39" in ids:
        results.append("비밀의 젖소방")
    if "40" in ids:
        results.append("루트 골레인")
    if "41" in ids:
        results.append("바위투성이 황무지")
    if "42" in ids:
        results.append("메마른 언덕")
    if "43" in ids:
        results.append("머나먼 오아시스")
    if "44" in ids:
        results.append("잊힌 도시")
    if "45" in ids:
        results.append("뱀의 골짜기")
    if "46" in ids:
        results.append("신비술사의 협곡")
    if "47" in ids and "48" in ids and "49" in ids:
        results.append("루트 골레인 하수도")
        ids.remove("47")
        ids.remove("48")
        ids.remove("49")
    if "47" in ids:
        results.append("루트 골레인 하수도 1층")
    if "48" in ids:
        results.append("루트 골레인 하수도 2층")
    if "49" in ids:
        results.append("루트 골레인 하수도 3층")
    if "50" in ids and "51" in ids:
        results.append("하렘")
        ids.remove("50")
        ids.remove("51")
    if "50" in ids:
        results.append("하렘 1층")
    if "51" in ids:
        results.append("하렘 2층")
    if "52" in ids and "53" in ids and "54" in ids:
        results.append("궁전 지하")
        ids.remove("52")
        ids.remove("53")
        ids.remove("54")
    if "52" in ids:
        results.append("궁전 지하 1층")
    if "53" in ids:
        results.append("궁전 지하 2층")
    if "54" in ids:
        results.append("궁전 지하 3층")
    if "55" in ids and "59" in ids:
        results.append("바위 무덤")
        ids.remove("55")
        ids.remove("59")
    if "55" in ids:
        results.append("바위 무덤 1층")
    if "56" in ids and "57" in ids and "60" in ids:
        results.append("망자의 전당")
        ids.remove("56")
        ids.remove("57")
        ids.remove("60")
    if "56" in ids:
        results.append("망자의 전당 1층")
    if "57" in ids:
        results.append("망자의 전당 2층")
    if "58" in ids and "61" in ids:
        results.append("발톱 독사 사원")
        ids.remove("58")
        ids.remove("61")
    if "58" in ids:
        results.append("발톱 독사 사원 1층")
    if "59" in ids:
        results.append("바위 무덤 2층")
    if "60" in ids:
        results.append("망자의 전당 3층")
    if "61" in ids:
        results.append("발톱 독사 사원 2층")
    if "62" in ids and "63" in ids and "64" in ids:
        results.append("구더기 굴")
        ids.remove("62")
        ids.remove("63")
        ids.remove("64")
    if "62" in ids:
        results.append("구더기 굴 1층")
    if "63" in ids:
        results.append("구더기 굴 2층")
    if "64" in ids:
        results.append("구더기 굴 3층")
    if "65" in ids:
        results.append("고대 토굴")
    if (
        "66" in ids
        or "67" in ids
        or "68" in ids
        or "69" in ids
        or "70" in ids
        or "71" in ids
        or "72" in ids
    ):
        results.append("탈 라샤의 무덤")
    if "73" in ids:
        results.append("탈 라샤의 방")
    if "74" in ids:
        results.append("비전의 성역")
    if "75" in ids:
        results.append("쿠라스트 부두")
    if "76" in ids:
        results.append("거미 숲")
    if "77" in ids:
        results.append("거대 습지")
    if "78" in ids:
        results.append("약탈자 밀림")
    if "79" in ids:
        results.append("하부 쿠라스트")
    if "80" in ids:
        results.append("쿠라스트 시장")
    if "81" in ids:
        results.append("상부 쿠라스트")
    if "82" in ids:
        results.append("쿠라스트 둑길")
    if "83" in ids:
        results.append("트라빈칼")
    if "84" in ids:
        results.append("독거미 둥지")
    if "85" in ids:
        results.append("거미 동굴")
    if "86" in ids and "87" in ids and "90" in ids:
        results.append("습한 구덩이")
        ids.remove("86")
        ids.remove("87")
        ids.remove("90")
    if "86" in ids:
        results.append("습한 구덩이 1층")
    if "87" in ids:
        results.append("습한 구덩이 2층")
    if "88" in ids and "89" in ids and "91" in ids:
        results.append("약탈자 소굴")
        ids.remove("88")
        ids.remove("89")
        ids.remove("91")
    if "88" in ids:
        results.append("약탈자 소굴 1층")
    if "89" in ids:
        results.append("약탈자 소굴 2층")
    if "90" in ids:
        results.append("습한 구덩이 3층")
    if "91" in ids:
        results.append("약탈자 소굴 3층")
    if "92" in ids and "93" in ids:
        results.append("쿠라스트 하수도")
        ids.remove("92")
        ids.remove("93")
    if "92" in ids:
        results.append("쿠라스트 하수도 1층")
    if "93" in ids:
        results.append("쿠라스트 하수도 2층")
    if "94" in ids:
        results.append("허물어진 사원")
    if "95" in ids:
        results.append("버려진 교회당")
    if "96" in ids:
        results.append("잊힌 성물실")
    if "97" in ids:
        results.append("잊힌 사원")
    if "98" in ids:
        results.append("허물어진 교회당")
    if "99" in ids:
        results.append("버려진 성물실")
    if "100" in ids and "101" in ids and "102" in ids:
        results.append("증오의 억류지")
        ids.remove("100")
        ids.remove("101")
        ids.remove("102")
    if "100" in ids:
        results.append("증오의 억류지 1층")
    if "101" in ids:
        results.append("증오의 억류지 2층")
    if "102" in ids:
        results.append("증오의 억류지 3층")
    if "103" in ids:
        results.append("혼돈의 요새")
    if "104" in ids:
        results.append("평원 외곽")
    if "105" in ids:
        results.append("절망의 평원")
    if "106" in ids:
        results.append("저주받은 자들의 도시")
    if "107" in ids:
        results.append("불길의 강")
    if "108" in ids:
        results.append("혼돈의 성역")
    if "109" in ids:
        results.append("하로가스")
    if "110" in ids:
        results.append("핏빛 언덕")
    if "111" in ids:
        results.append("혹한의 고산지")
    if "112" in ids:
        results.append("아리앗 고원")
    if "113" in ids:
        results.append("수정 동굴")
    if "114" in ids:
        results.append("얼어붙은 강")
    if "115" in ids:
        results.append("빙하의 길")
    if "116" in ids:
        results.append("부랑자의 동굴")
    if "117" in ids:
        results.append("얼어붙은 동토")
    if "118" in ids:
        results.append("고대인의 길")
    if "119" in ids:
        results.append("얼음 지하실")
    if "120" in ids:
        results.append("아리앗 정상")
    if "121" in ids:
        results.append("니흘라탁의 사원")
    if "122" in ids:
        results.append("고뇌의 전당")
    if "123" in ids:
        results.append("고통의 전당")
    if "124" in ids:
        results.append("보트의 전당")
    if "125" in ids:
        results.append("나락")
    if "126" in ids:
        results.append("아케론의 구덩이")
    if "127" in ids:
        results.append("지옥불 구덩이")
    if "128" in ids and "129" in ids and "130" in ids:
        results.append("세계석 성채")
        ids.remove("128")
        ids.remove("129")
        ids.remove("130")
    if "128" in ids:
        results.append("세계석 성채 1층")
    if "129" in ids:
        results.append("세계석 성채 2층")
    if "130" in ids:
        results.append("세계석 성채 3층")
    if "131" in ids:
        results.append("파괴의 왕좌")
    if "132" in ids:
        results.append("세계석 보관실")
    if "133" in ids:
        results.append("여제의 소굴")
    if "134" in ids:
        results.append("잊힌 사막")
    if "135" in ids:
        results.append("고통의 용광로")
    if "136" in ids:
        results.append("트리스트럼")

    return results


async def get_d2r_terror_zone_info(username: str, token: str):
    async with aiohttp.ClientSession(
        headers={
            "x-emu-username": username,
            "x-emu-token": token,
        },
    ) as session, session.get(
        "https://d2emu.com/api/v1/tz",
    ) as resp:
        blob = await resp.text()
        return json.loads(blob)


async def send_d2r_terror_zone_info_to_discord(webhook_url: str, message: str):
    webhook = AsyncDiscordWebhook(url=webhook_url, content=message)
    await webhook.execute()


async def say_d2r_terror_zone_info(bot: Bot, channel):
    data = await get_d2r_terror_zone_info(
        bot.config.D2EMU_USERNAME,
        bot.config.D2EMU_TOKEN,
    )

    now_dt = now()
    now_timestamp = int(now_dt.timestamp())
    now_fallback_time = now_dt.strftime("%Y-%m-%d %H:%M")

    current = ", ".join(tz_id_to_names(data["current"]))
    next_ = ", ".join(tz_id_to_names(data["next"]))
    dt = fromtimestamp(data["next_terror_time_utc"])
    fallback_time = dt.strftime("%Y-%m-%d %H:%M")

    text = f"""\
[<!date^{now_timestamp}^{{date_num}} {{time}}|{now_fallback_time}>] {current}
[<!date^{data['next_terror_time_utc']}^{{date_num}} {{time}}|{fallback_time}>] {next_}"""

    await bot.say(channel, text)


async def wait_next_d2r_terror_zone_info(bot: Bot, channel):
    data = await get_d2r_terror_zone_info(
        bot.config.D2EMU_USERNAME,
        bot.config.D2EMU_TOKEN,
    )
    this_time = now().replace(minute=0, second=0, microsecond=0).timestamp()

    loop_count = 0
    while data["next_terror_time_utc"] <= this_time:
        await asyncio.sleep(60 + loop_count * 30)
        data = await get_d2r_terror_zone_info(
            bot.config.D2EMU_USERNAME,
            bot.config.D2EMU_TOKEN,
        )
        loop_count += 1
        if loop_count > 20:
            return

    now_dt = now()
    now_timestamp = int(now_dt.timestamp())
    now_fallback_time = now_dt.strftime("%Y-%m-%d %H:%M")

    current = ", ".join(tz_id_to_names(data["current"]))
    next_ = ", ".join(tz_id_to_names(data["next"]))
    dt = fromtimestamp(data["next_terror_time_utc"])
    fallback_time = dt.strftime("%Y-%m-%d %H:%M")

    text = f"""\
[<!date^{now_timestamp}^{{date_num}} {{time}}|{now_fallback_time}>] {current}
[<!date^{data['next_terror_time_utc']}^{{date_num}} {{time}}|{fallback_time}>] {next_}"""
    discord_text = f"""\
<t:{now_timestamp}:f>: {current}
<t:{data['next_terror_time_utc']}:f>: {next_}"""

    await bot.say(channel, text)
    for webhook_url in bot.config.DISCORD_WEBHOOKS["d2tz"]:
        await send_d2r_terror_zone_info_to_discord(webhook_url, discord_text)
