"""
The CLI interface for crib.
"""
import code
import logging
from typing import IO

import click
import click_log  # type: ignore
from flask import current_app  # type: ignore
from flask.cli import FlaskGroup, ScriptInfo  # type: ignore

from crib import app, exceptions, injection
from crib.config import LoadedConfiguration
from crib.server import create_app

_log = logging.getLogger("crib")
click_log.basic_config(_log)


@click.group()
@click_log.simple_verbosity_option(_log)
@click.option("-c", "--config", type=click.File(), help="Yaml config file")
@click.pass_context
def main(ctx: click.Context, config: IO[str]) -> None:
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


@scrape.command()
@click.pass_obj
def list(obj) -> None:
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
@click.pass_obj
def clear_properties(obj) -> None:
    """Delete all properties."""
    repo = obj.property_repository
    repo.delete_all()


def create_app_wrapper(*args, **kwargs):
    ctx = click.get_current_context().find_root()
    container = ctx.obj
    return create_app(container)


@main.group(
    cls=FlaskGroup,
    create_app=create_app_wrapper,
    context_settings={"obj": ScriptInfo(create_app=create_app_wrapper)},
)
def server():
    """Run the crib server."""


@server.command()
@click.pass_context
def run(ctx):
    current_app.run()


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
    ctx.obj.directions_service.fetch_map_to_work(mode)
