"""
The CLI interface for crib.
"""
import asyncio
import code
import logging

import click
import click_log  # type: ignore
from quart.cli import QuartGroup, ScriptInfo  # type: ignore

from crib import app, exceptions, injection
from crib.config import LoadedConfiguration
from crib.server import create_app

_log = logging.getLogger("crib")
click_log.basic_config(_log)


@click.group()
@click_log.simple_verbosity_option(_log)
@click.option(
    "-c",
    "--config",
    type=click.Path(exists=True, dir_okay=False),
    help="Yaml config file",
)
@click.pass_context
def main(ctx: click.Context, config: str) -> None:
    """Find the best properties with crib!"""

    config_file_provider = injection.ObjectProvider(config)

    class Container(app.AppContainer):
        config_file = config_file_provider
        config = injection.SingletonProvider(LoadedConfiguration)

    ctx.obj = Container()


@main.group()
@click.pass_obj
def scrape(obj):
    """Scrape properties."""
    pass


@scrape.command()
@click.argument("spider")
@click.option("--loglevel", default="DEBUG", help="The loglevel for scrapy.")
@click.pass_obj
def crawl(obj, spider: str, loglevel: str) -> None:
    """Scrape with the given spider.
    """
    obj.scrape.crawl(spider, loglevel)


@scrape.command(name="list")
@click.pass_obj
def list_scapers(obj) -> None:
    """List all spiders.
    """
    for spider in obj.scrape.list_spiders():
        click.echo(spider)


@main.command()
@click.pass_obj
def browse(obj) -> None:
    """Browse properties"""
    from pprint import pprint as pp  # noqa: F401

    repo = obj.property_repository
    _console = code.InteractiveConsole(locals())
    try:
        import rlcompleter  # noqa: F401
        import readline
    except ImportError:
        pass
    else:
        readline.parse_and_bind("tab: complete")
    _console.interact(banner="You can access the repository via the 'repo' variable.")


@main.command()
@click.option("--max-duration", type=int)
@click.option("--hullbuffer", type=float)
@click.option("--alpha", type=int)
@click.pass_obj
def get_area(obj, max_duration, hullbuffer, alpha) -> None:
    """Cluster directions."""
    click.echo(
        obj.directions_service.get_area(
            max_duration=max_duration, hullbuffer=hullbuffer, alpha=alpha
        )
    )


@main.command()
@click.option("--banned", is_flag=True, help="Delete banned properties.")
@click.option("--favorite", is_flag=True, help="Delete favorite properties.")
@click.pass_obj
def clear_properties(obj, banned, favorite) -> None:
    """Delete all properties."""
    obj.property_service.clear_properties(banned, favorite)


def create_app_wrapper(*args, **kwargs):
    ctx = click.get_current_context().find_root()
    container = ctx.obj
    return create_app(container)


@main.group(
    cls=QuartGroup,
    create_app=create_app_wrapper,
    context_settings={"obj": ScriptInfo(create_app=create_app_wrapper)},
)
def server():
    """Run the crib server."""
    pass


@server.command()
@click.pass_context
def run(ctx):
    app = ctx.ensure_object(ScriptInfo).load_app()
    app.run(debug=True)


@server.command()
@click.argument("username")
@click.password_option("--password")
@click.pass_context
def add_user(ctx: click.Context, username: str, password: str) -> None:
    container = ctx.obj
    try:
        container.auth_service.register(username, password)
    except exceptions.DuplicateUser:
        raise click.UsageError(f"User {username} already exists")
    except ValueError as err:
        raise click.UsageError(str(err))
    else:
        click.echo(f"User {username} created")


@server.command()
@click.argument("mode", type=click.Choice(["transit"]))
@click.pass_context
def fetch_to_work(ctx: click.Context, mode) -> None:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(ctx.obj.directions_service.fetch_map_to_work(mode))
