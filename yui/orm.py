from attrdict import AttrDict

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.event import listens_for
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import select

__all__ = 'Base', 'get_database_engine'

Base = declarative_base()


def get_database_engine(config: AttrDict) -> Engine:
    try:
        return config.DATABASE_ENGINE
    except AttributeError:
        db_url = config.DATABASE_URL
        echo = config.DATABASE_ECHO
        engine = create_engine(db_url, echo=echo)

        @listens_for(engine, 'engine_connect')
        def ping_connection(connection, branch):
            """
            Disconnect handling

            http://docs.sqlalchemy.org/en/latest/core/
            pooling.html#disconnect-handling-pessimistic

            """

            if branch:
                return

            save_should_close_with_result = connection.should_close_with_result
            connection.should_close_with_result = False

            try:
                connection.scalar(select([1]))
            except DBAPIError as err:
                if err.connection_invalidated:
                    connection.scalar(select([1]))
                else:
                    raise
            finally:
                connection.should_close_with_result = \
                    save_should_close_with_result

        return engine
