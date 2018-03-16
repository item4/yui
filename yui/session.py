import socket

from aiohttp.client import ClientSession
from aiohttp.connector import TCPConnector
from aiohttp.resolver import AsyncResolver

__all__ = 'client_session',


class YuiAsyncResolver(AsyncResolver):
    """DNS resolver with aiodns but forced AF_INET family."""

    def resolve(self, host, port=0, family=socket.AF_INET):
        return super(
            YuiAsyncResolver,
            self,
        ).resolve(host, port, socket.AF_INET)


def client_session(*args, **kwargs) -> ClientSession:
    """aiohttp.client.ClientSession with aiodns"""

    resolver = YuiAsyncResolver()
    connector = TCPConnector(resolver=resolver)

    return ClientSession(*args, **kwargs, connector=connector)
