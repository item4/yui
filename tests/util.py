import json

from typing import Any, Callable, Dict, List, NamedTuple, Tuple

from yui.api import SlackAPI
from yui.bot import Bot


class Call(NamedTuple):
    """API Call from bot"""

    method: str
    data: Dict[str, str]


class FakeBot(Bot):
    """Fake bot for test"""

    def __init__(self) -> None:
        self.call_queue: List[Call] = []
        self.api = SlackAPI(self)
        self.channels: Dict[str, Dict[str, Any]] = {}

    async def call(self, method: str, data: Dict[str, str]=None):
        self.call_queue.append(Call(method, data))


class FakeImportLib:
    """Fake object for importlib.import_module."""

    def __init__(self) -> None:
        self.import_queue: List[str] = []

    def import_module(self, path: str):
        self.import_queue.append(path)


class FakeClientSession:
    """Fake class for aiohttp.ClientSession."""

    def __init__(self) -> None:
        self.responses: Dict[Tuple[str, str], Callable] = {}

    def add(self, method: str, url: str):
        def internal(func: Callable):
            self.responses[(method, url)] = func
        return internal

    def get(self, url: str):
        return self.add('get', url)

    def post(self, url: str):
        return self.add('post', url)

    def patch(self, url: str):
        return self.add('patch', url)

    def put(self, url: str):
        return self.add('put', url)

    def delete(self, url: str):
        return self.add('delete', url)

    def __call__(self, *args, **kwargs):
        return self

    def __enter__(self):
        return FakeClientSessionContext(self)

    async def __aenter__(self):
        return FakeClientSessionContext(self)

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class FakeClientSessionContext:
    """Fake context manager for aiohttp.ClientSession."""

    def __init__(self, parent: FakeClientSession) -> None:
        self.parent = parent

    def request(self, method: str, url, **kwargs):
        for key, callback in self.parent.responses.items():
            if (method, url) == key:
                res = callback(**kwargs)
                try:
                    status_code, data = res
                except ValueError:
                    status_code = 200
                    data = res
                return FakeResponse(data=data, status_code=status_code)
        raise RuntimeError()

    def get(self, url, **kwargs):
        return self.request('get', url, **kwargs)

    def post(self, url, **kwargs):
        return self.request('post', url, **kwargs)

    def patch(self, url, **kwargs):
        return self.request('patch', url, **kwargs)

    def put(self, url, **kwargs):
        return self.request('put', url, **kwargs)

    def delete(self, url, **kwargs):
        return self.request('delete', url, **kwargs)


class FakeResponse:
    """Fake object for aiohttp response."""

    def __init__(self, data: str, status_code: int) -> None:
        self.data = data
        self.status = status_code

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def text(self):
        return self.data

    async def json(self, loads=json.loads):
        return loads(self.data)
