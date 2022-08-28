import asyncio
import functools
import os.path
import pathlib

from alembic import command
from alembic.config import Config

import click

from .bot import Bot
from .config import ConfigurationError
from .config import load


def error(message: str):
    """Echo and die with error message"""

    click.echo("Error: " + message, err=True)
    raise SystemExit(1)


def load_config(func):
    """Decorator for add load config file option"""

    @functools.wraps(func)
    def internal(*args, **kwargs):
        filename = kwargs.pop("config")
        if filename is None:
            click.echo("--config option is required.", err=True)
            raise SystemExit(1)

        config = load(pathlib.Path(filename))
        kwargs["config"] = config
        return func(*args, **kwargs)

    decorator = click.option(
        "--config",
        "-c",
        type=click.Path(exists=True),
        envvar="YUI_CONFIG_FILE_PATH",
    )

    return decorator(internal)


@click.group()
def yui():
    """YUI, Slack Bot for item4.slack.com"""


@yui.command()
@load_config
def run(config):
    """Run YUI."""
    try:
        while True:
            bot = Bot(config)
            asyncio.run(bot.run())
    except ConfigurationError as e:
        error(str(e))


@yui.command()
@click.option("--message", "-m")
@click.option("--autogenerate", is_flag=True, default=False)
@click.option("--sql", is_flag=True, default=False)
@click.option("--head", default="head")
@click.option("--splice", is_flag=True, default=False)
@click.option("--branch-label")
@click.option("--version-path")
@click.option("--rev-id")
@load_config
def revision(
    config,
    message: str | None,
    autogenerate: bool,
    sql: bool,
    head: str,
    splice: bool,
    branch_label: str | None,
    version_path: str | None,
    rev_id: str | None,
):
    """Create a new revision file."""

    def op(connection, c):
        c.attributes["connection"] = connection
        command.revision(
            c,
            message,
            autogenerate=autogenerate,
            sql=sql,
            head=head,
            splice=splice,
            branch_label=branch_label,
            version_path=version_path,
            rev_id=rev_id,
        )

    async def main():
        bot = Bot(config)
        directory = os.path.join("yui", "migrations")
        c = Config(os.path.join(directory, "alembic.ini"))
        c.set_main_option("script_location", directory)
        c.set_main_option("sqlalchemy.url", bot.config.DATABASE_URL)
        c.attributes["Base"] = bot.orm_base
        async with bot.database_engine.begin() as conn:
            await conn.run_sync(op, c)

    asyncio.run(main())


@yui.command()
@click.option("--message", "-m")
@click.option("--sql", is_flag=True, default=False)
@click.option("--head", default="head")
@click.option("--splice", is_flag=True, default=False)
@click.option("--branch-label")
@click.option("--version-path")
@click.option("--rev-id")
@load_config
def migrate(
    config,
    message: str | None,
    sql: bool,
    head: str,
    splice: bool,
    branch_label: str | None,
    version_path: str | None,
    rev_id: str | None,
):
    """Alias for 'revision --autogenerate'"""

    def op(connection, c):
        c.attributes["connection"] = connection
        command.revision(
            c,
            message,
            autogenerate=True,
            sql=sql,
            head=head,
            splice=splice,
            branch_label=branch_label,
            version_path=version_path,
            rev_id=rev_id,
        )

    async def main():
        bot = Bot(config)
        directory = os.path.join("yui", "migrations")
        c = Config(os.path.join(directory, "alembic.ini"))
        c.set_main_option("script_location", directory)
        c.set_main_option("sqlalchemy.url", bot.config.DATABASE_URL)
        c.attributes["Base"] = bot.orm_base
        async with bot.database_engine.begin() as conn:
            await conn.run_sync(op, c)

    asyncio.run(main())


