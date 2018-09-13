from .channels import Channels
from .chat import Chat
from .groups import Groups
from .im import Im
from .type import Action, Attachment, Confirmation, Field, OptionField
from .users import Users


__all__ = (
    'Action',
    'Attachment',
    'Confirmation',
    'Field',
    'OptionField',
    'SlackAPI',
)


class SlackAPI:
    """Slack API Interface"""

    channels: Channels
    chat: Chat
    groups: Groups
    im: Im
    users: Users

    def __init__(self, bot) -> None:
        """Initialize"""

        self.channels = Channels(bot)
        self.chat = Chat(bot)
        self.groups = Groups(bot)
        self.im = Im(bot)
        self.users = Users(bot)
