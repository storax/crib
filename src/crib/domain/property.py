"""
Property model
"""
from typing import Dict, Union

from crib.domain.model import Model
from crib.validation import vbool, vdict, vdt, vfloat, vint, vlist, vstr


class Property(Model):
    schema: Dict[str, Dict[str, Union[str, bool, Dict]]] = {
        "bedrooms": vint(),
        "displayAddress": vstr(),
        "featuredProperty": vbool(0),
        "feesApply": vbool(),
        "feesApplyText": vstr(0),
        "firstVisibleDate": vdt(),
        "id": vstr(),
        "location": vdict({"latitude": vfloat(), "longitude": vfloat()}),
        "price": vdict({"amount": vint(), "currencyCode": vstr(), "frequency": vstr()}),
        "propertyImages": vlist({"type": "string"}),
        "floorplanImages": vlist({"type": "string"}),
        "propertySubType": vstr(),
        "propertyTypeFullDescription": vstr(),
        "propertyUrl": vstr(),
        "students": vbool(),
        "summary": vstr(),
        "transactionType": vstr(),
        "keyFeatures": vlist({"type": "string"}),
        "lettingInformation": {"type": "dict", "required": True},
        "toWork": {"type": "dict", "default_setter": lambda doc: {}},
    }
