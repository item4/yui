from mypy.plugin import Plugin
from mypy.plugins.attrs import attr_define_makers

attr_define_makers.add("yui.utils.attrs.define")


class YuiPlugin(Plugin):
    pass


def plugin(version):
    return YuiPlugin
