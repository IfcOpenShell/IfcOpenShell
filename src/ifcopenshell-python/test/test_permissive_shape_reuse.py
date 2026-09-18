# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 IfcOpenShell contributors
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

# This file was generated with the assistance of an AI coding tool.

"""Tests for permissive-shape-reuse task folding in the iterator (issue #143).

Occurrences of one IfcRepresentationMap whose IfcMappedItems carry their own
IfcStyledItem cannot be grouped by the regular reuse logic. With
no-parallel-mapping and permissive-shape-reuse the iterator folds such tasks
onto the shared taxonomy node, which must keep per-occurrence styles and
placements intact.
"""

import numpy as np

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.guid
import ifcopenshell.util.shape

RED = (1.0, 0.0, 0.0)
BLUE = (0.0, 0.0, 1.0)
GRAY = (0.7, 0.7, 0.7)  # default material


def make_model(occurrence_styles=(RED, RED, BLUE, None), target_offset=None):
    """One mapped box representation, one occurrence per entry in occurrence_styles.

    Styles are attached with an IfcStyledItem on each occurrence's IfcMappedItem,
    which defeats the regular mapped item grouping (StyledByItem count != 0).
    """
    f = ifcopenshell.file(schema="IFC4")
    origin = f.createIfcCartesianPoint((0.0, 0.0, 0.0))
    axis_placement = f.createIfcAxis2Placement3D(origin, None, None)
    context = f.createIfcGeometricRepresentationContext(None, "Model", 3, 1e-5, axis_placement, None)
    units = f.createIfcUnitAssignment(
        [
            f.createIfcSIUnit(None, "LENGTHUNIT", None, "METRE"),
            f.createIfcSIUnit(None, "PLANEANGLEUNIT", None, "RADIAN"),
        ]
    )
    f.createIfcProject(ifcopenshell.guid.new(), None, "Proj", None, None, None, None, [context], units)

    profile = f.createIfcRectangleProfileDef(
        "AREA", None, f.createIfcAxis2Placement2D(f.createIfcCartesianPoint((0.0, 0.0)), None), 1.0, 1.0
    )
    solid = f.createIfcExtrudedAreaSolid(profile, axis_placement, f.createIfcDirection((0.0, 0.0, 1.0)), 1.0)
    mapped_rep = f.createIfcShapeRepresentation(context, "Body", "SweptSolid", [solid])
    rep_map = f.createIfcRepresentationMap(axis_placement, mapped_rep)

    surface_styles = {}
    for colour in {s for s in occurrence_styles if s is not None}:
        rgb = f.createIfcColourRgb(None, *colour)
        shading = f.createIfcSurfaceStyleShading(rgb, 0.0)
        surface_styles[colour] = f.createIfcSurfaceStyle(str(colour), "POSITIVE", [shading])

    if target_offset is not None:
        target_origin = f.createIfcCartesianPoint(tuple(map(float, target_offset)))
    else:
        target_origin = origin

    products = []
    for i, colour in enumerate(occurrence_styles):
        target = f.createIfcCartesianTransformationOperator3D(None, None, target_origin, 1.0, None)
        mapped_item = f.createIfcMappedItem(rep_map, target)
        if colour is not None:
            f.createIfcStyledItem(mapped_item, [surface_styles[colour]], None)
        shape_rep = f.createIfcShapeRepresentation(context, "Body", "MappedRepresentation", [mapped_item])
        definition = f.createIfcProductDefinitionShape(None, None, [shape_rep])
        placement = f.createIfcLocalPlacement(
            None, f.createIfcAxis2Placement3D(f.createIfcCartesianPoint((i * 2.0, 0.0, 0.0)), None, None)
        )
        products.append(
            f.createIfcBuildingElementProxy(
                ifcopenshell.guid.new(), None, f"Elem{i}", None, None, placement, definition, None, None
            )
        )
    return f, products


def iterate(f, permissive_shape_reuse):
    settings = ifcopenshell.geom.settings()
    settings.set("apply-default-materials", True)
    if permissive_shape_reuse:
        settings.set("no-parallel-mapping", True)
        settings.set("permissive-shape-reuse", True)
    elements = {}
    iterator = ifcopenshell.geom.iterator(settings, f, 1)
    assert iterator.initialize()
    while True:
        element = iterator.get()
        elements[element.name] = element
        if not iterator.next():
            break
    return elements


def element_colours(element):
    return {
        tuple(round(c, 3) for c in rgba[:3]) for rgba in ifcopenshell.util.shape.get_material_colors(element.geometry)
    }


def world_vertices(element):
    matrix = ifcopenshell.util.shape.get_shape_matrix(element)
    verts = np.hstack(
        [ifcopenshell.util.shape.get_vertices(element.geometry), np.ones((len(element.geometry.verts) // 3, 1))]
    )
    return {tuple(np.round(row, 5)) for row in (verts @ matrix.T)[:, :3]}


def test_folding_keeps_styles_and_placements():
    f, _ = make_model()
    elements = iterate(f, permissive_shape_reuse=True)
    assert len(elements) == 4

    assert element_colours(elements["Elem0"]) == {RED}
    assert element_colours(elements["Elem1"]) == {RED}
    assert element_colours(elements["Elem2"]) == {BLUE}
    assert element_colours(elements["Elem3"]) == {GRAY}

    for i in range(4):
        matrix = ifcopenshell.util.shape.get_shape_matrix(elements[f"Elem{i}"])
        assert np.allclose(matrix[:3, 3], (i * 2.0, 0.0, 0.0))

    # occurrences with an identical style share one processed representation
    assert elements["Elem0"].geometry.id == elements["Elem1"].geometry.id
    assert elements["Elem0"].geometry.id != elements["Elem2"].geometry.id


def test_folding_matches_unfolded_output():
    f, _ = make_model()
    folded = iterate(f, permissive_shape_reuse=True)
    unfolded = iterate(f, permissive_shape_reuse=False)
    assert folded.keys() == unfolded.keys()
    for name in folded:
        assert world_vertices(folded[name]) == world_vertices(unfolded[name])
        assert element_colours(folded[name]) == element_colours(unfolded[name])


def test_folding_hoists_non_identity_mapping_target():
    f, _ = make_model(target_offset=(0.0, 0.0, 5.0))
    folded = iterate(f, permissive_shape_reuse=True)
    unfolded = iterate(f, permissive_shape_reuse=False)
    assert len(folded) == 4
    assert folded["Elem0"].geometry.id == folded["Elem1"].geometry.id
    for name in folded:
        assert world_vertices(folded[name]) == world_vertices(unfolded[name])
        assert element_colours(folded[name]) == element_colours(unfolded[name])
    # the mapping target translation must survive the fold
    assert min(v[2] for v in world_vertices(folded["Elem0"])) == 5.0


if __name__ == "__main__":
    import pytest

    pytest.main(["-vvsx", __file__])
