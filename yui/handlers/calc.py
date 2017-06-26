import ast
import decimal
import html
import math
import signal
from collections.abc import Iterable

from ..box import box

TIMEOUT = 3
LENGTH_LIMIT = 300

BUILTIN_ITERABLE = str, bytes, list, tuple, set, frozenset, dict


def timeout_handler(signum, frame):
    raise TimeoutError()


async def body(bot, channel, chunks, help, num_to_decimal=True, ts=None):
    expr = html.unescape(' '.join(chunks[1:]))
    if not expr:
        await bot.say(channel, help)
        return

    signal.signal(signal.SIGALRM, timeout_handler)

    result = None
    try:
        signal.alarm(TIMEOUT)
        result, local = calculate(expr, replace_num_to_decimal=num_to_decimal)
    except SyntaxError as e:
        await bot.say(
            channel,
            '에러가 발생했어요! {}'.format(e),
            thread_ts=ts,
        )
        return
    except ZeroDivisionError:
        await bot.say(
            channel,
            '`{}`는 0으로 나누게 되어요. 0으로 나누는 건 안 돼요!'.format(expr),
            thread_ts=ts,
        )
        return
    except TimeoutError:
        await bot.say(
            channel,
            '`{}`는 실행하기엔 너무 오래 걸려요!'.format(expr),
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
    finally:
        signal.alarm(0)

    if result is not None:
        result_string = str(result)
        if result_string.isprintable():
            if len(result_string) <= LENGTH_LIMIT:
                await bot.say(
                    channel,
                    '`{}` == `{}`'.format(expr, result_string),
                    thread_ts=ts,
                )
            else:
                await bot.say(
                    channel,
                    '`{}` == `{}⋯`'.format(expr, result_string[:LENGTH_LIMIT]),
                    thread_ts=ts,
                )
        else:
            await bot.say(
                channel,
                '`{}` 는 실행하면 출력할 수 없는 문자가 섞여있어요!'.format(expr),
                thread_ts=ts,
            )
    elif local:
        await bot.say(
            channel,
            '`{}` 를 실행하면 지역변수가 이렇게 돼요!\n\n{}'.format(
                expr,
                '\n'.join(
                    '`{}` = `{}`'.format(key, value)
                    for key, value in local.items()
                )
            ),
            thread_ts=ts,
        )
    else:
        await bot.say(
            channel,
            '`{}` 를 실행해도 반환값도 없고, 지역변수도 비어있어요!'.format(expr),
            thread_ts=ts,
        )


@box.command('=', ['calc'])
async def calc_decimal(bot, message, chunks):
    await body(
        bot,
        message['channel'],
        chunks,
        '사용법: `{}= <계산할 수식>`'.format(bot.config.PREFIX),
        True,
    )


@box.command('=', ['calc'], subtype='message_changed')
async def calc_decimal_on_change(bot, message, chunks):
    await body(
        bot,
        message['channel'],
        chunks,
        '사용법: `{}= <계산할 수식>`'.format(bot.config.PREFIX),
        True,
        message['message']['ts'],
    )


@box.command('==')
async def calc_num(bot, message, chunks):
    await body(
        bot,
        message['channel'],
        chunks,
        '사용법: `{}== <계산할 수식>`'.format(bot.config.PREFIX),
        False,
    )


@box.command('==', subtype='message_changed')
async def calc_num_on_change(bot, message, chunks):
    await body(
        bot,
        message['channel'],
        chunks,
        '사용법: `{}== <계산할 수식>`'.format(bot.config.PREFIX),
        False,
        message['message']['ts'],
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

GLOBAL_CONTEXT = {
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
    'type': type,
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
    # module level injection
    'math': math,
}

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
    ALLOWED_LIST_ATTRS + ALLOWED_SET_ATTRS + ALLOWED_TUPLE_ATTRS
)) + [
   '__name__',
]

ALLOWED_ATTRS = [
    '{}.{}'.format(g, a)
    for g in GLOBAL_CONTEXT.keys()
    for a in ALLOWED_GLOBAL_ATTRS
] + [
    'math.{}'.format(method) for method in MATH_CONTEXT.keys()
] + [
    'math.{}.__name__'.format(method) for method in MATH_CONTEXT.keys()
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
]


def resolve_attr_id(node):
    if isinstance(node, ast.Attribute):
        value_id = None
        if isinstance(node.value, (ast.Name, ast.Attribute)):
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

        return '{}.{}'.format(value_id, node.attr)
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

    def visit_If(self, node):  # noqa
        raise SyntaxError('if stmt is not permitted.')

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
    local = {}

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
