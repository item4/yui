from decimal import Decimal
from typing import Dict, List, Union

import aiomcache

from .utils import json

DATA_TYPE = Union[str, bytes, bool, int, float, Decimal, Dict, List]


class Cache:

    def __init__(self, mc: aiomcache.Client, prefix: str = '') -> None:
        self.mc = mc
        self.prefix = prefix.encode()

    def _key(self, key: Union[str, bytes]) -> bytes:
        if isinstance(key, str):
            key = key.encode()
        return self.prefix + key

    async def set(
        self,
        key: Union[str, bytes],
        value: DATA_TYPE,
        exptime: int = 0,
    ) -> bool:
        data = json.dumps(value).encode()
        key = self._key(key)
        return await self.mc.set(key, data, exptime=exptime)

    async def add(
        self,
        key: Union[str, bytes],
        value: DATA_TYPE,
        exptime: int = 0,
    ) -> bool:
        data = json.dumps(value).encode()
        key = self._key(key)
        return await self.mc.add(key, data, exptime=exptime)

    async def get(self, key: Union[str, bytes], default=None) -> DATA_TYPE:
        key = self._key(key)
        data = await self.mc.get(key)
        if data is None:
            return default
        return json.loads(data)

    async def multi_get(self, *keys: Union[str, bytes]) -> List[DATA_TYPE]:
        keys = [self._key(k) for k in keys]
        values = await self.mc.multi_get(*keys)
        return [None if v is None else json.loads(v) for v in values]

    async def delete(self, key: Union[str, bytes]):
        key = self._key(key)
        await self.mc.delete(key)
