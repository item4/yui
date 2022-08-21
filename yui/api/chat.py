from typing import Any

from .endpoint import Endpoint
from ..types.base import ChannelID
from ..types.base import Ts
from ..types.base import UserID
from ..types.slack.attachment import Attachment
from ..types.slack.block import Block
from ..types.slack.response import APIResponse


class Chat(Endpoint):

    name = "chat"

    async def delete(
        self,
        channel: ChannelID,
        ts: Ts,
        *,
        token: str | None = None,
    ) -> APIResponse:
        """https://api.slack.com/methods/chat.delete"""

        params = {
            "channel": str(channel),
            "ts": str(ts),
        }

        return await self._call("delete", params, token=token)

    async def postEphemeral(
        self,
        channel: ChannelID,
        user: UserID,
        text: str | None = None,
        *,
        attachments: list[Attachment] | None = None,
        blocks: list[Block] | None = None,
        icon_emoji: str | None = None,
        icon_url: str | None = None,
        link_names: bool | None = None,
        parse: str | None = None,
        thread_ts: Ts | None = None,
        username: str | None = None,
        token: str | None = None,
    ) -> APIResponse:
        """https://api.slack.com/methods/chat.postEphemeral"""

        params: dict[str, Any] = {
            "channel": channel,
            "user": user,
        }

        if text is None and blocks is None and attachments is None:
            raise TypeError("text or attachement or blocks is required.")

        if text is not None:
            params["text"] = text

        if attachments is not None:
            params["attachments"] = attachments

        if blocks is not None:
            params["blocks"] = blocks

        if icon_emoji is not None:
            params["icon_emoji"] = icon_emoji

        if icon_url is not None:
            params["icon_url"] = icon_url

        if link_names is not None:
            params["link_names"] = link_names

        if parse is not None:
            params["parse"] = parse

        if thread_ts is not None:
            params["thread_ts"] = thread_ts

        if username is not None:
            params["username"] = username

        return await self._call(
            "postEphemeral",
            params,
            token=token,
            json_mode=True,
        )

    async def postMessage(
        self,
        channel: ChannelID,
        text: str | None = None,
        *,
        attachments: list[Attachment] | None = None,
        blocks: list[Block] | None = None,
        icon_emoji: str | None = None,
        icon_url: str | None = None,
        link_names: bool | None = None,
        mrkdwn: bool = True,
        parse: str | None = None,
        reply_broadcast: bool | None = None,
        thread_ts: Ts | None = None,
        unfurl_links: bool | None = None,
        unfurl_media: bool | None = None,
        username: str | None = None,
        token: str | None = None,
    ) -> APIResponse:
        """https://api.slack.com/methods/chat.postMessage"""

        params: dict[str, Any] = {
            "channel": channel,
        }

        if text is None and blocks is None and attachments is None:
            raise TypeError("text or attachement or blocks is required.")

        if text is not None:
            params["text"] = text

        if attachments is not None:
            params["attachments"] = attachments

        if blocks is not None:
            params["blocks"] = blocks

        if icon_emoji is not None:
            params["icon_emoji"] = icon_emoji

        if icon_url is not None:
            params["icon_url"] = icon_url

        if link_names is not None:
            params["link_names"] = link_names

        if mrkdwn is not None:
            params["mrkdwn"] = mrkdwn

        if parse is not None:
            params["parse"] = parse

        if reply_broadcast is not None:
            params["reply_broadcast"] = reply_broadcast

        if thread_ts is not None:
            params["thread_ts"] = thread_ts

        if unfurl_links is not None:
            params["unfurl_links"] = unfurl_links

        if unfurl_media is not None:
            params["unfurl_media"] = unfurl_media

        if username is not None:
            params["username"] = username

        return await self._call(
            "postMessage",
            params,
            token=token,
            json_mode=True,
        )
