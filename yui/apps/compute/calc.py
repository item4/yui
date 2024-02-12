import _ast
import ast
import datetime
import decimal
import functools
import html
import itertools
import math
import operator
import random
import statistics
from collections.abc import Callable
from collections.abc import Iterable
from typing import Any
from typing import Self
from typing import TypeAlias

from async_timeout import timeout
from more_itertools import numeric_range

from ...bot import Bot
from ...box import box
from ...event import Message
from ...utils import json

TIMEOUT = 1
MAYBE_DECIMAL: TypeAlias = int | float | decimal.Decimal


class PLACEHOLDER:
    pass


async def body(
    bot: Bot,
    event: Message,
    expr: str,
    help: str,
    decimal_mode: bool = True,
):
    expr = expr.strip()
    expr_is_multiline = "\n" in expr
    ts = None if event.message is None else event.message.ts
    if not expr:
        await bot.say(event.channel, help)
        return

    try:
        async with timeout(TIMEOUT):
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
        bot,
        event,
        raw,
        f"사용법: `{bot.config.PREFIX}= <계산할 수식>`",
        True,
    )


@box.command("=", ["calc"], subtype="message_changed")
async def calc_decimal_on_change(bot, event: Message, raw: str):
    if event.message:
        await body(
            bot,
            event,
            raw,
            f"사용법: `{bot.config.PREFIX}= <계산할 수식>`",
            True,
        )


@box.command("==")
async def calc_num(bot, event: Message, raw: str):
    """
    부동소숫점타입 수식 계산기

    `{PREFIX}== 1+2+3`

    Python 문법과 모듈 일부가 사용 가능합니다.

    """

    await body(
        bot,
        event,
        raw,
        f"사용법: `{bot.config.PREFIX}== <계산할 수식>`",
        False,
    )


@box.command("==", subtype="message_changed")
async def calc_num_on_change(bot, event: Message, raw: str):
    if event.message:
        await body(
            bot,
            event,
            raw,
            f"사용법: `{bot.config.PREFIX}== <계산할 수식>`",
            False,
        )


class Decimal(decimal.Decimal):
    def __neg__(self, context=None):
        return Decimal(super().__neg__())

    def __pos__(self, context=None):
        return Decimal(super().__pos__())

    def __abs__(self, round=True, context=None):
        return Decimal(super().__abs__())

    def __add__(self, other, context=None):
        if isinstance(other, int | float):
            other = Decimal(other)
        return Decimal(super().__add__(other))

    def __radd__(self, other, context=None):
        if isinstance(other, int | float):
            other = Decimal(other)
        return Decimal(super(Decimal, other).__add__(self))

    def __sub__(self, other, context=None):
        if isinstance(other, int | float):
            other = Decimal(other)
        return Decimal(super().__sub__(other))

    def __rsub__(self, other, context=None):
        if isinstance(other, int | float):
            other = Decimal(other)
        return Decimal(super(Decimal, other).__sub__(self))

    def __mul__(self, other, context=None):
        if isinstance(other, int | float):
            other = Decimal(other)
        return Decimal(super().__mul__(other))

    def __rmul__(self, other, context=None):
        if isinstance(other, int | float):
            other = Decimal(other)
        return Decimal(super(Decimal, other).__mul__(self))

    def __truediv__(self, other, context=None):
        if isinstance(other, int | float):
            other = Decimal(other)
        return Decimal(super().__truediv__(other))

    def __rtruediv__(self, other, context=None):
        if isinstance(other, int | float):
            other = Decimal(other)
        return Decimal(super(Decimal, other).__truediv__(self))

    def __floordiv__(self, other, context=None):
        if isinstance(other, int | float):
            other = Decimal(other)
        return Decimal(super().__floordiv__(other))

    def __rfloordiv__(self, other, context=None):
        if isinstance(other, int | float):
            other = Decimal(other)
        return Decimal(super(Decimal, other).__floordiv__(self))

    def __mod__(self, other, context=None):
        if isinstance(other, int | float):
            other = Decimal(other)
        return Decimal(super().__mod__(other))

    def __rmod__(self, other, context=None):
        if isinstance(other, int | float):
            other = Decimal(other)
        return Decimal(super(Decimal, other).__mod__(self))

    def __divmod__(self, other, context=None):
        if isinstance(other, int | float):
            other = Decimal(other)
        quotient, remainder = super().__divmod__(other)
        return Decimal(quotient), Decimal(remainder)

    def __rdivmod__(self, other, context=None):
        if isinstance(other, int | float):
            other = Decimal(other)
        quotient, remainder = super(Decimal, other).__divmod__(self)
        return Decimal(quotient), Decimal(remainder)

    def __pow__(
        self,
        power: Self | MAYBE_DECIMAL,
        modulo: Self | MAYBE_DECIMAL | None = None,
    ):
        if isinstance(power, int | float):
            power = Decimal(power)
        if isinstance(modulo, int | float):
            modulo = Decimal(modulo)
        return Decimal(super().__pow__(power, modulo))

    def __rpow__(self, other, context=None):
        if isinstance(other, int | float):
            other = Decimal(other)
        return Decimal(super(Decimal, other).__pow__(self))


