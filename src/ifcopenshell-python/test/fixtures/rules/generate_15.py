import ifcopenshell

coords = [(0.0, 0.0), (10.0, 0.0)]
coords_2 = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]
make_3d = lambda cs: [c + (0.0,) for c in cs]
make_nd = lambda d: lambda c: (c + (0.0,)) if d == 3 else c

old_map = map
map = lambda fn, *args: list(old_map(fn, *args))

poly_2d = lambda f: [f.createIfcPolyline(map(f.createIfcCartesianPoint, coords))]
poly_3d = lambda f: [f.createIfcPolyline(map(f.createIfcCartesianPoint, make_3d(coords)))]
plane = lambda f: [f.createIfcPlane(f.createIfcAxis2Placement3D(f.createIfcCartesianPoint((0.0, 0.0, 0.0))))]
fbsm = lambda f: [
    f.createIfcFaceBasedSurfaceModel(
        FbsmFaces=[
            f.createIfcOpenShell(
                CfsFaces=[
                    f.createIfcFace(
                        Bounds=[
                            f.createIfcFaceOuterBound(
                                Bound=f.createIfcPolyLoop(Polygon=map(f.createIfcCartesianPoint, make_3d(coords_2)))
                            )
                        ]
                    )
                ]
            )
        ]
    )
]
extrusion = lambda f: [
    f.createIfcExtrudedAreaSolid(
        f.createIfcRectangleProfileDef(
            "AREA", None, f.createIfcAxis2Placement2D(f.createIfcCartesianPoint((0.0, 0.0))), 1.0, 1.0
        ),
        f.createIfcAxis2Placement3D(f.createIfcCartesianPoint((0.0, 0.0, 0.0))),
        f.createIfcDirection((0.0, 0.0, 1.0)),
        1.0,
    )
]
bbox = lambda f: [f.createIfcBoundingBox(f.createIfcCartesianPoint((0.0, 0.0, 0.0)), 1.0, 1.0, 1.0)]

gcs = lambda fn: lambda f: [f.createIfcGeometricSet(fn(f))]
repeat = lambda n, fn: lambda f: fn(f) * n

options = [
    (True, 2, "Curve2D", "2d-polyline", poly_2d),
    (False, 3, "Curve2D", "3d-polyline", poly_3d),
    (True, 2, "GeometricCurveSet", "with-curve", gcs(poly_2d)),
    (False, 3, "GeometricCurveSet", "with-surface", gcs(plane)),
    (False, 3, "SurfaceModel", "3d-polyline", poly_3d),
    (True, 3, "SurfaceModel", "surface-model", fbsm),
    (False, 3, "SweptSolid", "3d-polyline", poly_3d),
    (True, 3, "SweptSolid", "extrusion", extrusion),
    (True, 3, "BoundingBox", "single-bbox", bbox),
    (False, 3, "BoundingBox", "multiple-bbox", repeat(2, bbox)),
]

for is_valid, dims, rep_type, name, fn in options:
    f = ifcopenshell.file(schema="IFC2X3")
    f.createIfcProductDefinitionShape(
        Representations=[
            f.createIfcShapeRepresentation(
                f.createIfcGeometricRepresentationContext(
                    None,
                    None,
                    dims,
                    None,
                    f.create_entity(f"IfcAxis2Placement{dims}D", f.createIfcCartesianPoint(make_nd(dims)((0.0, 0.0)))),
                ),
                "Body",
                rep_type,
                fn(f),
            )
        ]
    )
    f.write(f"{'pass' if is_valid else 'fail'}-shaperep-{rep_type.lower()}-{name}-ifc2x3.ifc")
