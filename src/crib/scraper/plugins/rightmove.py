"""
Rightmove.co.uk scraper plugin
"""
import crib
from crib.scraper import scraper


class Rightmove(scraper.Scraper):
    @classmethod
    def config_schema(cls):
        return {"foo": {"type": "integer", "required": True}}


@crib.hookimpl
def crib_add_scrapers():
    return [Rightmove]
