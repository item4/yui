from yui.event import Event, Hello, TeamMigrationStarted, create_event


def test_create_event():
    event = create_event({'type': 'hello'})
    assert type(event) == Hello
    assert event.type == 'hello'

    event = create_event({'type': 'team_migration_started'})
    assert type(event) == TeamMigrationStarted
    assert event.type == 'team_migration_started'

    event = create_event({'type': 'not exists it'})
    assert type(event) == Event
    assert event.type == 'not exists it'
