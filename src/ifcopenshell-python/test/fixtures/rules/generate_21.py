import itertools

import ifcopenshell
from ...fixture_generate import normalize_header, pass_if, write_fixture


def EXISTS(v):
    return v is not None


def NOT(v):
    return not v


for LiningDepth, LiningThickness in itertools.product((None, 1.0), (None, 1.0)):
    f = ifcopenshell.file(schema="IFC4")
    valid = NOT(EXISTS(LiningDepth) and NOT(EXISTS(LiningThickness)))
    f.createIfcWindowType(
        ifcopenshell.guid.new(),
        None,
        "WindowType",
        HasPropertySets=[
            f.createIfcWindowLiningProperties(
                ifcopenshell.guid.new(), LiningDepth=LiningDepth, LiningThickness=LiningThickness
            )
        ],
    )
    normalize_header(f)
    write_fixture(f, __file__, pass_if(valid), f"lining-properties-{LiningDepth}-{LiningThickness}")
