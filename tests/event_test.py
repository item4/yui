import pytest

from yui.event import Hello
from yui.event import TeamMigrationStarted
from yui.event import UnknownEvent
from yui.event import create_event
from yui.event import create_unknown_event


def test_create_event():
    hello_event = create_event("hello", {})
    assert isinstance(hello_event, Hello)
    assert hello_event.type == "hello"

    team_migration_event: TeamMigrationStarted = create_event(
        "team_migration_started",
        {},
    )
    assert isinstance(team_migration_event, TeamMigrationStarted)
    assert team_migration_event.type == "team_migration_started"

    with pytest.raises(TypeError, match=""):
        create_event("not exists it", {})

    with pytest.raises(TypeError, match="Error at creating Message: "):
        create_event("message", {})


def test_create_unknown_event():
    source = {"a": 1, "b": [2, 3], "c": True, "d": {"e": 4, "f": 5}}
    event = create_unknown_event("unknown", source)
    assert isinstance(event, UnknownEvent)
    assert event.type == "unknown"
    assert event.kwargs == source
