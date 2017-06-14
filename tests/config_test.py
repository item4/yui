import pathlib

import pytest

from yui.config import error, load


def test_error():
    """Expect raising SystemExit"""

    with pytest.raises(SystemExit):
        error('Error')


def test_load_not_exists_file(fx_tmpdir: pathlib.Path):
    """Test config load function - not exists file"""

    no_file = fx_tmpdir / 'nofile'

    with pytest.raises(SystemExit):
        load(no_file)


def test_load_not_file(fx_tmpdir: pathlib.Path):
    """Test config load function - not exists file"""

    path = fx_tmpdir / 'path'
    path.mkdir()

    with pytest.raises(SystemExit):
        load(path)


def test_load_not_correct_suffix(fx_tmpdir: pathlib.Path):
    """Test config load function - not correct suffix"""

    file = fx_tmpdir / 'conf.py'
    file.touch()

    with pytest.raises(SystemExit):
        load(file)


def test_load_empty(fx_tmpdir: pathlib.Path):
    """Test config load function - empty file"""

    file = fx_tmpdir / 'empty.config.toml'
    file.touch()
    config = load(file)

    assert not config.DEBUG
    assert config.PREFIX == ''
    assert config.HANDLERS == ()


def test_load_fine(fx_tmpdir: pathlib.Path):
    """Test config load function - empty file"""

    file = fx_tmpdir / 'yui.config.toml'
    with file.open('w') as f:
        f.write('''
DEBUG = true
PREFIX = '.'
HANDLERS = ['a', 'b']
        ''')
    config = load(file)

    assert config.DEBUG
    assert config.PREFIX == '.'
    assert config.HANDLERS == ('a', 'b')
