from datetime import timedelta

import pytest
from more_itertools import flatten

from yui.apps.info.d2tz.tasks import auto_d2tz


def test_auto_d2tz_spec():
    assert auto_d2tz.has_valid_spec()


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
def test_auto_d2tz_match(sunday, delta, result):
    assert auto_d2tz.match(sunday + delta) is result
