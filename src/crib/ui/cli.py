"""
The CLI interface for crib.
"""
import itertools
import json
import logging
import pprint

import click
import click_log

from crib import config as _cfg
from crib import exceptions, plugins
from crib.app import browser, scraper

_log = logging.getLogger("crib")
click_log.basic_config(_log)


@click.group()
@click_log.simple_verbosity_option(_log)
@click.option("-c", "--config", type=click.File(), help="Yaml config file")
@click.pass_context
def main(ctx, config):
    """Find the best properties with crib!"""
    loaders = [
        Loader()
        for loaders in plugins.hook.crib_add_config_loaders()
        for Loader in loaders
    ]
    try:
        config = _cfg.load(loaders, config)
    except exceptions.ConfigError as err:
        raise click.UsageError(str(err))

    ctx.obj = {"CONFIG": config or {}}


@main.group()
@click.pass_obj
def scrape(obj):
    """Scrape property websites and store them in a repository."""
    scrapp = scraper.Scrapp(obj["CONFIG"])
    obj["SCRAPP"] = scrapp


@scrape.command()
@click.pass_obj
def list_scrapers(obj):
    """List all available scraper plugins."""
    scrapp = obj["SCRAPP"]
    for scraper in scrapp.scraper_plugins:
        click.echo(scraper)


@scrape.command()
@click.pass_obj
def run(obj):
    """Scrape properties."""
    scrapp = obj["SCRAPP"]
    scrapp.scrape()


@main.command()
@click.option("-q", "--query", help="Query as json string.")
@click.pass_obj
def browse(obj, query):
    """Browse properties."""
    if query:
        query = json.loads(query)
    brws = browser.Browser(obj["CONFIG"])
    for prop in brws.find(query):
        click.echo(pprint.pformat(prop))
