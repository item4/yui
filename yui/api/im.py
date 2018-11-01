from typing import Optional

from .endpoint import Endpoint


class Im(Endpoint):

    name = 'im'

    async def list(
        self,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
    ):
        """https://api.slack.com/methods/im.list"""

        params = {}
        if cursor:
            params['cursor'] = cursor
        if limit:
            params['limit'] = str(limit)

        return await self._call('list', params)
