# This file was generated with the assistance of an AI coding tool.

import math
from pathlib import Path

import numpy as np
import pytest

import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.geom
import ifcopenshell.guid
import ifcopenshell.util.shape


@pytest.mark.parametrize("hollow", [False, True], ids=["solid", "hollow"])
@pytest.mark.parametrize("path", ["circle", "polyline"])
def test_closed_swept_disk_has_no_seam_caps(path, hollow):
    model = ifcopenshell.file(schema="IFC4")
    if path == "circle":
        placement = model.createIfcAxis2Placement3D(model.createIfcCartesianPoint((0.0, 0.0, 0.0)))
        directrix = model.createIfcCircle(placement, 4.0)
        length = 8.0 * math.pi
    else:
        points = [(0.0, 0.0, 0.0), (4.0, 0.0, 0.0), (4.0, 3.0, 0.0), (0.0, 3.0, 0.0), (0.0, 0.0, 0.0)]
        directrix = model.createIfcPolyline([model.createIfcCartesianPoint(p) for p in points])
        length = 14.0
    solid = model.createIfcSweptDiskSolid(directrix, 0.4, 0.2 if hollow else None, None, None)
    settings = ifcopenshell.geom.settings()
    settings.set("mesher-linear-deflection", 0.001)
    settings.set("mesher-angular-deflection", 0.05)
    geometry = ifcopenshell.geom.create_shape(settings, solid, geometry_library="opencascade")
    assert ifcopenshell.util.shape.get_area(geometry) == pytest.approx(
        2.0 * math.pi * (0.6 if hollow else 0.4) * length, rel=0.002
    )
    assert ifcopenshell.util.shape.get_volume(geometry) == pytest.approx(
        math.pi * (0.12 if hollow else 0.16) * length, rel=0.002
    )
    # Coincident seam caps would give their boundary edges more than two incident faces.
    vertices = np.round(ifcopenshell.util.shape.get_vertices(geometry), 8)
    _, indices = np.unique(vertices, axis=0, return_inverse=True)
    faces = indices[ifcopenshell.util.shape.get_faces(geometry)]
    edges = np.concatenate([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]])
    _, counts = np.unique(np.sort(edges, axis=1), axis=0, return_counts=True)
    assert np.all(counts == 2)


@pytest.mark.parametrize("axis", [0, 2], ids=["x", "z"])
@pytest.mark.parametrize("reverse", [False, True], ids=["forward", "reverse"])
@pytest.mark.parametrize("offset", [0.0, 10.0], ids=["origin", "translated"])
@pytest.mark.parametrize("kernel", ["opencascade", "cgal", "cgal-simple", "manifold"])
def test_swept_disk_volume_9571(axis, reverse, offset, kernel):
    if not ifcopenshell.geom.has_geometry_library(kernel):
        pytest.skip(f"{kernel} geometry kernel is unavailable")
    # https://github.com/IfcOpenShell/IfcOpenShell/issues/9571
    model = ifcopenshell.file(schema="IFC4")
    placement = model.createIfcAxis2Placement3D(model.createIfcCartesianPoint((0.0, 0.0, 0.0)))
    context = model.createIfcGeometricRepresentationContext(None, "Model", 3, 1e-5, placement, None)
    units = model.createIfcUnitAssignment([model.createIfcSIUnit(None, "LENGTHUNIT", None, "METRE")])
    model.createIfcProject(ifcopenshell.guid.new(), None, "Test", None, None, None, None, [context], units)
    start = [offset, offset, offset]
    end = start.copy()
    end[axis] += 1.0
    points = [start, end][::-1] if reverse else [start, end]
    directrix = model.createIfcPolyline([model.createIfcCartesianPoint(p) for p in points])
    radius = 0.008
    solid = model.createIfcSweptDiskSolid(directrix, radius, None, None, None)
    representation = model.createIfcShapeRepresentation(context, "Body", "AdvancedSweptSolid", [solid])
    product = model.createIfcBuildingElementProxy(
        ifcopenshell.guid.new(),
        None,
        "Bar",
        None,
        None,
        model.createIfcLocalPlacement(None, placement),
        model.createIfcProductDefinitionShape(None, None, [representation]),
    )
    settings = ifcopenshell.geom.settings()
    settings.set("use-world-coords", True)
    if kernel != "opencascade":
        settings.set("circle-segments", 64)
    shape = ifcopenshell.geom.create_shape(settings, product, geometry_library=kernel)
    # Default tessellation underestimates this small circular section by about 1%.
    assert ifcopenshell.util.shape.get_volume(shape.geometry) == pytest.approx(math.pi * radius**2, rel=0.02)


@pytest.mark.parametrize("deflection", [1e-3, 1e-4], ids=["default", "fine"])
def test_advanced_brep_through_hole_volume_9570(deflection):
    # Preserve the reported edge loops, seam, bound orientations and SameSense values.
    path = Path(__file__).parent.parent / "fixtures/geom/advanced_brep_through_hole_9570.ifc"
    model = ifcopenshell.open(path)
    product = model.by_type("IfcBuildingElementProxy")[0]
    settings = ifcopenshell.geom.settings()
    settings.set("use-world-coords", True)
    settings.set("mesher-linear-deflection", deflection)
    shape = ifcopenshell.geom.create_shape(settings, product, geometry_library="opencascade")
    expected = 1.0 * 0.8 * 0.6 - math.pi * 0.15**2 * 0.6
    # Allow tessellation error, but reject the reported 12.9% excess volume.
    assert ifcopenshell.util.shape.get_volume(shape.geometry) == pytest.approx(expected, rel=0.005)


@pytest.mark.parametrize("axis_first", [True, False], ids=["axis_first", "body_first"])
def test_create_shape_prefers_body_over_axis_9771(axis_first):
    model = ifcopenshell.api.project.create_file(version="IFC4")
    ifcopenshell.api.root.create_entity(model, ifc_class="IfcProject")
    ifcopenshell.api.unit.assign_unit(model)
    model_context = ifcopenshell.api.context.add_context(model, context_type="Model")
    axis_context = ifcopenshell.api.context.add_context(
        model,
        context_type="Model",
        context_identifier="Axis",
        target_view="GRAPH_VIEW",
        parent=model_context,
    )
    body_context = ifcopenshell.api.context.add_context(
        model,
        context_type="Model",
        context_identifier="Body",
        target_view="MODEL_VIEW",
        parent=model_context,
    )
    column = ifcopenshell.api.root.create_entity(model, ifc_class="IfcColumn")
    points = [model.createIfcCartesianPoint((0.0, 0.0, 0.0)), model.createIfcCartesianPoint((0.0, 0.0, 3.0))]
    axis = model.createIfcShapeRepresentation(axis_context, "Axis", "Curve3D", [model.createIfcPolyline(points)])
    body = ifcopenshell.api.geometry.add_profile_representation(
        model,
        context=body_context,
        profile=model.createIfcRectangleProfileDef("AREA", None, None, 0.3, 0.5),
        depth=3.0,
    )
    representations = [axis, body] if axis_first else [body, axis]
    column.Representation = model.createIfcProductDefinitionShape(Representations=representations)
    shape = ifcopenshell.geom.create_shape(ifcopenshell.geom.settings(), column)
    assert len(shape.geometry.verts) // 3 == 8
