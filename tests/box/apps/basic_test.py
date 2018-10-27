from yui.box import Box
from yui.box.apps.basic import App
from yui.command.decorators import argument, option
from yui.event import Message


def test_basic_app():
    box = Box()

    @box.command('test', aliases=['tttt'])
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

    app: App = box.apps.pop()
    assert app.name == 'test'
    assert app.aliases == ['tttt']
    assert app.names == ['tttt', 'test']
    assert app.handler == test
    assert app.channel_validator is None
    assert app.is_command
    assert app.use_shlex
    assert app.has_short_help
    assert app.has_full_help
    assert app.short_help == 'TEST TITLE'
    assert app.help == """LONG
CAT
IS
LONG"""
    assert app.get_short_help('=') == '`=test`: TEST TITLE'
    assert app.get_full_help('=') == (
        '*=test*\n'
        '(Aliases: `=tttt`)\n'
        'TEST TITLE\n\n'
        'LONG\n'
        'CAT\n'
        'IS\n'
        'LONG'
    )
