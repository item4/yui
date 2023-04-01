from typing import Any
from typing import TypeAlias

from ..types.handler import Handler
from ..utils.cast import cast
from ..utils.cast import CastError

KWARGS_DICT: TypeAlias = dict[str, Any]


def parse_option_and_arguments(
    handler: Handler,
    chunks: list[str],
) -> tuple[KWARGS_DICT, list[str]]:
    end = False
    if not handler.is_prepared:
        handler.prepare()

    result: KWARGS_DICT = {}
    options = handler.options
    arguments = handler.arguments

    required = {o.dest for o in options if o.required}

    for option in options:
        if option.multiple:
            result[option.dest] = []
        elif callable(option.default):
            result[option.dest] = option.default()
        else:
            result[option.dest] = option.default

    while not end and chunks:
        for option in options:
            name = chunks.pop(0)
            if name.startswith(option.name + "="):
                name, new_chunk = name.split("=", 1)
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
                except IndexError as e:
                    raise SyntaxError(
                        option.count_error.format(
                            name=option.name,
                            expected=option.nargs,
                            given=length,
                        ),
                    ) from e
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
                    ) from e

                if option.transform_func:
                    if option.container_cls:
                        try:
                            r = option.container_cls(
                                option.transform_func(x) for x in r
                            )
                        except ValueError as e:
                            raise SyntaxError(
                                option.transform_error.format(
                                    name=option.name,
                                    e=e,
                                ),
                            ) from e
                    else:
                        try:
                            r = option.transform_func(r)
                        except ValueError as e:
                            raise SyntaxError(
                                option.transform_error.format(
                                    name=option.name,
                                    e=e,
                                ),
                            ) from e

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
            "\n".join(
                o.count_error.format(
                    name=o.name,
                    expected=o.nargs,
                    given=0,
                )
                for o in (
                    list(filter(lambda x: x.dest == o, options))[0]
                    for o in required
                )
            ),
        )

    for i, argument in enumerate(arguments):
        length = argument.nargs
        if argument.nargs < 0:
            length = len(chunks) - sum(a.nargs for a in arguments[i:]) - 1

        if length < 1:
            raise SyntaxError(
                argument.count_error.format(
                    name=argument.name,
                    expected=">0",
                    given=0,
                ),
            )
        if length <= len(chunks):
            args = [chunks.pop(0) for _ in range(length)]
        else:
            raise SyntaxError(
                argument.count_error.format(
                    name=argument.name,
                    expected=argument.nargs,
                    given=len(chunks),
                ),
            )
        try:
            if argument.concat:
                r = " ".join(args)
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
                argument.type_error.format(
                    name=argument.name,
                    e=e,
                ),
            ) from e

        if argument.transform_func:
            if argument.container_cls and r:
                try:
                    r = argument.container_cls(
                        argument.transform_func(x) for x in r
                    )
                except ValueError as e:
                    raise SyntaxError(
                        argument.transform_error.format(
                            name=argument.name,
                            e=e,
                        ),
                    ) from e
            else:
                try:
                    r = argument.transform_func(r)
                except ValueError as e:
                    raise SyntaxError(
                        argument.transform_error.format(
                            name=argument.name,
                            e=e,
                        ),
                    ) from e

        if r is not None:
            result[argument.dest] = r

    return result, chunks
