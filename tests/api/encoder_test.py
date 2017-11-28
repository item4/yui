import json

import pytest

from yui.api.encoder import SlackEncoder
from yui.api.type import Attachment, Field


def test_slack_encoder_class():
    def dumps(o):
        return json.dumps(o, cls=SlackEncoder, separators=(',', ':'))

    assert dumps(Field('title val', 'value val', True)) == (
        '{"title":"title val","value":"value val","short":true}'
    )
    assert dumps(Attachment(
        fallback='fallback val',
        title='title val',
        fields=[Field('field title1', 'field value1', False)],
    )) == (
       '{"fallback":"fallback val","title":"title val","fields":'
       '[{"title":"field title1","value":"field value1","short":false}]}'
    )

    class Dummy:
        pass

    with pytest.raises(TypeError):
        dumps(Dummy())
