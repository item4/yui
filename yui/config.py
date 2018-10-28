import copy
import pathlib
import sys
from typing import Any, Dict, List, Set

from sqlalchemy.engine import Engine

import toml

from .types.namespace.base import Namespace
from .utils.cast import cast


__all__ = (
    'Config',
    'ConfigurationError',
    'DEFAULT',
    'error',
    'load',
)

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
            'brief': {
                'format': '%(message)s',
            },
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
}


class ConfigurationError(Exception):
    pass


class Config(Namespace):

    TOKEN: str
    RECEIVE_TIMEOUT: int
    DEBUG: bool
    PREFIX: str
    APPS: List[str]
    DATABASE_URL: str
    DATABASE_ECHO: bool
    LOGGING: Dict[str, Any]
    REGISTER_CRONTAB: bool
    CHANNELS: Dict[str, Any]
    WEBSOCKETDEBUGGERURL: str
    DATABASE_ENGINE: Engine

    def __init__(self, **kwargs) -> None:
        kw = copy.deepcopy(DEFAULT)
        kw.update(kwargs)
        super(Config, self).__init__(**kw)

    def check_and_cast(self, fields: Dict):
        annotations = self.__annotations__
        annotations.update(fields)
        for key, type in annotations.items():
            try:
                value = getattr(self, key)
            except AttributeError:
                raise ConfigurationError(
                    f'Required config key was not defined: {key}'
                )
            else:
                try:
                    setattr(self, key, cast(type, value))
                except ValueError:
                    raise ConfigurationError(
                        f'Type of config value is wrong: {key}'
                    )

    def check_channel(
        self,
        single_channels: Set[str],
        multiple_channels: Set[str],
    ):
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
                if value != '*':
                    if isinstance(value, list):
                        if all(isinstance(x, str) for x in value):
                            continue
                else:
                    continue
                raise ConfigurationError(
                    f'Channel config has wrong type: {key}'
                )


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

    config = Config(**toml.load(path.open()))

    return config
