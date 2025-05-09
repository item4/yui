import copy
import sys
import tomllib
from types import SimpleNamespace
from typing import Any

import anyio

from .utils.cast import CastError
from .utils.cast import cast

REQUIRED = {
    "APPS",
    "DATABASE_URL",
    "APP_TOKEN",
    "BOT_TOKEN",
}


DEFAULT = {
    "DEBUG": False,
    "RECEIVE_TIMEOUT": 300,  # 60 * 5 seconds
    "REGISTER_CRONTAB": True,
    "PREFIX": "",
    "APPS": (),
    "DATABASE_URL": "",
    "DATABASE_ECHO": False,
    "LOGGING": {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "brief": {"format": "%(message)s"},
            "default": {
                "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "brief",
                "level": "INFO",
                "filters": [],
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "default",
                "level": "WARNING",
                "filename": "log/warning.log",
                "maxBytes": 1024,
                "backupCount": 3,
            },
        },
        "loggers": {
            "yui": {
                "handlers": ["console", "file"],
                "propagate": True,
                "level": "INFO",
            },
        },
    },
    "CACHE": {"URL": "valkey://localhost:6379/0", "PREFIX": "YUI_"},
}


class ConfigurationError(Exception):
    pass


class Config(SimpleNamespace):
    APP_TOKEN: str
    BOT_TOKEN: str
    RECEIVE_TIMEOUT: int
    DEBUG: bool
    PREFIX: str
    APPS: list[str]
    DATABASE_URL: str
    DATABASE_ECHO: bool
    LOGGING: dict[str, Any]
    REGISTER_CRONTAB: bool
    CHANNELS: dict[str, Any]
    USERS: dict[str, Any]
    CACHE: dict[str, Any]
    WEBSOCKETDEBUGGERURL: str | None

    def check(
        self,
        configs: dict[str, Any],
        single_channels: set[str],
        multiple_channels: set[str],
        single_users: set[str],
        multiple_users: set[str],
    ) -> bool:
        for key, value in configs.items():
            try:
                config = getattr(self, key)
            except AttributeError as e:
                error = f"Required config key was not defined: {key}"
                raise ConfigurationError(error) from e
            try:
                casted = cast(value, config)
            except CastError as e:
                error = f"Wrong config value type: {key}"
                raise ConfigurationError(error) from e
            if config != casted:
                error = f"Config value type mismatch: {key}"
                raise ConfigurationError(error)

        for key in single_channels:
            try:
                value = self.CHANNELS[key]
            except KeyError as e:
                error = f"Required channel key was not defined: {key}"
                raise ConfigurationError(error) from e
            else:
                if not isinstance(value, str):
                    error = f"Channel config has wrong type: {key}"
                    raise ConfigurationError(error)

        for key in multiple_channels:
            try:
                value = self.CHANNELS[key]
            except KeyError as e:
                error = f"Required channel key was not defined: {key}"
                raise ConfigurationError(error) from e
            else:
                if value == "*":
                    continue
                if isinstance(value, list) and all(
                    isinstance(x, str) for x in value
                ):
                    continue
                error = f"Channel config has wrong type: {key}"
                raise ConfigurationError(error)
        for key in single_users:
            try:
                value = self.USERS[key]
            except KeyError as e:
                error = f"Required user key was not defined: {key}"
                raise ConfigurationError(error) from e
            else:
                if not isinstance(value, str):
                    error = f"User config has wrong type: {key}"
                    raise ConfigurationError(error)

        for key in multiple_users:
            try:
                value = self.USERS[key]
            except KeyError as e:
                error = f"Required user key was not defined: {key}"
                raise ConfigurationError(error) from e
            else:
                if value == "*":
                    continue
                if isinstance(value, list) and all(
                    isinstance(x, str) for x in value
                ):
                    continue
                error = f"User config has wrong type: {key}"
                raise ConfigurationError(error)
        return True


def error(message: str, *args):
    msg = message.format(*args)
    print(msg, file=sys.stderr)  # noqa: T201 - use for cli
    raise SystemExit(1)


async def load(path: anyio.Path) -> Config:
    """Load configuration from given path."""

    if not await path.exists():
        error("File do not exists.")

    if not await path.is_file():
        error("Given path is not file.")

    if not path.match("*.config.toml"):
        error("File suffix must be *.config.toml")

    config_dict = copy.deepcopy(DEFAULT)
    data = tomllib.loads(await path.read_text())

    if missing := REQUIRED - set(data.keys()):
        error(f'Missing required keys: {", ".join(missing)}')

    config_dict.update(data)

    return Config(**config_dict)
