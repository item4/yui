import datetime
from typing import List

import aiohttp

import lxml.html

from .models import AWS
from ....bot import Bot
from ....box import box
from ....orm import EngineConfig, subprocess_session_manager
from ....session import client_session
from ....util import truncate_table


def process(html: str, engine_config: EngineConfig):
    with subprocess_session_manager(engine_config) as sess:
        h = lxml.html.fromstring(html)
        try:
            observed_at = datetime.datetime.strptime(
                h.cssselect('span.ehead')[0].text_content().replace(
                    '[ 매분관측자료 ] ',
                    ''
                ),
                '%Y.%m.%d.%H:%M'
            )
        except IndexError:
            return []

        records: List[AWS] = []
        for tr in h.cssselect('table table tr')[1:]:
            record = AWS()
            try:
                record.id = int(tr[0].text_content())
                record.name = tr[1].text_content().replace('*', '').strip()
            except (ValueError, IndexError):
                continue
            try:
                record.height = int(tr[2].text_content()[:-1])
            except (ValueError, IndexError):
                record.height = -1

            try:
                record.is_raining = {'○': False, '●': True}.get(
                    tr[3].text_content()
                )
            except IndexError:
                pass
            try:
                record.rain15 = float(tr[4].text_content())
            except (ValueError, IndexError):
                pass
            try:
                record.rain60 = float(tr[5].text_content())
            except (ValueError, IndexError):
                pass
            try:
                record.rain3h = float(tr[6].text_content())
            except (ValueError, IndexError):
                pass
            try:
                record.rain6h = float(tr[7].text_content())
            except (ValueError, IndexError):
                pass
            try:
                record.rain12h = float(tr[8].text_content())
            except (ValueError, IndexError):
                pass
            try:
                record.rainday = float(tr[9].text_content())
            except (ValueError, IndexError):
                pass

            try:
                record.temperature = float(tr[10].text_content())
            except (ValueError, IndexError):
                pass

            try:
                wind_d1 = tr[12].text_content().strip()
            except IndexError:
                pass
            else:
                record.wind_direction1 = wind_d1 if wind_d1 else None
            try:
                record.wind_speed1 = float(tr[13].text_content())
            except (ValueError, IndexError):
                pass
            try:
                wind_d10 = tr[15].text_content().strip()
            except IndexError:
                pass
            else:
                record.wind_direction10 = wind_d10 if wind_d10 else None
            try:
                record.wind_speed10 = float(tr[16].text_content())
            except (ValueError, IndexError):
                pass

            try:
                record.humidity = int(tr[17].text_content())
            except (ValueError, IndexError):
                pass

            try:
                record.pressure = float(tr[18].text_content())
            except (ValueError, IndexError):
                pass

            try:
                record.location = tr[19].text_content()
            except IndexError:
                pass

            record.observed_at = observed_at

            records.append(record)

        if not records:
            return

        truncate_table(sess.bind, AWS)

        with sess.begin():
            sess.add_all(records)


@box.crontab('*/3 * * * *')
async def crawl(bot: Bot, engine_config: EngineConfig):
    """Crawl from Korea Meteorological Administration AWS."""

    html = ''
    url = 'http://www.kma.go.kr/cgi-bin/aws/nph-aws_txt_min'
    try:
        async with client_session() as session:
            async with session.get(url) as res:
                html = await res.text()
    except aiohttp.client_exceptions.ClientConnectorError:
        return
    except aiohttp.client_exceptions.ServerDisconnectedError:
        return

    await bot.run_in_other_process(process, html, engine_config)
