import inspect
from functools import partial
from typing import Dict, Iterable, List, TYPE_CHECKING

import attr

from ..utils.datetime import fromtimestamp

if TYPE_CHECKING:
    from ..bot import Bot


class Namespace:
    """Factory of attr.s decorator with supporting unexpected kwargs."""

    _bot: 'Bot'

    def __init__(self, **kwargs):
        # These params was not supported
        kwargs.pop('maybe_cls', None)
        kwargs.pop('these', None)
        kwargs.pop('repr_ns', None)
        kwargs.pop('slots', None)  # can not use __slots__ and __dict__ both

        if 'auto_attribs' not in kwargs:
            kwargs['auto_attribs'] = True

        self.kwargs = kwargs

    def __call__(self, cls):
        # At first, apply attr.dataclass to cls
        cls = attr.s(**self.kwargs)(cls)

        # Move and keep old init
        cls.__old_init__ = cls.__init__
        cls.__old_init__.__name__ = '__old_init__'
        cls.__old_init__.__qualname__ = f'{cls.__qualname__}.__old_init__'

        # make parts of new body of __init__
        old_signature = inspect.signature(cls.__old_init__)
        init_args = ', '.join(
            key for key in old_signature.parameters.keys() if key != 'self'
        )
        params = [
            p.replace(annotation=inspect.Parameter.empty)
            for p in old_signature.parameters.values()
        ]
        params.append(inspect.Parameter(
            '_kwargs',
            inspect.Parameter.VAR_KEYWORD,
        ))
        new_signature = inspect.Signature(
            params,
            return_annotation=old_signature.return_annotation,
        )

        # make new __init__ by eval
        _global: Dict = {}
        _local: Dict = {}
        code = f"""\
def __init__{str(new_signature)}:
    self.__old_init__({init_args})
    self.__dict__.update(_kwargs)
"""
        eval(compile(code, cls.__qualname__, 'exec'), _global, _local)

        # update metadata of new __init__
        __new_init__ = _local['__init__']
        __new_init__.__module__ = cls.__module__
        __new_init__.__annotations__ = cls.__old_init__.__annotations__
        __new_init__.__qualname__ = f'{cls.__qualname__}.__init__'
        __new_init__.__name__ = f'__init__'

        # overwrite __init__
        cls.__init__ = __new_init__

        return cls


def channel_id_convert(value):
    bot = Namespace._bot

    if value is None:
        return value
    elif isinstance(value, str):
        id = value
    else:
        id = value.get('id')
    if id is None:
        return id

    try:
        objs = {
            'C': bot.channels,
            'D': bot.ims,
            'G': bot.groups,
        }[id[0]]
    except KeyError:
        raise KeyError('Given Channel ID prefix was not expected.')
    raise_error = bool(objs)
    for obj in objs:
        if obj.id == id:
            return obj
    if raise_error:
        raise KeyError('Bot did not know given ID.')

    from .channel import create_unknown_channel  # circular dependency
    return create_unknown_channel(**value)


def user_id_convert(value):
    bot = Namespace._bot
    raise_error = bool(bot.users)
    if value is None:
        return value
    elif isinstance(value, str):
        id = value
    else:
        id = value.get('id')
    if id is None:
        return id

    from .user import create_unknown_user  # circular dependency
    if not id.startswith('U'):
        raise KeyError('Given ID value has unexpected prefix.')
    for obj in bot.users:
        if obj.id == id:
            return obj
    if raise_error:
        raise KeyError('Bot did not know given ID.')

    return create_unknown_user(**value)


def id_convert(value):
    if value is None:
        return value
    elif isinstance(value, str):
        id = value
    else:
        id = value.get('id')
    if id is None:
        return id

    if id.startswith('U'):
        return user_id_convert(value)
    return channel_id_convert(value)


def name_convert(value, type: str = None):
    bot = Namespace._bot
    fields: List[Iterable] = []
    if type is None:
        fields.extend([
            bot.channels,
            bot.ims,
            bot.groups,
            bot.users,
        ])
    else:
        fields.append(getattr(bot, type))
    for field in fields:
        for obj in field:
            if obj.name == value:
                return obj
    raise KeyError('Bot did not know given name.')


def user_name_convert(value):
    return name_convert(value, 'users')


def list_convert(values, conv):
    if values is None:
        return values
    return [conv(v) for v in values]


# shortcut decorator
namespace = Namespace()

SlackObjectField = partial(attr.ib, converter=id_convert)
ChannelField = partial(attr.ib, converter=channel_id_convert)
UserField = partial(attr.ib, converter=user_id_convert)
NameField = partial(attr.ib, repr=True, converter=str)
IDField = partial(attr.ib, repr=True, converter=str)
TsField = partial(attr.ib, repr=True, converter=str, default='')
required = partial(attr.ib, repr=True)
Field = partial(attr.ib, default=None, repr=False)
BooleanField = partial(Field, converter=bool)


def OptionalField(conv):  # noqa
    return partial(Field, converter=attr.converters.optional(conv))


IntegerField = OptionalField(int)
StringField = OptionalField(str)
DateTimeField = OptionalField(fromtimestamp)
OptionalUserField = OptionalField(user_id_convert)


def ListField(conv):  # noqa
    return partial(Field, converter=lambda x: list_convert(x, conv))


ChannelListField = ListField(channel_id_convert)
UserListField = ListField(user_id_convert)
