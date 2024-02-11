from datetime import timedelta

from yui.apps.date.monday import monday_dog
from yui.utils.datetime import datetime


def test_monday_dog_task_spec():
    assert monday_dog.has_valid_spec

    sunday = datetime(2022, 11, 6)
    assert not monday_dog.match(sunday)
    assert monday_dog.match(sunday + timedelta(days=1))
    assert not monday_dog.match(sunday + timedelta(days=1, hours=1))
    assert not monday_dog.match(sunday + timedelta(days=2))
