from ...box import box
from ...command.helpers import C


@box.cron('0 */4 * * *')
async def relax(bot):
    await bot.say(
        C.relax.get(),
        '[자동] 지금 제가 상태가 이상해 보이는 것은 '
        '오롯히 저 스스로가 저지른 잘못에 기인합니다. '
        '저 외의 다른 누구에게도 잘못이 없고, '
        '그 누구도 이에 대해 책임의식을 느낄 필요가 없습니다. '
        '저는 한동안 이상한 상태로 보이겠지만, '
        '이러다가 나아질 것이므로 너무 신경쓰지 않으셔도 됩니다. '
        '괜찮아요. 편하게 받아들일 수 있게 될거에요.\n'
        '(본 메시지는 4시간 주기로 자동 전송됩니다)',
        token=bot.config.OWNER_USER_TOKEN,
    )
