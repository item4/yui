import decimal
import math
import re

from ..box import box


@box.command('calc', ['='])
async def calc(bot, message, chunks):
    expr = ' '.join(chunks[1:])
    if not expr:
        await bot.say(
            message['channel'],
            '사용법: `{}= <계산할 수식>`'.format(bot.config.PREFIX)
        )
        return

    res = None
    try:
        res = calculate(expr)
    except SyntaxError as e:
        await bot.say(message['channel'], '에러가 발생했어요! {}'.format(e))
        return
    except ZeroDivisionError:
        await bot.say(
            message['channel'],
            '`{}`는 0으로 나누게 되어요. 0으로 나누는 건 안 돼요!'
        )
        return
    except Exception as e:
        await bot.say(message['channel'], '에러가 발생했어요! {}'.format(e))
        return

    assert res is not None

    await bot.say(
        message['channel'],
        '`{}` == {}'.format(expr, res)
    )


operator_function = [
    'abs',
    'sqrt',
    'factorial',
    'max',
    'min',
    'sum',
    'count',
    'len',
    'avg',
    'average',
    'varp',
    'var',
    'stdevp',
    'stdev',
    'ceil',
    'floor',
    'round',
    'log',
    'ln',
    'log10',
    'deg',
    'rad',
    'degree',
    'radian',
    'acosh',
    'asinh',
    'atanh',
    'acos',
    'asin',
    'atan',
    'cosh',
    'sinh',
    'tanh',
    'cos',
    'sin',
    'tan',
]

operator_level = {
    '(': -1,
    ')': -1,
    ',': 0,
    '+': 1,
    '-': 1,
    '%': 2,
    '*': 3,
    '/': 3,
    '**': 4,
    '^': 4,
}
for x in operator_function:
    operator_level[x] = 1000

operator_term = {
    '(': 0,
    ')': 0,
    ',': 2,
    '+': 2,
    '-': 2,
    '%': 2,
    '*': 2,
    '/': 2,
    '**': 2,
    '^': 2,
}
for x in operator_function:
    operator_term[x] = 1


term_pattern = re.compile('\s*(-?\s*(?:\d+\.\d+|\.\d+|\d+\.|\d+)|pi|e)\s*')
operator_pattern = re.compile(
    '\s*(,|\+|-|\^|\*\*|\*|/|%|\(\s*|\s*\)|' +
    '|'.join(operator_function) + ')\s*'
)


def average(args):
    return sum(args) / len(args)


def variance(args, entire=False):
    var = 0
    avg = average(args)
    for x in args:
        var += (avg - x) ** 2
    if entire:
        return var / (len(args) - 1)
    else:
        return var / len(args)


def priority(op):
    return operator_level[op]


def need_term(op):
    return operator_term[op]


