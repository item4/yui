from typing import Optional, Union

from .encoder import bool2str
from .endpoint import Endpoint
from .type import APIResponse
from ..types.user import User


class Im(Endpoint):

    name = 'im'

    async def list(
        self,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> APIResponse:
        """https://api.slack.com/methods/im.list"""

        params = {}
        if cursor:
            params['cursor'] = cursor
        if limit:
            params['limit'] = str(limit)

        return await self._call('list', params)

    async def open(
        self,
        user: Union[User, str],
        include_locale: Optional[bool] = None,
        return_im: Optional[bool] = None,
    ) -> APIResponse:
        """https://api.slack.com/methods/im.open"""

        if isinstance(user, str):
            user_id = user
        else:
            user_id = user.id

        params = {
            'user': user_id,
        }
        if include_locale is not None:
            params['include_locale'] = bool2str(include_locale)
        if return_im is not None:
            params['return_im'] = bool2str(return_im)

        return await self._call('open', params)
