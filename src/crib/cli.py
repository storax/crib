"""
Module that contains the command line app.
"""
import logging

import click
import click_log

from crib.scraper import app

logger = logging.getLogger("crib")
click_log.basic_config(logger)


@click.group()
@click_log.simple_verbosity_option(logger)
@click.pass_context
def main(ctx):
    ctx.obj = {}
    ctx.obj["CONFIG"] = {"scrapers": [{"name": "Rightmove"}]}


@main.group()
@click.pass_obj
def scrape(obj):
    pass


@scrape.command()
@click.pass_obj
def list_scrapers(obj):
    config = obj["CONFIG"]
    scrapp = app.Scrapp(config)
    for scraper in scrapp.scraper_plugins:
        click.echo(scraper)


@scrape.command()
@click.pass_obj
def scrapers(obj):
    config = obj["CONFIG"]
    scrapp = app.Scrapp(config)
    for scraper in scrapp.scrapers:
        click.echo(scraper)
