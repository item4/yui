from typing import Any

import aiohttp

from ...box import box
from ...command import argument
from ...command import option
from ...event import Message
from ...utils import json

box.assert_config_required("NAVER_CLIENT_ID", str)
box.assert_config_required("NAVER_CLIENT_SECRET", str)

LANGUAGE_MAP: dict[str | None, str | None] = {
    None: None,
    "auto": None,
    "자동": None,
    "자동감지": None,
    "ko": "ko",
    "korea": "ko",
    "korean": "ko",
    "한": "ko",
    "한글": "ko",
    "한국": "ko",
    "한국어": "ko",
    "en": "en",
    "eng": "en",
    "english": "en",
    "영": "en",
    "영어": "en",
    "ja": "ja",
    "japan": "ja",
    "japanese": "ja",
    "일": "ja",
    "일어": "ja",
    "일본": "ja",
    "일본어": "ja",
    "zh": "zh-CN",
    "zh-cn": "zh-CN",
    "중": "zh-CN",
    "중국": "zh-CN",
    "중국어": "zh-CN",
    "중국어간체": "zh-CN",
    "중국어 간체": "zh-CN",
    "간체": "zh-CN",
    "중국어번체": "zh-TW",
    "중국어 번체": "zh-TW",
    "번체": "zh-TW",
    "es": "es",
    "스페인": "es",
    "스페인어": "es",
    "fr": "fr",
    "프랑스": "fr",
    "프랑스어": "fr",
    "러시아": "ru",
    "러시아어": "ru",
    "vi": "vi",
    "베트남": "vi",
    "베트남어": "vi",
    "th": "th",
    "태국": "th",
    "태국어": "th",
    "이탈리아": "it",
    "이탈리아어": "it",
    "id": "id",
    "인도네시아": "id",
    "인도네시아어": "id",
    "de": "de",
    "독일": "de",
    "독일어": "de",
}

LANGUAGE_NAME: dict[str, str] = {
    "ko": "한국어",
    "ja": "일본어",
    "zh-CN": "중국어 간체",
    "zh-TW": "중국어 번체",
    "hi": "힌디어",
    "en": "영어",
    "es": "스페인어",
    "fr": "프랑스어",
    "de": "독일어",
    "pt": "포르투갈어",
    "vi": "베트남어",
    "id": "인도네시아어",
    "fa": "페르시아어",
    "ar": "아랍어",
    "mm": "미얀마어",
    "th": "태국어",
    "ru": "러시아어",
    "it": "이탈리아어",
}

AVAILABLE_COMBINATIONS: set[tuple[str, str]] = {
    ("ko", "en"),
    ("ko", "ja"),
    ("ko", "zh-CN"),
    ("ko", "zh-TW"),
    ("ko", "vi"),
    ("ko", "id"),
    ("ko", "th"),
    ("ko", "de"),
    ("ko", "ru"),
    ("ko", "es"),
    ("ko", "it"),
    ("ko", "fr"),
    ("en", "ja"),
    ("en", "fr"),
    ("en", "zh-CN"),
    ("en", "zh-TW"),
    ("ja", "zh-CN"),
    ("ja", "zh-TW"),
    ("zh-CN", "zh-TW"),
}
AVAILABLE_COMBINATIONS |= {(t, s) for s, t in AVAILABLE_COMBINATIONS}


async def detect_language(headers: dict[str, str], text: str) -> str:
    url = "https://openapi.naver.com/v1/papago/detectLangs"
    async with aiohttp.ClientSession(headers=headers) as session, session.post(
        url, data={"query": text}
    ) as resp:
        result: dict[str, Any] = await resp.json(loads=json.loads)
        return result["langCode"]


async def _translate(
    headers: dict[str, str],
    source: str,
    target: str,
    text: str,
) -> str:
    url = "https://openapi.naver.com/v1/papago/n2mt"
    data = {
        "source": source,
        "target": target,
        "text": text,
    }
    async with aiohttp.ClientSession(headers=headers) as session, session.post(
        url, data=data
    ) as resp:
        result: dict[str, Any] = await resp.json(loads=json.loads)
        return result["message"]["result"]["translatedText"]


@box.command(
    "번역", aliases=["번역기", "translate", "tr", "t"], use_shlex=False
)
@option("--source", "-s")
@option("--target", "-t", default="ko")
@argument("text", nargs=-1, concat=True)
async def translate(bot, event: Message, source, target, text: str):
    """
    번역

    파파고 NMT 번역을 활용하여 주어진 문장을 다른 언어로 번역합니다.

    `{PREFIX}번역 ソードアート・オンライン`
    (주어진 문장의 언어를 자동으로 추론해서 한국어로 번역)
    `{PREFIX}번역 --source=ja ソードアート・オンライン`
    (`--source` 옵션으로 원문 언어 지정)
    `{PREFIX}번역 --target=en ソードアート・オンライン`
    (`--target` 옵션으로 결과 언어 지정)

    번역할 원문 문장은 최대 500자까지만 지원합니다.

    """

    if len(text) > 500:
        await bot.say(
            event.channel,
            "500자 이상의 긴 문장의 번역은 다른 번역기를 사용해주세요!",
        )
        return

    headers = {
        "X-Naver-Client-Id": bot.config.NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": bot.config.NAVER_CLIENT_SECRET,
    }
    source_code = LANGUAGE_MAP.get(source, "error")
    target_code = LANGUAGE_MAP.get(target, "error")

    if source_code is None:
        source_code = await detect_language(headers, text)

    if source_code == target_code == "ko":
        target_code = "en"

    if source_code == "error":
        await bot.say(event.channel, "원문 언어가 올바르지 않아요!")
    elif source_code == "unk":
        await bot.say(event.channel, "원문 언어를 추론하는데에 실패했어요!")
    elif target_code is None or target_code == "error":
        await bot.say(event.channel, "결과값 언어가 올바르지 않아요!")
    elif source_code == target_code:
        await bot.say(event.channel, "원문 언어와 결과값 언어가 같아요!")
    elif (source_code, target_code) not in AVAILABLE_COMBINATIONS:
        await bot.say(
            event.channel,
            (
                f"{LANGUAGE_NAME[source_code]}에서"
                f" {LANGUAGE_NAME[target_code]}로의 번역은 현재 지원되지"
                " 않아요!"
            ),
        )
    else:
        result = await _translate(headers, source_code, target_code, text)

        await bot.say(
            event.channel,
            (
                f"{LANGUAGE_NAME[source_code]} 원문: {text}\n"
                f"{LANGUAGE_NAME[target_code]} 번역: {result}"
            ),
        )
