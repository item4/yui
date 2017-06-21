import ast
import decimal
import html
import math

from ..box import box


@box.command('calc', ['='])
async def calc(bot, message, chunks):
    expr = html.unescape(' '.join(chunks[1:]))
    if not expr:
        await bot.say(
            message['channel'],
            '사용법: `{}= <계산할 수식>`'.format(bot.config.PREFIX)
        )
        return

    result = None
    try:
        result, local = calculate(expr)
    except SyntaxError as e:
        await bot.say(message['channel'], '에러가 발생했어요! {}'.format(e))
        return
    except ZeroDivisionError:
        await bot.say(
            message['channel'],
            '`{}`는 0으로 나누게 되어요. 0으로 나누는 건 안 돼요!'.format(expr)
        )
        return
    except Exception as e:
        await bot.say(
            message['channel'],
            '에러가 발생했어요! {}: {}'.format(e.__class__.__name__, e)
        )
        return

    if result is not None:
        await bot.say(
            message['channel'],
            '`{}` == `{}`'.format(expr, result)
        )
    else:
        await bot.say(
            message['channel'],
            '`{}` 를 실행하면 지역변수가 이렇게 되요!\n\n{}'.format(
                expr,
                '\n'.join(
                    '`{}` = `{}`'.format(key, value)
                    for key, value in local.items()
                )
            )
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

ALLOWED_GLOBAL_ATTRS = [
    '__name__',
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

ALLOWED_ATTRS = [
    '{}.{}'.format(g, a)
    for g in GLOBAL_CONTEXT.keys()
    for a in ALLOWED_GLOBAL_ATTRS
] + [
    'math.{}'.format(method) for method in MATH_CONTEXT.keys()
] + [
    'math.{}.__name__'.format(method) for method in MATH_CONTEXT.keys()
]


def resolve_attr_id(node):
    if isinstance(node, ast.Attribute):
        return '{}.{}'.format(resolve_attr_id(node.value), node.attr)
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

        if id not in allowed:
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
        raise SyntaxError('with stmt is not permitted')

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

    return result, local
