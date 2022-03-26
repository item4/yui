from sqlalchemy.ext.asyncio import AsyncSession


def make_session(*args, **kwargs) -> AsyncSession:
    kwargs['expire_on_commit'] = False
    return AsyncSession(*args, **kwargs)
