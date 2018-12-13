"""
Rightmove.co.uk scraper plugin
"""
import datetime
import json
import logging
import re
import urllib

import mechanicalsoup
import requests

import crib
from crib.domain.property import Property
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
            model = self._load_page(browser, search)
            _log.info(f"{self.name()}: found {model['resultCount']} properties")

            pages = self._get_pages(model)
            pages[0]["properties"] = model["properties"]

            for page in pages:
                if page["properties"] is None:
                    url = self._next_page(search, page)
                    model = self._load_page(browser, url)
                    page["properties"] = model["properties"]
                yield from (self._to_prop(p) for p in page["properties"])

    @staticmethod
    def _to_prop(data):
        keys = (
            "bedrooms",
            "displayAddress",
            "featuredProperty",
            "feesApply",
            "feesApplyText",
            "firstVisibleDate",
            "id",
            "location",
            "price",
            "propertyImages",
            "propertySubType",
            "propertyTypeFullDescription",
            "propertyUrl",
            "students",
            "summary",
            "transactionType",
        )
        dtc = lambda x: datetime.datetime.strptime(x, "%Y-%m-%dT%H:%M:%S%z")

        def imgc(images):
            images = images["images"]
            return [
                {"order": img["order"], "url": img["mediaServerHost"] + img["url"]}
                for img in images
            ]

        identity = lambda x: x

        conversions = {
            "firstVisibleDate": dtc,
            "id": lambda x: f"RM-{x}",
            "propertyImages": imgc,
            "price": lambda x: {
                k: x[k] for k in ("amount", "currencyCode", "frequency")
            },
            "propertyUrl": lambda x: "https://rightmove.co.uk" + x,
            "feesApplyText": lambda x: x or "",
        }

        d = {k: conversions.get(k, identity)(data[k]) for k in keys}

        return Property(d)

    @staticmethod
    def _get_pages(model):
        pagination = model["pagination"]
        return [
            {
                "index": option["value"],
                "page": option["description"],
                "properties": None,
            }
            for option in pagination["options"]
        ]

    def _load_page(self, browser, url):
        _log.info(f"{self.name()}: searching {url}")
        result_page = browser.get(url)
        result_page.raise_for_status()
        script = result_page.soup.find("script", text=self._result_model_pattern).text
        jsmodel = re.sub(self._result_model_pattern, "", script)
        return json.loads(jsmodel)

    def _next_page(self, url, page):
        qr = urllib.parse.urlparse(url)
        qs = urllib.parse.parse_qs(qr.query)
        qs["index"] = page["index"]
        query = urllib.parse.urlencode(qs, doseq=True)
        parsed = list(qr)
        parsed[4] = query
        return urllib.parse.urlunparse(parsed)


@crib.hookimpl
def crib_add_scrapers():
    return [Rightmove]
