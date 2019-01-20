"""
User model
"""
from typing import Dict, Union

from crib.domain.model import Model
from crib.validation import vstr


class User(Model):
    schema: Dict[str, Dict[str, Union[str, bool]]] = {
        "username": vstr(),
        "password": vstr(),
    }
