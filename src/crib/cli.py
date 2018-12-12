"""
Module that contains the command line app.
"""
import logging

import click
import click_log

from crib.config import YamlLoader
from crib.scraper import app

logger = logging.getLogger("crib")
click_log.basic_config(logger)


@click.group()
@click_log.simple_verbosity_option(logger)
@click.pass_context
def main(ctx):
    ctx.obj = {}


@main.group()
@click.option("-c", "--config", type=click.File(), help="Yaml config file")
@click.pass_obj
def scrape(obj, config=None):
    config = YamlLoader().load(config) if config else {}
    scrapp = app.Scrapp(config)
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
