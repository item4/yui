import unicodedata
from typing import Dict

from fuzzywuzzy import fuzz

__all__ = (
    'KOREAN_ALPHABETS_FIRST_MAP',
    'KOREAN_ALPHABETS_MIDDLE_MAP',
    'KOREAN_END',
    'KOREAN_START',
    'fuzzy_korean_partial_ratio',
    'fuzzy_korean_ratio',
    'normalize_korean_nfc_to_nfd',
)

KOREAN_START = ord('가')
KOREAN_END = ord('힣')
KOREAN_ALPHABETS_FIRST_MAP: Dict[str, str] = {
    'ㄱ': chr(4352+0),
    'ㄲ': chr(4352+1),
    'ㄴ': chr(4352+2),
    'ㄷ': chr(4352+3),
    'ㄸ': chr(4352+4),
    'ㄹ': chr(4352+5),
    'ㅁ': chr(4352+6),
    'ㅂ': chr(4352+7),
    'ㅃ': chr(4352+8),
    'ㅅ': chr(4352+9),
    'ㅆ': chr(4352+10),
    'ㅇ': chr(4352+11),
    'ㅈ': chr(4352+12),
    'ㅉ': chr(4352+13),
    'ㅊ': chr(4352+14),
    'ㅋ': chr(4352+15),
    'ㅌ': chr(4352+16),
    'ㅍ': chr(4352+17),
    'ㅎ': chr(4352+18),
}

KOREAN_ALPHABETS_MIDDLE_MAP: Dict[str, str] = {
    chr(x+12623): chr(x+4449) for x in range(21+1)
}


def normalize_korean_nfc_to_nfd(value: str) -> str:
    """Normalize Korean string to NFD."""

    for from_, to_ in KOREAN_ALPHABETS_FIRST_MAP.items():
        value = value.replace(from_, to_)

    for from_, to_ in KOREAN_ALPHABETS_MIDDLE_MAP.items():
        value = value.replace(from_, to_)

    return ''.join(
        unicodedata.normalize('NFD', x) if KOREAN_START <= ord(x) <= KOREAN_END
        else x for x in list(value)
    )


def fuzzy_korean_ratio(str1: str, str2: str) -> int:
    """Fuzzy Search with Korean"""

    return fuzz.ratio(
        normalize_korean_nfc_to_nfd(str1),
        normalize_korean_nfc_to_nfd(str2),
    )


def fuzzy_korean_partial_ratio(str1: str, str2: str) -> int:
    """Fuzzy Search with partial Korean strings"""

    nstr1 = normalize_korean_nfc_to_nfd(str1)
    nstr2 = normalize_korean_nfc_to_nfd(str2)

    len1 = len(nstr1)
    len2 = len(nstr2)

    ratio = fuzz.ratio(nstr1, nstr2)
    if len1 * 1.2 < len2 or len2 * 1.2 < len1:
        return int(
            (fuzz.partial_ratio(nstr1, nstr2) * 2 + ratio) / 3
        )
    else:
        return ratio
