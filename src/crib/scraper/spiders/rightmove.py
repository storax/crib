import datetime
import functools
import json
from typing import Any, Dict, Iterable, List, Union
from urllib import parse as urlparse

import scrapy  # type: ignore
from scrapy.http.response import Response  # type: ignore
from w3lib.html import remove_tags  # type: ignore

from crib.domain.property import Property
from crib.scraper import base
from crib.scraper.items import PropertyItem

PR = Iterable[Union[Dict, scrapy.Request]]


class RightmoveSpider(base.WithRepo, scrapy.Spider):
    name: str = "rightmove"

    def start_requests(self) -> Iterable[scrapy.Request]:
        urls = self.settings.getlist("RIGHTMOVE_SEARCHES") or []
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response: Response) -> PR:
        model = _load_model(response)
        for page in _get_pages(response, model):
            yield scrapy.Request(page, callback=self.parse_page)

        yield from self.parse_propertymodel(response, model)

    def parse_page(self, response: Response) -> PR:
        model = _load_model(response)
        yield from self.parse_propertymodel(response, model)

    def parse_propertymodel(self, response: Response, model: Dict) -> PR:
        properties = model["properties"]
        for data in properties:
            _make_id(data)
            if self.repo.exists(data["id"]):
                continue
            callback = functools.partial(self.parse_property, data)
            yield response.follow(data["propertyUrl"], callback=callback)

    def parse_property(self, data, response: Response) -> PR:
        data["propertyImages"] = self._get_property_images(response)
        data["floorplanImages"] = self._get_floorplan_images(response)
        data["lettingInformation"] = self._get_letting_information(response)
        data["keyFeatures"] = self._get_key_features(response)
        data["summary"] = self._get_summary(response)
        prop = to_prop(data)
        yield PropertyItem({"prop": prop})

    def _get_key_features(self, response: Response) -> List[str]:
        xpath = "//div[contains(@class,'key-features')]/ul/li/text()"
        return response.xpath(xpath).extract()

    def _get_letting_information(self, response: Response) -> Dict[str, str]:
        xpath = "//div[@id='lettingInformation']//td/text()"
        flat_info = response.xpath(xpath).extract()
        tuples = zip(flat_info[::2], flat_info[1::2])
        table_info = dict((k.rstrip(": "), v) for k, v in tuples)
        return table_info

    def _get_summary(self, response: Response) -> str:
        xpath = "//div[@id='description']//div[@class='sect ']/node()"
        return "\n".join(response.xpath(xpath).extract()).strip()

    def _get_property_images(self, response: Response) -> List[str]:
        xpath = "//div[@class='gallery gallery-grid']/ul/*/a/img/@src"
        return response.xpath(xpath).extract()

    def _get_floorplan_images(self, response: Response) -> List[str]:
        xpath = "//div[contains(@class,'floorplancontent')]//img/@src"
        return list(set(response.xpath(xpath).extract()))


def _load_model(response: Response) -> Dict:
    script = response.xpath("/html/body/script[1]/text()").extract_first()
    jsmodel = script[len("window.jsonModel = ") :]
    model = json.loads(jsmodel)
    return model


def _get_pages(response: Response, model: Dict) -> Iterable[str]:
    url = response.url
    pagination = model["pagination"]
    options = pagination["options"]

    qr = urlparse.urlparse(url)
    parsed = list(qr)
    qs = urlparse.parse_qs(qr.query)

    # ignore first page. We only parse pages once, by loading the first page.
    for option in options[1:]:
        newqs = qs.copy()
        newqs["index"] = option["value"]
        newquery = urlparse.urlencode(newqs, doseq=True)
        parsed[4] = newquery
        yield urlparse.urlunparse(parsed)


def _make_id(propmodel: Dict):
    propmodel["id"] = f"RM-{propmodel['id']}"


def to_prop(data):
    keys = (
        "bedrooms",
        "displayAddress",
        "featuredProperty",
        "feesApply",
        "feesApplyText",
        "firstVisibleDate",
        "floorplanImages",
        "id",
        "keyFeatures",
        "lettingInformation",
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
    identity = lambda x: x

    conversions = {
        "firstVisibleDate": _to_dt,
        "price": _to_price,
        "propertyUrl": lambda x: "https://www.rightmove.co.uk" + x,
        "feesApplyText": lambda x: x or "",
    }

    d = {k: conversions.get(k, identity)(data[k]) for k in keys}

    return Property(d)


def _to_dt(string: str) -> datetime.datetime:
    return datetime.datetime.strptime(string, "%Y-%m-%dT%H:%M:%S%z")


def _to_price(data: Dict) -> Dict[str, Any]:
    return {k: data[k] for k in ("amount", "currencyCode", "frequency")}
