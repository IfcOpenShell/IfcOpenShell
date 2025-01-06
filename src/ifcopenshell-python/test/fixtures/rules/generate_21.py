import itertools
import ifcopenshell


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
    f.write(f"{'pass' if valid else 'fail'}-lining-properties-{LiningDepth}-{LiningThickness}.ifc")
