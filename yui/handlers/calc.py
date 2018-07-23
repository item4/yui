import ast
import asyncio
import datetime
import decimal
import functools
import hashlib
import itertools
import math
import operator
import random
import statistics
from collections.abc import Iterable
from typing import Any, Dict

from async_timeout import timeout

from ..box import box
from ..event import Message
from ..type import Channel

TIMEOUT = 1
LENGTH_LIMIT = 300

BUILTIN_ITERABLE = str, bytes, list, tuple, set, frozenset, dict

RESULT_TEMPLATE = {
    True: {
        True: {
            True: '*Expr*\n```{expr}```\n*Result*: Empty string',
            False: '*Expr*\n```{expr}```\n*Result*\n```{result}{more}```',
        },
        False: {
            True: '*Expr*\n```{expr}```\n*Result*: Empty string',
            False: '*Expr*\n```{expr}```\n*Result*: `{result}{more}`',
        }
    },
    False: {
        True: {
            True: '*Expr*: `{expr}`\n*Result*: Empty string',
            False: '*Expr*: `{expr}`\n*Result*\n```{result}{more}```',
        },
        False: {
            True: '`{expr}` == Empty string',
            False: '`{expr}` == `{result}{more}`',
        }
    },
}


def timeout_handler(signum, frame):
    raise TimeoutError()


async def body(
    bot,
    loop,
    channel: Channel,
    expr: str,
    help: str,
    num_to_decimal: bool=True,
    ts: str=None
):
    expr_is_multiline = '\n' in expr
    if not expr:
        await bot.say(channel, help)
        return

    result = None
    local = None
    try:
        async with timeout(TIMEOUT):
            result, local = await loop.run_in_executor(
                bot.process_pool_executor,
                functools.partial(
                    calculate,
                    expr,
                    replace_num_to_decimal=num_to_decimal,
                ),
            )
    except SyntaxError as e:
        await bot.say(
            channel,
            '에러가 발생했어요! {}'.format(e),
            thread_ts=ts,
        )
        return
    except ZeroDivisionError:
        if expr_is_multiline:
            await bot.say(
                channel,
                '주어진 식은 0으로 나누게 되어요. 0으로 나누는 건 안 돼요!',
                thread_ts=ts,
            )
        else:
            await bot.say(
                channel,
                '`{}` 는 0으로 나누게 되어요. 0으로 나누는 건 안 돼요!'.format(expr),
                thread_ts=ts,
            )
        return
    except asyncio.TimeoutError:
        if expr_is_multiline:
            await bot.say(
                channel,
                '주어진 식은 실행하기엔 너무 오래 걸려요!',
                thread_ts=ts,
            )
        else:
            await bot.say(
                channel,
                '`{}` 는 실행하기엔 너무 오래 걸려요!'.format(expr),
                thread_ts=ts,
            )
        return
    except Exception as e:
        await bot.say(
            channel,
            '에러가 발생했어요! {}: {}'.format(e.__class__.__name__, e),
            thread_ts=ts,
        )
        return

    if result is not None:
        result_string = str(result)

        if result_string.count('\n') > 30:
            await bot.say(
                channel,
                '계산 결과에 개행이 너무 많이 들어있어요!',
                thread_ts=ts
            )
        else:
            await bot.say(
                channel,
                RESULT_TEMPLATE[
                    expr_is_multiline
                ][
                    '\n' in result_string
                ][
                    result_string.strip() == ''
                ].format(
                    expr=expr,
                    result=result_string[:300],
                    more='⋯' if len(result_string) > LENGTH_LIMIT else '',
                ),
                thread_ts=ts
            )
    elif local:
        r = '\n'.join(
            '{} = {}'.format(key, value)
            for key, value in local.items()
        )
        if r.count('\n') > 30:
            await bot.say(
                channel,
                '계산 결과에 개행이 너무 많이 들어있어요!',
                thread_ts=ts
            )
        else:
            if expr_is_multiline:
                await bot.say(
                    channel,
                    '*Expr*\n```{}```\n*Local*\n```{}```'.format(expr, r),
                    thread_ts=ts,
                )
            else:
                await bot.say(
                    channel,
                    '*Expr*: `{}`\n*Local*\n```{}```'.format(expr, r),
                    thread_ts=ts,
                )
    else:
        if expr_is_multiline:
            await bot.say(
                channel,
                '*Expr*\n```{}```\n*Local*: Empty'.format(expr),
                thread_ts=ts,
            )
        else:
            await bot.say(
                channel,
                '*Expr*: `{}`\n*Local*: Empty'.format(expr),
                thread_ts=ts,
            )


