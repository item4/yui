import copy
import pathlib
import sys
from typing import Any
from typing import Optional

import attr

from sqlalchemy.engine import Engine

import toml

from .types.namespace import namespace
from .utils.cast import CastError
from .utils.cast import cast


DEFAULT = {
    'DEBUG': False,
    'RECEIVE_TIMEOUT': 300,  # 60 * 5 seconds
    'REGISTER_CRONTAB': True,
    'PREFIX': '',
    'APPS': (),
    'DATABASE_URL': '',
    'DATABASE_ECHO': False,
    'LOGGING': {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'brief': {'format': '%(message)s'},
            'default': {
                'format': '%(asctime)s %(levelname)s %(name)s %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'brief',
                'level': 'INFO',
                'filters': [],
                'stream': 'ext://sys.stdout',
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'default',
                'level': 'WARNING',
                'filename': 'log/warning.log',
                'maxBytes': 1024,
                'backupCount': 3,
            },
        },
        'loggers': {
            'yui': {
                'handlers': ['console', 'file'],
                'propagate': True,
                'level': 'INFO',
            },
        },
    },
    'CACHE': {'HOST': 'localhost', 'PORT': 11211, 'PREFIX': 'YUI_'},
}


class ConfigurationError(Exception):
    pass


@namespace
class Config:

    TOKEN: str
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
    WEBSOCKETDEBUGGERURL: Optional[str] = None
    DATABASE_ENGINE: Engine = attr.ib(init=False, repr=False, cmp=False)

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
            except AttributeError:
                raise ConfigurationError(
                    f'Required config key was not defined: {key}'
                )
            try:
                casted = cast(value, config)
                if config != casted:
                    raise CastError
            except CastError:
                raise ConfigurationError(f'Wrong config value type: {key}')

        for key in single_channels:
            try:
                value = self.CHANNELS[key]
            except KeyError:
                raise ConfigurationError(
                    f'Required channel key was not defined: {key}'
                )
            else:
                if not isinstance(value, str):
                    raise ConfigurationError(
                        f'Channel config has wrong type: {key}'
                    )

        for key in multiple_channels:
            try:
                value = self.CHANNELS[key]
            except KeyError:
                raise ConfigurationError(
                    f'Required channel key was not defined: {key}'
                )
            else:
                if value == '*':
                    continue
                elif isinstance(value, list):
                    if all(isinstance(x, str) for x in value):
                        continue
                raise ConfigurationError(
                    f'Channel config has wrong type: {key}'
                )
        for key in single_users:
            try:
                value = self.USERS[key]
            except KeyError:
                raise ConfigurationError(
                    f'Required user key was not defined: {key}'
                )
            else:
                if not isinstance(value, str):
                    raise ConfigurationError(
                        f'User config has wrong type: {key}'
                    )

        for key in multiple_users:
            try:
                value = self.USERS[key]
            except KeyError:
                raise ConfigurationError(
                    f'Required user key was not defined: {key}'
                )
            else:
                if value == '*':
                    continue
                elif isinstance(value, list):
                    if all(isinstance(x, str) for x in value):
                        continue
                raise ConfigurationError(f'User config has wrong type: {key}')
        return True


def error(message: str, *args):
    msg = message.format(*args)
    print(msg, file=sys.stderr)
    raise SystemExit(1)


def load(path: pathlib.Path) -> Config:
    """Load configuration from given path."""

    if not path.exists():
        error('File do not exists.')

    if not path.is_file():
        error('Given path is not file.')

    if not path.match('*.config.toml'):
        error('File suffix must be *.config.toml')

    config_dict = copy.deepcopy(DEFAULT)
    config_dict.update(toml.load(path.open()))

    try:
        config = Config(**config_dict)  # type: ignore
    except TypeError as e:  # pragma: no cover
        error(str(e))
        raise

    return config
