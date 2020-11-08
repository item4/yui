from yui.box.utils import is_container


def test_is_container():
    assert is_container(list[int])
    assert is_container(set[int])
    assert is_container(tuple[int])
    assert is_container(list)
    assert is_container(set)
    assert is_container(tuple)
    assert not is_container(int)
    assert not is_container(float)
    assert not is_container(bool)
