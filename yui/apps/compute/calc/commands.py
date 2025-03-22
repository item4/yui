import ast
import asyncio
import resource
from typing import Final

from ....bot import Bot
from ....box import box
from ....event import Message
from .evaluator import Evaluator
from .exceptions import BadSyntax

TIMEOUT: Final = 1


async def body(
    *,
    bot: Bot,
    event: Message,
    expr: str,
    help: str,
    decimal_mode: bool = True,
    timeout: float = 1,  # noqa: ASYNC109
):
    expr = expr.strip()
    expr_is_multiline = "\n" in expr
    ts = None if event.message is None else event.message.ts
    if not expr:
        await bot.say(event.channel, help)
        return

    try:
        async with asyncio.timeout(timeout):
            result, local = await bot.run_in_other_process(
                calculate,
                expr,
                decimal_mode=decimal_mode,
            )
    except (SyntaxError, BadSyntax) as e:
        await bot.say(
            event.channel,
            f"입력해주신 수식에 문법 오류가 있어요! {e}",
            thread_ts=ts,
        )
        return
    except ZeroDivisionError:
        await bot.say(
            event.channel,
            "입력해주신 수식은 계산하다보면 0으로 나누기가 발생해서 계산할 수 없어요!",
            thread_ts=ts,
        )
        return
    except TimeoutError:
        await bot.say(
            event.channel,
            "입력해주신 수식을 계산하려고 했지만 연산 시간이 너무 길어서 중단했어요!",
            thread_ts=ts,
        )
        return
    except Exception as e:  # noqa: BLE001
        await bot.say(
            event.channel,
            f"예기치 않은 에러가 발생했어요! {e.__class__.__name__}: {e}",
            thread_ts=ts,
        )
        return

    if result is not None:
        result_string = str(result)[:1500].strip()

        if expr_is_multiline or "\n" in result_string:
            r = (
                f"```\n{result_string}\n```"
                if result_string.strip()
                else "_Empty_"
            )
            text = f"*Input*\n```\n{expr}\n```\n*Output*\n{r}"
            if ts is None:
                ts = event.ts
        else:
            r = f"`{result_string}`" if result_string.strip() else "_Empty_"
            text = f"`{expr}` == {r}"
        await bot.say(
            event.channel,
            text,
            thread_ts=ts,
        )
    elif local:
        r = "\n".join(f"{key} = {value!r}" for key, value in local.items())[
            :1500
        ].strip()
        if ts is None:
            ts = event.ts
        await bot.say(
            event.channel,
            f"*Input*\n```\n{expr}\n```\n*Local State*\n```\n{r}\n```",
            thread_ts=ts,
        )
    else:
        await bot.say(
            event.channel,
            "입력해주신 수식을 계산했지만 아무런 값도 나오지 않았어요!",
            thread_ts=ts,
        )


@box.command("=", ["calc"])
async def calc_decimal(bot, event: Message, raw: str):
    """
    정수타입 수식 계산기

    `{PREFIX}= 1+2+3`

    Python 문법과 모듈 일부가 사용 가능합니다.

    """

    await body(
        bot=bot,
        event=event,
        expr=raw,
        help=f"사용법: `{bot.config.PREFIX}= <계산할 수식>`",
        decimal_mode=True,
    )


@box.command("=", ["calc"], subtype="message_changed")
async def calc_decimal_on_change(bot, event: Message, raw: str):
    if event.message:
        await body(
            bot=bot,
            event=event,
            expr=raw,
            help=f"사용법: `{bot.config.PREFIX}= <계산할 수식>`",
            decimal_mode=True,
        )


@box.command("==")
async def calc_num(bot, event: Message, raw: str):
    """
    부동소숫점타입 수식 계산기

    `{PREFIX}== 1+2+3`

    Python 문법과 모듈 일부가 사용 가능합니다.

    """

    await body(
        bot=bot,
        event=event,
        expr=raw,
        help=f"사용법: `{bot.config.PREFIX}== <계산할 수식>`",
        decimal_mode=False,
    )


@box.command("==", subtype="message_changed")
async def calc_num_on_change(bot, event: Message, raw: str):
    if event.message:
        await body(
            bot=bot,
            event=event,
            expr=raw,
            help=f"사용법: `{bot.config.PREFIX}== <계산할 수식>`",
            decimal_mode=False,
        )


TYPE_STORE = type(ast.Store())
TYPE_LOAD = type(ast.Load())
TYPE_DEL = type(ast.Del())
TYPE_EXPR = type(ast.Expr(ast.expr()))


def calculate(
    expr: str,
    *,
    decimal_mode: bool = True,
):  # pragma: no cover  -- run on other process

    limit = 2 * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
    e = Evaluator(decimal_mode=decimal_mode)
    result = e.run(expr)

    return result, e.scope
