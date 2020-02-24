import pytest

from yui.command.helpers import C, Cs, U, Us
from yui.exceptions import (
    AllChannelsError,
    AllUsersError,
    NoChannelsError,
    NoUsersError,
)

from ..util import FakeBot


def test_c(fx_config):
    fx_config.CHANNELS['general'] = 1
    fx_config.CHANNELS['food'] = 'foodporn'
    bot = FakeBot(fx_config)
    foodporn = bot.add_channel('C1', 'foodporn')

    ch = C.general
    assert isinstance(ch, C)
    assert ch.key == 'general'
    err = 'general in CHANNELS is not str.'
    with pytest.raises(ValueError, match=err):
        ch.get()

    ch = C['food']
    assert isinstance(ch, C)
    assert ch.key == 'food'
    assert ch.get() == foodporn


def test_cs(fx_config):
    fx_config.CHANNELS['tests1'] = 1
    fx_config.CHANNELS['tests2'] = []
    fx_config.CHANNELS['tests3'] = False
    fx_config.CHANNELS['tests4'] = '*'
    fx_config.CHANNELS['tests5'] = ['*']
    fx_config.CHANNELS['food'] = ['foodporn', 'food']
    bot = FakeBot(fx_config)
    foodporn = bot.add_channel('C1', 'foodporn')
    food = bot.add_channel('C2', 'food')

    ch = Cs.tests1
    assert isinstance(ch, Cs)
    assert ch.key == 'tests1'
    err = 'tests1 in CHANNELS is not list.'
    with pytest.raises(ValueError, match=err):
        ch.gets()

    ch = Cs['tests2']
    assert isinstance(ch, Cs)
    assert ch.key == 'tests2'
    with pytest.raises(NoChannelsError):
        ch.gets()

    ch = Cs['tests3']
    assert isinstance(ch, Cs)
    assert ch.key == 'tests3'
    with pytest.raises(NoChannelsError):
        ch.gets()

    ch = Cs['tests4']
    assert isinstance(ch, Cs)
    assert ch.key == 'tests4'
    with pytest.raises(AllChannelsError):
        ch.gets()

    ch = Cs['tests5']
    assert isinstance(ch, Cs)
    assert ch.key == 'tests5'
    with pytest.raises(AllChannelsError):
        ch.gets()

    ch = Cs['food']
    assert isinstance(ch, Cs)
    assert ch.key == 'food'
    assert ch.gets() == [foodporn, food]


def test_u(fx_config):
    fx_config.USERS['mob'] = 1
    fx_config.USERS['admin'] = 'U1'
    bot = FakeBot(fx_config)
    item4 = bot.add_user('U1', 'item4')

    user = U.mob
    assert isinstance(user, U)
    assert user.key == 'mob'
    err = 'mob in USERS is not str.'
    with pytest.raises(ValueError, match=err):
        user.get()

    user = U['admin']
    assert isinstance(user, U)
    assert user.key == 'admin'
    assert user.get() == item4


def test_us(fx_config):
    fx_config.USERS['tests1'] = 1
    fx_config.USERS['tests2'] = []
    fx_config.USERS['tests3'] = False
    fx_config.USERS['tests4'] = '*'
    fx_config.USERS['tests5'] = ['*']
    fx_config.USERS['developers'] = ['UA', 'UB', 'UC']
    fx_config.USERS['designers'] = ['UC', 'UD', 'UE']
    bot = FakeBot(fx_config)
    a = bot.add_user('UA', 'aaa')
    b = bot.add_user('UB', 'bbb')
    c = bot.add_user('UC', 'ccc')
    d = bot.add_user('UD', 'ddd')
    e = bot.add_user('UE', 'eee')

    users = Us.tests1
    assert isinstance(users, Us)
    assert users.key == 'tests1'
    err = 'tests1 in USERS is not list.'
    with pytest.raises(ValueError, match=err):
        users.gets()

    users = Us.tests2
    assert isinstance(users, Us)
    assert users.key == 'tests2'
    with pytest.raises(NoUsersError):
        users.gets()

    users = Us.tests3
    assert isinstance(users, Us)
    assert users.key == 'tests3'
    with pytest.raises(NoUsersError):
        users.gets()

    users = Us.tests4
    assert isinstance(users, Us)
    assert users.key == 'tests4'
    with pytest.raises(AllUsersError):
        users.gets()

    users = Us.tests5
    assert isinstance(users, Us)
    assert users.key == 'tests5'
    with pytest.raises(AllUsersError):
        users.gets()

    users = Us.developers
    assert isinstance(users, Us)
    assert users.key == 'developers'
    assert users.gets() == [a, b, c]

    users = Us['designers']
    assert isinstance(users, Us)
    assert users.key == 'designers'
    assert users.gets() == [c, d, e]
