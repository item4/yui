import datetime
import shlex
from typing import List, Set

import pytest

from yui.box import Box, Handler
from yui.command import argument, option
from yui.event import Hello, Message
from yui.transform import str_to_date, value_range


def test_box_class():
    box = Box()

    assert not box.aliases
    assert not box.handlers
    assert not box.crontabs

    @box.command('test1')
    async def test1(bot, event):
        """
        TEST SHORT HELP

        LONG CAT IS LONG

        """

    assert not box.aliases
    assert type(box.handlers['message'][None]['test1']) == Handler
    assert box.handlers['message'][None]['test1'].is_command
    assert box.handlers['message'][None]['test1'].use_shlex
    assert box.handlers['message'][None]['test1'].callback == test1
    params = set(
        box.handlers['message'][None]['test1'].signature.parameters.keys()
    )
    assert params == {'bot', 'event'}
    assert box.handlers['message'][None]['test1'].short_help == (
        'TEST SHORT HELP'
    )
    assert box.handlers['message'][None]['test1'].help == (
        'LONG CAT IS LONG'
    )
    assert not box.crontabs

    @box.command('test2', ['t2'], use_shlex=False)
    async def test2():
        pass

    assert box.aliases[None]['t2'] == 'test2'
    assert type(box.handlers['message'][None]['test1']) == Handler
    assert type(box.handlers['message'][None]['test2']) == Handler
    assert box.handlers['message'][None]['test1'].is_command
    assert box.handlers['message'][None]['test2'].is_command
    assert box.handlers['message'][None]['test1'].use_shlex
    assert not box.handlers['message'][None]['test2'].use_shlex
    assert box.handlers['message'][None]['test1'].callback == test1
    assert box.handlers['message'][None]['test2'].callback == test2
    assert not box.crontabs

    @box.on(Hello)
    async def test3():
        pass

    assert box.aliases[None]['t2'] == 'test2'
    assert type(box.handlers['message'][None]['test1']) == Handler
    assert type(box.handlers['message'][None]['test2']) == Handler
    assert type(box.handlers['hello'][None]['test3']) == Handler
    assert box.handlers['message'][None]['test1'].is_command
    assert box.handlers['message'][None]['test2'].is_command
    assert not box.handlers['hello'][None]['test3'].is_command
    assert box.handlers['message'][None]['test1'].is_command
    assert not box.handlers['message'][None]['test2'].use_shlex
    assert not box.handlers['hello'][None]['test3'].use_shlex
    assert box.handlers['message'][None]['test1'].callback == test1
    assert box.handlers['message'][None]['test2'].callback == test2
    assert box.handlers['hello'][None]['test3'].callback == test3
    assert not box.crontabs

    @box.crontab('*/3 * * * *')
    async def test4():
        pass

    assert box.aliases[None]['t2'] == 'test2'
    assert type(box.handlers['message'][None]['test1']) == Handler
    assert type(box.handlers['message'][None]['test2']) == Handler
    assert type(box.handlers['hello'][None]['test3']) == Handler
    assert box.handlers['message'][None]['test1'].is_command
    assert box.handlers['message'][None]['test2'].is_command
    assert not box.handlers['hello'][None]['test3'].is_command
    assert box.handlers['message'][None]['test1'].is_command
    assert not box.handlers['message'][None]['test2'].use_shlex
    assert not box.handlers['hello'][None]['test3'].use_shlex
    assert box.handlers['message'][None]['test1'].callback == test1
    assert box.handlers['message'][None]['test2'].callback == test2
    assert box.handlers['hello'][None]['test3'].callback == test3
    assert box.crontabs[0].spec == '*/3 * * * *'
    assert box.crontabs[0].func == test4


