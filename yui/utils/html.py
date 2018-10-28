import lxml.html

__all__ = (
    'strip_tags',
)


def strip_tags(text: str) -> str:
    """Remove HTML Tags from input text"""

    return lxml.html.fromstring(text).text_content()
