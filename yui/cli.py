from typing import Final

import anyio
import asyncclick as click
from alembic import command
from alembic.config import Config

from .bot import Bot
from .config import ConfigurationError
from .config import load

ALEMBIC_BASE_DIR: Final = anyio.Path("yui", "migrations")


def error(message: str):
    """Echo and die with error message"""

    click.echo("Error: " + message, err=True)
    raise SystemExit(1)


config_option = click.option(
    "--config",
    "-c",
    "config_path",
    type=click.Path(exists=True, path_type=anyio.Path),
    envvar="YUI_CONFIG_FILE_PATH",
)


async def run_alembic_op(config, op):
    async with Bot(config) as bot:
        c = Config(ALEMBIC_BASE_DIR / "alembic.ini")
        c.set_main_option("script_location", str(ALEMBIC_BASE_DIR))
        c.set_main_option("sqlalchemy.url", bot.config.DATABASE_URL)
        c.attributes["Base"] = bot.orm_base
        async with bot.database_engine.begin() as conn:
            await conn.run_sync(op, c)


@click.group()
def yui():
    """YUI, Slack Bot for item4.slack.com"""


@yui.command()
@config_option
async def run(*, config_path: anyio.Path):
    """Run YUI."""

    config = await load(config_path)
    try:
        while True:
            async with Bot(config) as bot:
                await bot.run()
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
@config_option
async def revision(
    *,
    config_path: anyio.Path,
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

    config = await load(config_path)

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

    await run_alembic_op(config, op)


@yui.command()
@click.option("--message", "-m")
@click.option("--sql", is_flag=True, default=False)
@click.option("--head", default="head")
@click.option("--splice", is_flag=True, default=False)
@click.option("--branch-label")
@click.option("--version-path")
@click.option("--rev-id")
@config_option
async def migrate(
    *,
    config_path: anyio.Path,
    message: str | None,
    sql: bool,
    head: str,
    splice: bool,
    branch_label: str | None,
    version_path: str | None,
    rev_id: str | None,
):
    """Alias for 'revision --autogenerate'"""

    config = await load(config_path)

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

    await run_alembic_op(config, op)


@yui.command()
@click.argument("revision", default="current")
@config_option
async def edit(*, config_path: anyio.Path, revision: str):
    """Edit current revision."""

    config = await load(config_path)

    def op(connection, c):
        c.attributes["connection"] = connection
        command.edit(c, revision)

    await run_alembic_op(config, op)


@yui.command()
@click.option("--rev-id")
@click.option("--branch-label")
@click.option("--message", "-m")
@click.argument("revisions", nargs=-1)
@config_option
async def merge(
    *,
    config_path: anyio.Path,
    revisions: str,
    message: str | None,
    branch_label: str | None,
    rev_id: str | None,
):
    """Merge two revisions together.  Creates a new migration file."""

    config = await load(config_path)

    def op(connection, c):
        c.attributes["connection"] = connection
        command.merge(
            c,
            revisions,
            message=message,
            branch_label=branch_label,
            rev_id=rev_id,
        )

    await run_alembic_op(config, op)


@yui.command()
@click.option("--tag")
@click.option("--sql", is_flag=True, default=False)
@click.argument("revision", default="head")
@config_option
async def upgrade(
    *,
    config_path: anyio.Path,
    revision: str,
    sql: bool,
    tag: str | None,
):
    """Upgrade to a later version."""

    config = await load(config_path)

    def op(connection, c):
        c.attributes["connection"] = connection
        command.upgrade(c, revision, sql=sql, tag=tag)

    await run_alembic_op(config, op)


@yui.command()
@click.option("--tag")
@click.option("--sql", is_flag=True, default=False)
@click.argument("revision", default="-1")
@config_option
async def downgrade(
    *,
    config_path: anyio.Path,
    revision: str,
    sql: bool,
    tag: str,
):
    """Revert to a previous version."""

    config = await load(config_path)

    def op(connection, c):
        c.attributes["connection"] = connection
        command.downgrade(c, revision, sql=sql, tag=tag)

    await run_alembic_op(config, op)


@yui.command()
@click.argument("revision", default="head")
@config_option
async def show(*, config_path: anyio.Path, revision: str):
    """Show the revision denoted by the given symbol."""

    config = await load(config_path)

    def op(connection, c):
        c.attributes["connection"] = connection
        command.show(c, revision)

    await run_alembic_op(config, op)


@yui.command()
@click.option("--verbose", "-v", is_flag=True, default=False)
@click.option("--rev-range", "-r")
@config_option
async def history(
    *,
    config_path: anyio.Path,
    verbose: bool,
    rev_range: str | None,
):
    """List changeset scripts in chronological order."""

    config = await load(config_path)

    def op(connection, c):
        c.attributes["connection"] = connection
        command.history(c, rev_range, verbose=verbose)

    await run_alembic_op(config, op)


@yui.command()
@click.option("--resolve-dependencies", is_flag=True, default=False)
@click.option("--verbose", "-v", is_flag=True, default=False)
@config_option
async def heads(
    *,
    config_path: anyio.Path,
    verbose: bool,
    resolve_dependencies: bool,
):
    """Show current available heads in the script directory."""

    config = await load(config_path)

    def op(connection, c):
        c.attributes["connection"] = connection
        command.heads(
            c,
            verbose=verbose,
            resolve_dependencies=resolve_dependencies,
        )

    await run_alembic_op(config, op)


@yui.command()
@click.option("--verbose", "-v", is_flag=True, default=False)
@config_option
async def branches(*, config_path: anyio.Path, verbose: bool):
    """Show current branch points."""

    config = await load(config_path)

    def op(connection, c):
        c.attributes["connection"] = connection
        command.branches(c, verbose=verbose)

    await run_alembic_op(config, op)


@yui.command()
@click.option("--verbose", "-v", is_flag=True, default=False)
@config_option
async def current(*, config_path: anyio.Path, verbose: bool):
    """Display the current revision for each database."""

    config = await load(config_path)

    def op(connection, c):
        c.attributes["connection"] = connection
        command.current(c, verbose=verbose)

    await run_alembic_op(config, op)


@yui.command()
@click.option("--tag")
@click.option("--sql", is_flag=True, default=False)
@click.argument("revision", default="head")
@config_option
async def stamp(
    *,
    config_path: anyio.Path,
    revision: str,
    sql: bool,
    tag: str | None,
):
    """'stamp' the revision table with the given revision; don't run any
    migrations."""

    config = await load(config_path)

    def op(connection, c):
        c.attributes["connection"] = connection
        command.stamp(c, revision, sql=sql, tag=tag)

    await run_alembic_op(config, op)


main = yui


if __name__ == "__main__":
    yui()
