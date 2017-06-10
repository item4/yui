from .util import AttrDict, bool2str


__all__ = 'SlackAPI',


class SlackAPI:
    """API Interface"""

    def __init__(self, bot):
        """Initialize"""

        self.bot = bot

        self.chat = AttrDict()
        self.chat.postMessage = self.chat_post_message

        self.users = AttrDict()
        self.users.info = self.users_info

    async def chat_post_message(
            self,
            channel: str,
            text: str,
            parse=None,
            link_names: bool=None,
            attachments: list=None,
            unfurl_links: bool=None,
            unfurl_media: bool=None,
            username: str=None,
            as_user: bool=None,
            icon_url: str=None,
            icon_emoji: str=None,
            thread_ts: str=None,
            reply_broadcast: bool=None,
    ):
        """https://api.slack.com/methods/chat.postMessage"""

        param = {
            'channel': channel,
            'text': text,
        }

        if parse is not None:
            param['parse'] = parse

        if link_names is not None:
            param['link_names'] = bool2str(link_names)

        if attachments is not None:
            param['attachments'] = json.dumps(attachments)

        if unfurl_links is not None:
            param['unfurl_links'] = bool2str(unfurl_links)

        if unfurl_media is not None:
            param['unfurl_media'] = bool2str(unfurl_media)

        if username is not None:
            param['username'] = username

        if as_user is not None:
            param['as_user'] = bool2str(as_user)

        if icon_url is not None:
            param['icon_url'] = icon_url

        if icon_emoji is not None:
            param['icon_emoji'] = icon_emoji

        if thread_ts is not None:
            param['thread_ts'] = thread_ts

        if reply_broadcast is not None:
            param['reply_broadcast'] = bool2str(reply_broadcast)

        return await self.bot.call('chat.postMessage', param)

    async def users_info(self, user: str):
        """https://api.slack.com/methods/users.info"""

        return await self.bot.call(
            'users.info',
            {
                'user': user,
            }
        )
