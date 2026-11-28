# This file was generated with the assistance of an AI coding tool.

import collections

import numpy as np

import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.geom


def box_with_retraced_face():
    """A unit box as an IfcFacetedBrep whose x = 1 face traces its full outline and then
    retraces a strip of it the other way round, a hair off the first pass, like face #61
    of test/input/faceted_brep.ifc. The winding leaves the strip out of the face."""
    model = ifcopenshell.file(schema="IFC4")
    ifcopenshell.api.root.create_entity(model, ifc_class="IfcProject")
    ifcopenshell.api.unit.assign_unit(model, length={"is_metric": True, "raw": "METERS"})
    context = ifcopenshell.api.context.add_context(model, context_type="Model")
    body = ifcopenshell.api.context.add_context(
        model, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=context
    )
    h = 2e-7
    loops = [
        [(0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0)],  # z = 0
        [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)],  # z = 1
        [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)],  # y = 0
        [(0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0)],  # y = 1
        [(0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0)],  # x = 0
        [(1, 1, 1), (1, 0, 1), (1, 0, 0), (1, 1, 0), (1, 0.9, h), (1, 0.9, 1 - h)],  # x = 1, retraced
    ]
    faces = [
        model.createIfcFace(
            [
                model.createIfcFaceOuterBound(
                    model.createIfcPolyLoop([model.createIfcCartesianPoint([float(c) for c in p]) for p in loop]), True
                )
            ]
        )
        for loop in loops
    ]
    brep = model.createIfcFacetedBrep(model.createIfcClosedShell(faces))
    product = ifcopenshell.api.root.create_entity(model, ifc_class="IfcBuildingElementProxy")
    product.ObjectPlacement = model.createIfcLocalPlacement(
        None, model.createIfcAxis2Placement3D(model.createIfcCartesianPoint((0.0, 0.0, 0.0)))
    )
    product.Representation = model.createIfcProductDefinitionShape(
        None, None, [model.createIfcShapeRepresentation(body, "Body", "Brep", [brep])]
    )
    return model, product


def test_cut_cycle_keeps_the_sense_of_its_loop():
    # https://github.com/IfcOpenShell/IfcOpenShell/issues/10359
    model, product = box_with_retraced_face()
    settings = ifcopenshell.geom.settings()
    settings.set("weld-vertices", True)
    geometry = ifcopenshell.geom.create_shape(settings, product, geometry_library="opencascade").geometry
    verts = np.array(geometry.verts).reshape(-1, 3)
    faces = np.array(geometry.faces).reshape(-1, 3)

    on_x1 = [tri for tri in faces if np.allclose(verts[tri][:, 0], 1.0)]
    assert len(on_x1) == 2
    for tri in on_x1:
        a, b, c = verts[tri]
        normal = np.cross(b - a, c - a)
        assert normal[0] > 0, "the x = 1 face must point outwards, as its loop does"

    # Consistently wound neighbours traverse their shared edge in opposite directions.
    directed = collections.Counter((int(i), int(j)) for tri in faces for i, j in zip(tri, np.roll(tri, -1)))
    assert all(n == 1 for n in directed.values())