@box.command('=', ['calc'])
async def calc_decimal(bot, loop, event: Message, raw: str):
    """
    정수타입 수식 계산기

    `{PREFIX}= 1+2+3`

    Python 문법과 모듈 일부가 사용 가능합니다.

    """

    await body(
        bot,
        loop,
        event.channel,
        raw,
        '사용법: `{}= <계산할 수식>`'.format(bot.config.PREFIX),
        True,
    )


@box.command('=', ['calc'], subtype='message_changed')
async def calc_decimal_on_change(bot, loop, event: Message, raw: str):
    if event.message:
        await body(
            bot,
            loop,
            event.channel,
            raw,
            '사용법: `{}= <계산할 수식>`'.format(bot.config.PREFIX),
            True,
            event.message.ts,
        )


@box.command('==')
async def calc_num(bot, loop, event: Message, raw: str):
    """
    부동소숫점타입 수식 계산기

    `{PREFIX}== 1+2+3`

    Python 문법과 모듈 일부가 사용 가능합니다.

    """

    await body(
        bot,
        loop,
        event.channel,
        raw,
        '사용법: `{}== <계산할 수식>`'.format(bot.config.PREFIX),
        False,
    )


@box.command('==', subtype='message_changed')
async def calc_num_on_change(bot, loop, event: Message, raw: str):
    if event.message:
        await body(
            bot,
            loop,
            event.channel,
            raw,
            '사용법: `{}== <계산할 수식>`'.format(bot.config.PREFIX),
            False,
            event.message.ts,
        )


class Decimal(decimal.Decimal):

    def __neg__(self):
        return Decimal(super(Decimal, self).__neg__())

    def __pos__(self):
        return Decimal(super(Decimal, self).__pos__())

    def __abs__(self):
        return Decimal(super(Decimal, self).__abs__())

    def __add__(self, other):
        if isinstance(other, (int, float)):
            other = Decimal(other)
        return Decimal(super(Decimal, self).__add__(other))

    def __radd__(self, other):
        if isinstance(other, (int, float)):
            other = Decimal(other)
        return Decimal(super(Decimal, other).__add__(self))

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            other = Decimal(other)
        return Decimal(super(Decimal, self).__sub__(other))

    def __rsub__(self, other):
        if isinstance(other, (int, float)):
            other = Decimal(other)
        return Decimal(super(Decimal, other).__sub__(self))

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            other = Decimal(other)
        return Decimal(super(Decimal, self).__mul__(other))

    def __rmul__(self, other):
        if isinstance(other, (int, float)):
            other = Decimal(other)
        return Decimal(super(Decimal, other).__mul__(self))

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            other = Decimal(other)
        return Decimal(super(Decimal, self).__truediv__(other))

    def __rtruediv__(self, other):
        if isinstance(other, (int, float)):
            other = Decimal(other)
        return Decimal(super(Decimal, other).__truediv__(self))

    def __floordiv__(self, other):
        if isinstance(other, (int, float)):
            other = Decimal(other)
        return Decimal(super(Decimal, self).__floordiv__(other))

    def __rfloordiv__(self, other):
        if isinstance(other, (int, float)):
            other = Decimal(other)
        return Decimal(super(Decimal, other).__floordiv__(self))

    def __mod__(self, other):
        if isinstance(other, (int, float)):
            other = Decimal(other)
        return Decimal(super(Decimal, self).__mod__(other))

    def __rmod__(self, other):
        if isinstance(other, (int, float)):
            other = Decimal(other)
        return Decimal(super(Decimal, other).__mod__(self))

    def __divmod__(self, other):
        if isinstance(other, (int, float)):
            other = Decimal(other)
        quotient, remainder = super(Decimal, self).__divmod__(other)
        return Decimal(quotient), Decimal(remainder)

    def __rdivmod__(self, other):
        if isinstance(other, (int, float)):
            other = Decimal(other)
        quotient, remainder = super(Decimal, other).__divmod__(self)
        return Decimal(quotient), Decimal(remainder)

    def __pow__(self, power, modulo=None):
        if isinstance(power, (int, float)):
            power = Decimal(power)
        return Decimal(super(Decimal, self).__pow__(power, modulo))

    def __rpow__(self, other):
        if isinstance(other, (int, float)):
            other = Decimal(other)
        return Decimal(super(Decimal, other).__pow__(self))


