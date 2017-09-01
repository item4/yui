import datetime

from babel.dates import get_timezone

from sqlalchemy.sql.expression import func

__all__ = (
    'KST',
    'TRUNCATE_QUERY',
    'UTC',
    'bold',
    'bool2str',
    'code',
    'get_count',
    'italics',
    'preformatted',
    'quote',
    'strike',
    'truncate_table',
    'tz_none_to_kst',
    'tz_none_to_utc',
)

KST = get_timezone('Asia/Seoul')
UTC = get_timezone('UTC')

TRUNCATE_QUERY = {
    'mysql': 'TRUNCATE TABLE {};',
    'postgresql': 'TRUNCATE TABLE {} RESTART IDENTITY CASCADE;',
    'sqlite': 'DELETE FROM {};',
}


def tz_none_to_kst(dt: datetime.datetime) -> datetime.datetime:
    """Convert non tz datetime to KST."""

    return UTC.localize(dt).astimezone(KST)


def tz_none_to_utc(dt: datetime.datetime) -> datetime.datetime:
    """Convert non tz datetime to UTC."""

    return dt.astimezone(UTC)


def bold(text: str) -> str:
    """Make text to bold."""

    return f'*{text}*'


def italics(text: str) -> str:
    """Make text to italics."""

    return f'_{text}_'


def strike(text: str) -> str:
    """Make text to strike."""

    return f'~{text}~'


def code(text: str) -> str:
    """Make text to code."""

    return f'`{text}`'


def preformatted(text: str) -> str:
    """Make text to pre-formatted text."""

    return f'```{text}```'


def quote(text: str) -> str:
    """Make text to qoute."""

    return f'>{text}'


def bool2str(value: bool) -> str:
    """Return bool as str."""

    if value:
        return 'true'
    return 'false'


def truncate_table(engine, table_cls):
    """Truncate given table."""

    table_name = table_cls.__table__.name
    engine_name = engine.name

    with engine.begin() as conn:
        conn.execute(TRUNCATE_QUERY[engine_name].format(table_name))


def get_count(q) -> int:
    """
    Get count of record.

    https://gist.github.com/hest/8798884

    """

    count_q = q.statement.with_only_columns([func.count()]).order_by(None)
    count = q.session.execute(count_q).scalar()
    return count
