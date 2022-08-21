from .endpoint import Endpoint
from ..types.slack.response import APIResponse


class Connections(Endpoint):

    name = "apps.connections"

    async def open(
        self,
        *,
        token: str,
    ) -> APIResponse:
        """https://api.slack.com/methods/apps.connections.open"""

        return await self._call("open", {}, token=token, json_mode=True)


class Apps:
    connections: Connections

    def __init__(self, bot):
        self.connections = Connections(bot)
