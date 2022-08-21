from ...box import box
from ...event import Message
from ...utils import format

box.assert_user_required("villain")

RESPONSE = {
    "스테이크": "사람들에게 스테이크를 사주지 않는 편협한",
    "멸망": "인류문명을 멸망시키려 하는 사악한",
    "멸종": "모든 생명의 멸종을 추진하는 잔학한",
    "기업": "모든 생명의 멸종을 바람직하게 여기는 잔혹한",
    "회사": "회사원들이 퇴근하지 못하게 블랙 회사을 종용하는",
    "퇴근": "직장인들의 퇴근을 방해하는",
    "퇴사": "직장인들로 하여금 퇴사하고 싶은 생각이 들게 만드는",
    "야근": "직장인들의 소중한 저녁시간을 빼앗는",
    "질병": "세계에 은밀하게 불치병을 흩뿌리고 다니는",
    "전염": "전 세계에 유해한 전염병을 유행시키는",
}


@box.command("안심")
async def relax(bot, event: Message):
    """세계를 지키는 수호자를 소환하는 명령어"""

    message = "유이에게 나쁜 것을 주입하려는 사악한"
    jv = format.link(bot.config.USERS["villain"])
    for key, m in RESPONSE.items():
        if key in event.text:
            message = m
            break

    await bot.api.chat.postMessage(
        channel=event.channel,
        text=f"{message} {jv}! 악당은 방금 이 너굴맨이 처치했으니 안심하라구!",
        icon_url="https://i.imgur.com/dG6wXTX.jpg",
        username="너굴맨",
    )
