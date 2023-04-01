from ..types.base import UserID
from ..types.slack.response import APIResponse
from ..types.user import User
from .encoder import bool2str
from .endpoint import Endpoint


class Users(Endpoint):
    name = "users"

    async def info(self, user: User | UserID) -> APIResponse:
        """https://api.slack.com/methods/users.info"""

        user_id = user.id if isinstance(user, User) else user

        return await self._call("info", {"user": user_id})

    async def list(
        self,
        curser: str | None = None,
        include_locale: bool | None = None,
        limit: int = 0,
        presence: bool | None = None,
    ) -> APIResponse:
        params = {}

        if curser:
            params["cursor"] = curser

        if include_locale is not None:
            params["include_locale"] = bool2str(include_locale)

        if limit:
            params["limit"] = str(limit)

        if presence is not None:
            params["presence"] = bool2str(presence)

        return await self._call("list", params)
