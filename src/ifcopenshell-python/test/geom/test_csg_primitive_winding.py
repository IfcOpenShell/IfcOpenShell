# This file was generated with the assistance of an AI coding tool.

import collections

import numpy as np
import pytest

import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.geom


def csg_product(make_primitive):
    model = ifcopenshell.file(schema="IFC4")
    ifcopenshell.api.root.create_entity(model, ifc_class="IfcProject")
    ifcopenshell.api.unit.assign_unit(model, length={"is_metric": True, "raw": "METERS"})
    context = ifcopenshell.api.context.add_context(model, context_type="Model")
    body = ifcopenshell.api.context.add_context(
        model, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=context
    )
    origin = lambda: model.createIfcAxis2Placement3D(model.createIfcCartesianPoint((0.0, 0.0, 0.0)))
    product = ifcopenshell.api.root.create_entity(model, ifc_class="IfcBuildingElementProxy")
    product.ObjectPlacement = model.createIfcLocalPlacement(None, origin())
    solid = model.createIfcCsgSolid(make_primitive(model, origin()))
    product.Representation = model.createIfcProductDefinitionShape(
        None, None, [model.createIfcShapeRepresentation(body, "Body", "CSG", [solid])]
    )
    return model, product


def signed_volume_and_flipped_edges(geometry):
    verts = np.array(geometry.verts).reshape(-1, 3)
    faces = np.array(geometry.faces).reshape(-1, 3)
    a, b, c = verts[faces[:, 0]], verts[faces[:, 1]], verts[faces[:, 2]]
    volume = np.einsum("ij,ij->i", a, np.cross(b, c)).sum() / 6
    # Consistently wound neighbours traverse their shared edge in opposite directions.
    directed = collections.Counter((int(i), int(j)) for tri in faces for i, j in zip(tri, np.roll(tri, -1)))
    flipped = sum(1 for (i, j), n in directed.items() if n > 1 or (n == 1 and (j, i) not in directed))
    return volume, flipped


@pytest.mark.parametrize(
    "make_primitive, volume",
    [
        (lambda m, p: m.createIfcBlock(p, 1.0, 2.0, 3.0), 6.0),
        (lambda m, p: m.createIfcRectangularPyramid(p, 1.0, 2.0, 3.0), 2.0),
    ],
    ids=["IfcBlock", "IfcRectangularPyramid"],
)
def test_csg_primitive_faces_point_outwards(make_primitive, volume):
    # https://github.com/IfcOpenShell/IfcOpenShell/issues/10357
    settings = ifcopenshell.geom.settings()
    settings.set("weld-vertices", True)
    model, product = csg_product(make_primitive)
    shape = ifcopenshell.geom.create_shape(settings, product, geometry_library="opencascade")
    signed_volume, flipped_edges = signed_volume_and_flipped_edges(shape.geometry)
    assert signed_volume == pytest.approx(volume, rel=1e-6)
    assert flipped_edges == 0