TYPE_STORE = type(ast.Store())
TYPE_LOAD = type(ast.Load())
TYPE_DEL = type(ast.Del())
TYPE_EXPR = type(ast.Expr())

MATH_CONTEXT = {
    'acos': math.acos,
    'acosh': math.acosh,
    'asin': math.asin,
    'asinh': math.asinh,
    'atan': math.atan,
    'atan2': math.atan2,
    'atanh': math.atanh,
    'ceil': math.ceil,
    'copysign': math.copysign,
    'cos': math.cos,
    'cosh': math.cosh,
    'degrees': math.degrees,
    'erf': math.erf,
    'erfc': math.erfc,
    'exp': math.exp,
    'expm1': math.expm1,
    'fabs': math.fabs,
    'factorial': math.factorial,
    'floor': math.floor,
    'fmod': math.fmod,
    'frexp': math.frexp,
    'fsum': math.fsum,
    'gamma': math.gamma,
    'gcd': math.gcd,
    'hypot': math.hypot,
    'isclose': math.isclose,
    'isfinite': math.isfinite,
    'isinf': math.isinf,
    'isnan': math.isnan,
    'ldexp': math.ldexp,
    'lgamma': math.lgamma,
    'log': math.log,
    'log1p': math.log1p,
    'log10': math.log10,
    'log2': math.log2,
    'modf': math.modf,
    'pow': math.pow,
    'radians': math.radians,
    'sin': math.sin,
    'sinh': math.sinh,
    'sqrt': math.sqrt,
    'tan': math.tan,
    'tanh': math.tanh,
    'trunc': math.trunc,
    'pi': math.pi,
    'e': math.e,
    'tau': math.tau,
    'inf': math.inf,
    'nan': math.nan,
}

FUNCTOOLS_CONTEXT = {
    'reduce': functools.reduce,
}

GLOBAL_CONTEXT: Dict[str, Any] = {
    # builtin constant
    'True': True,
    'False': False,
    'None': None,
    # builtin type
    'bool': bool,
    'bytes': bytes,
    'complex': complex,
    'dict': dict,
    'float': float,
    'frozenset': frozenset,
    'int': int,
    'list': list,
    'set': set,
    'str': str,
    'tuple': tuple,
    # builtin func
    'abs': abs,
    'all': all,
    'any': any,
    'ascii': ascii,
    'bin': bin,
    'chr': chr,
    'divmod': divmod,
    'enumerate': enumerate,
    'filter': filter,
    'hex': hex,
    'isinstance': isinstance,
    'issubclass': issubclass,
    'len': len,
    'map': map,
    'max': max,
    'min': min,
    'oct': oct,
    'ord': ord,
    'pow': pow,
    'range': range,
    'repr': repr,
    'reversed': reversed,
    'round': round,
    'sorted': sorted,
    'zip': zip,
    # decimal
    'Decimal': Decimal,
    # hash algorithm
    'sha1': lambda *x: hashlib.sha1(*x).hexdigest(),
    'sha224': lambda *x: hashlib.sha224(*x).hexdigest(),
    'sha256': lambda *x: hashlib.sha256(*x).hexdigest(),
    'sha384': lambda *x: hashlib.sha384(*x).hexdigest(),
    'sha512': lambda *x: hashlib.sha512(*x).hexdigest(),
    'sha3_224': lambda *x: hashlib.sha3_224(*x).hexdigest(),
    'sha3_256': lambda *x: hashlib.sha3_256(*x).hexdigest(),
    'sha3_384': lambda *x: hashlib.sha3_384(*x).hexdigest(),
    'sha3_512': lambda *x: hashlib.sha3_512(*x).hexdigest(),
    'md5': lambda *x: hashlib.md5(*x).hexdigest(),
    # datetime
    'date': datetime.date,
    'time': datetime.time,
    'datetime': datetime.datetime,
    'timedelta': datetime.timedelta,
    'tzinfo': datetime.tzinfo,
    'timezone': datetime.timezone,
    # module level injection
    'functools': functools,
    'itertools': itertools,
    'math': math,
    'operator': operator,
    'random': random,
    'statistics': statistics,
}

