from ._box import Box
from .apps import App, BaseApp, route
from .parsers import KWARGS_DICT, parse_option_and_arguments
from .tasks import CronTask
from .utils import (
    CONTAINER,
    SPACE_RE,
    is_container,
)

# (:class:`Box`) Default Box instance
box = Box()
