from yui.models.saomd import Scout
from yui.saomd import SCOUT
from yui.util import get_count


def test_scout_list(fx_sess):
    scouts = set()
    functions = set()
    for title, type_, func in SCOUT:
        assert (title, type_) not in scouts
        assert func not in functions
        scouts.add((title, type_))
        functions.add(func)
    assert len(SCOUT) == len(scouts) == len(functions)

    for title, type_, func in SCOUT:
        func(fx_sess)
        fx_sess.query(Scout).filter_by(title=title, type=type_).one()

    assert get_count(fx_sess.query(Scout)) == len(SCOUT)
