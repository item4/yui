from yui.event import Hello
from yui.event import TeamMigrationStarted
from yui.event import UnknownEvent
from yui.event import create_event


def test_create_event():
    event: Hello = create_event("hello", {})
    assert isinstance(event, Hello)
    assert event.type == "hello"

    event: TeamMigrationStarted = create_event("team_migration_started", {})
    assert isinstance(event, TeamMigrationStarted)
    assert event.type == "team_migration_started"

    event: UnknownEvent = create_event("not exists it", {})
    assert isinstance(event, UnknownEvent)
    assert event.type == "not exists it"
