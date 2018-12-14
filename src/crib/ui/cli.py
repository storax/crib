"""
The CLI interface for crib.
"""
import itertools
import json
import logging
import pprint
from typing import IO, Any, Dict, Union

import click
import click_log  # type: ignore

from crib import config as _cfg
from crib import exceptions, plugins
from crib.app import browser, scraper

_log = logging.getLogger("crib")
click_log.basic_config(_log)


class Context:
    config: Dict[str, Any]
    scrapp: scraper.Scrapp


@click.group()
@click_log.simple_verbosity_option(_log)
@click.option("-c", "--config", type=click.File(), help="Yaml config file")
@click.pass_context
def main(ctx: click.Context, config: IO[str]) -> None:
    """Find the best properties with crib!"""
    loaders = [l for loaders in plugins.hook.crib_add_config_loaders() for l in loaders]
    try:
        cfg = _cfg.load(loaders, config)
    except exceptions.ConfigError as err:
        raise click.UsageError(str(err))

    ctx.obj = Context()
    ctx.obj.config = cfg


@main.group()
@click.pass_obj
def scrape(obj: Context) -> None:
    """Scrape property websites and store them in a repository."""
    scrapp = scraper.Scrapp(obj.config)
    obj.scrapp = scrapp


@scrape.command()
@click.pass_obj
def list_scrapers(obj: Context) -> None:
    """List all available scraper plugins."""
    scrapp = obj.scrapp
    for name, scraper in scrapp.scraper_plugins.items():
        doc = scraper.__doc__
        msg = f"{name}:"
        if doc:
            lines = doc.split("\n")
            msg += " " + lines[0]
            msg += "\n".join(lines[1:])
        click.echo(msg)


@scrape.command()
@click.pass_obj
def run(obj: Context) -> None:
    """Scrape properties."""
    scrapp = obj.scrapp
    scrapp.scrape()


@main.command()
@click.option("-q", "--query", help="Query as json string.")
@click.pass_obj
def browse(obj: Context, query: str) -> None:
    """Browse properties."""
    if query:
        query_params = json.loads(query)
    brws = browser.Browser(obj.config)
    for prop in brws.find(query_params):
        click.echo(pprint.pformat(prop))
