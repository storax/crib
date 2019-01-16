"""
The CLI interface for crib.
"""
import code
import logging
import os
import sys
import types
from typing import IO, Any, Dict, List

import click
import click_log  # type: ignore
from flask import current_app  # type: ignore
from flask.cli import FlaskGroup, ScriptInfo  # type: ignore
from scrapy.cmdline import execute  # type: ignore

from crib import app, exceptions
from crib.server import auth, create_app

_log = logging.getLogger("crib")
click_log.basic_config(_log)


class Context:
    config: Dict[str, Any]
    script_info: ScriptInfo


@click.group()
@click_log.simple_verbosity_option(_log)
@click.option("-c", "--config", type=click.File(), help="Yaml config file")
@click.pass_context
def main(ctx: click.Context, config: IO[str]) -> None:
    """Find the best properties with crib!"""
    try:
        cfg = app.load_config(config)
    except exceptions.ConfigError as err:
        raise click.UsageError(str(err))

    ctx.obj = Context()
    ctx.obj.config = cfg


@main.command(context_settings=dict(ignore_unknown_options=True), add_help_option=False)
@click.argument("scrapy_args", nargs=-1, type=click.UNPROCESSED)
@click.pass_obj
def scrape(obj: Context, scrapy_args: List[str]) -> None:
    """Scrape property websites and store them in a repository.

    Forwards all arguments to scrapy.
    """
    argv = ["scrapy"]
    argv.extend(scrapy_args)
    settings_module = types.ModuleType("_crib_scrapy_settings_")
    cfg = obj.config.copy()
    scrape_cfg = cfg.pop("scrape", {})
    settings_module.__dict__.update(scrape_cfg)
    settings_module.CRIB = cfg  # type: ignore
    sys.modules[settings_module.__name__] = settings_module
    os.environ["SCRAPY_SETTINGS_MODULE"] = settings_module.__name__

    execute(argv)


@main.command()
@click.pass_obj
def browse(obj: Context) -> None:
    """Browse properties"""
    from pprint import pprint as pp  # noqa: F401

    repo = app.get_property_repository(obj.config)
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
    cfg = ctx.find_object(Context).config
    return create_app(cfg)


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
    cfg = ctx.find_object(Context).config
    current_app.prop_repo = app.get_property_repository(cfg)
    current_app.user_repo = app.get_user_repository(cfg)
    current_app.directions_service = app.get_direction_service(cfg)
    current_app.run()


@server.command()
@click.argument("username")
@click.password_option("--password")
@click.pass_context
def add_user(ctx: click.Context, username: str, password: str) -> None:
    cfg = ctx.find_object(Context).config
    current_app.user_repo = app.get_user_repository(cfg)
    try:
        auth.register(username, password)
    except exceptions.DuplicateUser:
        raise click.UsageError(f"User {username} already exists")
    else:
        click.echo(f"User {username} created")
