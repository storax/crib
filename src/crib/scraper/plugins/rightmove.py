"""
Rightmove.co.uk scraper plugin
"""
import json
import re
import logging

import mechanicalsoup
import requests

import crib
from crib.scraper import scraper

_log = logging.getLogger(__name__)


class Rightmove(scraper.Scraper):
    _result_model_pattern = re.compile("window.jsonModel = ")

    @classmethod
    def config_schema(cls):
        return {
            "searches": {"type": "list", "schema": {"type": "string"}, "required": True}
        }

    def scrape(self):
        browser = mechanicalsoup.Browser()
        for search in self.config["searches"]:
            result_page = browser.get(search)
            result_page.raise_for_status()
            script = result_page.soup.find(
                "script", text=self._result_model_pattern
            ).text
            jsmodel = re.sub(self._result_model_pattern, "", script)
            model = json.loads(jsmodel)
            _log.info(f"{self.name()}: found {model['resultCount']} properties")

            for p in model["properties"]:
                yield p


@crib.hookimpl
def crib_add_scrapers():
    return [Rightmove]
