from fuzzywuzzy import fuzz


from yui.utils.fuzz import (
    match,
    normalize_korean_nfc_to_nfd,
    partial_ratio,
    ratio,
    token_sort_ratio,
)


def test_normalize_nfd():
    """Test Korean to NFD tool."""

    assert normalize_korean_nfc_to_nfd('123asdf가나다라밯맣희QWERTY') == ''.join(
        chr(x)
        for x in [
            49,
            50,
            51,  # 123
            97,
            115,
            100,
            102,  # asdf
            4352,
            4449,
            4354,
            4449,
            4355,
            4449,
            4357,
            4449,  # 가나다라
            4359,
            4449,
            4546,
            4358,
            4449,
            4546,
            4370,
            4468,  # 밯맣희
            81,
            87,
            69,
            82,
            84,
            89,  # QWERTY
        ]
    )

    assert normalize_korean_nfc_to_nfd('ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ') == (
        ''.join(chr(x) for x in range(4352, 4370 + 1))
    )

    assert normalize_korean_nfc_to_nfd('ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ') == (
        ''.join(chr(x) for x in range(4449, 4469 + 1))
    )


def test_partial_ratio():
    title = '소드 아트 온라인 3기 엘리시제이션 인계편'
    assert partial_ratio('소드', title) == 100
    assert partial_ratio('소드 아트', title) == 100
    assert partial_ratio('소드 아트 온라인', title) == 100
    assert partial_ratio('소드 아트 온라인 3기', title) == 100
    assert partial_ratio('소드 아트 온라인 3기 엘리시', title) == 100
    assert partial_ratio('소드 아트 온라인 3기 엘리시제이션', title) == 100
    assert partial_ratio(title, title) == 100


def test_ratio():
    """Test Korean-specific fuzzy search."""

    assert fuzz.ratio('강', '공') == 0
    assert ratio('강', '공') == 67

    assert fuzz.ratio('안녕', '인형') == 0
    assert ratio('안녕', '인형') == 67

    assert fuzz.ratio('사당', 'ㅅㄷ') == 0
    assert ratio('사당', 'ㅅㄷ') == 57

    assert fuzz.ratio('사당', 'ㅏㅏ') == 0
    assert ratio('사당', 'ㅏㅏ') == 57

    assert fuzz.ratio('사당', 'ㅅㅏㄷㅏㅇ') == 0
    assert ratio('사당', 'ㅅㅏㄷㅏㅇ') == 80


def test_token_sort_ratio():
    assert token_sort_ratio('밥 국 반찬', '반찬 밥 국') == 100


def test_match():
    assert match('소드 아트 온라인', '소아온') == 76
    assert match('소드 아트 온라인', '소드') == 46
    assert match('소드 아트 온라인', '소드아트') == 83
    assert match('소드 아트 온라인', '소드 아트') == 86
    assert match('소드 아트 온라인', '아트') == 46
    assert match('소드 아트 온라인', '온라인') == 87
    assert match('소드 아트 온라인', '소드 아트 온라인') == 100
    assert match('소드 아트 온라인', '소드아트온라인') == 100
    assert match('소드 아트 온라인', '소드 오라토리아') == 71