GLOBAL_CONTEXT.update(FUNCTOOLS_CONTEXT)
GLOBAL_CONTEXT.update(MATH_CONTEXT)

ALLOWED_STR_ATTRS = [
    'capitalize',
    'casefold',
    'center',
    'count',
    'encode',
    'endswith',
    'expandtabs',
    'find',
    'format',
    'format_map',
    'index',
    'isalnum',
    'isalpha',
    'isdecimal',
    'isdigit',
    'isidentifier',
    'islower',
    'isnumeric',
    'isprintable',
    'isspace',
    'istitle',
    'isupper',
    'join',
    'ljust',
    'lower',
    'lstrip',
    'maketrans',
    'partition',
    'replace',
    'rfind',
    'rindex',
    'rjust',
    'rpartition',
    'rsplit',
    'rstrip',
    'split',
    'splitlines',
    'swapcase',
    'startswith',
    'strip',
    'title',
    'translate',
    'upper',
    'zfill',
]

ALLOWED_BYTES_ATTRS = [
    'fromhex',
    'hex',
    'count',
    'decode',
    'endswith',
    'find',
    'index',
    'join',
    'maketrans',
    'partition',
    'replace',
    'rfind',
    'rindex',
    'rpartition',
    'startswith',
    'translate',
    'center',
    'ljust',
    'lstrip',
    'rjust',
    'rsplit',
    'rstrip',
    'split',
    'strip',
    'capitalize',
    'expandtabs',
    'isalnum',
    'isalpha',
    'isdigit',
    'islower',
    'isspace',
    'istitle',
    'isupper',
    'lower',
    'splitlines',
    'swapcase',
    'title',
    'upper',
    'zfill',
]

ALLOWED_LIST_ATTRS = [
    'index',
    'count',
    'append',
    'clear',
    'copy',
    'extend',
    'insert',
    'pop',
    'remove',
    'reverse',
    'sort',
]

ALLOWED_TUPLE_ATTRS = [
    'index',
    'count',
    'append',
    'clear',
    'copy',
    'extend',
    'insert',
    'pop',
    'remove',
    'reverse',
]

ALLOWED_SET_ATTRS = [
    'isdisjoint',
    'issubset',
    'issuperset',
    'union',
    'intersection',
    'difference',
    'symmetric_difference',
    'copy',
    'update',
    'intersection_update',
    'difference_update',
    'symmetric_difference_update',
    'add',
    'remove',
    'discard',
    'pop',
    'clear',
]

ALLOWED_DICT_ATTRS = [
    'copy',
    'fromkeys',
    'get',
    'items',
    'keys',
    'pop',
    'popitem',
    'setdefault',
    'update',
    'values',
]

ALLOWED_HTML_ATTRS = [
    'escape',
    'unescape',
]

ALLOWED_JSON_ATTRS = [
    'dumps',
    'loads',
]

ALLOWED_OPERATOR_ATTRS = [
    'lt',
    'le',
    'eq',
    'ne',
    'ge',
    'gt',
    'not_',
    'truth',
    'is_',
    'is_not',
    'add',
    'and_',
    'floordiv',
    'index',
    'inv',
    'invert',
    'lshift',
    'mod',
    'mul',
    'matmul',
    'neg',
    'or_',
    'pos',
    'pow',
    'rshift',
    'sub',
    'truediv',
    'xor',
    'concat',
    'contains',
    'countOf',
    'delitem',
    'getitem',
    'indexOf',
    'setitem',
    'length_hint',
    'itemgetter',
]

ALLOWED_RANDOM_ATTRS = [
    'randrange',
    'randint',
    'choice',
    'choices',
    'shuffle',
    'sample',
    'random',
    'uniform',
    'triangular',
    'betavariate',
    'expovariate',
    'gammavariate',
    'gauss',
    'lognormvariate',
    'normalvariate',
    'vonmisesvariate',
    'paretovariate',
    'weibullvariate',
]

