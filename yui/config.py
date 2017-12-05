import copy
import pathlib
import sys
from typing import Any, Dict, Sequence

from attrdict import AttrDict

import toml


__all__ = 'error', 'load',

DEFAULT = {
    'DEBUG': False,
    'PREFIX': '',
    'HANDLERS': (),
    'DATABASE_URL': '',
    'DATABASE_ECHO': False,
    'MODELS': (),
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


class Config(AttrDict):

    TOKEN: str
    DEBUG: bool
    PREFIX: str
    HANDLERS: Sequence[str]
    DATABASE_URL: str
    DATABASE_ECHO: bool
    MODELS: Sequence[str]
    LOGGING: Dict[str, Any]


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

    config = Config(copy.deepcopy(DEFAULT))
    config.update(toml.load(path.open()))

    return config
