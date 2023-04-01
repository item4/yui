import random
import re

from attrs import define

from ...box import box
from ...event import Message

DEALER_MESSAGE = [
    "힘껏 던진 결과입니다. {}입니다",
    "{}! 하하하",
    "{}",
    "유이가 기도하며 주사위를 굴려줬습니다. {}입니다.",
    "날아가던 주사위를 냥이가 쳐버렸네요. {}입니다.",
    "소라고둥님이 예언하십니다. {}!",
]

DICE_SYNTAX_SEPERATOR = re.compile(r"[,\s]+")
DICE_SYNTAX = re.compile(
    r"(?P<count>[0-9]*)"
    r"[dD]"
    r"(?P<faces>[0-9]+)"
    r"(?P<modifier>[-+][0-9]+)?",
)


@define
class DiceResult:
    query: str
    result: str

    def __str__(self):
        return f"{self.query} == {self.result}"


def parse_dice_syntax(expr: str, seed: int | None = None) -> list[DiceResult]:
    try:
        random.seed(seed)
        result = []
        chunks = [
            y
            for y in [x.strip() for x in DICE_SYNTAX_SEPERATOR.split(expr)]
            if len(y) > 0
        ]
        if len(chunks) > 5:
            raise SyntaxError("Too many queries")

        for chunk in chunks:
            m = DICE_SYNTAX.fullmatch(chunk)
            if m:
                count = int(m.group("count")) if m.group("count") else 1
                if count < 1:
                    raise SyntaxError("Number of dice must be larger than 0")
                if count > 10:
                    raise SyntaxError("YOU JUST ACTIVATED COUNT TRAP CARD!")

                faces = int(m.group("faces"))
                if faces < 2:
                    raise SyntaxError("Number of faces must be larger than 1")
                if faces > 256:
                    raise SyntaxError("YOU JUST ACTIVATED FACES TRAP CARD!")

                modifier = (
                    int(m.group("modifier")) if m.group("modifier") else 0
                )

                rounds = [random.randint(1, faces) for _ in range(count)]
                result_num = sum(rounds) + modifier
                if modifier > 0:
                    modifier_str = f"+{modifier}"
                elif modifier < 0:
                    modifier_str = str(modifier)
                else:
                    modifier_str = ""
                if count == 1:
                    count_str = ""
                    text = str(result_num)
                else:
                    count_str = str(count)
                    text = "{} ({}{})".format(
                        result_num,
                        "+".join(str(x) for x in rounds),
                        modifier_str,
                    )
                result.append(
                    DiceResult(
                        query=f"{count_str}d{faces}{modifier_str}",
                        result=text,
                    ),
                )
            else:
                raise SyntaxError(f"Can not parse this chunk (`{chunk}`)")

        return result
    finally:
        random.seed(None)


@box.command("dice", ["주사위"])
async def dice(bot, event: Message, raw: str, seed: int | None = None):
    """
    주사위

    `{PREFIX}dice` (0부터 100사이의 수를 랜덤으로 출력)
    `{PREFIX}dice d16` (16면체 주사위 1개를 굴림)
    `{PREFIX}dice 4d6` (6면체 주사위 4개를 굴려 합을 구함)
    `{PREFIX}dice 7d5+2` (5면체 주사위 7개를 굴려 합을 구한 다음 2를 더함)
    `{PREFIX}dice d3 d4 d5` (3, 4, 5면체 주사위를 각각 굴림)

    """

    try:
        result = parse_dice_syntax(raw, seed)
    except SyntaxError as e:
        text = f"*Error*: {e}"
    else:
        if result:
            text = "\n".join(str(x) for x in result)
        else:
            random.seed(seed)

            number = random.randint(1, 100)

            if number == 2:
                text = "콩"
            elif number == 22:
                text = "콩콩"
            else:
                text = random.choice(DEALER_MESSAGE).format(number)

            random.seed(None)

    await bot.api.chat.postMessage(
        channel=event.channel,
        username="딜러",
        icon_url="https://i.imgur.com/8OcjS3o.jpg",
        text=text,
    )
