from yui.command.helpers import C, Cs


def test_c():
    ch = C.general
    assert isinstance(ch, C)
    assert ch.key == 'general'

    ch = C['food']
    assert isinstance(ch, C)
    assert ch.key == 'food'


def test_cs():
    ch = Cs.tests
    assert isinstance(ch, Cs)
    assert ch.key == 'tests'

    ch = Cs['commons']
    assert isinstance(ch, Cs)
    assert ch.key == 'commons'
