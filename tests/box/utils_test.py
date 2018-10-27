from typing import List, Set, Tuple

from yui.box.utils import is_container


def test_is_container():
    assert is_container(List[int])
    assert is_container(Set[int])
    assert is_container(Tuple[int])
    assert is_container(list)
    assert is_container(set)
    assert is_container(tuple)
    assert not is_container(int)
    assert not is_container(float)
    assert not is_container(bool)
