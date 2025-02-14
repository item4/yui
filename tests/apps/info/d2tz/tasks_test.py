from datetime import timedelta

import pytest
from more_itertools import flatten

from yui.apps.info.d2tz.tasks import auto_d2tz

from ....util import assert_crontab_match
from ....util import assert_crontab_spec


def test_auto_d2tz_spec():
    assert_crontab_spec(auto_d2tz)


@pytest.mark.parametrize(
    ("delta", "result"),
    flatten(
        [
            (timedelta(days=x), False),
            (timedelta(days=x, minutes=20), True),
        ]
        for x in range(7)
    ),
)
def test_auto_d2tz_match(sunday, delta, result):
    assert_crontab_match(auto_d2tz, sunday + delta, result)
