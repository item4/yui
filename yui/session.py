import socket

from aiohttp.resolver import AsyncResolver

from aiohttp_doh import ClientSession

import ujson

__all__ = 'client_session',


class YuiAsyncResolver(AsyncResolver):
    """DNS resolver with aiodns but forced AF_INET family."""

    def resolve(self, host, port=0, family=socket.AF_INET):
        return super(
            YuiAsyncResolver,
            self,
        ).resolve(host, port, socket.AF_INET)


def client_session(*args, **kwargs) -> ClientSession:
    """aiohttp.client.ClientSession with DNS over HTTPS"""

    return ClientSession(
        *args,
        **kwargs,
        json_loads=ujson.loads,
        resolver_class=YuiAsyncResolver,
    )
