import enum
from typing import Any

import attr

from ..types.slack.response import APIResponse


def prepare_for_json(obj):
    if isinstance(obj, (list, tuple, set)):
        return [prepare_for_json(x) for x in obj]
    elif issubclass(obj.__class__, enum.Enum):
        return obj.value
    elif isinstance(obj, dict):
        return {
            prepare_for_json(k): prepare_for_json(v)
            for k, v in obj.items()
            if v is not None
            and ((isinstance(v, list) and v) or not isinstance(v, list))
        }
    elif isinstance(obj, str):
        return obj
    try:
        return prepare_for_json(attr.asdict(obj))
    except attr.exceptions.NotAnAttrsClassError:
        pass
    return obj


class Endpoint:
    """Slack API endpoint."""

    name: str

    def __init__(self, bot) -> None:
        self.bot = bot

    async def _call(
        self,
        method: str,
        data: dict[str, Any],
        *,
        token=None,
        json_mode: bool = False,
    ) -> APIResponse:
        if json_mode:
            data = prepare_for_json(data)

        return await self.bot.call(
            f'{self.name}.{method}',
            data,
            token=token,
            json_mode=json_mode,
        )
