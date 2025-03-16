from datetime import timedelta

import pytest
from more_itertools import flatten

from yui.apps.manage.cleanup.tasks import cleanup_channels
from yui.apps.manage.cleanup.tasks import get_old_history

from ....util import assert_crontab_match
from ....util import assert_crontab_spec


def test_get_old_history_spec():
    assert_crontab_spec(get_old_history)


@pytest.mark.parametrize(
    ("delta", "result"),
    flatten(
        [
            (timedelta(days=x), False),
            (timedelta(days=x, minutes=5), True),
        ]
        for x in range(7)
    ),
)
def test_get_old_history_match(sunday, delta, result):
    assert_crontab_match(get_old_history, sunday + delta, expected=result)


def test_cleanup_channels_spec():
    assert_crontab_spec(cleanup_channels)


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
    assert_crontab_match(cleanup_channels, sunday + delta, expected=result)
