import datetime

from fuzzywuzzy import fuzz


from yui.util import (
    bold,
    bool2str,
    code,
    fuzzy_korean_ratio,
    italics,
    normalize_korean_nfc_to_nfd,
    preformatted,
    quote,
    strike,
    tz_none_to_kst,
    tz_none_to_utc
)


def test_datetime_utils():
    """Test utils for datetime."""

    now = datetime.datetime.utcnow()

    utcnow = tz_none_to_utc(now)

    assert utcnow.tzinfo.tzname(dt=None) == 'UTC'

    kstnow = tz_none_to_kst(now)

    assert kstnow.tzinfo.tzname(dt=None) == 'Asia/Seoul'


def test_bool2str():
    """True -> 'true', False -> 'false'"""

    assert bool2str(True) == 'true'
    assert bool2str(False) == 'false'


def text_slack_syntax():
    """Test slack syntax helpers."""

    assert bold('item4') == '*item4*'
    assert code('item4') == '`item4`'
    assert italics('item4') == '_item4_'
    assert preformatted('item4') == '```item4```'
    assert strike('item4') == '~item4~'
    assert quote('item4') == '>item4'


def test_normalize_nfd():
    """Test Korean to NFD tool."""

    assert normalize_korean_nfc_to_nfd('123ㄱㄴㄷㄹ가나다라밯맣희ㅏㅑㅓㅕ') == ''.join(
        chr(x) for x in
        [49, 50, 51, 12593, 12596, 12599, 12601, 4352, 4449, 4354, 4449, 4355,
         4449, 4357, 4449, 4359, 4449, 4546, 4358, 4449, 4546, 4370, 4468,
         12623, 12625, 12627, 12629]
    )


def test_fuzzy_korean_ratio():
    """Test Korean-specific fuzzy search."""

    assert fuzz.ratio('강', '공') == 0
    assert fuzzy_korean_ratio('강', '공') == 67

    assert fuzz.ratio('안녕', '인형') == 0
    assert fuzzy_korean_ratio('안녕', '인형') == 67
