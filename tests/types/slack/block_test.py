import pytest

from yui.types.slack.block import PlainTextField
from yui.types.slack.block import TextFieldType


def test_plain_text_field():
    with pytest.raises(ValueError, match="this field support only plain text"):
        PlainTextField(text="*test*", type=TextFieldType.mrkdwn)
