import asyncio
from datetime import datetime
from decimal import Decimal

from valkey.asyncio import Valkey

from .utils import json
from .utils.datetime import fromtimestamp

type DataType = str | bytes | bool | int | float | Decimal | dict | list
type CacheKey = str | bytes


class Cache:
    def __init__(self, valkey_client: Valkey, prefix: str = "") -> None:
        self.valkey_client = valkey_client
        self.prefix = prefix.encode()
        self.is_ready = asyncio.Event()

    def _key(self, key: CacheKey) -> bytes:
        if isinstance(key, str):
            key = key.encode()
        return self.prefix + key

    async def set(
        self,
        key: CacheKey,
        value: DataType,
        exptime: int | None = None,
    ):
        data = json.dumps(value).encode()
        key = self._key(key)
        await self.valkey_client.set(key, data, ex=exptime)

    async def get[T: DataType](self, key: CacheKey, default: T | None = None) -> T | None:
        key = self._key(key)
        data = await self.valkey_client.get(key)
        if data is None:
            return default
        return json.loads(data.decode())

    async def set_dt(
        self,
        key: CacheKey,
        value: datetime,
        exptime: int | None = None,
    ):
        await self.set(key, value.timestamp(), exptime)

    async def get_dt(
        self,
        key: CacheKey,
        default: datetime | None = None,
    ) -> datetime | None:
        value: float | None = await self.get(key)  # type: ignore[assignment]
        if value is None:
            return default
        return fromtimestamp(value)

    async def delete(self, key: CacheKey):
        key = self._key(key)
        await self.valkey_client.delete(key)

    async def flushall(self):
        await self.valkey_client.flushall()

    async def close(self):
        await self.valkey_client.aclose()
