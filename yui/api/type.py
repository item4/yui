from typing import List, Optional

__all__ = 'Attachment', 'Field'


class Field:
    """Field on Attachment"""

    def __init__(self, title: str, value: str, short: bool) -> None:
        """Initialize"""

        self.title = title
        self.value = value
        self.short = short

    def __str__(self) -> str:
        return f'Field({self.title!r}, {self.value!r}, {self.short!r})'


class Attachment:
    """Slack Attachment"""

    def __init__(
        self,
        *,
        fallback: Optional[str]=None,
        color: Optional[str]=None,
        pretext: Optional[str]=None,
        author_name: Optional[str]=None,
        author_link: Optional[str]=None,
        author_icon: Optional[str]=None,
        title: Optional[str]=None,
        title_link: Optional[str]=None,
        text: Optional[str]=None,
        fields: Optional[List[Field]]=None,
        image_url: Optional[str]=None,
        thumb_url: Optional[str]=None,
        footer: Optional[str]=None,
        footer_icon: Optional[str]=None,
        ts: Optional[int]=None
    ) -> None:
        """Initialize"""

        self.fallback = fallback
        self.color = color
        self.pretext = pretext
        self.author_name = author_name
        self.author_link = author_link
        self.author_icon = author_icon
        self.title = title
        self.title_link = title_link
        self.text = text
        self.fields = fields if fields else []
        self.image_url = image_url
        self.thumb_url = thumb_url
        self.footer = footer
        self.footer_icon = footer_icon
        self.ts = ts

    def add_field(self, title: str, value: str, short: Optional[bool]=False):
        self.fields.append(Field(title, value, short))

    def __str__(self) -> str:
        return f'Attachment(title={self.title!r})'