TYPE_STORE = type(ast.Store())
TYPE_LOAD = type(ast.Load())
TYPE_DEL = type(ast.Del())
TYPE_EXPR = type(ast.Expr())


class BadSyntax(Exception):
    pass


BINOP_TABLE: dict[Any, Callable[[Any, Any], Any]] = {
    _ast.Add: lambda a, b: a + b,
    _ast.BitAnd: lambda a, b: a & b,
    _ast.BitOr: lambda a, b: a | b,
    _ast.BitXor: lambda a, b: a ^ b,
    _ast.Div: lambda a, b: a / b,
    _ast.FloorDiv: lambda a, b: a // b,
    _ast.LShift: lambda a, b: a << b,
    _ast.MatMult: lambda a, b: a @ b,
    _ast.Mult: lambda a, b: a * b,
    _ast.Mod: lambda a, b: a % b,
    _ast.Pow: lambda a, b: a**b,
    _ast.RShift: lambda a, b: a >> b,
    _ast.Sub: lambda a, b: a - b,
}
BOOLOP_TABLE: dict[Any, Callable[[Any, Any], Any]] = {
    _ast.And: lambda a, b: a and b,
    _ast.Or: lambda a, b: a or b,
}
COMPARE_TABLE: dict[Any, Callable[[Any, Any], bool]] = {
    _ast.Eq: lambda a, b: a == b,
    _ast.Gt: lambda a, b: a > b,
    _ast.GtE: lambda a, b: a >= b,
    _ast.In: lambda a, b: a in b,
    _ast.Is: lambda a, b: a is b,
    _ast.IsNot: lambda a, b: a is not b,
    _ast.Lt: lambda a, b: a < b,
    _ast.LtE: lambda a, b: a <= b,
    _ast.NotEq: lambda a, b: a != b,
    _ast.NotIn: lambda a, b: a not in b,
}
UNARYOP_TABLE: dict[Any, Callable[[Any], Any]] = {
    _ast.Invert: lambda x: ~x,
    _ast.Not: lambda x: not x,
    _ast.UAdd: lambda x: +x,
    _ast.USub: lambda x: -x,
}


class ScopeStack:
    stack: list[dict[str, Any]]

    def __init__(self) -> None:
        self.stack = [{}]

    def create_new_scope(self):
        self.stack.append({})

    def remove_top_scope(self):
        self.stack.pop()

    def __getitem__(self, item: str) -> Any:
        for scope in reversed(self.stack):
            try:
                return scope[item]
            except KeyError:
                continue
        raise NameError(item)

    def keys(self):
        yield from {key for scope in self.stack for key in scope}

    def __iter__(self):
        return self.keys()

    def __setitem__(self, key: str, value: Any) -> None:
        self.stack[-1][key] = value

    def __delitem__(self, key: str) -> None:
        try:
            self.stack[-1].pop(key)
        except KeyError as e:
            raise NameError(key) from e

    def __contains__(self, item: str) -> bool:
        return any(item in x for x in self.stack)

    def __enter__(self) -> None:
        self.create_new_scope()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.remove_top_scope()


