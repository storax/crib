"""
Rightmove.co.uk scraper plugin
"""
import datetime
import json
import logging
import re
from typing import Any, Dict, Iterable, List, NamedTuple, Type, TypeVar, Union
from urllib import parse

import mechanicalsoup  # type: ignore
import requests

import crib
from crib.domain.property import Property
from crib.scraper import scraper

_log = logging.getLogger(__name__)


class Rightmove(scraper.Scraper):
    """Scrape properties from rightmove.co.uk

    Configuration::

      searches:
        - https://rightmove.co.uk/property-to-rent/find.html?...
    """

    _result_model_pattern = re.compile("window.jsonModel = ")

    @classmethod
    def config_schema(cls) -> Dict[str, Any]:
        return {
            "searches": {"type": "list", "schema": {"type": "string"}, "required": True}
        }

    def scrape(self) -> Iterable[Property]:
        browser = mechanicalsoup.Browser()
        for search in self.config["searches"]:
            model = self._load_page(browser, search)
            _log.info(f"{self.name()}: found {model['resultCount']} properties")

            pages = self._get_pages(model)
            pages[0].properties.extend(model["properties"])

            for i, page in enumerate(pages):
                if i == 0:
                    url = self._next_page(search, page)
                    model = self._load_page(browser, url)
                    page.properties.extend(model["properties"])
                properties = page.properties
                yield from (to_prop(p) for p in properties)

    @staticmethod
    def _get_pages(model: Dict) -> List[Page]:
        pagination = model["pagination"]
        options = pagination["options"]
        return [Page(option["value"], option["description"], []) for option in options]

    def _load_page(self, browser: mechanicalsoup.Browser, url: str) -> Dict[str, Any]:
        _log.info(f"{self.name()}: searching {url}")
        result_page = browser.get(url)
        result_page.raise_for_status()
        script = result_page.soup.find("script", text=self._result_model_pattern).text
        jsmodel = re.sub(self._result_model_pattern, "", script)
        return json.loads(jsmodel)

    def _next_page(self, url: str, page: Page) -> str:
        qr = parse.urlparse(url)
        qs = parse.parse_qs(qr.query)
        qs["index"] = [page.pageindex]
        query = parse.urlencode(qs, doseq=True)
        parsed = list(qr)
        parsed[4] = query
        return parse.urlunparse(parsed)


def to_prop(data: Dict) -> Property:
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

    def imgc(images: Dict) -> List[Dict[str, str]]:
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
        "price": lambda x: {k: x[k] for k in ("amount", "currencyCode", "frequency")},
        "propertyUrl": lambda x: "https://rightmove.co.uk" + x,
        "feesApplyText": lambda x: x or "",
    }

    d = {k: conversions.get(k, identity)(data[k]) for k in keys}

    return Property(d)


class Page(NamedTuple):
    pageindex: str
    description: Dict
    properties: List[Dict]


SC = TypeVar("SC", bound=scraper.Scraper)
TSC = Type[SC]


@crib.hookimpl
def crib_add_scrapers() -> Iterable[TSC]:
    return [Rightmove]
