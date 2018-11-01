from .channels import Channels
from .chat import Chat
from .encoder import (
    SlackEncoder,
    bool2str,
    remove_none,
)
from .endpoint import Endpoint
from .groups import Groups
from .im import Im
from .type import (
    Action,
    ActionDataSource,
    ActionStyle,
    ActionType,
    Attachment,
    Confirmation,
    Field,
    OptionField,
    OptionGroup,
    call_or_none,
)
from .users import Users


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
