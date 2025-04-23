import bcf.v2.model.extensions
import bcf.v3.model.extensions
from typing import NamedTuple, Union
from dataclasses import fields


class AttributeData(NamedTuple):
    attr_type: type
    subattr_name: str
    subattr_xsd_name: str


Extensions = Union[bcf.v2.model.extensions.Extensions, bcf.v3.model.extensions.Extensions]


def get_extensions_attributes(extensions: Extensions) -> dict[str, AttributeData]:
    """Return mapping of xsd attribute name to a tuple that consists of:
    - Extensions attribute name
    - Extensions attribute type type
    - subattribute name"""
    possible_attributes = {}
    for field in fields(type(extensions)):
        field_type = field.type.__args__[0]  # type: ignore [reportAttributeAccessIssue]
        subfield = next(iter(fields(field_type)))
        xsd_name = subfield.metadata["name"]
        possible_attributes[field.name] = AttributeData(field_type, subfield.name, xsd_name)

    return possible_attributes
