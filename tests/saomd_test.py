from typing import List, Type

from yui.models.saomd import Scout
from yui.saomd import MigrationStatus, ScoutMigration
from yui.util import get_count


def test_scout_list(fx_sess):
    scouts = set()
    subclasses: List[Type[ScoutMigration]] = list(
        ScoutMigration.__subclasses__()
    )
    for cls in subclasses:
        scout = cls()
        assert str(scout).startswith('ScoutMigration(')
        assert get_count(
            fx_sess.query(Scout).filter_by(title=scout.title, type=scout.type)
        ) == 0

        result = scout.patch(fx_sess)
        assert result == MigrationStatus.create
        assert get_count(
            fx_sess.query(Scout).filter_by(title=scout.title, type=scout.type)
        ) == 1

        result = scout.patch(fx_sess)
        assert result == MigrationStatus.passed
        assert get_count(
            fx_sess.query(Scout).filter_by(title=scout.title, type=scout.type)
        ) == 1

        scout.delete(fx_sess)
        assert get_count(
            fx_sess.query(Scout).filter_by(title=scout.title, type=scout.type)
        ) == 0

        scout.create(fx_sess)

        scouts.add((scout.title, scout.type))

    assert len(scouts) == len(subclasses) == get_count(fx_sess.query(Scout))
