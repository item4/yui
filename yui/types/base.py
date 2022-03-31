from typing import NewType
from typing import TypeAlias

#: :type:`type` User ID type. It must start with 'U' or 'W'.
UserID = NewType("UserID", str)

#: :type:`type` Public Channel ID type. It must start with 'C'.
PublicChannelID = NewType("PublicChannelID", str)

#: :type:`type` IM(as known as Direct Message) Channel ID type.
#: It must start with 'D'.
DirectMessageChannelID = NewType("DirectMessageChannelID", str)

#: :type:`type` Group(as known as Private Channel) ID type.
#: It must start with 'G'.
PrivateChannelID = NewType("PrivateChannelID", str)

ChannelID = PublicChannelID | PrivateChannelID | DirectMessageChannelID

#: :type:`type` Type for slack event unique ID.
Ts = NewType("Ts", str)

#: :type:`type` Type for store UnixTimestamp.
UnixTimestamp: TypeAlias = int