def test_handler_class():
    box = Box()

    @box.command('test')
    @option('--foo', '-f')
    @option('--bar')
    @argument('baz')
    @argument('kw', nargs=-1, concat=True)
    async def test(bot, event: Message, foo: int, bar: str, baz: str, kw: str):
        """
        TEST TITLE

        LONG
        CAT
        IS
        LONG

        """

    handler: Handler = box.handlers['message'][None]['test']
    assert handler.callback == test
    assert handler.channel_validator is None
    assert handler.is_command
    assert handler.use_shlex
    assert handler.short_help == 'TEST TITLE'
    assert handler.help == """LONG
CAT
IS
LONG"""
    assert handler.signature.parameters['bot']
    assert handler.signature.parameters['event']
    assert handler.signature.parameters['event'].annotation == Message
    assert handler.signature.parameters['foo']
    assert handler.signature.parameters['foo'].annotation == int
    assert handler.signature.parameters['bar']
    assert handler.signature.parameters['bar'].annotation == str
    assert handler.signature.parameters['baz']
    assert handler.signature.parameters['baz'].annotation == str
    assert handler.signature.parameters['kw']
    assert handler.signature.parameters['kw'].annotation == str

    option_chunks = shlex.split('-f 111 --bar aaaa first_arg second is long')

    options, argument_chunks = handler.parse_options(option_chunks)
    assert options['foo'] == 111
    assert options['bar'] == 'aaaa'

    arguments, remain_chunks = handler.parse_arguments(argument_chunks)
    assert arguments['baz'] == 'first_arg'
    assert arguments['kw'] == 'second is long'
    assert not remain_chunks


def test_handler_parse_option():
    box = Box()

    def callable_default():
        return 'hello'

    @box.command('test')
    @option('--required-option', required=True)
    @option('--dest-change-option', dest='dest_changed_option')
    @option('--is-flag', is_flag=True)
    @option('--multiple', multiple=True)
    @option('--container', container_cls=set, type_=float, nargs=2)
    @option('--callable-default', default=callable_default)
    @option('--non-type')
    @option('--default-option', default='!!!')
    @option('--transform', type_=int, transform_func=value_range(1, 10))
    @option('--transform-non-type', transform_func=str_to_date())
    @option('--transform-container', type_=int,
            transform_func=value_range(1, 10),
            container_cls=set, nargs=3)
    @option('--transform-two', transform_func=str_to_date(),
            container_cls=list, nargs=2)
    async def test(
        required_option: int,
        dest_changed_option: int,
        is_flag: bool,
        multiple: List[int],
        container,
        callable_default: str,
        non_type,
        default_option,
        transform: int,
        transform_non_type: datetime.date,
        transform_container: Set[int],
        transform_two: List[datetime.date],
    ):
        pass

    handler: Handler = box.handlers['message'][None]['test']

    option_chunks = shlex.split(
        '--required-option 1111 '
        '--dest-change-option 2222 '
        '--is-flag '
        '--multiple 3333 --multiple=4444 '
        '--container 55.55 66.66 '
        '--non-type world '
        '--transform 4 '
        '--transform-non-type 2017-10-07 '
        '--transform-container 4 6 2 '
        '--transform-two 2017-10-07 2017-10-24 '
    )

    options, argument_chunks = handler.parse_options(option_chunks)
    assert options['required_option'] == 1111
    assert options['dest_changed_option'] == 2222
    assert options['is_flag']
    assert options['multiple'] == [3333, 4444]
    assert options['container'] == {55.55, 66.66}
    assert options['callable_default'] == 'hello'
    assert options['non_type'] == 'world'
    assert options['default_option'] == '!!!'
    assert options['transform'] == 4
    assert options['transform_non_type'] == datetime.date(2017, 10, 7)
    assert options['transform_container'] == {2, 4, 6}
    assert options['transform_two'] == [
        datetime.date(2017, 10, 7),
        datetime.date(2017, 10, 24),
    ]
    assert not argument_chunks

    option_chunks = shlex.split('')

    with pytest.raises(SyntaxError) as e:
        handler.parse_options(option_chunks)
    assert e.value.msg == ('--required-option: incorrect option value count.'
                           ' expected 1, 0 given.')

    option_chunks = shlex.split(
        '--required-option 1111 '
        '--container 55.55 '
    )

    with pytest.raises(SyntaxError) as e:
        handler.parse_options(option_chunks)
    assert e.value.msg == ("--container: incorrect option value count."
                           " expected 2, 1 given.")

    option_chunks = shlex.split(
        '--required-option 1111 '
        '--container a b '
    )

    with pytest.raises(SyntaxError) as e:
        handler.parse_options(option_chunks)
    assert e.value.msg == ("--container: invalid type of option value"
                           "(could not convert string to float: 'a')")

    option_chunks = shlex.split(
        '--required-option 1111 '
        '--transform-non-type 2017-10-99'
    )

    with pytest.raises(SyntaxError) as e:
        handler.parse_options(option_chunks)
    assert e.value.msg == ("--transform-non-type: fail to transform option "
                           "value (day is out of range for month)")

    option_chunks = shlex.split(
        '--required-option 1111 '
        '--transform-two 2017-10-99 2017-10-00'
    )

    with pytest.raises(SyntaxError) as e:
        handler.parse_options(option_chunks)
    assert e.value.msg == ("--transform-two: fail to transform option "
                           "value (day is out of range for month)")


