import pathlib

import pytest

from yui.config import ConfigurationError
from yui.config import error
from yui.config import load


def test_error():
    """Expect raising SystemExit"""

    with pytest.raises(SystemExit):
        error("Error")


def test_load_not_exists_file(fx_tmpdir: pathlib.Path):
    """Test config load function - not exists file"""

    no_file = fx_tmpdir / "nofile"

    with pytest.raises(SystemExit):
        load(no_file)


def test_load_not_file(fx_tmpdir: pathlib.Path):
    """Test config load function - not exists file"""

    path = fx_tmpdir / "path"
    path.mkdir()

    with pytest.raises(SystemExit):
        load(path)


def test_load_not_correct_suffix(fx_tmpdir: pathlib.Path):
    """Test config load function - not correct suffix"""

    file = fx_tmpdir / "conf.py"
    file.touch()

    with pytest.raises(SystemExit):
        load(file)


def test_load_empty(fx_tmpdir: pathlib.Path):
    """Test config load function - empty file"""

    file = fx_tmpdir / "empty.config.toml"
    file.touch()

    with pytest.raises(SystemExit):
        load(file)


def test_load_fine(fx_tmpdir: pathlib.Path):
    """Test config load function - empty file"""

    file = fx_tmpdir / "yui.config.toml"
    with file.open("w") as f:
        f.write(
            """
APP_TOKEN = 'TEST_APP_TOKEN'
BOT_TOKEN = 'TEST_BOT_TOKEN'
DATABASE_URL = 'sqlite:///:memory:'
DEBUG = true
PREFIX = '.'
APPS = ['a', 'b']

[CHANNELS]
general = 'C1'

[USERS]
owner = 'U111'

        """,
        )
    config = load(file)

    assert config.APP_TOKEN == "TEST_APP_TOKEN"  # noqa: S105
    assert config.BOT_TOKEN == "TEST_BOT_TOKEN"  # noqa: S105
    assert config.DEBUG
    assert config.PREFIX == "."
    assert config.APPS == ["a", "b"]
    assert {
        "general": "C1",
    } == config.CHANNELS


def test_config_check(bot_config):
    del bot_config.APP_TOKEN

    err = "Required config key was not defined: APP_TOKEN"
    with pytest.raises(ConfigurationError, match=err):
        bot_config.check(
            {"APP_TOKEN": str},
            set(),
            set(),
            set(),
            set(),
        )

    bot_config.APP_TOKEN = "TEST_APP_TOKEN"  # noqa: S105
    err = "Wrong config value type: APP_TOKEN"
    with pytest.raises(ConfigurationError, match=err):
        bot_config.check(
            {"APP_TOKEN": list[int]},
            set(),
            set(),
            set(),
            set(),
        )

    bot_config.APP_TOKEN = 123.456
    err = "Wrong config value type: APP_TOKEN"
    with pytest.raises(ConfigurationError, match=err):
        assert bot_config.check(
            {"APP_TOKEN": int},
            set(),
            set(),
            set(),
            set(),
        )

    bot_config.APP_TOKEN = "XXXX"  # noqa: S105
    assert bot_config.check(
        {"APP_TOKEN": str},
        set(),
        set(),
        set(),
        set(),
    )

    bot_config.CHANNELS = {}
    err = "Required channel key was not defined: general"
    with pytest.raises(ConfigurationError, match=err):
        bot_config.check(
            {},
            {"general"},
            set(),
            set(),
            set(),
        )

    bot_config.CHANNELS = {"general": 1}
    err = "Channel config has wrong type: general"
    with pytest.raises(ConfigurationError, match=err):
        bot_config.check(
            {},
            {"general"},
            set(),
            set(),
            set(),
        )

    bot_config.CHANNELS = {"general": "C1"}
    assert bot_config.check(
        {},
        {"general"},
        set(),
        set(),
        set(),
    )

    err = "Required channel key was not defined: test"
    with pytest.raises(ConfigurationError, match=err):
        bot_config.check(
            {},
            set(),
            {"test"},
            set(),
            set(),
        )

    bot_config.CHANNELS = {"test": 1}
    err = "Channel config has wrong type: test"
    with pytest.raises(ConfigurationError, match=err):
        bot_config.check(
            {},
            set(),
            {"test"},
            set(),
            set(),
        )
    bot_config.CHANNELS = {"test": [1]}
    err = "Channel config has wrong type: test"
    with pytest.raises(ConfigurationError, match=err):
        bot_config.check(
            {},
            set(),
            {"test"},
            set(),
            set(),
        )

    bot_config.CHANNELS = {"test": ["C1", "C2"]}
    assert bot_config.check(
        {},
        set(),
        {"test"},
        set(),
        set(),
    )

    bot_config.CHANNELS = {"test": "*"}
    assert bot_config.check(
        {},
        set(),
        {"test"},
        set(),
        set(),
    )

    bot_config.USERS = {}
    err = "Required user key was not defined: owner"
    with pytest.raises(ConfigurationError, match=err):
        bot_config.check(
            {},
            set(),
            set(),
            {"owner"},
            set(),
        )

    bot_config.USERS = {"owner": 1}
    err = "User config has wrong type: owner"
    with pytest.raises(ConfigurationError, match=err):
        bot_config.check(
            {},
            set(),
            set(),
            {"owner"},
            set(),
        )

    bot_config.USERS = {"owner": "U1"}
    assert bot_config.check(
        {},
        set(),
        set(),
        {"owner"},
        set(),
    )

    err = "Required user key was not defined: tester"
    with pytest.raises(ConfigurationError, match=err):
        bot_config.check(
            {},
            set(),
            set(),
            set(),
            {"tester"},
        )

    bot_config.USERS = {"tester": 1}
    err = "User config has wrong type: tester"
    with pytest.raises(ConfigurationError, match=err):
        bot_config.check(
            {},
            set(),
            set(),
            set(),
            {"tester"},
        )

    bot_config.USERS = {"tester": [1]}
    err = "User config has wrong type: tester"
    with pytest.raises(ConfigurationError, match=err):
        bot_config.check(
            {},
            set(),
            set(),
            set(),
            {"tester"},
        )

    bot_config.USERS = {"tester": ["aaa", "bbb"]}
    assert bot_config.check(
        {},
        set(),
        set(),
        set(),
        {"tester"},
    )

    bot_config.USERS = {"tester": "*"}
    assert bot_config.check(
        {},
        set(),
        set(),
        set(),
        {"tester"},
    )
