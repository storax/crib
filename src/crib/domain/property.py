"""
Property model
"""
from crib.domain.model import Model, SchemaType
from crib.validation import vbool, vdict, vdt, vfloat, vint, vlist, vstr


class Property(Model):
    schema: SchemaType = {
        "bedrooms": vint(),
        "displayAddress": vstr(),
        "featuredProperty": vbool(0),
        "feesApply": vbool(),
        "feesApplyText": vstr(0),
        "firstVisibleDate": vdt(),
        "id": vstr(),
        "location": vdict({"latitude": vfloat(), "longitude": vfloat()}),
        "price": vdict({"amount": vint(), "currencyCode": vstr(), "frequency": vstr()}),
        "propertyImages": vlist(vstr(False)),
        "floorplanImages": vlist(vstr(False)),
        "propertySubType": vstr(),
        "propertyTypeFullDescription": vstr(),
        "propertyUrl": vstr(),
        "students": vbool(),
        "summary": vstr(),
        "transactionType": vstr(),
        "keyFeatures": vlist(vstr(False)),
        "lettingInformation": {"type": "dict", "required": True},
        "toWork": {"type": "dict", "default_setter": lambda doc: {}},
        "favorite": {"type": "boolean", "default": False},
        "banned": {"type": "boolean", "default": False},
    }
