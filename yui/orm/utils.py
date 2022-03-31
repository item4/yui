from sqlalchemy.sql.expression import func

TRUNCATE_QUERY = {
    "mysql": "TRUNCATE TABLE {};",
    "postgresql": "TRUNCATE TABLE {} RESTART IDENTITY CASCADE;",
    "sqlite": "DELETE FROM {};",
}


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
