import asyncio

from typing import Dict, List, NamedTuple
from urllib.parse import urlencode

import aiohttp

from ..box import box
from ..command import argument, option
from ..event import Message
from ..transform import extract_url


class DNSServer(NamedTuple):
    """DNS Server info."""

    name: str
    ip: str


class Result(NamedTuple):

    server_name: str
    server_ip: str
    a_record: str


SERVER_LIST: List[DNSServer] = [
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
    DNSServer('OpenDNS', '208.67.220.220'),
]


async def query_custom(domain: str, ip: str) -> Dict[str, str]:
    name = 'Custom Input'
    for s in SERVER_LIST:
        if ip == s.ip:
            name = s.name
            break
    server = DNSServer(name, ip)
    return await query(domain, server)


async def query(domain: str, server: DNSServer) -> Dict[str, str]:
    url = 'http://checkdnskr.appspot.com/api/lookup?{}'.format(
        urlencode({
            'domain': domain,
            'ip': server.ip,
        })
    )
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as res:
            result = await res.json()
            result['server_name'] = server.name
            result['server_ip'] = server.ip
            return result


@box.command('dns')
@option('--dns', '-d', dest='server_list', multiple=True)
@argument('domain', transform_func=extract_url)
async def dns(bot, event: Message, server_list: List[str], domain: str):
    await bot.say(
        event.channel,
        f'{domain} 에 대해 조회를 시작합니다. 조회에는 시간이 소요되니 기다려주세요!'
    )
    tasks = []
    if server_list:
        for ip in server_list:
            tasks.append(query_custom(domain, ip))
    else:
        for server in SERVER_LIST:
            tasks.append(query(domain, server))

    ok, no = await asyncio.wait(tasks)

    result: List[Result] = []
    for r in ok:
        try:
            res = r.result()
        except:
            continue
        result.append(Result(
            server_name=res['server_name'],
            server_ip=res['server_ip'],
            a_record=res['A'],
        ))

    result.sort(key=lambda x: x.server_name)

    await bot.say(
        event.channel,
        '{} 에 대해 {} DNS에 조회한 결과에요!\n\n{}'.format(
            domain,
            '주어진' if server_list else '많이 쓰이는',
            '\n'.join(
                f'{r.server_name}({r.server_ip}): {r.a_record}'
                for r in result
            )
        )
    )
