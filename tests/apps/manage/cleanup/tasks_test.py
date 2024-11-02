from datetime import timedelta

import pytest
from more_itertools import flatten

from yui.apps.manage.cleanup.tasks import cleanup_channels
from yui.apps.manage.cleanup.tasks import get_old_history


def test_get_old_history_spec():
    assert get_old_history.has_valid_spec()


@pytest.mark.parametrize(
    ("delta", "result"),
    flatten(
        [
            (timedelta(days=x), True),
            (timedelta(days=x, minutes=5), False),
        ]
        for x in range(7)
    ),
)
def test_get_old_history_match(sunday, delta, result):
    assert get_old_history.match(sunday + delta) is result


def test_cleanup_channels_spec():
    assert cleanup_channels.has_valid_spec()


@pytest.mark.parametrize(
    ("delta", "result"),
    flatten(
        [
            (timedelta(days=x), True),
            (timedelta(days=x, minutes=5), False),
            (timedelta(days=x, minutes=10), True),
            (timedelta(days=x, minutes=20), True),
            (timedelta(days=x, minutes=30), True),
            (timedelta(days=x, minutes=40), True),
            (timedelta(days=x, minutes=50), True),
        ]
        for x in range(7)
    ),
)
def test_cleanup_channels_match(sunday, delta, result):
    assert cleanup_channels.match(sunday + delta) is result
