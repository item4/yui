import unicodedata

from rapidfuzz import fuzz

KOREAN_START = ord("가")
KOREAN_END = ord("힣")
KOREAN_ALPHABETS_FIRST_MAP: dict[str, str] = {
    "ㄱ": chr(4352 + 0),
    "ㄲ": chr(4352 + 1),
    "ㄴ": chr(4352 + 2),
    "ㄷ": chr(4352 + 3),
    "ㄸ": chr(4352 + 4),
    "ㄹ": chr(4352 + 5),
    "ㅁ": chr(4352 + 6),
    "ㅂ": chr(4352 + 7),
    "ㅃ": chr(4352 + 8),
    "ㅅ": chr(4352 + 9),
    "ㅆ": chr(4352 + 10),
    "ㅇ": chr(4352 + 11),
    "ㅈ": chr(4352 + 12),
    "ㅉ": chr(4352 + 13),
    "ㅊ": chr(4352 + 14),
    "ㅋ": chr(4352 + 15),
    "ㅌ": chr(4352 + 16),
    "ㅍ": chr(4352 + 17),
    "ㅎ": chr(4352 + 18),
}

KOREAN_ALPHABETS_MIDDLE_MAP: dict[str, str] = {
    chr(x + 12623): chr(x + 4449) for x in range(21 + 1)
}


def normalize_korean_nfc_to_nfd(value: str) -> str:
    """Normalize Korean string to NFD."""

    for from_, to_ in KOREAN_ALPHABETS_FIRST_MAP.items():
        value = value.replace(from_, to_)

    for from_, to_ in KOREAN_ALPHABETS_MIDDLE_MAP.items():
        value = value.replace(from_, to_)

    return "".join(
        (
            unicodedata.normalize("NFD", x)
            if KOREAN_START <= ord(x) <= KOREAN_END
            else x
        )
        for x in list(value)
    )


def ratio(str1: str, str2: str) -> int:
    """Get fuzzy ratio with korean text"""

    return int(
        fuzz.ratio(
            normalize_korean_nfc_to_nfd(str1),
            normalize_korean_nfc_to_nfd(str2),
        ),
    )


def partial_ratio(str1: str, str2: str) -> int:
    """Get partial fuzzy ratio with korean text"""

    return int(
        fuzz.partial_ratio(
            normalize_korean_nfc_to_nfd(str1),
            normalize_korean_nfc_to_nfd(str2),
        ),
    )


def token_sort_ratio(str1: str, str2: str) -> int:
    """Get token sorted fuzzy ratio with korean text"""

    return int(
        fuzz.token_sort_ratio(
            normalize_korean_nfc_to_nfd(str1),
            normalize_korean_nfc_to_nfd(str2),
        ),
    )


def match(s1: str, s2: str) -> int:
    """Get custom ratio for yui functions"""
    if s1 == s2:
        return 100

    pr = partial_ratio(s1, s2)
    r = ratio(s1, s2)
    tsr = token_sort_ratio(s1, s2)
    maximum_ratio = max(pr, r, tsr)
    return min(100, int((pr + r + tsr + maximum_ratio * 2) / 5))
