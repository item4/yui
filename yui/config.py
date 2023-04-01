import copy
import pathlib
import sys
import tomllib
from types import SimpleNamespace
from typing import Any

from .utils.cast import cast
from .utils.cast import CastError

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
    "CACHE": {"HOST": "localhost", "PORT": 11211, "PREFIX": "YUI_"},
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
                raise ConfigurationError(
                    f"Required config key was not defined: {key}"
                ) from e
            try:
                casted = cast(value, config)
                if config != casted:
                    raise CastError
            except CastError as e:
                raise ConfigurationError(
                    f"Wrong config value type: {key}"
                ) from e

        for key in single_channels:
            try:
                value = self.CHANNELS[key]
            except KeyError as e:
                raise ConfigurationError(
                    f"Required channel key was not defined: {key}"
                ) from e
            else:
                if not isinstance(value, str):
                    raise ConfigurationError(
                        f"Channel config has wrong type: {key}"
                    )

        for key in multiple_channels:
            try:
                value = self.CHANNELS[key]
            except KeyError as e:
                raise ConfigurationError(
                    f"Required channel key was not defined: {key}"
                ) from e
            else:
                if value == "*":
                    continue
                if isinstance(value, list) and all(
                    isinstance(x, str) for x in value
                ):
                    continue
                raise ConfigurationError(
                    f"Channel config has wrong type: {key}"
                )
        for key in single_users:
            try:
                value = self.USERS[key]
            except KeyError as e:
                raise ConfigurationError(
                    f"Required user key was not defined: {key}"
                ) from e
            else:
                if not isinstance(value, str):
                    raise ConfigurationError(
                        f"User config has wrong type: {key}"
                    )

        for key in multiple_users:
            try:
                value = self.USERS[key]
            except KeyError as e:
                raise ConfigurationError(
                    f"Required user key was not defined: {key}"
                ) from e
            else:
                if value == "*":
                    continue
                if isinstance(value, list) and all(
                    isinstance(x, str) for x in value
                ):
                    continue
                raise ConfigurationError(f"User config has wrong type: {key}")
        return True


def error(message: str, *args):
    msg = message.format(*args)
    print(msg, file=sys.stderr)
    raise SystemExit(1)


def load(path: pathlib.Path) -> Config:
    """Load configuration from given path."""

    if not path.exists():
        error("File do not exists.")

    if not path.is_file():
        error("Given path is not file.")

    if not path.match("*.config.toml"):
        error("File suffix must be *.config.toml")

    config_dict = copy.deepcopy(DEFAULT)
    data = tomllib.load(path.open("rb"))

    if missing := REQUIRED - set(data.keys()):
        error(f'Missing required keys: {", ".join(missing)}')

    config_dict.update(data)

    return Config(**config_dict)
