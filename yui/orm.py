from attrdict import AttrDict

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.event import listens_for
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session as _Session, identity
from sqlalchemy.sql.expression import select

__all__ = 'Base', 'Session', 'get_database_engine', 'make_session'

Base = declarative_base()


class Session(_Session):

    def __getstate__(self):
        return dict(
            weak_identity_map=self._identity_cls == identity.WeakInstanceDict,
            bind=dict(
                DATABASE_URL=self.bind.url,
                DATABASE_ECHO=self.bind.echo,
            ),
            autoflush=self.autoflush,
            expire_on_commit=self.expire_on_commit,
            _enable_transaction_accounting=self._enable_transaction_accounting,
            binds=None,
            extension=None,
            autocommit=self.autocommit,
            enable_baked_queries=self.enable_baked_queries,
            info=self.info,
        )

    def __setstate__(self, state):
        state['bind'] = get_database_engine(AttrDict(state['bind']))
        self.__init__(**state)


def make_session(*args, **kwargs) -> Session:  # noqa
    kwargs['autocommit'] = True
    return Session(*args, **kwargs)


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