def calculate(args):
    args = re.sub('(-\s*(?:\.\d+|\d+\.\d+|\d+\.|\d+|pi|e))', '+(\\1)', args)

    if args[0] == '+':
        args = '0' + args

    args = args.replace('(+', '(0+').replace(',+', ',0+')

    result_stack = []
    operator_stack = []

    length = len(args)
    i = 0

    while i < length:
        term = term_pattern.match(args[i:])
        if term:
            temp = term.group(1).replace(' ', '')
            if temp == 'pi':
                t = math.pi
            elif temp == 'e':
                t = math.e
            else:
                t = temp

            result_stack.append(decimal.Decimal(t))
            i += len(term.group(0))
            continue

        operator = operator_pattern.match(args[i:])
        if operator:
            op = operator.group(1).replace(' ', '')

            if op == '(':
                operator_stack.append(op)
            elif op == ')':
                temp = operator_stack.pop()
                while temp != '(':
                    result_stack.append(temp)
                    temp = operator_stack.pop()
            else:
                if operator_stack and \
                   priority(operator_stack[-1]) >= priority(op):
                    result_stack.append(operator_stack.pop())
                operator_stack.append(op)

            i += len(operator.group(0))
            continue
        raise SyntaxError(u'비정상적인 연산자 : `{}`'.format(args[i:]))

    while operator_stack:
        result_stack.append(operator_stack.pop())

    term_stack = []

    while result_stack:
        some = result_stack[0]
        result_stack[:] = result_stack[1:]
        if type(some) == decimal.Decimal:
            term_stack.append(some)
        else:
            op = some
            temp = need_term(op)
            if temp == 1:
                t = term_stack.pop()
                if op == 'abs':
                    res = abs(t)
                elif op == 'sin':
                    res = math.sin(t)
                elif op == 'cos':
                    res = math.cos(t)
                elif op == 'tan':
                    res = math.tan(t)
                elif op == 'sqrt':
                    res = math.sqrt(t)
                elif op == 'ceil':
                    res = math.ceil(t)
                elif op == 'floor':
                    res = math.floor(t)
                elif op == 'round':
                    res = round(float(t[0]), int(t[1]))
                elif op == 'acos':
                    res = math.acos(t)
                elif op == 'asin':
                    res = math.asin(t)
                elif op == 'atan':
                    res = math.atan(t)
                elif op == 'factorial':
                    res = math.factorial(t)
                elif op == 'log':
                    if type(t) == list:
                        res = math.log(t[0], t[1])
                    else:
                        res = math.log(t)
                elif op == 'ln':
                    res = math.log(t)
                elif op == 'log10':
                    res = math.log10(t)
                elif op in ['deg', 'degree']:
                    res = math.degrees(t)
                elif op in ['rad', 'radian']:
                    res = math.radians(t)
                elif op == 'acosh':
                    res = math.acosh(t)
                elif op == 'asinh':
                    res = math.asinh(t)
                elif op == 'atanh':
                    res = math.atanh(t)
                elif op == 'cosh':
                    res = math.cosh(t)
                elif op == 'sinh':
                    res = math.sinh(t)
                elif op == 'tanh':
                    res = math.tanh(t)
                elif op == 'max':
                    if type(t) != list:
                        res = t
                    else:
                        res = max(t)
                elif op == 'min':
                    if type(t) != list:
                        res = t
                    else:
                        res = min(t)
                elif op == 'sum':
                    if type(t) != list:
                        res = t
                    else:
                        res = sum(t)
                elif op in ['count',  'len']:
                    if type(t) != list:
                        res = 1
                    else:
                        res = len(t)
                elif op in ['avg', 'average']:
                    if type(t) != list:
                        res = 1
                    else:
                        res = average(t)
                elif op == 'var':
                    if type(t) != list:
                        res = 0
                    else:
                        res = variance(t)
                elif op == 'varp':
                    if type(t) != list:
                        res = 0
                    else:
                        res = variance(t, True)
                elif op == 'stdev':
                    if type(t) != list:
                        res = 0
                    else:
                        res = float(variance(t)) ** .5
                elif op == 'stdevp':
                    if type(t) != list:
                        res = 0
                    else:
                        res = float(variance(t, True)) ** .5
                elif op == 'test':
                    res = 0

                res = decimal.Decimal(res)
            elif temp == 2:
                try:
                    back = term_stack.pop()
                    front = term_stack.pop()
                except IndexError:
                    raise SyntaxError(u'인자 갯수가 올바르지 않음')

                if op == '+':
                    res = decimal.Decimal(front + back)
                elif op == '-':
                    res = decimal.Decimal(front - back)
                elif op == '*':
                    res = decimal.Decimal(front * back)
                elif op == '/':
                    res = decimal.Decimal(front / back)
                elif op == '%':
                    res = decimal.Decimal(front % back)
                elif op in ['**', '^']:
                    res = decimal.Decimal(front ** back)
                elif op == ',':
                    if type(front) == list:
                        res = front + [back]
                    elif type(back) == list:
                        res = [front] + back
                    else:
                        res = [front, back]

            term_stack.append(res)
    if len(term_stack) > 1:
        raise SyntaxError(u'비정상적인 인자들')

    return term_stack[0]
