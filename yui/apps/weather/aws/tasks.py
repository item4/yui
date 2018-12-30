from sqlalchemy.orm.exc import NoResultFound

import ujson

from ...shared.cache import JSONCache
from ....box import box
from ....session import client_session
from ....utils.datetime import now


def get_or_create_cache(name: str, sess) -> JSONCache:
    try:
        cache = sess.query(JSONCache).filter_by(name=name).one()
    except NoResultFound:
        cache = JSONCache()
        cache.name = name
    return cache


@box.cron('*/1 * * * *')
async def crawl(sess):
    """Crawl from Korea Meteorological Administration AWS via item4.net"""

    data = None
    url = 'https://item4.net/api/weather/'
    async with client_session() as session:
        async with session.get(url) as res:
            data = await res.json(loads=ujson.loads)

    cache = get_or_create_cache('aws', sess)
    cache.body = data
    cache.created_at = now()

    with sess.begin():
        sess.add(cache)
