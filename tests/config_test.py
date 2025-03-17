import pytest

from yui.config import ConfigurationError
from yui.config import error
from yui.config import load


def test_error():
    """Expect raising SystemExit"""

    with pytest.raises(SystemExit):
        error("Error")


@pytest.mark.anyio
async def test_load_not_exists_file(fx_tmpdir):
    """Test config load function - not exists file"""

    no_file = fx_tmpdir / "nofile"

    with pytest.raises(SystemExit):
        await load(no_file)


@pytest.mark.anyio
async def test_load_not_file(fx_tmpdir):
    """Test config load function - path is not file"""

    with pytest.raises(SystemExit):
        await load(fx_tmpdir)


@pytest.mark.anyio
async def test_load_not_correct_suffix(fx_tmpdir):
    """Test config load function - not correct suffix"""

    file = fx_tmpdir / "conf.py"
    await file.touch()

    with pytest.raises(SystemExit):
        await load(file)


@pytest.mark.anyio
async def test_load_empty(fx_tmpdir):
    """Test config load function - empty file"""

    file = fx_tmpdir / "empty.config.toml"
    await file.touch()

    with pytest.raises(SystemExit):
        await load(file)


@pytest.mark.anyio
async def test_load_fine(fx_tmpdir):
    """Test config load function - empty file"""
    APP_TOKEN = "TEST_APP_TOKEN"  # noqa: S105 - fake value
    BOT_TOKEN = "TEST_BOT_TOKEN"  # noqa: S105 - fake value

    file = fx_tmpdir / "yui.config.toml"
    await file.write_text(
        f"""\
APP_TOKEN = '{APP_TOKEN}'
BOT_TOKEN = '{BOT_TOKEN}'
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

    config = await load(file)

    assert config.APP_TOKEN == APP_TOKEN
    assert config.BOT_TOKEN == BOT_TOKEN
    assert config.DEBUG
    assert config.PREFIX == "."
    assert config.APPS == ["a", "b"]
    assert config.CHANNELS == {
        "general": "C1",
    }


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

    bot_config.APP_TOKEN = "TEST_APP_TOKEN"  # noqa: S105 - fake value
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
    err = "Config value type mismatch: APP_TOKEN"
    with pytest.raises(ConfigurationError, match=err):
        assert bot_config.check(
            {"APP_TOKEN": int},
            set(),
            set(),
            set(),
            set(),
        )

    bot_config.APP_TOKEN = "XXXX"  # noqa: S105 - fake value
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
