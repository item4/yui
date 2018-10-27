from yui.utils.format import (
    bold,
    code,
    italics,
    preformatted,
    quote,
    strike,
)


def test_format_helpers():
    """Test slack syntax helpers."""

    assert bold('item4') == '*item4*'
    assert code('item4') == '`item4`'
    assert italics('item4') == '_item4_'
    assert preformatted('item4') == '```item4```'
    assert strike('item4') == '~item4~'
    assert quote('item4') == '>item4'
