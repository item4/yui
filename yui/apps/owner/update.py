from typing import Any, Dict, List

from ...api import Attachment
from ...box import box
from ...command import C
from ...event import Message
from ...transform import extract_url

box.assert_config_required('OWNER_ID', str)
box.assert_channel_required('notice')

FLAG_MAP = {
    'primary': '428bca',
    'new': '428bca',
    'add': '428bca',
    'good': '5cb85c',
    'nice': '5cb85c',
    'update': '5cb85c',
    'patch': '5cb85c',
    'danger': 'd9534f',
    'del': 'd9534f',
    'delete': 'd9534f',
    'remove': 'd9534f',
    'bug': 'd9534f',
    'warning': 'd9534f',
    'info': '5bc0de',
    'test': '5bc0de',
    'internal': '5bc0de',
    'mics': '5bc0de',
}


def prepare(kw):
    if not kw:
        return
    for key, value in kw.items():
        kw[key] = value.strip()

    if 'title' in kw:
        kw['fallback'] = '{}: {}'.format(
            kw['title'],
            kw.get('text', '').replace('\n', ' '),
        ).strip()
    else:
        kw['fallback'] = kw.get('text', '').replace('\n', ' ').strip()


@box.command('update', aliases=['업데이트'])
async def update(bot, event: Message, raw: str):
    """
    봇을 통해 업데이트 공지 메시지를 전송합니다.

    `{PREFIX}update payload` (현재 채널)

    봇 주인만 사용 가능합니다.

    """

    if event.user.id == bot.config.OWNER_ID:
        lines = raw.splitlines()
        attachments: List[Attachment] = []
        kw: Dict[str, Any] = {}
        pretext = '유이 업데이트 안내'
        for line in lines:
            if line == '---':
                prepare(kw)
                if kw:
                    attachments.append(Attachment(**kw))
                    kw.clear()
            elif line.startswith('PRETEXT='):
                pretext = line[8:]
            elif line.startswith('TITLE='):
                kw['title'] = line[6:]
            elif line.startswith('COLOR='):
                kw['color'] = line[6:]
            elif line.startswith('LINK='):
                kw['title_link'] = extract_url(line[5:])
            elif line.startswith('FLAG='):
                flag = line[5:].lower()
                kw['color'] = FLAG_MAP[flag]
                if 'title' in kw:
                    kw['title'] = f"[{flag}] {kw['title']}"
            else:
                if 'text' not in kw:
                    kw['text'] = ''
                kw['text'] += f'{line.strip()}\n'
        if kw:
            prepare(kw)
            attachments.append(Attachment(**kw))

        await bot.api.chat.postMessage(
            channel=C.notice.get(),
            text=pretext,
            attachments=attachments,
            as_user=True,
        )
    else:
        await bot.say(
            event.channel,
            '<@{}> 이 명령어는 아빠만 사용할 수 있어요!'.format(event.user.name)
        )
