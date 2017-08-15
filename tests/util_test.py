from yui.util import bold, bool2str, code, italics, preformatted, quote, strike


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
