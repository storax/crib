"""
Module that contains the command line app.
"""
import json
import logging
import pprint

import click
import click_log

from crib import browser
from crib.config import YamlLoader
from crib.scraper import app

logger = logging.getLogger("crib")
click_log.basic_config(logger)


@click.group()
@click_log.simple_verbosity_option(logger)
@click.option("-c", "--config", type=click.File(), help="Yaml config file")
@click.pass_context
def main(ctx, config):
    config = YamlLoader().load(config) if config else {}
    ctx.obj = {"CONFIG": config}


@main.group()
@click.pass_obj
def scrape(obj):
    scrapp = app.Scrapp(obj["CONFIG"])
    obj["SCRAPP"] = scrapp


@scrape.command()
@click.pass_obj
def list_scrapers(obj):
    scrapp = obj["SCRAPP"]
    for scraper in scrapp.scraper_plugins:
        click.echo(scraper)


@scrape.command()
@click.pass_obj
def scrapers(obj):
    scrapp = obj["SCRAPP"]
    for scraper in scrapp.scrapers:
        click.echo(scraper)


@scrape.command()
@click.pass_obj
def run(obj):
    scrapp = obj["SCRAPP"]
    scrapp.scrape()


@main.command()
@click.option("-q", "--query", help="Query as json string.")
@click.pass_obj
def browse(obj, query):
    if query:
        query = json.loads(query)
    brws = browser.Browser(obj["CONFIG"])
    for prop in brws.find(query):
        click.echo(pprint.pformat(prop))
