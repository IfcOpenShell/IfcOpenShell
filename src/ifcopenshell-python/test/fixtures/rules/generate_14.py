import ifcopenshell
from generate import normalize_header, pass_if, write_fixture

dims = [
    (1, 0, 0, 0, 0, 0, 0),
    (1, 1, 0, 0, 0, 0, 0),
    (0, 1, 0, 0, 0, 0, 0),
    (-1, 0, 0, 0, 0, 0, 0),
    (2, 0, 0, 0, 0, 0, 0),
]

for i, d in enumerate(dims):
    f = ifcopenshell.file(schema="IFC2X3")
    f.createIfcConversionBasedUnit(
        f.createIfcDimensionalExponents(*d),
        "LENGTHUNIT",
        "beard-second",
        f.createIfcMeasureWithUnit(f.createIfcLengthMeasure(5.0), f.createIfcSIUnit(Prefix="NANO", Name="METRE")),
    )
    normalize_header(f)
    write_fixture(f, __file__, pass_if(i == 0), f"conv-unit-{i}-ifc2x3")
