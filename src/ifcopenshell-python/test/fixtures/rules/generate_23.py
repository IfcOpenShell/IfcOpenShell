import ifcopenshell

fns = [
    (False, lambda f: f.createIfcLengthMeasure(-1.0)),
    (True, lambda f: f.createIfcLengthMeasure(1.0)),
    (True, lambda f: f.createIfcPositiveLengthMeasure(1.0)),
    (False, lambda f: f.createIfcDescriptiveMeasure("large")),
]

for valid, fn in fns:
    f = ifcopenshell.file(schema="IFC4")
    fs = fn(f)
    f.createIfcTextStyleFontModel("Comic Sans", ("Comic Sans",), FontSize=fs)
    f.write(f"{'pass' if valid else 'fail'}-font-{fs.is_a()}-{fs[0]}.ifc")
