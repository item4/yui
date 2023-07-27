from ..types.handler import HANDLER_CALL_TYPE
from ..types.handler import Handler


def get_handler(obj: HANDLER_CALL_TYPE | Handler) -> Handler:
    if isinstance(obj, Handler):
        return obj
    return Handler(f=obj)
