import datetime
import functools
import json
import re
from typing import Dict, Iterable, List, Union
from urllib import parse as urlparse

import scrapy  # type: ignore
from scrapy.http.response import Response  # type: ignore

from crib import injection
from crib.domain import Property
from crib.scraper import base
from crib.scraper.items import PropertyItem

PR = Iterable[Union[Dict, scrapy.Request]]


class ZooplaSpider(base.WithInjection, scrapy.Spider):
    name: str = "zoopla"
    property_repository = injection.Dependency()

    def start_requests(self) -> Iterable[scrapy.Request]:
        urls = self.settings.getlist("ZOOPLA_SEARCHES") or []
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response: Response) -> PR:
        model = json.loads(response.body)
        for page in _get_pages(response, model):
            yield scrapy.Request(page, callback=self.parse_page)
        yield from self.parse_propertymodel(response, model)

    def parse_page(self, response: Response) -> PR:
        model = json.loads(response.body)
        yield from self.parse_propertymodel(response, model)

    def parse_propertymodel(self, response: Response, model: Dict) -> PR:
        properties = model["listing"]
        for data in properties:
            _make_id(data)
            existing = self.property_repository.get(data["id"])
            if existing and existing.banned:
                continue
            callback = functools.partial(self.parse_property, data, existing)
            yield response.follow(data["details_url"], callback=callback)

    def parse_property(self, data, existing, response: Response) -> PR:
        propd = {
            "bedrooms": int(data["num_bedrooms"]),
            "displayAddress": data["displayable_address"],
            "feesApply": False,
            "firstVisibleDate": _to_dt(data["first_published_date"]),
            "id": data["id"],
            "location": {"latitude": data["latitude"], "longitude": data["longitude"]},
            "price": {
                "amount": data["rental_prices"]["per_month"],
                "currencyCode": "GPB",
                "frequency": "monthly",
            },
            "propertyImages": self._get_property_images(response),
            "floorplanImages": self._get_floorplan_images(response),
            "propertySubType": data["property_type"],
            "propertyTypeFullDescription": "{} bedroom {}".format(
                data["num_bedrooms"], data["property_type"]
            ),
            "propertyUrl": data["details_url"],
            "students": False,
            "summary": data["description"],
            "transactionType": "rent",
            "keyFeatures": self._get_key_features(response),
            "lettingInformation": {
                "Updated": _to_dt(data["last_published_date"]),
                "Furnishing": data["furnished_state"],
            },
            "feesApplyText": data.get("letting_fees", ""),
            "favorite": existing.favorite if existing else False,
            "toWork": existing.toWork.asdict()
            if existing and existing.toWork
            else None,
        }
        prop = Property.fromdict(propd)
        yield PropertyItem({"prop": prop, "existing": existing})

    def _get_key_features(self, response: Response) -> List[str]:
        xpath = "//ul[contains(@class, 'dp-features-list--bullets')]/li/text()"
        return [s.strip() for s in response.xpath(xpath).extract()]

    def _get_property_images(self, response: Response) -> List[str]:
        data = json.loads(response.xpath("/html/body/script[4]/text()").extract_first())
        photos = data["@graph"][3]["photo"]
        return [p["contentUrl"] for p in photos]

    def _get_floorplan_images(self, response: Response) -> List[str]:
        xpath = "//div[@id = 'floorplan-1']//div[contains(@class, 'ui-modal-gallery__asset')]/@style"
        style = response.xpath(xpath).extract_first()
        if style:
            match = re.match(r".*url\('(.*)'\).*", style)
            if match:
                return [(match.group(1))]
        return []


def _get_pages(response: Response, model: Dict) -> Iterable[str]:
    url = response.url

    qr = urlparse.urlparse(url)
    parsed = list(qr)
    qs = urlparse.parse_qs(qr.query)

    count = model["result_count"]
    pages = int(count / int(qs.get("page_size", [100])[0]))
    for p in range(2, min(pages + 1, 3)):
        newqs = qs.copy()
        newqs["page_number"] = [p]
        newquery = urlparse.urlencode(newqs, doseq=True)
        parsed[4] = newquery
        yield urlparse.urlunparse(parsed)


def _make_id(propmodel: Dict):
    propmodel["id"] = f"ZOOPLA-{propmodel['listing_id']}"


def _to_dt(string: str) -> datetime.datetime:
    return datetime.datetime.strptime(string, "%Y-%m-%d %H:%M:%S")
