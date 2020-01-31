import lxml.html


def strip_tags(text: str) -> str:
    """Remove HTML Tags from input text"""

    return str(lxml.html.fromstring(text).text_content())
