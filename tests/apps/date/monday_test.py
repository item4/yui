from datetime import timedelta

import pytest

from yui.apps.date.monday import monday_dog


def test_monday_dog_task_spec():
    assert monday_dog.has_valid_spec()


@pytest.mark.parametrize(
    ("delta", "result"),
    [
        (timedelta(days=0), False),
        (timedelta(days=1), True),
        (timedelta(days=1, minutes=11), False),
        (timedelta(days=2), False),
        (timedelta(days=3), False),
        (timedelta(days=4), False),
        (timedelta(days=5), False),
        (timedelta(days=6), False),
    ],
)
def test_monday_dog_task_match(sunday, delta, result):
    assert monday_dog.match(sunday + delta) is result
