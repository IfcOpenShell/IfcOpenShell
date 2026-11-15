# This file was generated with the assistance of an AI coding tool.

import math

import pytest

import ifcopenshell.api.aggregate
import ifcopenshell.api.context
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcopenshell.api.unit
import ifcopenshell.geom
import ifcopenshell.util.shape


@pytest.fixture
def mixed_brep_model():
    # Reproducer from https://github.com/IfcOpenShell/IfcOpenShell/issues/10223.
    f = ifcopenshell.api.project.create_file(version="IFC4")
    project = ifcopenshell.api.root.create_entity(f, ifc_class="IfcProject", name="Hybrid kernel repro")
    ifcopenshell.api.unit.assign_unit(f)  # its default: millimetres
    model = ifcopenshell.api.context.add_context(f, context_type="Model")
    body = ifcopenshell.api.context.add_context(
        f, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
    )
    site = ifcopenshell.api.root.create_entity(f, ifc_class="IfcSite", name="Site")
    ifcopenshell.api.aggregate.assign_object(f, products=[site], relating_object=project)

    P = lambda *c: f.createIfcCartesianPoint([float(x) for x in c])
    D = lambda *c: f.createIfcDirection([float(x) for x in c])
    A3 = lambda o, z=None, x=None: f.createIfcAxis2Placement3D(P(*o), D(*z) if z else None, D(*x) if x else None)

    def vertex(*c):
        return f.createIfcVertexPoint(P(*c))

    def edge(v0, v1, curve):
        return f.createIfcEdgeCurve(v0, v1, curve, True)

    def loop(*oriented):
        return f.createIfcEdgeLoop([f.createIfcOrientedEdge(None, None, e, s) for e, s in oriented])

    def face(surface, bound, same_sense=True):
        return f.createIfcAdvancedFace([f.createIfcFaceOuterBound(bound, True)], surface, same_sense)

    def box_brep(x0, y0, z0, dx, dy, dz):
        """Axis-aligned box as an IfcAdvancedBrep of six IfcPlane faces bounded by IfcPolyline edges."""
        c = [(x0 + i * dx, y0 + j * dy, z0 + k * dz) for k in (0, 1) for j in (0, 1) for i in (0, 1)]
        v = [vertex(*p) for p in c]
        E = {}

        def e(a, b):
            if (b, a) in E:
                return E[(b, a)], False
            if (a, b) not in E:
                E[(a, b)] = edge(v[a], v[b], f.createIfcPolyline([P(*c[a]), P(*c[b])]))
            return E[(a, b)], True

        # vertex index = i + 2j + 4k; each quad listed counter-clockwise seen from outside
        quads = {
            (0, 0, -1): (0, 2, 3, 1),
            (0, 0, 1): (4, 5, 7, 6),
            (0, -1, 0): (0, 1, 5, 4),
            (0, 1, 0): (2, 6, 7, 3),
            (-1, 0, 0): (0, 4, 6, 2),
            (1, 0, 0): (1, 3, 7, 5),
        }
        faces = []
        for n, q in quads.items():
            o = c[q[0]]
            ref = [c[q[1]][i] - o[i] for i in range(3)]
            plane = f.createIfcPlane(A3(o, n, [r / max(abs(x) for x in ref) for r in ref]))
            faces.append(face(plane, loop(*[e(q[i], q[(i + 1) % 4]) for i in range(4)])))
        return f.createIfcAdvancedBrep(f.createIfcClosedShell(faces))

    def cylinder_brep(cx, cy, z0, r, h):
        """Vertical cylinder as an IfcAdvancedBrep: one IfcCylindricalSurface face with a seam, two IfcPlane caps."""
        vb, vt = vertex(cx + r, cy, z0), vertex(cx + r, cy, z0 + h)
        cb = edge(vb, vb, f.createIfcCircle(A3((cx, cy, z0), (0, 0, 1), (1, 0, 0)), r))
        ct = edge(vt, vt, f.createIfcCircle(A3((cx, cy, z0 + h), (0, 0, 1), (1, 0, 0)), r))
        seam = edge(vb, vt, f.createIfcPolyline([P(cx + r, cy, z0), P(cx + r, cy, z0 + h)]))
        side = face(
            f.createIfcCylindricalSurface(A3((cx, cy, z0), (0, 0, 1), (1, 0, 0)), r),
            loop((cb, True), (seam, True), (ct, False), (seam, False)),
        )
        bottom = face(f.createIfcPlane(A3((cx, cy, z0), (0, 0, 1), (1, 0, 0))), loop((cb, True)), False)
        top = face(f.createIfcPlane(A3((cx, cy, z0 + h), (0, 0, 1), (1, 0, 0))), loop((ct, True)), True)
        return f.createIfcAdvancedBrep(f.createIfcClosedShell([side, bottom, top]))

    def extruded_box(x0, y0, z0, dx, dy, dz):
        prof = f.createIfcRectangleProfileDef(
            "AREA",
            None,
            f.createIfcAxis2Placement2D(f.createIfcCartesianPoint([x0 + dx / 2, y0 + dy / 2]), None),
            dx,
            dy,
        )
        return f.createIfcExtrudedAreaSolid(prof, A3((0, 0, z0)), D(0, 0, 1), dz)

    def shape(items, rep_type):
        return f.createIfcProductDefinitionShape(
            None, None, [f.createIfcShapeRepresentation(body, "Body", rep_type, items)]
        )

    def proxy(name, x, product_shape):
        p = ifcopenshell.api.root.create_entity(f, ifc_class="IfcBuildingElementProxy", name=name)
        p.ObjectPlacement = f.createIfcLocalPlacement(None, A3((x, 0, 0)))
        p.Representation = product_shape
        ifcopenshell.api.spatial.assign_container(f, products=[p], relating_structure=site)
        return p

    # the parts: a 200 x 100 x 100 mm box sitting on top of a 50 mm radius, 600 mm tall cylinder
    BOX = (-100.0, -50.0, 600.0, 200.0, 100.0, 100.0)
    CYL = (0.0, 0.0, 0.0, 50.0, 600.0)

    source = f.createIfcRepresentationMap(
        A3((0, 0, 0)),
        f.createIfcShapeRepresentation(body, "Body", "AdvancedBrep", [box_brep(*BOX), cylinder_brep(*CYL)]),
    )
    target = f.createIfcCartesianTransformationOperator3D(None, None, P(0, 0, 0), 1.0, None)
    proxy("mapped-mixed", 0.0, shape([f.createIfcMappedItem(source, target)], "MappedRepresentation"))
    proxy("direct-mixed", 1000.0, shape([box_brep(*BOX), cylinder_brep(*CYL)], "AdvancedBrep"))
    proxy("extrusion-mix", 2000.0, shape([extruded_box(*BOX), cylinder_brep(*CYL)], "SolidModel"))
    proxy("cyl-only", 3000.0, shape([cylinder_brep(*CYL)], "AdvancedBrep"))
    return f


