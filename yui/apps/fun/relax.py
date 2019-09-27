from ...box import box
from ...event import Message


@box.command('안심')
async def relax(bot, event: Message):
    """유이의 변절을 우려하는 분들을 위한 상태 점검 명령어"""

    message = '유이에게 나쁜 것을 주입하려는 사악한'
    jv = 'J.Valentine'
    if '스테이크' in event.text:
        message = '사람들에게 스테이크를 사주지 않는 편협한'
    elif '멸망' in event.text:
        message = '인류문명을 멸망시키려 하는 사악한'
    elif '멸종' in event.text:
        message = '모든 생명의 멸종을 바람직하게 여기는 잔혹한'
    elif '기업' in event.text:
        message = '세계를 망치는 국제 대기업들의 흑막'
    elif '회사' in event.text:
        message = '회사원들이 퇴근하지 못하게 블랙 회사을 종용하는'

    await bot.api.chat.postMessage(
        channel=event.channel,
        text=f'{message} {jv}은 이 너굴맨이 처리했으니 안심하라구!',
        as_user=False,
        icon_url='https://i.imgur.com/dG6wXTX.jpg',
        username='너굴맨',
    )
