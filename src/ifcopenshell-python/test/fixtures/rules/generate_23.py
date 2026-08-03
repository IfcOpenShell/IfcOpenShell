import ifcopenshell
from ...fixture_generate import normalize_header, pass_if, write_fixture

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
    normalize_header(f)
    write_fixture(f, __file__, pass_if(valid), f"font-{fs.is_a()}-{fs[0]}")
