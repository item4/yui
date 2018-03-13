import json

import pytest

from yui.api.encoder import SlackEncoder, bool2str
from yui.api.type import Attachment, Field
from yui.type import ChannelFromConfig, ChannelsFromConfig


def test_bool2str():
    assert bool2str(True) == '1'
    assert bool2str(False) == '0'


def test_slack_encoder_class():
    def dumps(o):
        return json.dumps(o, cls=SlackEncoder, separators=(',', ':'))

    assert dumps(Field('title val', 'value val', True)) == (
        '{"title":"title val","value":"value val","short":"1"}'
    )
    assert dumps(Attachment(
        fallback='fallback val',
        title='title val',
        fields=[Field('field title1', 'field value1', False)],
    )) == (
       '{"fallback":"fallback val","title":"title val","fields":'
       '[{"title":"field title1","value":"field value1","short":"0"}]}'
    )

    class Dummy:
        pass

    with pytest.raises(TypeError):
        dumps(Dummy())

    with pytest.raises(TypeError):
        dumps(ChannelFromConfig('general'))

    with pytest.raises(TypeError):
        dumps(ChannelsFromConfig('commons'))
