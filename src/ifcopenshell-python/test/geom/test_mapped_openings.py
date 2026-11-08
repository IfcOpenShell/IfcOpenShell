# This file was generated with the assistance of an AI coding tool.

import numpy as np
import pytest

import ifcopenshell.api.context
import ifcopenshell.api.feature
import ifcopenshell.api.geometry
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.type
import ifcopenshell.api.unit
import ifcopenshell.geom
import ifcopenshell.util.shape_builder


def surface_genus(geometry):
    """Euler genus of the reproducer's connected, closed triangulated surface."""
    if not geometry.faces:
        return None
    # Weld duplicate vertices along face/normal seams before counting edges.
    vertices = np.asarray(geometry.verts).reshape(-1, 3)
    _, indices = np.unique(np.round(vertices, 9), axis=0, return_inverse=True)
    faces = indices[np.asarray(geometry.faces).reshape(-1, 3)]
    edges = np.sort(np.concatenate((faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]])), axis=1)
    edges, counts = np.unique(edges, axis=0, return_counts=True)
    if not np.all(counts == 2):
        return None
    euler = len(np.unique(faces)) - len(edges) + len(faces)
    return (2 - euler) / 2


@pytest.mark.parametrize("mapped", [True, False], ids=["mapped", "direct"])
@pytest.mark.parametrize("method", ["create_shape", "iterator"])
@pytest.mark.parametrize(
    "library,expected_genus",
    [
        ("opencascade", 1),
        ("cgal-simple", 0),  # No boolean support: the box remains unopened.
        ("hybrid-cgal-simple-opencascade", 1),
    ],
)
def test_opening_surface_genus_10049(mapped, method, library, expected_genus):
    # https://github.com/IfcOpenShell/IfcOpenShell/issues/10049
    kernels = ("cgal-simple", "opencascade") if library.startswith("hybrid-") else (library,)
    for kernel in kernels:
        if not ifcopenshell.geom.has_geometry_library(kernel):
            pytest.skip(f"{kernel} geometry kernel is unavailable")

    f = ifcopenshell.api.project.create_file(version="IFC4")
    ifcopenshell.api.root.create_entity(f, ifc_class="IfcProject")
    ifcopenshell.api.unit.assign_unit(f)
    model = ifcopenshell.api.context.add_context(f, context_type="Model")
    body = ifcopenshell.api.context.add_context(
        f, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
    )
    builder = ifcopenshell.util.shape_builder.ShapeBuilder(f)

    # The same 2 x 1 x 1 box, either mapped from a type or assigned directly.
    element_type = ifcopenshell.api.root.create_entity(f, ifc_class="IfcFurnitureType")
    box = builder.extrude(builder.rectangle(size=np.array((2.0, 1.0))), magnitude=1.0)
    ifcopenshell.api.geometry.assign_representation(f, element_type, builder.get_representation(body, [box]))
    element = ifcopenshell.api.root.create_entity(f, ifc_class="IfcFurniture")
    ifcopenshell.api.geometry.edit_object_placement(f, product=element)
    if mapped:
        ifcopenshell.api.type.assign_type(f, related_objects=[element], relating_type=element_type)
    else:
        ifcopenshell.api.geometry.assign_representation(f, element, builder.get_representation(body, [box]))

    # A through-opening changes the surface genus from zero to one.
    opening = ifcopenshell.api.root.create_entity(f, ifc_class="IfcOpeningElement")
    cutter = builder.extrude(builder.rectangle(size=np.array((0.5, 0.5))), magnitude=1.5, position=(0.75, 0.25, -0.25))
    ifcopenshell.api.geometry.assign_representation(f, opening, builder.get_representation(body, [cutter]))
    ifcopenshell.api.geometry.edit_object_placement(f, product=opening)
    ifcopenshell.api.feature.add_feature(f, feature=opening, element=element)

    settings = ifcopenshell.geom.settings()
    if method == "create_shape":
        shape = ifcopenshell.geom.create_shape(settings, element, geometry_library=library)
    else:
        iterator = ifcopenshell.geom.iterator(settings, f, 1, include=[element], geometry_library=library)
        assert iterator.initialize()
        shape = iterator.get()
    assert surface_genus(shape.geometry) == expected_genus