ALLOWED_ITERTOOLS_ATTRS = [
    'accumulate',
    'chain',
    'chain.from_iterable',
    'compress',
    'dropwhile',
    'filterfalse',
    'groupby',
    'starmap',
    'takewhile',
    'tee',
    'zip_longest',
    'product',
    'permutations',
    'combinations',
    'combinations_with_replacement',
]

ALLOWED_STATISTICS_ATTRS = [
    'mean',
    'harmonic_mean',
    'median',
    'median_low',
    'median_high',
    'median_grouped',
    'mode',
    'pstdev',
    'pvariance',
    'stdev',
    'variance',
]

PROTECTED_IDS = [
    '__name__', '__doc__', '__package__', '__loader__', '__spec__',
    '__build_class__', '__import__', 'abs', 'all', 'any', 'ascii', 'bin',
    'callable', 'chr', 'compile', 'delattr', 'dir', 'divmod', 'eval', 'exec',
    'format', 'getattr', 'globals', 'hasattr', 'hash', 'hex', 'id', 'input',
    'isinstance', 'issubclass', 'iter', 'len', 'locals', 'max', 'min', 'next',
    'oct', 'ord', 'pow', 'print', 'repr', 'round', 'setattr', 'sorted', 'sum',
    'vars', 'None', 'Ellipsis', 'NotImplemented', 'False', 'True', 'bool',
    'memoryview', 'bytearray', 'bytes', 'classmethod', 'complex', 'dict',
    'enumerate', 'filter', 'float', 'frozenset', 'property', 'int', 'list',
    'map', 'object', 'range', 'reversed', 'set', 'slice', 'staticmethod',
    'str', 'super', 'tuple', 'type', 'zip', '__debug__', 'BaseException',
    'Exception', 'TypeError', 'StopAsyncIteration', 'StopIteration',
    'GeneratorExit', 'SystemExit', 'KeyboardInterrupt', 'ImportError',
    'ModuleNotFoundError', 'OSError', 'EnvironmentError', 'IOError',
    'EOFError', 'RuntimeError', 'RecursionError', 'NotImplementedError',
    'NameError', 'UnboundLocalError', 'AttributeError', 'SyntaxError',
    'IndentationError', 'TabError', 'LookupError', 'IndexError', 'KeyError',
    'ValueError', 'UnicodeError', 'UnicodeEncodeError', 'UnicodeDecodeError',
    'UnicodeTranslateError', 'AssertionError', 'ArithmeticError',
    'FloatingPointError', 'OverflowError', 'ZeroDivisionError', 'SystemError',
    'ReferenceError', 'BufferError', 'MemoryError', 'Warning', 'UserWarning',
    'DeprecationWarning', 'PendingDeprecationWarning', 'SyntaxWarning',
    'RuntimeWarning', 'FutureWarning', 'ImportWarning', 'UnicodeWarning',
    'BytesWarning', 'ResourceWarning', 'ConnectionError', 'BlockingIOError',
    'BrokenPipeError', 'ChildProcessError', 'ConnectionAbortedError',
    'ConnectionRefusedError', 'ConnectionResetError', 'FileExistsError',
    'FileNotFoundError', 'IsADirectoryError', 'NotADirectoryError',
    'InterruptedError', 'PermissionError', 'ProcessLookupError',
    'TimeoutError', 'open', 'quit', 'exit', 'copyright', 'credits',
    'license', 'help', '_'
]

ALLOWED_GLOBAL_ATTRS = list(set(
    ALLOWED_DICT_ATTRS + ALLOWED_STR_ATTRS + ALLOWED_BYTES_ATTRS +
    ALLOWED_LIST_ATTRS + ALLOWED_SET_ATTRS + ALLOWED_TUPLE_ATTRS +
    ALLOWED_ITERTOOLS_ATTRS + ALLOWED_OPERATOR_ATTRS +
    ALLOWED_RANDOM_ATTRS + ALLOWED_STATISTICS_ATTRS
)) + [
    # datetime
    'min',
    'max',
    'resolution'
    'days',
    'seconds',
    'microseconds',
    'total_seconds',
    'today',
    'fromtimestamp',
    'fromordinal',
    'year',
    'month',
    'day',
    'replace',
    'timetuple',
    'toordinal',
    'weekday',
    'isoweekday',
    'isocalendar',
    'isoformat',
    'ctime',
    'strftime',
    'now',
    'utcnow',
    'utcfromtimestamp',
    'combine',
    'strptime',
    'hour',
    'minute',
    'second',
    'microsecond',
    'tzinfo',
    'fold',
    'date',
    'time',
    'timetz',
    'astimezone',
    'utcoffset',
    'dst',
    'tzname',
    'utctimetuple',
    'timestamp',
    'fromutc',
]

