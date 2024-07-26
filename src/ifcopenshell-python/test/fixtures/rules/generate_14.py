import ifcopenshell

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
    f.write(f"{'pass' if i == 0 else 'fail'}-conv-unit-{i}-ifc2x3.ifc")
