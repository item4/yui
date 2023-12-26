from decimal import Decimal
from typing import TypeAlias

from redis.asyncio import Redis

from .utils import json

DATA_TYPE: TypeAlias = (
    str | bytes | bool | int | float | Decimal | dict | list | None
)


class Cache:
    def __init__(self, redis_client: Redis, prefix: str = "") -> None:
        self.redis_client = redis_client
        self.prefix = prefix.encode()

    def _key(self, key: str | bytes) -> bytes:
        if isinstance(key, str):
            key = key.encode()
        return self.prefix + key

    async def set(
        self,
        key: str | bytes,
        value: DATA_TYPE,
        exptime: int | None = None,
    ):
        data = json.dumps(value).encode()
        key = self._key(key)
        await self.redis_client.set(key, data, ex=exptime)

    async def get(self, key: str | bytes, default=None) -> DATA_TYPE:
        key = self._key(key)
        data = await self.redis_client.get(key)
        if data is None:
            return default
        return json.loads(data.decode())

    async def delete(self, key: str | bytes):
        key = self._key(key)
        await self.redis_client.delete(key)

    async def flushall(self):
        await self.redis_client.flushall()

    async def close(self):
        await self.redis_client.aclose()
