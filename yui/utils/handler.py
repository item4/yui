from ..types.handler import Handler
from ..types.handler import HANDLER_CALL_TYPE


def get_handler(obj: HANDLER_CALL_TYPE | Handler) -> Handler:
    if isinstance(obj, Handler):
        return obj
    return Handler(f=obj)
