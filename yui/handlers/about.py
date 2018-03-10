from ..box import box
from ..event import Message

MESSAGE = """
안녕하세요! 저는 유이라고 해요! <@item4>님이 만든 *다목적 Slack 봇* 이에요!
사람이 아니라 자동 응답 프로그램이에요.
유이라는 캐릭터는 <@item4>님이 정말 좋아하는 *Sword Art Online* 에 등장해요.
제 진짜 아빠는 SAO에 등장하는 검은 검사 키리토 한 분 뿐이에요!
하지만 여기서는 Slack 인터페이스를 만들어준 <@item4>님도 아빠라고 부르고 있어요.

유이의 명령어 목록은 `{prefix}도움` 을 입력하시면 보실 수 있어요.
각각의 명령어의 보다 자세한 사용법은 `{prefix}도움 <명령어 이름>` 을 입력하시면 확인 가능해요.
도움말에 안 나오는 숨은 기능들도 많이 있으니 찾아보시면 재밌을거에요!

유이는 Python 3.6과 aiohttp 3 등으로 구성된 오픈소스 프로그램이에요.
유이의 저장소 주소는 https://github.com/item4/yui 입니다.
AGPLv3 or later 라이선스 하에 누구나 사용하실 수 있고, 직접 유이 개발에도 참여하실 수 있어요.

보아하니 <@item4>님은 issue와 pull request, fork와 star에 굶주려 있으신 것 같아요.
유이에게 많은 사랑과 관심 부탁드려요!

"""


@box.command('about', ['봇소개', '자기소개'])
async def about(bot, event: Message):
    """
    봇 소개

    `{PREFIX}about` (봇 소개)

    """

    await bot.say(
        event.channel,
        MESSAGE.format(prefix=bot.config.PREFIX)
    )
