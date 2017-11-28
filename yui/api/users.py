from .endpoint import Endpoint
from ..type import UserID

__all__ = 'Users',


class Users(Endpoint):

    name = 'users'

    async def info(self, user: UserID):
        """https://api.slack.com/methods/users.info"""

        return await self._call(
            'info',
            {
                'user': user,
            }
        )
