from collections import defaultdict
from datetime import timedelta

from .apps import Apps
from .chat import Chat
from .conversations import Conversations
from .users import Users


def _limit_to_timedelta(limit: int) -> timedelta:
    return timedelta(microseconds=(60 / (limit * 0.9)) * 1_000_000)


TIER1 = _limit_to_timedelta(1)  # 1+ per minute
TIER2 = _limit_to_timedelta(20)  # 20+ per minute
TIER3 = _limit_to_timedelta(50)  # 50+ per minute
TIER4 = _limit_to_timedelta(100)  # 100+ per minute
POST_MESSAGE = _limit_to_timedelta(60)  # 1 per second


class SlackAPI:
    """Slack API Interface"""

    apps: Apps
    converstations: Conversations
    chat: Chat
    users: Users

    def __init__(self, bot) -> None:
        """Initialize"""

        self.apps = Apps(bot)
        self.chat = Chat(bot)
        self.conversations = Conversations(bot)
        self.users = Users(bot)

        self.throttle_interval: defaultdict[str, timedelta] = defaultdict(
            lambda: TIER3
        )

        # apps.connections tier 1
        self.throttle_interval["apps.connections.open"] = TIER1

        # chat tier 3
        self.throttle_interval["chat.delete"] = TIER3
        # chat tier 4
        self.throttle_interval["chat.postEphemeral"] = TIER4
        # chat special
        self.throttle_interval["chat.postMessage"] = POST_MESSAGE

        # conversations tier 2
        self.throttle_interval["conversations.list"] = TIER2
        # conversations tier 3
        self.throttle_interval["conversations.history"] = TIER3
        self.throttle_interval["conversations.info"] = TIER3
        self.throttle_interval["conversations.open"] = TIER3
        self.throttle_interval["conversations.replies"] = TIER3

        # users tier 2
        self.throttle_interval["users.list"] = TIER2
        # users tier 4
        self.throttle_interval["users.info"] = TIER4

        # rtm tier 1
        self.throttle_interval["rtm.start"] = TIER1
