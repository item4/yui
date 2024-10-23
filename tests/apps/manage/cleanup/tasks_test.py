from datetime import timedelta

from yui.apps.manage.cleanup.tasks import cleanup_channels
from yui.apps.manage.cleanup.tasks import get_old_history


def test_get_old_history_spec():
    assert get_old_history.has_valid_spec()


def test_get_old_history_match(sunday):
    for x in range(7):
        assert get_old_history.match(sunday + timedelta(days=x))
        assert not get_old_history.match(sunday + timedelta(days=x, minutes=1))


def test_cleanup_channels_spec():
    assert cleanup_channels.has_valid_spec()


def test_cleanup_channels_match(sunday):
    for x in range(7):
        assert cleanup_channels.match(sunday + timedelta(days=x))
        assert not cleanup_channels.match(sunday + timedelta(days=x, minutes=1))
        assert cleanup_channels.match(sunday + timedelta(days=x, minutes=10))
        assert cleanup_channels.match(sunday + timedelta(days=x, minutes=20))
        assert cleanup_channels.match(sunday + timedelta(days=x, minutes=30))
        assert cleanup_channels.match(sunday + timedelta(days=x, minutes=40))
        assert cleanup_channels.match(sunday + timedelta(days=x, minutes=50))
