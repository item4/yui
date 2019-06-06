from typing import Dict

from ..types.slack.response import APIResponse


class Endpoint:
    """Slack API endpoint."""

    name: str

    def __init__(self, bot) -> None:
        self.bot = bot

    async def _call(
        self,
        method: str,
        data: Dict[str, str],
        *,
        token=None,
    ) -> APIResponse:
        return await self.bot.call(f'{self.name}.{method}', data, token=token)
