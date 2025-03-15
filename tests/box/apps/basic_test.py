from __future__ import annotations

from typing import TYPE_CHECKING

from yui.box import Box
from yui.command.decorators import argument
from yui.command.decorators import option
from yui.event import Message
from yui.event import MessageMessage
from yui.types.base import Ts

if TYPE_CHECKING:
    from yui.box.apps.basic import App


def test_basic_app(channel_id, user_id):
    box = Box()
    ts = Ts("123.456")
    event_ts = Ts("456.789")
    message_ts = Ts("789.012")

    @box.command("test", aliases=["tttt"])
    @option("--foo", "-f")
    @option("--bar")
    @argument("baz")
    @argument("kw", nargs=-1, concat=True)
    async def test(bot, event: Message, foo: int, bar: str, baz: str, kw: str):
        """
        TEST TITLE

        LONG
        CAT
        IS
        LONG

        """

    app: App = box.apps.pop()
    assert app.name == "test"
    assert app.aliases == ["tttt"]
    assert app.names == ["tttt", "test"]
    assert app.handler == test
    assert app.is_command
    assert app.use_shlex
    assert app.has_short_help
    assert app.has_full_help
    assert app.short_help == "TEST TITLE"
    assert (
        app.help
        == """LONG
CAT
IS
LONG"""
    )
    assert app.get_short_help("=") == "`=test`: TEST TITLE"
    assert (
        app.get_full_help("=")
        == "*=test*\n(Aliases: `=tttt`)\nTEST TITLE\n\nLONG\nCAT\nIS\nLONG"
    )
    event = Message(
        channel=channel_id,
        ts=ts,
        event_ts=event_ts,
    )
    assert not app.get_event_text(event)
    event = Message(
        channel=channel_id,
        ts=ts,
        event_ts=event_ts,
        user=user_id,
        text="=test --foo 1 --bar 2 3 4 5",
    )
    assert app.get_event_text(event) == "=test --foo 1 --bar 2 3 4 5"
    event = Message(
        channel=channel_id,
        ts=ts,
        event_ts=event_ts,
        user=user_id,
        message=MessageMessage(
            user=user_id,
            ts=message_ts,
            text="=test --foo 1 --bar 2 3 4 5",
        ),
    )
    assert app.get_event_text(event) == "=test --foo 1 --bar 2 3 4 5"
    assert app.split_call_and_args("=test 1 2 3 4 5") == ("=test", "1 2 3 4 5")
    assert app.split_call_and_args("=test") == ("=test", "")
