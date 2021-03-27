import datetime
import functools
import json
from typing import Any, Dict, Iterable, List, Union
from urllib import parse as urlparse

import dateutil.parser
import scrapy  # type: ignore
from scrapy.http.response import Response  # type: ignore

from crib import injection
from crib.domain import Property
from crib.scraper import base
from crib.scraper.items import PropertyItem

PR = Iterable[Union[Dict, scrapy.Request]]


class RightmoveSpider(base.WithInjection, scrapy.Spider):
    name: str = "rightmove"
    property_repository = injection.Dependency()

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
            existing = self.property_repository.get(data["id"])
            if existing and existing.banned:
                continue
            callback = functools.partial(self.parse_property, data, existing)
            yield response.follow(data["propertyUrl"], callback=callback)

    def parse_property(self, data, existing, response: Response) -> PR:
        model = _load_property_page_model(response)

        propertyData = model["propertyData"]
        data["bedrooms"] = propertyData["bedrooms"]
        data["displayAddress"] = propertyData["address"]["displayAddress"]
        data["propertyImages"] = [img["url"] for img in propertyData["images"]]
        data["floorplanImages"] = [img["url"] for img in propertyData["floorplans"]]
        data["keyFeatures"] = propertyData["keyFeatures"]
        data["lettingInformation"] = propertyData["lettings"]
        prop = to_prop(data, existing)
        yield PropertyItem({"prop": prop, "existing": existing})


def _load_model(response: Response) -> Dict:
    script = response.xpath(
        "/html/body/script[text()[contains(.,'window.jsonModel = ')]]/text()"
    ).extract_first()
    jsmodel = script[len("window.jsonModel = ") :]
    model = json.loads(jsmodel)
    return model


def _load_property_page_model(response: Response) -> Dict:
    script = (
        response.xpath(
            "/html/body/script[text()[contains(.,'window.PAGE_MODEL = ')]]/text()"
        )
        .extract_first()
        .strip()
    )
    jsmodel = script[len("window.PAGE_MODEL = ") :]
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


def to_prop(data, existing=None):
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

    def identity(x):
        return x

    conversions = {
        "firstVisibleDate": _to_dt,
        "price": _to_price,
        "propertyUrl": lambda x: "https://www.rightmove.co.uk" + x,
        "feesApplyText": lambda x: x or "",
    }

    d = {k: conversions.get(k, identity)(data[k]) for k in keys}
    if existing:
        d["favorite"] = existing.favorite
        if existing.toWork:
            d["toWork"] = existing.toWork.asdict()

    return Property.fromdict(d)


def _to_dt(string: str) -> datetime.datetime:
    return dateutil.parser.parse(string)


def _to_price(data: Dict) -> Dict[str, Any]:
    price = {k: data[k] for k in ("amount", "currencyCode", "frequency")}
    if price["frequency"] == "weekly":
        price["amount"] = int(price["amount"] * 52 / 12)
        price["frequency"] = "monthly"
    return price
