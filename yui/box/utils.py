import re
import shlex

SPACE_RE = re.compile(r"[\s\xa0]+")


def split_chunks(text: str, use_shlex: bool) -> list[str]:
    if use_shlex:
        lex = shlex.shlex(text, posix=True)
        lex.whitespace_split = True
        lex.whitespace += "\xa0"
        lex.commenters = ""
        return list(lex)
    return SPACE_RE.split(text)