@yui.command()
@click.argument("revision", default="current")
@load_config
def edit(config, revision: str):
    """Edit current revision."""

    def op(connection, c):
        c.attributes["connection"] = connection
        command.edit(c, revision)

    async def main():
        bot = Bot(config)
        directory = os.path.join("yui", "migrations")
        c = Config(os.path.join(directory, "alembic.ini"))
        c.set_main_option("script_location", directory)
        c.set_main_option("sqlalchemy.url", bot.config.DATABASE_URL)
        c.attributes["Base"] = bot.orm_base
        async with bot.database_engine.begin() as conn:
            await conn.run_sync(op, c)

    asyncio.run(main())


@yui.command()
@click.option("--rev-id")
@click.option("--branch-label")
@click.option("--message", "-m")
@click.argument("revisions", nargs=-1)
@load_config
def merge(
    config,
    revisions: str,
    message: str | None,
    branch_label=str | None,
    rev_id=str | None,
):
    """Merge two revisions together.  Creates a new migration file."""

    def op(connection, c):
        c.attributes["connection"] = connection
        command.merge(
            c,
            revisions,
            message=message,
            branch_label=branch_label,
            rev_id=rev_id,
        )

    async def main():
        bot = Bot(config)
        directory = os.path.join("yui", "migrations")
        c = Config(os.path.join(directory, "alembic.ini"))
        c.set_main_option("script_location", directory)
        c.set_main_option("sqlalchemy.url", bot.config.DATABASE_URL)
        c.attributes["Base"] = bot.orm_base
        async with bot.database_engine.begin() as conn:
            await conn.run_sync(op, c)

    asyncio.run(main())


@yui.command()
@click.option("--tag")
@click.option("--sql", is_flag=True, default=False)
@click.argument("revision", default="head")
@load_config
def upgrade(config, revision: str, sql: bool, tag: str | None):
    """Upgrade to a later version."""

    def op(connection, c):
        c.attributes["connection"] = connection
        command.upgrade(c, revision, sql=sql, tag=tag)

    async def main():
        bot = Bot(config)
        directory = os.path.join("yui", "migrations")
        c = Config(os.path.join(directory, "alembic.ini"))
        c.set_main_option("script_location", directory)
        c.set_main_option("sqlalchemy.url", bot.config.DATABASE_URL)
        c.attributes["Base"] = bot.orm_base
        async with bot.database_engine.begin() as conn:
            await conn.run_sync(op, c)

    asyncio.run(main())


@yui.command()
@click.option("--tag")
@click.option("--sql", is_flag=True, default=False)
@click.argument("revision", default="-1")
@load_config
def downgrade(config, revision: str, sql: bool, tag: str):
    """Revert to a previous version."""

    def op(connection, c):
        c.attributes["connection"] = connection
        command.downgrade(c, revision, sql=sql, tag=tag)

    async def main():
        bot = Bot(config)
        directory = os.path.join("yui", "migrations")
        c = Config(os.path.join(directory, "alembic.ini"))
        c.set_main_option("script_location", directory)
        c.set_main_option("sqlalchemy.url", bot.config.DATABASE_URL)
        c.attributes["Base"] = bot.orm_base
        async with bot.database_engine.begin() as conn:
            await conn.run_sync(op, c)

    asyncio.run(main())


@yui.command()
@click.argument("revision", default="head")
@load_config
def show(config, revision: str):
    """Show the revision denoted by the given symbol."""

    def op(connection, c):
        c.attributes["connection"] = connection
        command.show(c, revision)

    async def main():
        bot = Bot(config)
        directory = os.path.join("yui", "migrations")
        c = Config(os.path.join(directory, "alembic.ini"))
        c.set_main_option("script_location", directory)
        c.set_main_option("sqlalchemy.url", bot.config.DATABASE_URL)
        c.attributes["Base"] = bot.orm_base
        async with bot.database_engine.begin() as conn:
            await conn.run_sync(op, c)

    asyncio.run(main())


