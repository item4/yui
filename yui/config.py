import pathlib
import sys

import toml

__all__ = 'error', 'load',


def error(msgfmt, *args):
    msg = msgfmt.format(*args)
    print(msg, file=sys.stderr)
    raise SystemExit(1)


def load(path: pathlib.Path) -> dict:
    """Load configuration from given path."""

    if not path.exists():
        error('File do not exists.')

    if not path.is_file():
        error('Given path is not file.')

    if not path.match('*.config.toml'):
        error('File suffix must be *.config.toml')

    config = toml.load(path.name)

    return config
