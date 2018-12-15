from yui.command.helpers import C, Cs, U, Us


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


def test_u():
    user = U.owner
    assert isinstance(user, U)
    assert user.key == 'owner'

    user = U['monster']
    assert isinstance(user, U)
    assert user.key == 'monster'


def test_us():
    user = Us.developers
    assert isinstance(user, Us)
    assert user.key == 'developers'

    user = Us['designers']
    assert isinstance(user, Us)
    assert user.key == 'designers'
