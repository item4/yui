from .chat import Chat
from .conversations import Conversations
from .endpoint import Endpoint
from .users import Users


class SlackAPI:
    """Slack API Interface"""

    converstations: Conversations
    chat: Chat
    users: Users

    def __init__(self, bot) -> None:
        """Initialize"""

        self.conversations = Conversations(bot)
        self.chat = Chat(bot)
        self.users = Users(bot)
