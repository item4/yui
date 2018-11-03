from yui.event import Hello, TeamMigrationStarted, UnknownEvent, create_event


def test_create_event():
    event: Hello = create_event({'type': 'hello'})
    assert type(event) == Hello
    assert event.type == 'hello'

    event: TeamMigrationStarted = create_event({
        'type': 'team_migration_started'})
    assert type(event) == TeamMigrationStarted
    assert event.type == 'team_migration_started'

    event: UnknownEvent = create_event({'type': 'not exists it'})
    assert type(event) == UnknownEvent
    assert event.type == 'not exists it'
