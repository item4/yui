from typing import TypeAlias

#: :type:`type` User ID type. It must start with 'U' or 'W'.
UserID: TypeAlias = str

#: :type:`type` Public Channel ID type. It must start with 'C'.
PublicChannelID: TypeAlias = str

#: :type:`type` IM(as known as Direct Message) Channel ID type.
#: It must start with 'D'.
DirectMessageChannelID: TypeAlias = str

#: :type:`type` Group(as known as Private Channel) ID type.
#: It must start with 'G'.
PrivateChannelID: TypeAlias = str

ChannelID: TypeAlias = str

#: :type:`type` File ID type. It must start with 'F'.
FileID: TypeAlias = str

Comment: TypeAlias = dict

#: :type:`type` Comment ID type.
CommentID: TypeAlias = str

#: :type:`type` Type for slack event unique ID.
Ts: TypeAlias = str

#: :type:`type` Team ID type. It must start with 'T'.
TeamID: TypeAlias = str

#: :type:`type` Sub-team ID type. It must start with 'S'.
SubteamID: TypeAlias = str

#: :type:`type` App ID type. IT must start with 'A'.
AppID: TypeAlias = str

#: :type:`type` Bot ID type. It must start with 'B'.
BotID: TypeAlias = str

#: :type:`type` Type for store UnixTimestamp.
UnixTimestamp: TypeAlias = int
