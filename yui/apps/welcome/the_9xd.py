from ...box import box
from ...event import TeamJoin

box.assert_channel_required('welcome')


@box.on(TeamJoin)
async def welcome_9xd(bot, event: TeamJoin):
    channel = bot.config.CHANNELS['welcome']
    chat = await bot.say(
        channel,
        f'<@{event.user}>님 9XD Slack에 오신걸 환영합니다! :tada:\n'
        '갑자기 알림이 울려서 놀라셨죠? 저는 Slack 봇 유이라고 해요. '
        f'제 도움이 필요하면 언제든지 `{bot.config.PREFIX}도움`을 입력해서 '
        '도움말을 확인해주세요!\n'
        '9XD Slack에는 여러가지 채널들이 있으니 제가 남기는 thread의 설명을 읽어주세요!\n'
        '그럼 즐거운 Slack 이용이 되셨으면 좋겠습니다! 잘 부탁드려요!',
    )
    if chat.body['ok']:
        await bot.say(
            channel,
            '9XD Slack에는 다음과 같은 채널들이 있으니 참가해보셔도 좋을 것 같아요!\n\n'
            '- #_general - 일상적인 대화는 여기서 하면 돼요.\n'
            '- #_notice - 공지사항이 올라오는 곳이에요. 여기는 대화 말고 읽기만 해주세요.\n'
            '- #blogs - 9XD 회원분들의 블로그 글이 자동으로 공유되는 채널이에요.\n'
            '- #game - 게임 이야기는 여기서! 게임 개발은 #game-dev \n'
            '- #job - 일자리 이야기를 하는 곳이에요. 스타트업은 #startup\n'
            '- #hobby - 지름신, 술, 음식 기타 취미에 관한 이야기를 나누는 곳이에요.\n'
            '- #music - 올 어바웃 음악! 노동요, 페스티벌 자유롭게 이야기 해주세요!\n'
            '- #animal - 귀여운 동물 보면서 힐링하는 곳이에요.\n'
            '- #otaku - 서브컬쳐 덕질은 여기서 하면 돼요.\n'
            '- #laboratory - 제게 이것저것 시켜보고 싶으실 땐 이곳에서 해주세요!\n'
            '- 개발 분야별 채널 - #data-science, #backend, #embeded, '
            '#frontend, #ios\n'
            '- 개발 도구 채널 - #dev-tool 여러분의 비밀 도구들을 알려주세요!\n'
            '- 언어별 채널 - #cplusplus, #dotnet, #fp, #go, #java, #js, '
            '#kotlin, #php, #python, #ruby, #rust\n\n'
            '이외에도 더 많은 채널들이 있어요. 채널 목록을 참조해주세요!',
            thread_ts=chat.body['ts'],
        )
