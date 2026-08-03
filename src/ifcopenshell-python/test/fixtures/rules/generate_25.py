import ifcopenshell
from generate import fail_if, normalize_header, write_fixture

segs = [
    lambda _: None,
    lambda f: [f.createIfcLineIndex((1, 2)), f.createIfcLineIndex((2, 3))],
    lambda f: [f.createIfcLineIndex((1, 2)), f.createIfcLineIndex((1, 2))],
]

for schema in ("IFC4", "IFC4X3"):
    for i, seg in enumerate(segs):
        f = ifcopenshell.file(schema=schema)
        s = seg(f)
        f.createIfcIndexedPolyCurve(f.createIfcCartesianPointList2D([(0.0, 0.0), (0.0, 1.0), (1.0, 1.0)]), s)
        normalize_header(f)
        write_fixture(
            f,
            __file__,
            fail_if(i == 2),
            f'poly-curve-{"no-segments" if s is None else "-".join(["-".join(map(str, x[0])) for x in s])}-{schema.lower()}',
        )
