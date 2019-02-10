"""
The CLI interface for crib.
"""
import code
import logging
import os
import sys
import types
from typing import IO, List

import click
import click_log  # type: ignore
from flask import current_app  # type: ignore
from flask.cli import FlaskGroup, ScriptInfo  # type: ignore
from scrapy.cmdline import execute  # type: ignore

from crib import app, exceptions, injection
from crib.server import auth, create_app, directions

_log = logging.getLogger("crib")
click_log.basic_config(_log)


@click.group()
@click_log.simple_verbosity_option(_log)
@click.option("-c", "--config", type=click.File(), help="Yaml config file")
@click.pass_context
def main(ctx: click.Context, config: IO[str]) -> None:
    """Find the best properties with crib!"""

    class Container(app.App):
        config_file = injection.ObjectProvider(config)

    ctx.obj = Container()


@main.command(context_settings=dict(ignore_unknown_options=True), add_help_option=False)
@click.argument("scrapy_args", nargs=-1, type=click.UNPROCESSED)
@click.pass_obj
def scrape(obj, scrapy_args: List[str]) -> None:
    """Scrape property websites and store them in a repository.

    Forwards all arguments to scrapy.
    """
    argv = ["scrapy"]
    argv.extend(scrapy_args)
    settings_module = types.ModuleType("_crib_scrapy_settings_")
    scrape_cfg = obj.config["scrape"]
    settings_module.__dict__.update(scrape_cfg)
    settings_module.CONTAINER = obj  # type: ignore
    sys.modules[settings_module.__name__] = settings_module
    os.environ["SCRAPY_SETTINGS_MODULE"] = settings_module.__name__

    execute(argv)


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


def create_app_wrapper(*args, **kwargs):
    ctx = click.get_current_context()
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
    try:
        auth.register(username, password)
    except exceptions.DuplicateUser:
        raise click.UsageError(f"User {username} already exists")
    else:
        click.echo(f"User {username} created")


@server.command()
@click.argument("mode", type=click.Choice(["transit"]))
@click.pass_context
def fetch_to_work(ctx: click.Context, mode) -> None:
    directions.fetch_map_to_work(mode)