@yui.command()
@click.option("--verbose", "-v", is_flag=True, default=False)
@click.option("--rev-range", "-r")
@load_config
def history(config, verbose: bool, rev_range: str | None):
    """List changeset scripts in chronological order."""

    def op(connection, c):
        c.attributes["connection"] = connection
        command.history(c, rev_range, verbose=verbose)

    async def main():
        bot = Bot(config)
        directory = os.path.join("yui", "migrations")
        c = Config(os.path.join(directory, "alembic.ini"))
        c.set_main_option("script_location", directory)
        c.set_main_option("sqlalchemy.url", bot.config.DATABASE_URL)
        c.attributes["Base"] = bot.orm_base
        async with bot.database_engine.begin() as conn:
            await conn.run_sync(op, c)

    asyncio.run(main())


@yui.command()
@click.option("--resolve-dependencies", is_flag=True, default=False)
@click.option("--verbose", "-v", is_flag=True, default=False)
@load_config
def heads(config, verbose: bool, resolve_dependencies: bool):
    """Show current available heads in the script directory."""

    def op(connection, c):
        c.attributes["connection"] = connection
        command.heads(
            c, verbose=verbose, resolve_dependencies=resolve_dependencies
        )

    async def main():
        bot = Bot(config)
        directory = os.path.join("yui", "migrations")
        c = Config(os.path.join(directory, "alembic.ini"))
        c.set_main_option("script_location", directory)
        c.set_main_option("sqlalchemy.url", bot.config.DATABASE_URL)
        c.attributes["Base"] = bot.orm_base
        async with bot.database_engine.begin() as conn:
            await conn.run_sync(op, c)

    asyncio.run(main())


@yui.command()
@click.option("--verbose", "-v", is_flag=True, default=False)
@load_config
def branches(config, verbose: bool):
    """Show current branch points."""

    def op(connection, c):
        c.attributes["connection"] = connection
        command.branches(c, verbose=verbose)

    async def main():
        bot = Bot(config)
        directory = os.path.join("yui", "migrations")
        c = Config(os.path.join(directory, "alembic.ini"))
        c.set_main_option("script_location", directory)
        c.set_main_option("sqlalchemy.url", bot.config.DATABASE_URL)
        c.attributes["Base"] = bot.orm_base
        async with bot.database_engine.begin() as conn:
            await conn.run_sync(op, c)

    asyncio.run(main())


@yui.command()
@click.option("--verbose", "-v", is_flag=True, default=False)
@load_config
def current(config, verbose: bool):
    """Display the current revision for each database."""

    def op(connection, c):
        c.attributes["connection"] = connection
        command.current(c, verbose=verbose)

    async def main():
        bot = Bot(config)
        directory = os.path.join("yui", "migrations")
        c = Config(os.path.join(directory, "alembic.ini"))
        c.set_main_option("script_location", directory)
        c.set_main_option("sqlalchemy.url", bot.config.DATABASE_URL)
        c.attributes["Base"] = bot.orm_base
        async with bot.database_engine.begin() as conn:
            await conn.run_sync(op, c)

    asyncio.run(main())


@yui.command()
@click.option("--tag")
@click.option("--sql", is_flag=True, default=False)
@click.argument("revision", default="head")
@load_config
def stamp(config, revision: str, sql: bool, tag: str | None):
    """'stamp' the revision table with the given revision; don't run any
    migrations."""

    def op(connection, c):
        c.attributes["connection"] = connection
        command.stamp(c, revision, sql=sql, tag=tag)

    async def main():
        bot = Bot(config)
        directory = os.path.join("yui", "migrations")
        c = Config(os.path.join(directory, "alembic.ini"))
        c.set_main_option("script_location", directory)
        c.set_main_option("sqlalchemy.url", bot.config.DATABASE_URL)
        c.attributes["Base"] = bot.orm_base
        async with bot.database_engine.begin() as conn:
            await conn.run_sync(op, c)

    asyncio.run(main())


main = yui


if __name__ == "__main__":
    yui()