def test_handler_parse_argument():
    box = Box()

    @box.command('test')
    @argument('non_type')
    @argument('transform_non_type', transform_func=str_to_date())
    @argument('container', nargs=3, container_cls=set, type_=float)
    @argument('container_with_typing', nargs=3)
    @argument('container_with_transform', nargs=2, container_cls=list,
              transform_func=str_to_date())
    async def test(
        non_type,
        transform_non_type: datetime.date,
        container_with_typing: List[int],
        container_with_transform: List[datetime.date],
    ):
        pass

    handler: Handler = box.handlers['message'][None]['test']

    argument_chunks = shlex.split(
        'hello '
        '2017-10-07 '
        '3.3 1.1 2.2 '
        '1 2 3 '
        '2017-10-07 2017-10-24 '
    )

    arguments, remain_chunks = handler.parse_arguments(argument_chunks)

    assert arguments['non_type'] == 'hello'
    assert arguments['transform_non_type'] == datetime.date(2017, 10, 7)
    assert arguments['container'] == {1.1, 2.2, 3.3}
    assert arguments['container_with_typing'] == [1, 2, 3]
    assert arguments['container_with_transform'] == [
        datetime.date(2017, 10, 7),
        datetime.date(2017, 10, 24),
    ]

    @box.command('test2')
    @argument('args', nargs=-1)
    async def test2(args):
        pass

    handler: Handler = box.handlers['message'][None]['test2']

    argument_chunks = shlex.split('')

    with pytest.raises(SyntaxError) as e:
        handler.parse_arguments(argument_chunks)
    assert e.value.msg == ('args: incorrect argument value count.'
                           ' expected >0, 0 given.')

    @box.command('test3')
    @argument('args', nargs=2)
    @argument('concat', nargs=3, concat=True)
    async def test3(args):
        pass

    handler: Handler = box.handlers['message'][None]['test3']

    argument_chunks = shlex.split('1')

    with pytest.raises(SyntaxError) as e:
        handler.parse_arguments(argument_chunks)
    assert e.value.msg == ('args: incorrect argument value count.'
                           ' expected 2, 1 given.')

    argument_chunks = shlex.split('1 2 hell o world')

    arguments, remain_chunks = handler.parse_arguments(argument_chunks)
    assert arguments['args'] == ('1', '2')
    assert arguments['concat'] == 'hell o world'
    assert not remain_chunks

    @box.command('test4')
    @argument('args')
    async def test4(args: int):
        pass

    handler: Handler = box.handlers['message'][None]['test4']

    argument_chunks = shlex.split('asdf')

    with pytest.raises(SyntaxError) as e:
        handler.parse_arguments(argument_chunks)
    assert e.value.msg == ("args: invalid type of argument value"
                           "(invalid literal for int() with "
                           "base 10: 'asdf')")

    @box.command('test5')
    @argument('args', transform_func=str_to_date())
    async def test5(args):
        pass

    handler: Handler = box.handlers['message'][None]['test5']

    argument_chunks = shlex.split('2017-10-99')

    with pytest.raises(SyntaxError) as e:
        handler.parse_arguments(argument_chunks)
    assert e.value.msg == ('args: fail to transform argument value '
                           '(day is out of range for month)')

    @box.command('test6')
    @argument('args', nargs=2, transform_func=str_to_date())
    async def test6(args):
        pass

    handler: Handler = box.handlers['message'][None]['test6']

    argument_chunks = shlex.split('2017-10-99 2017-10-00')

    with pytest.raises(SyntaxError) as e:
        handler.parse_arguments(argument_chunks)
    assert e.value.msg == ('args: fail to transform argument value '
                           '(day is out of range for month)')
