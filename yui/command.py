""":mod:`yui.command` --- decorators for making command
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Decorators and classes for making command.

"""

import functools
import typing

__all__ = 'Argument', 'Option', 'argument', 'option'


def argument(
    name: str,
    dest: str=None,
    nargs: int=1,
    type_: typing.Union[type, typing.Callable]=str,
    concat: bool=False,
    type_error: str='{name}: invalid type of argument value({e})',
    count_error: str=('{name}: incorrect argument value count.'
                      ' expected {expected}, {given} given.')
) -> typing.Callable:
    """
    Add argument to command.

    :param name: argument name
    :type name: :class:`str`
    :param dest: destination name to assign value
    :type dest: :class:`str`
    :param nargs: :class:`str`
    :type nargs: :class:`int`
    :param type_: type of argument value
    :type type_: :class:`type` or :class:`typing.Callable`
    :param concat: flag to concat arguments
    :type concat: :class:`bool`
    :param type_error: error message for wrong type
    :type type_error: :class:`str`
    :param count_error: error message for wrong value count
    :type count_error: :class:`str`

    :return: decorator
    :rtype: :class:`typing.Callable`

    """

    if dest is None:
        dest = name.lower()

    def decorator(func):

        @functools.wraps(func)
        def internal(func_):
            if not hasattr(func_, '__arguments__'):
                func_.__arguments__ = []
            func_.__arguments__.insert(
                0,
                Argument(
                    name=name,
                    dest=dest,
                    nargs=nargs,
                    type_=type_,
                    concat=concat,
                    type_error=type_error,
                    count_error=count_error,
                )
            )
            return func_

        return internal(func)

    return decorator


def option(
    *args: str,
    default: typing.Any=None,
    dest: str=None,
    is_flag: bool=False,
    nargs: int=1,
    multiple: bool=False,
    required: bool=False,
    type_: typing.Union[type, typing.Callable]=str,
    value: typing.Any=None,
    type_error: str='{name}: invalid type of option value({e})',
    count_error: str=('{name}: incorrect option value count.'
                      ' expected {expected}, {given} given.')
) -> typing.Callable:
    """
    Add option parameter to command.

    :param args: names
    :type id: :class:`tuple` of :class:`str`
    :param default: default value
    :param dest: destination name to assign value
    :type dest: :class:`str`
    :param is_flag: set to flag option
    :type is_flag: :class:`bool`
    :param nargs: count of argument what option needed
    :type nargs: :class:`int`
    :param multiple: flag for assume values as list
    :type multiple: :class:`bool`
    :param required: set to required option
    :type required: :class:`bool`
    :param type_: type of option value
    :type type_: :class:`type` or :class:`typing.Callable`
    :param value: value to store flag
    :param type_error: error message for wrong type
    :type type_error: :class:`str`
    :param count_error: error message for wrong value count
    :type count_error: :class:`str`

    :return: real decorator
    :rtype: :class:`typing.Callable`

    """

    options: typing.List[Option] = []

    key: str = ' '.join(args)

    if dest is None:
        dest = args[0].lstrip('-').split('/')[0].replace('-', '_')

    for name in args:
        if '/' in name:
            true_case, false_case = name.split('/')
            options.append(
                Option(
                    key=key,
                    name=true_case,
                    default=default,
                    dest=dest,
                    nargs=0,
                    multiple=multiple,
                    required=required,
                    type_=bool,
                    value=True,
                    type_error=type_error,
                    count_error=count_error,
                )
            )
            options.append(
                Option(
                    key=key,
                    name=false_case,
                    default=default,
                    dest=dest,
                    nargs=0,
                    multiple=multiple,
                    required=required,
                    type_=bool,
                    value=False,
                    type_error=type_error,
                    count_error=count_error,
                )
            )
        elif is_flag:
            options.append(
                Option(
                    key=key,
                    name=name,
                    default=default,
                    dest=dest,
                    nargs=0,
                    multiple=multiple,
                    required=required,
                    type_=bool,
                    value=True if value is None else value,
                    type_error=type_error,
                    count_error=count_error,
                )
            )
        else:
            options.append(
                Option(
                    key=key,
                    name=name,
                    default=default,
                    dest=dest,
                    nargs=nargs,
                    multiple=multiple,
                    required=required,
                    type_=type_,
                    value=value,
                    type_error=type_error,
                    count_error=count_error,
                )
            )

    def decorator(func):

        @functools.wraps(func)
        def internal(func_):
            if not hasattr(func_, '__options__'):
                func_.__options__ = []
            func_.__options__[:] = options + func_.__options__

            return func_

        return internal(func)

    return decorator


class Argument:
    """Argument"""

    def __init__(
        self,
        name: str,
        dest: str,
        nargs: int,
        type_: typing.Union[type, typing.Callable],
        concat: bool,
        type_error: str,
        count_error: str
    ):
        """Initialize"""

        self.name = name
        self.dest = dest
        self.nargs = nargs
        self.type_ = type_
        self.concat = concat
        self.type_error = type_error
        self.count_error = count_error


class Option:
    """Option"""

    def __init__(
        self,
        key: str,
        name: str,
        default: typing.Any,
        dest: str,
        nargs: int,
        multiple: bool,
        required: bool,
        type_: typing.Union[type, typing.Callable],
        value: typing.Any,
        type_error: str,
        count_error: str
    ):
        """Initialize"""

        self.key = key
        self.name = name
        self.default = default
        self.dest = dest
        self.nargs = nargs
        self.multiple = multiple
        self.required = required
        self.type_ = type_
        self.value = value
        self.type_error = type_error
        self.count_error = count_error