ALLOWED_ATTRS = [
    '{}.{}'.format(g, a)
    for g in GLOBAL_CONTEXT.keys()
    for a in ALLOWED_GLOBAL_ATTRS
] + [
    'math.{}'.format(method) for method in MATH_CONTEXT.keys()
] + [
    'str.{}'.format(method) for method in ALLOWED_STR_ATTRS
] + [
    'bytes.{}'.format(method) for method in ALLOWED_BYTES_ATTRS
] + [
    'list.{}'.format(method) for method in ALLOWED_LIST_ATTRS
] + [
    'tuple.{}'.format(method) for method in ALLOWED_TUPLE_ATTRS
] + [
    'set.{}'.format(method) for method in ALLOWED_SET_ATTRS
] + [
    'dict.{}'.format(method) for method in ALLOWED_DICT_ATTRS
] + [
    'functools.{}'.format(method) for method in FUNCTOOLS_CONTEXT.keys()
] + [
    'itertools.{}'.format(method) for method in ALLOWED_ITERTOOLS_ATTRS
] + [
    'operator.{}'.format(method) for method in ALLOWED_OPERATOR_ATTRS
] + [
    'random.{}'.format(method) for method in ALLOWED_RANDOM_ATTRS
] + [
    'statistics.{}'.format(method) for method in ALLOWED_STATISTICS_ATTRS
]


def resolve_attr_id(node):
    if isinstance(node, (ast.Attribute, ast.Subscript)):
        value_id = None
        if isinstance(node.value, (ast.Name, ast.Attribute, ast.Subscript)):
            value_id = resolve_attr_id(node.value)
        elif isinstance(node.value, ast.Call):
            value_id = resolve_attr_id(node.value)
        elif isinstance(node.value, ast.Str):
            value_id = 'str'
        elif isinstance(node.value, ast.Bytes):
            value_id = 'bytes'
        elif isinstance(node.value, (ast.List, ast.ListComp)):
            value_id = 'list'
        elif isinstance(node.value, ast.Tuple):
            value_id = 'tuple'
        elif isinstance(node.value, (ast.Set, ast.SetComp)):
            value_id = 'set'
        elif isinstance(node.value, (ast.Dict, ast.DictComp)):
            value_id = 'dict'
        else:
            raise SyntaxError(
                'unsupport type: {}'.format(ast.dump(node.value))
            )

        if isinstance(node, ast.Attribute):
            return '{}.{}'.format(value_id, node.attr)
        elif isinstance(node, ast.Subscript):
            slice = None
            if isinstance(node.slice.value, ast.Str):
                slice = node.slice.value.s
            elif isinstance(node.slice.value, ast.Num):
                slice = node.slice.value.n
            elif isinstance(node.slice.value, ast.Name):
                slice = resolve_attr_id(node.slice.value)
            return '{}[{}]'.format(value_id, slice)
    elif isinstance(node, ast.Call):
        return '{}()'.format(resolve_attr_id(node.func))
    return node.id


class Transformer(ast.NodeTransformer):

    def visit_Num(self, node):  # noqa
        """Replace Num node to Decimal instance."""

        return ast.Call(
            func=ast.Name(id='Decimal', ctx=ast.Load()),
            args=[ast.Str(s=str(node.n))],
            keywords=[]
        )


class ExtractNames(ast.NodeVisitor):

    def __init__(self):
        self.names = []

    def visit_arg(self, node):
        self.names.append(node.arg)

    def visit_Name(self, node):  # noqa
        if isinstance(node.ctx, (TYPE_STORE, TYPE_DEL)):
            self.names.append(node.id)
        self.generic_visit(node)


