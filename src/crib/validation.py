"""
Validation helper
"""
from typing import Dict


def vdict(schema: Dict, required=True) -> Dict:
    return {"type": "dict", "required": bool(required), "schema": schema}


def vlist(schema: Dict, required=True) -> Dict:
    return {"type": "list", "required": bool(required), "schema": schema}


def vstr(required=True) -> Dict:
    return {"type": "string", "required": bool(required)}


def vint(required=True) -> Dict:
    return {"type": "integer", "required": bool(required)}


def vfloat(required=True) -> Dict:
    return {"type": "float", "required": bool(required)}


def vbool(required=True) -> Dict:
    return {"type": "boolean", "required": bool(required)}


def vdt(required=True) -> Dict:
    return {"type": "datetime", "required": bool(required)}