class Evaluator:
    last_dump: str

    def __init__(self, decimal_mode: bool = False) -> None:
        self.decimal_mode = decimal_mode
        self.allowed_modules = {
            datetime: {"date", "datetime", "time", "timedelta", "tzinfo"},
            functools: {"reduce"},
            html: {"escape", "unescape"},
            itertools: {
                "accumulate",
                "chain",
                "chain.from_iterable",
                "compress",
                "dropwhile",
                "filterfalse",
                "groupby",
                "starmap",
                "takewhile",
                "tee",
                "zip_longest",
                "product",
                "permutations",
                "combinations",
                "combinations_with_replacement",
            },
            math: {
                "acos",
                "acosh",
                "asin",
                "asinh",
                "atan",
                "atan2",
                "atanh",
                "ceil",
                "copysign",
                "cos",
                "cosh",
                "degrees",
                "erf",
                "erfc",
                "exp",
                "expm1",
                "fabs",
                "factorial",
                "floor",
                "fmod",
                "frexp",
                "fsum",
                "gamma",
                "gcd",
                "hypot",
                "isclose",
                "isfinite",
                "isinf",
                "isnan",
                "ldexp",
                "lgamma",
                "log",
                "log1p",
                "log10",
                "log2",
                "modf",
                "pow",
                "radians",
                "sin",
                "sinh",
                "sqrt",
                "tan",
                "tanh",
                "trunc",
                "pi",
                "e",
                "tau",
                "inf",
                "nan",
            },
            operator: {
                "lt",
                "le",
                "eq",
                "ne",
                "ge",
                "gt",
                "not_",
                "truth",
                "is_",
                "is_not",
                "add",
                "and_",
                "floordiv",
                "index",
                "inv",
                "invert",
                "lshift",
                "mod",
                "mul",
                "matmul",
                "neg",
                "or_",
                "pos",
                "pow",
                "rshift",
                "sub",
                "truediv",
                "xor",
                "concat",
                "contains",
                "countOf",
                "delitem",
                "getitem",
                "indexOf",
                "setitem",
                "length_hint",
                "itemgetter",
            },
            random: {
                "randrange",
                "randint",
                "choice",
                "choices",
                "shuffle",
                "sample",
                "random",
                "uniform",
                "triangular",
                "betavariate",
                "expovariate",
                "gammavariate",
                "gauss",
                "lognormvariate",
                "normalvariate",
                "vonmisesvariate",
                "paretovariate",
                "weibullvariate",
            },
            statistics: {
                "mean",
                "harmonic_mean",
                "median",
                "median_low",
                "median_high",
                "median_grouped",
                "mode",
                "pstdev",
                "pvariance",
                "stdev",
                "variance",
            },
            json: {"dumps", "loads"},
        }
        self.allowed_class_properties = {
            bytes: {"fromhex", "maketrans"},
            datetime.date: {
                "today",
                "fromtimestamp",
                "fromordinal",
                "fromisoformat",
                "min",
                "max",
                "resolution",
            },
            datetime.datetime: {
                "today",
                "now",
                "utcnowfromtimestamp",
                "utcfromtimestamp",
                "fromordinal",
                "combine",
                "fromisoformat",
                "strptime",
                "min",
                "max",
                "resolution",
            },
            datetime.time: {"min", "max", "resolution", "fromisoformat"},
            datetime.timedelta: {"min", "max", "resolution"},
            datetime.timezone: {"utc"},
            dict: {"fromkeys"},
            float: {"fromhex"},
            int: {"from_bytes"},
            str: {"maketrans"},
        }
        self.allowed_instance_properties = {
            bytes: {
                "hex",
                "count",
                "decode",
                "endswith",
                "find",
                "index",
                "join",
                "partition",
                "replace",
                "rfind",
                "rindex",
                "rpartition",
                "startswith",
                "translate",
                "center",
                "ljust",
                "lstrip",
                "rjust",
                "rsplit",
                "rstrip",
                "split",
                "strip",
                "capitalize",
                "expandtabs",
                "isalnum",
                "isalpha",
                "isdigit",
                "islower",
                "isspace",
                "istitle",
                "isupper",
                "lower",
                "splitlines",
                "swapcase",
                "title",
                "upper",
                "zfill",
            },
            datetime.date: {
                "year",
                "month",
                "day",
                "replace",
                "timetuple",
                "toordinal",
                "weekday",
                "isoweekday",
                "isocalendar",
                "isoformat",
                "ctime",
                "strftime",
            },
            datetime.datetime: {
                "year",
                "month",
                "dayhour",
                "minute",
                "second",
                "microsecond",
                "tzinfo",
                "fold",
                "date",
                "time",
                "timetz",
                "replace",
                "astimezone",
                "dst",
                "tzname",
                "timetuple",
                "utctimetuple",
                "toordinal",
                "timestamp",
                "weekday",
                "isoweekday",
                "isocalendar",
                "isoformat",
                "ctime",
                "strftime",
            },
            datetime.time: {
                "hour",
                "minute",
                "second",
                "microsecond",
                "tzinfo",
                "fold",
                "replace",
                "isoformat",
                "strftime",
                "utcoffset",
                "dst",
                "tzname",
            },
            datetime.timedelta: {"total_seconds"},
            datetime.timezone: {"utcoffset", "tzname", "dst", "fromutc"},
            datetime.tzinfo: {"utcoffset", "dst", "tzname", "fromutc"},
            dict: {
                "copy",
                "get",
                "items",
                "keys",
                "pop",
                "popitem",
                "setdefault",
                "update",
                "values",
            },
            float: {"as_integer_ratio", "is_integer", "hex"},
            int: {"bit_length", "to_bytes"},
            list: {
                "index",
                "count",
                "append",
                "clear",
                "copy",
                "extend",
                "insert",
                "pop",
                "remove",
                "reverse",
                "sort",
            },
            range: {"start", "stop", "step"},
            numeric_range: {"start", "stop", "step"},
            str: {
                "capitalize",
                "casefold",
                "center",
                "count",
                "encode",
                "endswith",
                "expandtabs",
                "find",
                "format",
                "format_map",
                "index",
                "isalnum",
                "isalpha",
                "isdecimal",
                "isdigit",
                "isidentifier",
                "islower",
                "isnumeric",
                "isprintable",
                "isspace",
                "istitle",
                "isupper",
                "join",
                "ljust",
                "lower",
                "lstrip",
                "partition",
                "replace",
                "rfind",
                "rindex",
                "rjust",
                "rpartition",
                "rsplit",
                "rstrip",
                "split",
                "splitlines",
                "swapcase",
                "startswith",
                "strip",
                "title",
                "translate",
                "upper",
                "zfill",
            },
            set: {
                "isdisjoint",
                "issubset",
                "issuperset",
                "union",
                "intersection",
                "difference",
                "symmetric_difference",
                "copy",
                "update",
                "intersection_update",
                "difference_update",
                "symmetric_difference_update",
                "add",
                "remove",
                "discard",
                "pop",
                "clear",
            },
            tuple: {
                "index",
                "count",
                "append",
                "clear",
                "copy",
                "extend",
                "insert",
                "pop",
                "remove",
                "reverse",
            },
        }
        self.global_symbol_table: dict[str, Any] = {
            # builtin func
            "abs": abs,
            "all": all,
            "any": any,
            "ascii": ascii,
            "bin": bin,
            "bool": bool,
            "bytes": bytes,
            "chr": chr,
            "complex": complex,
            "dict": dict,
            "divmod": divmod,
            "enumerate": enumerate,
            "filter": filter,
            "float": float,
            "format": format,
            "frozenset": frozenset,
            "hex": hex,
            "int": int,
            "isinstance": isinstance,
            "issubclass": issubclass,
            "len": len,
            "list": list,
            "map": map,
            "max": max,
            "min": min,
            "oct": oct,
            "ord": ord,
            "pow": pow,
            "range": numeric_range if self.decimal_mode else range,
            "numeric_range": numeric_range,
            "repr": repr,
            "reversed": reversed,
            "round": round,
            "set": set,
            "slice": slice,
            "sorted": sorted,
            "str": str,
            "sum": sum,
            "tuple": tuple,
            "zip": zip,
            # additional type
            "Decimal": Decimal,
            # math shortcut
            "acos": math.acos,
            "acosh": math.acosh,
            "asin": math.asin,
            "asinh": math.asinh,
            "atan": math.atan,
            "atan2": math.atan2,
            "atanh": math.atanh,
            "ceil": math.ceil,
            "copysign": math.copysign,
            "cos": math.cos,
            "cosh": math.cosh,
            "degrees": math.degrees,
            "erf": math.erf,
            "erfc": math.erfc,
            "exp": math.exp,
            "expm1": math.expm1,
            "fabs": math.fabs,
            "factorial": math.factorial,
            "floor": math.floor,
            "fmod": math.fmod,
            "frexp": math.frexp,
            "fsum": math.fsum,
            "gamma": math.gamma,
            "gcd": math.gcd,
            "hypot": math.hypot,
            "isclose": math.isclose,
            "isfinite": math.isfinite,
            "isinf": math.isinf,
            "isnan": math.isnan,
            "ldexp": math.ldexp,
            "lgamma": math.lgamma,
            "log": math.log,
            "log1p": math.log1p,
            "log10": math.log10,
            "log2": math.log2,
            "modf": math.modf,
            "radians": math.radians,
            "sin": math.sin,
            "sinh": math.sinh,
            "sqrt": math.sqrt,
            "tan": math.tan,
            "tanh": math.tanh,
            "trunc": math.trunc,
            "pi": math.pi,
            "e": math.e,
            "tau": math.tau,
            "inf": math.inf,
            "nan": math.nan,
            # module level injection
            "datetime": datetime,
            "functools": functools,
            "html": html,
            "itertools": itertools,
            "json": json,
            "math": math,
            "operator": operator,
            "random": random,
            "statistics": statistics,
        }
        self.scope = ScopeStack()
        self.current_interrupt: _ast.Break | _ast.Continue | None = None

    def run(self, expr: str):
        h = ast.parse(expr, mode="exec")
        self.last_dump = ast.dump(h)
        return self._run(h)

    def _run(self, node):
        if node is None:
            return None

        return getattr(
            self,
            f"visit_{node.__class__.__name__.lower()}",
            self.no_impl,
        )(node)

    def assign(self, node, val):
        cls = node.__class__

        if cls == _ast.Name:
            self.scope[node.id] = val
        elif cls in (_ast.Tuple, _ast.List):
            if not isinstance(val, Iterable):
                raise TypeError(
                    f"cannot unpack non-iterable {type(val).__name__} object",
                )
            for telem, tval in itertools.zip_longest(
                node.elts,
                val,
                fillvalue=PLACEHOLDER,
            ):
                if telem == PLACEHOLDER:
                    raise ValueError("not enough values to unpack")
                if tval == PLACEHOLDER:
                    raise ValueError("too many values to unpack")
                self.assign(telem, tval)
        elif cls == _ast.Subscript:
            sym = self._run(node.value)
            xslice = self._run(node.slice)
            if isinstance(node.slice, _ast.Slice):
                sym[slice(xslice.start, xslice.stop)] = val
            else:
                sym[xslice] = val
        else:
            raise BadSyntax("This assign method is not allowed")

    def delete(self, node):
        cls = node.__class__

        if cls == _ast.Name:
            del self.scope[node.id]
        elif cls == _ast.Tuple:
            for elt in node.elts:
                self.delete(elt)

    def no_impl(self, node):
        raise NotImplementedError

    def visit_annassign(self, node: _ast.AnnAssign):
        raise BadSyntax("You can not use annotation syntax")

    def visit_assert(self, node: _ast.Assert):
        raise BadSyntax("You can not use assertion syntax")

    def visit_assign(self, node: _ast.Assign):  # targets, value
        value = self._run(node.value)
        for tnode in node.targets:
            self.assign(tnode, value)

    def visit_asyncfor(self, node: _ast.AsyncFor):
        raise BadSyntax("You can not use `async for` loop syntax")

    def visit_asyncfunctiondef(self, node: _ast.AsyncFunctionDef):
        raise BadSyntax("Defining new coroutine via def syntax is not allowed")

    def visit_asyncwith(self, node: _ast.AsyncWith):
        raise BadSyntax("You can not use `async with` syntax")

    def visit_attribute(self, node: _ast.Attribute):  # value, attr, ctx
        value = self._run(node.value)
        t = type(value)
        try:
            if value in self.allowed_modules:
                if node.attr in self.allowed_modules[value]:
                    return getattr(value, node.attr)
                raise BadSyntax(f"You can not access `{node.attr}` attribute")
            if value in self.allowed_class_properties:
                if node.attr in self.allowed_class_properties[value]:
                    return getattr(value, node.attr)
                raise BadSyntax(f"You can not access `{node.attr}` attribute")
        except TypeError:
            pass
        if t in self.allowed_instance_properties:
            if node.attr in self.allowed_instance_properties[t]:
                return getattr(value, node.attr)
            raise BadSyntax(f"You can not access `{node.attr}` attribute")
        raise BadSyntax(f"You can not access attributes of {t}")

    def visit_augassign(self, node: _ast.AugAssign):  # target, op, value
        value = self._run(node.value)
        target = node.target
        target_cls = target.__class__
        op_cls = node.op.__class__

        if target_cls == _ast.Name:
            target_id = target.id  # type: ignore
            self.scope[target_id] = BINOP_TABLE[op_cls](
                self.scope[target_id],
                value,
            )
        elif target_cls == _ast.Subscript:
            sym = self._run(target.value)  # type: ignore
            xslice = self._run(target.slice)  # type: ignore
            if not isinstance(target.slice, _ast.Tuple | _ast.Slice):  # type: ignore
                sym[xslice] = BINOP_TABLE[op_cls](
                    sym[xslice],
                    value,
                )
            else:
                raise BadSyntax("This assign method is not allowed")
        else:
            raise BadSyntax("This assign method is not allowed")

    def visit_await(self, node: _ast.Await):
        raise BadSyntax("You can not await anything")

    def visit_binop(self, node: _ast.BinOp):  # left, op, right
        op = BINOP_TABLE.get(node.op.__class__)

        if op:
            return op(self._run(node.left), self._run(node.right))
        raise NotImplementedError

    def visit_boolop(self, node: _ast.BoolOp):  # left, op, right
        op = BOOLOP_TABLE.get(node.op.__class__)

        if op:
            return functools.reduce(op, map(self._run, node.values), True)
        raise NotImplementedError

    def visit_break(self, node: _ast.Break):
        self.current_interrupt = node

    def visit_call(self, node: _ast.Call):  # func, args, keywords
        func = self._run(node.func)
        args = [self._run(x) for x in node.args]
        keywords = {x.arg: self._run(x.value) for x in node.keywords}
        return func(*args, **keywords)

    def visit_compare(self, node: _ast.Compare):  # left, ops, comparators
        lval = self._run(node.left)
        out = True
        for op, rnode in zip(node.ops, node.comparators, strict=True):
            rval = self._run(rnode)
            cmpop = COMPARE_TABLE.get(op.__class__)
            if cmpop:
                out = cmpop(lval, rval)
                lval = rval
            else:
                raise NotImplementedError
        return out

    def visit_constant(self, node: _ast.Constant):  # value, kind
        if self.decimal_mode and isinstance(node.value, int | float):
            return Decimal(str(node.value))
        return node.value

    def visit_continue(self, node: _ast.Continue):
        self.current_interrupt = node

    def visit_classdef(self, node: _ast.ClassDef):
        raise BadSyntax("Defining new class via def syntax is not allowed")

    def visit_delete(self, node: _ast.Delete):  # targets
        for target in node.targets:
            target_cls = target.__class__
            if target_cls == _ast.Name:
                del self.scope[target.id]  # type: ignore
            elif target_cls == _ast.Subscript:
                sym = self._run(target.value)  # type: ignore
                xslice = self._run(target.slice)  # type: ignore
                if not isinstance(
                    target.slice,  # type: ignore
                    _ast.Tuple | _ast.Slice,
                ):
                    del sym[xslice]
                else:
                    raise BadSyntax("This delete method is not allowed")
            else:
                raise BadSyntax("This delete method is not allowed")

    def visit_dict(self, node: _ast.Dict):  # keys, values
        return {
            self._run(k): self._run(v)
            for k, v in zip(node.keys, node.values, strict=True)
        }

    def visit_dictcomp(self, node: _ast.DictComp):  # key, value, generators
        result: dict = {}
        current_gen = node.generators[0]
        if current_gen.__class__ == _ast.comprehension:
            with self.scope:
                for val in self._run(current_gen.iter):
                    self.assign(current_gen.target, val)
                    add = True
                    for cond in current_gen.ifs:
                        add = add and self._run(cond)
                    if add:
                        if len(node.generators) > 1:
                            r = self.visit_dictcomp(
                                _ast.DictComp(
                                    key=node.key,
                                    value=node.value,
                                    generators=node.generators[1:],
                                ),
                            )
                            result.update(r)
                        else:
                            key = self._run(node.key)
                            value = self._run(node.value)
                            result[key] = value
                    self.delete(current_gen.target)
        return result

    def visit_expr(self, node: _ast.Expr):  # value,
        return self._run(node.value)

    def visit_functiondef(self, node: _ast.FunctionDef):
        raise BadSyntax("Defining new function via def syntax is not allowed")

    def visit_for(self, node: _ast.For):  # target, iter, body, orelse
        for val in self._run(node.iter):
            self.assign(node.target, val)
            self.current_interrupt = None
            for tnode in node.body:
                self._run(tnode)
                if self.current_interrupt is not None:
                    break
            if isinstance(self.current_interrupt, _ast.Break):
                break
        else:
            for tnode in node.orelse:
                self._run(tnode)

        self.current_interrupt = None

    def visit_formattedvalue(self, node: _ast.FormattedValue):
        # value, conversion, format_spec
        value = self._run(node.value)
        format_spec = self._run(node.format_spec)
        if format_spec is None:
            format_spec = ""
        return format(value, format_spec)

    def visit_generatorexp(self, node: _ast.GeneratorExp):
        raise BadSyntax("Defining new generator expression is not allowed")

    def visit_global(self, node: _ast.Global):
        raise BadSyntax("You can not use `global` syntax")

    def visit_if(self, node: _ast.If):  # test, body, orelse
        stmts = node.body if self._run(node.test) else node.orelse
        for stmt in stmts:
            self._run(stmt)

    def visit_ifexp(self, node: _ast.IfExp):  # test, body, orelse
        return self._run(node.body if self._run(node.test) else node.orelse)

    def visit_import(self, node: _ast.Import):
        raise BadSyntax("You can not import anything")

    def visit_importfrom(self, node: _ast.ImportFrom):
        raise BadSyntax("You can not import anything")

    def visit_joinedstr(self, node: _ast.JoinedStr):  # values,
        return "".join(self._run(x) for x in node.values)

    def visit_lambda(self, node: _ast.Lambda):
        raise BadSyntax(
            "Defining new function via lambda syntax is not allowed",
        )

    def visit_list(self, node: _ast.List):  # elts, ctx
        return [self._run(x) for x in node.elts]

    def visit_listcomp(self, node: _ast.ListComp):  # elt, generators
        result: list = []
        current_gen = node.generators[0]
        if current_gen.__class__ == _ast.comprehension:
            with self.scope:
                for val in self._run(current_gen.iter):
                    self.assign(current_gen.target, val)
                    add = True
                    for cond in current_gen.ifs:
                        add = add and self._run(cond)
                    if add:
                        if len(node.generators) > 1:
                            r = self.visit_listcomp(
                                _ast.ListComp(
                                    elt=node.elt,
                                    generators=node.generators[1:],
                                ),
                            )
                            result += r
                        else:
                            r = self._run(node.elt)
                            result.append(r)
                    self.delete(current_gen.target)
        return result

    def visit_module(self, node: _ast.Module):  # body,
        last = None
        for body_node in node.body:
            last = self._run(body_node)
        return last

    def visit_name(self, node: _ast.Name):  # id, ctx
        ctx = node.ctx.__class__
        if ctx == ast.Del:
            return node.id
        if node.id in self.scope:
            return self.scope[node.id]
        if node.id in self.global_symbol_table:
            return self.global_symbol_table[node.id]
        raise NameError

    def visit_nonlocal(self, node: _ast.Nonlocal):
        raise BadSyntax("You can not use `nonlocal` syntax")

    def visit_pass(self, node: _ast.Pass):
        return

    def visit_raise(self, node: _ast.Raise):
        raise BadSyntax("You can not use `raise` syntax")

    def visit_return(self, node: _ast.Return):
        raise BadSyntax("You can not use `return` syntax")

    def visit_set(self, node: _ast.Set):  # elts,
        return {self._run(x) for x in node.elts}

    def visit_setcomp(self, node: _ast.SetComp):  # elt, generators
        result = set()
        current_gen = node.generators[0]
        if current_gen.__class__ == _ast.comprehension:
            with self.scope:
                for val in self._run(current_gen.iter):
                    self.assign(current_gen.target, val)
                    add = True
                    for cond in current_gen.ifs:
                        add = add and self._run(cond)
                    if add:
                        if len(node.generators) > 1:
                            r = self.visit_setcomp(
                                _ast.SetComp(
                                    elt=node.elt,
                                    generators=node.generators[1:],
                                ),
                            )
                            result |= r
                        else:
                            r = self._run(node.elt)
                            result.add(r)
                    self.delete(current_gen.target)
        return result

    def visit_slice(self, node: _ast.Slice):  # lower, upper, step
        return slice(
            self._run(node.lower),
            self._run(node.upper),
            self._run(node.step),
        )

    def visit_subscript(self, node: _ast.Subscript):  # value, slice, ctx
        return self._run(node.value)[self._run(node.slice)]

    def visit_try(self, node: _ast.Try):
        raise BadSyntax("You can not use `try` syntax")

    def visit_trystar(self, node: _ast.TryStar):
        raise BadSyntax("You can not use `try` syntax with star")

    def visit_tuple(self, node: _ast.Tuple):  # elts, ctx
        return tuple(self._run(x) for x in node.elts)

    def visit_typealias(self, node: _ast.TypeAlias):  # name, type_params, value
        raise BadSyntax("You can not define type alias")

    def visit_unaryop(self, node: _ast.UnaryOp):  # op, operand
        op = UNARYOP_TABLE.get(node.op.__class__)
        if op:
            return op(self._run(node.operand))
        raise NotImplementedError

    def visit_while(self, node: _ast.While):  # test, body, orelse
        while self._run(node.test):
            self.current_interrupt = None
            for tnode in node.body:
                self._run(tnode)
                if self.current_interrupt is not None:
                    break
            if isinstance(self.current_interrupt, _ast.Break):
                break
        else:
            for tnode in node.orelse:
                self._run(tnode)

        self.current_interrupt = None

    def visit_with(self, node: _ast.With):
        raise BadSyntax("You can not use `with` syntax")

    def visit_yield(self, node: _ast.Yield):
        raise BadSyntax("You can not use `yield` syntax")

    def visit_yieldfrom(self, node: _ast.YieldFrom):
        raise BadSyntax("You can not use `yield from` syntax")


def calculate(expr: str, *, decimal_mode: bool = True):
    import resource

    limit = 2 * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
    e = Evaluator(decimal_mode=decimal_mode)
    result = e.run(expr)

    return result, e.scope