@pytest.mark.parametrize("library", ["opencascade", "hybrid-cgal-simple-opencascade", "hybrid-cgal-opencascade"])
@pytest.mark.parametrize("method", ["create_shape", "iterator-1", "iterator-4"])
@pytest.mark.parametrize("product_name", ["mapped-mixed", "direct-mixed", "extrusion-mix", "cyl-only"])
def test_hybrid_mixed_brep_10223(mixed_brep_model, library, method, product_name):
    kernels = library.removeprefix("hybrid-").rsplit("-opencascade", 1)[0], "opencascade"
    for kernel in kernels:
        if not ifcopenshell.geom.has_geometry_library(kernel):
            pytest.skip(f"{kernel} geometry kernel is unavailable")

    model = mixed_brep_model
    product = next(p for p in model.by_type("IfcBuildingElementProxy") if p.Name == product_name)
    settings = ifcopenshell.geom.settings()
    if method == "create_shape":
        shape = ifcopenshell.geom.create_shape(settings, product, geometry_library=library)
    else:
        threads = int(method.rsplit("-", 1)[1])
        iterator = ifcopenshell.geom.iterator(settings, model, threads, include=[product], geometry_library=library)
        assert iterator.initialize()
        shape = iterator.get()
        assert shape.id == product.id()

    vertices = ifcopenshell.util.shape.get_vertices(shape.geometry)
    cylinder_only = product_name == "cyl-only"
    # Local coordinates are in metres despite the model's millimetre length unit.
    assert vertices.min(axis=0) == pytest.approx(
        (-0.05, -0.05, 0.0) if cylinder_only else (-0.1, -0.05, 0.0), abs=0.001
    )
    assert vertices.max(axis=0) == pytest.approx((0.05, 0.05, 0.6) if cylinder_only else (0.1, 0.05, 0.7), abs=0.001)
    expected_volume = math.pi * 0.05**2 * 0.6 + (0.0 if cylinder_only else 0.2 * 0.1 * 0.1)
    # Allow default cylinder tessellation error while detecting a missing cylinder or duplicate box.
    assert ifcopenshell.util.shape.get_volume(shape.geometry) == pytest.approx(expected_volume, rel=0.02)
