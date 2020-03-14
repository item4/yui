import inspect
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

from .utils import is_container
from ..types.handler import Handler
from ..utils.cast import CastError
from ..utils.cast import cast

KWARGS_DICT = Dict[str, Any]


def parse_option_and_arguments(
    handler: Handler, chunks: List[str],
) -> Tuple[KWARGS_DICT, List[str]]:
    end = False

    result: KWARGS_DICT = {}
    options = handler.options
    arguments = handler.arguments

    for o in options:
        if o.type_ is None:
            type_ = handler.params[o.dest].annotation

            if type_ == inspect._empty:  # type: ignore
                type_ = str
            else:
                if o.transform_func:
                    type_ = str

            o.type_ = type_

    for a in arguments:
        if a.type_ is None:
            type_ = handler.params[a.dest].annotation

            if type_ == inspect._empty:  # type: ignore
                type_ = str
            else:
                if a.transform_func:
                    type_ = str

            a.type_ = type_
            if is_container(a.type_):
                a.container_cls = None
                a.typing_has_container = True

    required = {o.dest for o in options if o.required}

    for option in options:
        if option.multiple:
            result[option.dest] = []
        else:
            if callable(option.default):
                result[option.dest] = option.default()
            else:
                result[option.dest] = option.default

    while not end and chunks:
        for option in options:
            name = chunks.pop(0)
            if name.startswith(option.name + '='):
                name, new_chunk = name.split('=', 1)
                chunks.insert(0, new_chunk)

            if name == option.name:
                if option.dest in required:
                    required.remove(option.dest)

                if option.nargs == 0:
                    result[option.dest] = option.value
                    break

                length = len(chunks)
                try:
                    args = [chunks.pop(0) for _ in range(option.nargs)]
                except IndexError:
                    raise SyntaxError(
                        option.count_error.format(
                            name=option.name,
                            expected=option.nargs,
                            given=length,
                        )
                    )
                try:
                    if option.container_cls:
                        if option.multiple:
                            r = cast(option.type_, args)
                        else:
                            r = option.container_cls(
                                cast(option.type_, x) for x in args
                            )
                    else:
                        r = cast(option.type_, args[0])
                except (ValueError, CastError) as e:
                    raise SyntaxError(
                        option.type_error.format(name=option.name, e=e)
                    )

                if option.transform_func:
                    if option.container_cls:
                        try:
                            r = option.container_cls(
                                option.transform_func(x) for x in r
                            )
                        except ValueError as e:
                            raise SyntaxError(
                                option.transform_error.format(
                                    name=option.name, e=e,
                                )
                            )
                    else:
                        try:
                            r = option.transform_func(r)
                        except ValueError as e:
                            raise SyntaxError(
                                option.transform_error.format(
                                    name=option.name, e=e,
                                )
                            )

                if option.multiple:
                    result[option.dest].append(r[0])
                else:
                    result[option.dest] = r

                break
            chunks.insert(0, name)
        else:
            end = True

    if required:
        raise SyntaxError(
            '\n'.join(
                o.count_error.format(name=o.name, expected=o.nargs, given=0,)
                for o in (
                    list(filter(lambda x: x.dest == o, options))[0]
                    for o in required
                )
            )
        )

    for i, argument in enumerate(arguments):
        length = argument.nargs
        if argument.nargs < 0:
            length = len(chunks) - sum(a.nargs for a in arguments[i:]) - 1

        if length < 1:
            raise SyntaxError(
                argument.count_error.format(
                    name=argument.name, expected='>0', given=0,
                )
            )
        if length <= len(chunks):
            args = [chunks.pop(0) for _ in range(length)]
        else:
            raise SyntaxError(
                argument.count_error.format(
                    name=argument.name,
                    expected=argument.nargs,
                    given=len(chunks),
                )
            )
        try:
            if argument.concat:
                r = ' '.join(args)
            elif argument.container_cls:
                r = argument.container_cls(
                    cast(argument.type_, x) for x in args
                )
            elif argument.typing_has_container:
                r = cast(argument.type_, args)
            else:
                r = cast(argument.type_, args[0])
        except (ValueError, CastError) as e:
            raise SyntaxError(
                argument.type_error.format(name=argument.name, e=e,)
            )

        if argument.transform_func:
            if argument.container_cls and r:
                try:
                    r = argument.container_cls(
                        argument.transform_func(x) for x in r
                    )
                except ValueError as e:
                    raise SyntaxError(
                        argument.transform_error.format(
                            name=argument.name, e=e,
                        )
                    )
            else:
                try:
                    r = argument.transform_func(r)
                except ValueError as e:
                    raise SyntaxError(
                        argument.transform_error.format(
                            name=argument.name, e=e,
                        )
                    )

        if r is not None:
            result[argument.dest] = r

    return result, chunks
