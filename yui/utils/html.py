from lxml.etree import strip_elements
from lxml.html import HTMLParser
from lxml.html import fromstring

USELESS_TAGS = frozenset(
    {
        "head",
        "script",
        "style",
        "iframe",
        "noscript",
    },
)


def get_root(
    html: str | bytes,
    *,
    useless_tags: list[str] | None = None,
    remove_comments: bool = True,
):
    """Get root of DOM Tree without useless data"""

    parser = HTMLParser(remove_comments=remove_comments)
    h = fromstring(html, parser=parser)
    if useless_tags is None:
        useless_tags = list(USELESS_TAGS)
    strip_elements(h, *useless_tags, with_tail=False)
    return h


def strip_tags(text: str) -> str:
    """Remove HTML Tags from input text"""

    return str(fromstring(text).text_content())
