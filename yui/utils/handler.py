from typing import Union

from ..types.handler import HANDLER_CALL_TYPE, Handler

__all__ = (
    'get_handler',
)


def get_handler(obj: Union[HANDLER_CALL_TYPE, Handler]) -> Handler:
    if isinstance(obj, Handler):
        return obj
    return Handler(obj)
