from yui.utils.format import (
    bold,
    code,
    escape,
    italics,
    link,
    link_channel,
    link_everyone,
    link_here,
    link_url,
    preformatted,
    quote,
    strike,
)

from ..util import FakeBot


def test_escape():
    assert escape('&') == '&amp;'
    assert escape('<') == '&lt;'
    assert escape('>') == '&gt;'


def test_format_helpers():
    """Test slack syntax helpers."""

    assert bold('item4') == '*item4*'
    assert code('item4') == '`item4`'
    assert italics('item4') == '_item4_'
    assert preformatted('item4') == '```item4```'
    assert strike('item4') == '~item4~'
    assert quote('item4') == '>item4'


def test_link():
    bot = FakeBot()
    user = bot.add_user('U1234', 'tester')
    channel = bot.add_channel('C1234', 'test')
    assert link(channel) == '<#C1234>'
    assert link(user) == '<@U1234>'
    assert link('C1234') == '<#C1234>'
    assert link('U1234') == '<@U1234>'
    assert link('W1234') == '<@W1234>'
    assert link('S1234') == '<!subteam^S1234>'
    assert link('unknown') == '<unknown>'
    assert link(1234) == '<1234>'


def test_link_url():
    url = 'https://github.com/item4/yui'
    assert link_url(url) == f'<{url}>'
    assert link_url(url, 'Repo') == f'<{url}|Repo>'
    assert link_url(url, 'Repo & Code') == f'<{url}|Repo &amp; Code>'


def test_special_mentions():
    assert link_channel() == '<!channel|channel>'
    assert link_everyone() == '<!everyone|everyone>'
    assert link_here() == '<!here|here>'
