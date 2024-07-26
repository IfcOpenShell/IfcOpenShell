import ifcopenshell

segs = [
    lambda _: None,
    lambda f: [f.createIfcLineIndex((1, 2)), f.createIfcLineIndex((2, 3))],
    lambda f: [f.createIfcLineIndex((1, 2)), f.createIfcLineIndex((1, 2))],
]

for schema in ("ifc4", "ifc4x3_add1"):
    for i, seg in enumerate(segs):
        f = ifcopenshell.file(schema=schema)
        s = seg(f)
        f.createIfcIndexedPolyCurve(f.createIfcCartesianPointList2D([(0.0, 0.0), (0.0, 1.0), (1.0, 1.0)]), s)
        f.write(
            f'{"fail" if i == 2 else "pass"}-poly-curve-{"no-segments" if s is None else "-".join(["-".join(map(str, x[0])) for x in s])}-{schema}.ifc'
        )
