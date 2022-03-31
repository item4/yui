import re
import shlex
import typing

SPACE_RE = re.compile(r"[\s\xa0]+")

CONTAINER = (set, tuple, list)


def is_container(t) -> bool:
    """Check given value is container type?"""

    return t in CONTAINER or typing.get_origin(t) in CONTAINER


def split_chunks(text: str, use_shlex: bool) -> list[str]:
    if use_shlex:
        lex = shlex.shlex(text, posix=True)
        lex.whitespace_split = True
        lex.whitespace += "\xa0"
        lex.commenters = ""
        return list(lex)
    return SPACE_RE.split(text)
