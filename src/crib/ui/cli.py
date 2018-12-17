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
from scrapy.cmdline import execute  # type: ignore

from crib import app, exceptions

_log = logging.getLogger("crib")
click_log.basic_config(_log)


class Context:
    config: Dict[str, Any]


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
    from pprint import pprint as pp

    repo = app.get_repository(obj.config)
    props = repo._props
    _console = code.InteractiveConsole(locals())
    try:
        import rlcompleter
        import readline
    except ImportError:
        pass
    else:
        readline.parse_and_bind("tab: complete")
    _console.interact(banner="You can access the repository via the 'repo' variable.")