class Validator(ast.NodeVisitor):

    def __init__(self, names):
        self.allowed_names = list(GLOBAL_CONTEXT.keys()) + names

    def visit_Call(self, node):  # noqa
        id = resolve_attr_id(node.func)
        allowed = []

        if isinstance(node.func, ast.Attribute):
            allowed = ALLOWED_ATTRS
        elif isinstance(node.func, ast.Name):
            allowed = self.allowed_names

        error = False
        if id not in allowed:
            error = True
            if isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name):
                    if node.func.attr in ALLOWED_GLOBAL_ATTRS:
                        error = False

        if error:
            raise SyntaxError('call {} is not permitted.'.format(id))

        self.generic_visit(node)

    def visit_Name(self, node):  # noqa
        if isinstance(node.ctx, (TYPE_STORE, TYPE_DEL)):
            if node.id in PROTECTED_IDS:
                raise SyntaxError('override builtins is not permitted.')
        else:
            if node.id not in self.allowed_names:
                raise SyntaxError(
                    'access to {} is not permitted.'.format(node.id))
        self.generic_visit(node)

    def visit_Attribute(self, node):  # noqa
        id = resolve_attr_id(node)
        if id not in ALLOWED_ATTRS:
            if node.attr not in ALLOWED_GLOBAL_ATTRS:
                raise SyntaxError(
                    'access to {} attr is not permitted.'.format(id)
                )
        self.generic_visit(node)

    def visit_FunctionDef(self, node):  # noqa
        raise SyntaxError('func def is not permitted.')

    def visit_AsyncFunctionDef(self, node):  # noqa
        raise SyntaxError('async func def is not permitted.')

    def visit_ClassDef(self, node):  # noqa
        raise SyntaxError('class def is not permitted.')

    def visit_Return(self, node):  # noqa
        raise SyntaxError('return is not permitted.')

    def visit_For(self, node):  # noqa
        raise SyntaxError('for stmt is not permitted.')

    def visit_AsyncFor(self, node):  # noqa
        raise SyntaxError('async for stmt is not permitted.')

    def visit_While(self, node):  # noqa
        raise SyntaxError('while stmt is not permitted.')

    def visit_With(self, node):  # noqa
        raise SyntaxError('with stmt is not permitted.')

    def visit_AsyncWith(self, node):  # noqa
        raise SyntaxError('async with stmt is not permitted.')

    def visit_Raise(self, node):  # noqa
        raise SyntaxError('raise stmt is not permitted.')

    def visit_Try(self, node):  # noqa
        raise SyntaxError('try stmt is not permitted.')

    def visit_Assert(self, node):  # noqa
        raise SyntaxError('assert stmt is not permitted.')

    def visit_Import(self, node):  # noqa
        raise SyntaxError('import is not permitted.')

    def visit_ImportFrom(self, node):  # noqa
        raise SyntaxError('import is not permitted.')

    def visit_Global(self, node):  # noqa
        raise SyntaxError('global stmt is not permitted.')

    def visit_Nonlocal(self, node):  # noqa
        raise SyntaxError('nonlocal stmt is not permitted.')

    def visit_Pass(self, node):  # noqa
        raise SyntaxError('pass stmt is not permitted.')

    def visit_Break(self, node):  # noqa
        raise SyntaxError('break stmt is not permitted.')

    def visit_Continue(self, node):  # noqa
        raise SyntaxError('continue stmt is not permitted.')


def calculate(
    expr: str,
    *,
    replace_num_to_decimal: bool=True
):
    node = ast.parse(expr, filename='<ast>', mode='exec')
    local: Dict[str, Any] = {}

    if replace_num_to_decimal:
        Transformer().visit(node)
        ast.fix_missing_locations(node)

    en = ExtractNames()
    en.visit(node)
    names = en.names

    if '__result__' in names:
        raise SyntaxError('assign __result__ value is not allowed.')

    Validator(names).visit(node)
    last = node.body[-1]
    expect_result = False
    result = None
    if isinstance(last, TYPE_EXPR):
        expect_result = True
        node.body[-1] = ast.Assign(
            targets=[ast.Name(id='__result__', ctx=ast.Store())],
            value=last.value
        )
        ast.fix_missing_locations(node)

    exec(compile(node, filename='<ast>', mode='exec'), GLOBAL_CONTEXT, local)

    if expect_result:
        result = local['__result__']
        del local['__result__']

    if isinstance(result, Iterable) and \
       not isinstance(result, BUILTIN_ITERABLE):
        result = list(result)

    return result, local
