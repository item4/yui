from yui.box import Box
from yui.box.apps.basic import App
from yui.event import Hello


def test_box_class():
    box = Box()

    assert not box.apps
    assert not box.tasks

    @box.command("test1")
    async def test1(bot, event):
        """
        TEST SHORT HELP

        LONG CAT IS LONG

        """

    h1 = box.apps.pop()
    assert isinstance(h1, App)
    assert h1.is_command
    assert h1.use_shlex
    assert h1.handler == test1
    assert h1.short_help == "TEST SHORT HELP"
    assert h1.help == "LONG CAT IS LONG"
    assert not box.tasks

    @box.command("test2", ["t2"], use_shlex=False)
    async def test2():
        """Short only"""

    h2 = box.apps.pop()
    assert isinstance(h2, App)
    assert h2.is_command
    assert not h2.use_shlex
    assert h2.handler == test2
    assert h2.short_help == "Short only"
    assert h2.help is None
    assert not box.tasks

    @box.on(Hello)
    async def test3():
        pass

    h3 = box.apps.pop()
    assert isinstance(h3, App)
    assert not h3.is_command
    assert not h3.use_shlex
    assert h3.handler == test3
    assert not box.tasks

    @box.cron("*/3 * * * *")
    async def test4():
        pass

    assert box.tasks[0].spec == "*/3 * * * *"
    assert box.tasks[0].handler == test4

    @box.on("message")
    async def test4():
        pass

    h4 = box.apps.pop()
    assert isinstance(h4, App)
    assert not h4.is_command
    assert not h4.use_shlex
    assert h4.handler == test4

    box.assert_config_required("OWNER_TOKEN", str)
    assert box.config_required["OWNER_TOKEN"] is str

    box.assert_channel_required("game")
    assert box.channel_required == {"game"}

    box.assert_channels_required("test")
    assert box.channels_required == {"test"}

    box.assert_user_required("admin")
    assert box.user_required == {"admin"}

    box.assert_users_required("player")
    assert box.users_required == {"player"}

    class Test(App):
        pass

    testapp = Test(handler=test4, type="message", subtype=None)
    box.register(testapp)
    assert box.apps.pop() == testapp
