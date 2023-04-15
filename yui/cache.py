from decimal import Decimal
from typing import TypeAlias

from emcache.client import _Client
from emcache.client import Client

from .utils import json

DATA_TYPE: TypeAlias = (
    str | bytes | bool | int | float | Decimal | dict | list | None
)


class Cache:
    def __init__(self, mc: Client | _Client, prefix: str = "") -> None:
        self.mc = mc
        self.prefix = prefix.encode()

    def _key(self, key: str | bytes) -> bytes:
        if isinstance(key, str):
            key = key.encode()
        return self.prefix + key

    async def set(
        self,
        key: str | bytes,
        value: DATA_TYPE,
        exptime: int = 0,
    ):
        data = json.dumps(value).encode()
        key = self._key(key)
        await self.mc.set(key, data, exptime=exptime)

    async def add(
        self,
        key: str | bytes,
        value: DATA_TYPE,
        exptime: int = 0,
    ):
        data = json.dumps(value).encode()
        key = self._key(key)
        await self.mc.add(key, data, exptime=exptime)

    async def get(self, key: str | bytes, default=None) -> DATA_TYPE:
        key = self._key(key)
        data = await self.mc.get(key)
        if data is None:
            return default
        return json.loads(data.value.decode())

    async def get_many(self, *keys: str | bytes) -> dict[str, DATA_TYPE]:
        prefixed_keys = [self._key(k) for k in keys]
        values = await self.mc.get_many(prefixed_keys)
        return {
            k.decode(): None if v is None else json.loads(v.value.decode())
            for k, v in values.items()
        }

    async def delete(self, key: str | bytes):
        key = self._key(key)
        await self.mc.delete(key)

    async def flush_all(self):
        await self.mc.flush_all(
            self.mc._cluster.nodes[0].memcached_host_address
        )

    async def close(self):
        await self.mc.close()
