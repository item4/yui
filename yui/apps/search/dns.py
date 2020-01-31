import asyncio
from typing import List, NamedTuple
from urllib.parse import urlencode

from aiohttp.client_exceptions import ClientConnectionError, ContentTypeError

from ...box import box
from ...command import argument, option
from ...event import Message
from ...session import client_session
from ...transform import extract_url
from ...utils import json


class DNSServer(NamedTuple):
    """DNS Server info."""

    name: str
    ip: str


class Result(NamedTuple):

    server_name: str
    server_ip: str
    a_record: str
    error: bool


SERVER_LIST_V4: List[DNSServer] = [
    DNSServer('KT', '168.126.63.1'),
    DNSServer('KT', '168.126.63.2'),
    DNSServer('SK', '210.220.163.82'),
    DNSServer('SK', '219.250.36.130'),
    DNSServer('Dacom', '164.124.101.2'),
    DNSServer('Dacom', '203.248.252.2'),
    DNSServer('Powercom', '164.124.107.9'),
    DNSServer('Dreamline', '210.181.1.24'),
    DNSServer('Dreamline', '210.181.4.25'),
    DNSServer('Google', '8.8.8.8'),
    DNSServer('Google', '8.8.4.4'),
    DNSServer('OpenDNS', '208.67.222.222'),
    DNSServer('CloudFlare', '1.1.1.1'),
    DNSServer('CloudFlare', '1.0.0.1'),
    DNSServer('Quad9', '9.9.9.9'),
    DNSServer('Quad9', '149.112.112.112'),
]

SERVER_LIST_V6: List[DNSServer] = [
    DNSServer('Google', '2001:4860:4860::8888'),
    DNSServer('Google', '2001:4860:4860::8844'),
    DNSServer('Quad9', '2620:fe::fe'),
]


async def is_ipv6_enabled() -> bool:
    try:
        async with client_session() as session:
            async with session.get('http://ipv6.icanhazip.com'):
                return True
    except:  # noqa
        return False


async def query_custom(domain: str, ip: str) -> Result:
    name = 'Custom Input'
    for s in SERVER_LIST_V4 + SERVER_LIST_V6:
        if ip == s.ip:
            name = s.name
            break
    server = DNSServer(name, ip)
    return await query(domain, server)


async def query(domain: str, server: DNSServer) -> Result:
    url = 'http://checkdnskr.appspot.com/api/lookup?{}'.format(
        urlencode({
            'domain': domain,
            'ip': server.ip,
        })
    )
    async with client_session() as session:
        async with session.get(url) as res:
            async with res:
                if res.status == 200:
                    try:
                        data = await res.json(loads=json.loads)
                        data['error'] = False
                    except ContentTypeError:
                        data = {
                            'A': '',
                            'error': True,
                        }
                    return Result(
                        server_name=server.name,
                        server_ip=server.ip,
                        a_record=data['A'],
                        error=data['error'],
                    )

                return Result(
                    server_name=server.name,
                    server_ip=server.ip,
                    a_record='',
                    error=False,
                )


@box.command('dns')
@option('--dns', '-d', dest='server_list', multiple=True)
@argument('domain', transform_func=extract_url)
async def dns(bot, event: Message, server_list: List[str], domain: str):
    """
    주어진 도메인의 A레코드 조회

    주어진 도메인에 대해 많이 쓰이는 DNS들에서 A레코드 값을 가져옵니다.

    `{PREFIX}dns item4.net` (`item4.net`의 A 레코드를 국내에서 많이 쓰이는 DNS들에서 조회)
    `{PREFIX}dns --dns 8.8.8.8 item4.net` (`8.8.8.8`에서 A레코드 조회)

    `--dns`/`-d` 인자는 여러개 지정 가능합니다.

    """

    chat = await bot.say(
        event.channel,
        f'`{domain}`에 대해 조회를 시작합니다. 조회에는 시간이 소요되니 기다려주세요!'
    )
    if chat.body['ok']:
        tasks = []
        if server_list:
            for ip in server_list:
                tasks.append(query_custom(domain, ip))
        else:
            servers = SERVER_LIST_V4
            if await is_ipv6_enabled():
                servers += SERVER_LIST_V6

            for server in servers:
                tasks.append(query(domain, server))

        ok, no = await asyncio.wait(tasks)

        result: List[Result] = []
        for r in ok:
            try:
                res = r.result()
            except ClientConnectionError:
                continue
            result.append(res)

        result.sort(key=lambda x: x.server_name)

        await bot.say(
            event.channel,
            '<@{}>, `{}`에 대해 {} DNS에 조회한 결과에요!\n\n{}'.format(
                event.user.id,
                domain,
                '주어진' if server_list else '많이 쓰이는',
                '\n'.join(
                    f'{r.server_name}({r.server_ip}): 조회중 에러발생'
                    if r.error else
                    f'{r.server_name}({r.server_ip}): {r.a_record}'
                    for r in result
                )
            ),
            thread_ts=chat.body['ts'],
        )
