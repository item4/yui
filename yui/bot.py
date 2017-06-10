import asyncio
import json

import aiohttp


def bool2str(value: bool) -> str:
    if value:
        return 'true'
    return 'false'


class AttrDict(dict):
    """Helper object for attr get/set."""

    def __getattr__(self, item):
        return self[item]

    def __setattr__(self, key, value):
        self[key] = value


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


class Bot:
    """Yui."""

    def __init__(self, token: str, debug: bool=False):
        """Initialize"""

        self.token = token
        self.debug = debug
        self.queue = asyncio.Queue()
        self.api = SlackAPI(self)

    def run(self):
        """Run"""

        loop = asyncio.get_event_loop()
        loop.set_debug(self.debug)

        loop.run_until_complete(
            asyncio.wait(
                (
                    self.receive(self.queue.put),
                    self.process(self.queue.get),
                )
            )
        )
        loop.close()

    async def call(self, method: str, data: dict=None):
        """Call API methods."""

        with aiohttp.ClientSession() as session:

            form = aiohttp.FormData(data or {})
            form.add_field('token', self.token)
            async with session.post(
                'https://slack.com/api/{}'.format(method),
                data=form
            ) as response:
                assert 200 == response.status, ('{0} with {1} failed.'
                                                .format(method, data))
                return await response.json()

    async def say(self, channel: str, text: str) -> dict:
        """Shortcut for bot saying."""

        return await self.api.chat.postMessage(channel, text, as_user=True)

    async def process(self, get):
        """Process messages."""

        while True:
            message = await get()

            print(message)
            if message.get('type') == 'message':
                if message['text'].startswith('안녕 '):
                    user = await self.api.users.info(message.get('user'))
                    await self.say(
                        'test',
                        '안녕하세요! {}'.format(user['user']['name'])
                    )

    async def receive(self, put):
        """Receive stream from slack."""

        rtm = await self.call('rtm.start')
        assert rtm['ok'], "Error connecting to RTM."
        with aiohttp.ClientSession() as session:
            async with session.ws_connect(rtm['url']) as ws:
                async for msg in ws:
                    assert msg.tp == aiohttp.WSMsgType.text
                    message = json.loads(msg.data)
                    await put(message)
