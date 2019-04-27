"""
Property model
"""
from datetime import datetime
from typing import Dict, Optional, Tuple

import attr

from crib.domain.direction import Direction, Location
from crib.domain.model import Model


@attr.s(frozen=True)
class Price:
    amount: int = attr.ib()
    currencyCode: str = attr.ib()
    frequency: str = attr.ib()


@attr.s(frozen=True)
class Property(Model):
    bedrooms: int = attr.ib()
    displayAddress: str = attr.ib()
    feesApply: bool = attr.ib()
    firstVisibleDate: datetime = attr.ib()
    id: str = attr.ib()
    location: Location = attr.ib()
    price: Price = attr.ib()
    propertyImages: Tuple[str, ...] = attr.ib()
    floorplanImages: Tuple[str, ...] = attr.ib()
    propertySubType: str = attr.ib()
    propertyTypeFullDescription: str = attr.ib()
    propertyUrl: str = attr.ib()
    students: bool = attr.ib()
    summary: str = attr.ib()
    transactionType: str = attr.ib()
    keyFeatures: Tuple[str, ...] = attr.ib()
    lettingInformation: Dict = attr.ib()
    feesApplyText: str = attr.ib(default="")
    featuredProperty: bool = attr.ib(default=False)
    toWork: Optional[Direction] = attr.ib(default=None)
    favorite: bool = attr.ib(default=False)
    banned: bool = attr.ib(default=False)
