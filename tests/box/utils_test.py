from yui.box.utils import is_container
from yui.box.utils import split_chunks


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


def test_split_chunks():
    assert split_chunks("ls -al", use_shlex=True) == ["ls", "-al"]
    assert split_chunks("git commit -m 'test'", use_shlex=True) == [
        "git",
        "commit",
        "-m",
        "test",
    ]
    assert split_chunks("test --value=b", use_shlex=True) == [
        "test",
        "--value=b",
    ]
    assert split_chunks("test --value='b c d'", use_shlex=True) == [
        "test",
        "--value=b c d",
    ]
    assert split_chunks("test\xa0--value='b c d'", use_shlex=True) == [
        "test",
        "--value=b c d",
    ]

    assert split_chunks("ls -al", use_shlex=False) == ["ls", "-al"]
    assert split_chunks("git commit -m 'test'", use_shlex=False) == [
        "git",
        "commit",
        "-m",
        "'test'",
    ]
    assert split_chunks("test --value=b", use_shlex=False) == [
        "test",
        "--value=b",
    ]
    assert split_chunks("test --value='b c d'", use_shlex=False) == [
        "test",
        "--value='b",
        "c",
        "d'",
    ]
    assert split_chunks("test\xa0--value='b c d'", use_shlex=False) == [
        "test",
        "--value='b",
        "c",
        "d'",
    ]
