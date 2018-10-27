from yui.command.helpers import C, Cs
from yui.types.namespace.linked import ChannelFromConfig, ChannelsFromConfig


def test_c():
    ch = C.general
    assert isinstance(ch, ChannelFromConfig)
    assert ch.key == 'general'

    ch = C['food']
    assert isinstance(ch, ChannelFromConfig)
    assert ch.key == 'food'


def test_cs():
    ch = Cs.tests
    assert isinstance(ch, ChannelsFromConfig)
    assert ch.key == 'tests'

    ch = Cs['commons']
    assert isinstance(ch, ChannelsFromConfig)
    assert ch.key == 'commons'
