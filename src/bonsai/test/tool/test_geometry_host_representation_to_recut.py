# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.
#
# This file was generated with the assistance of an AI coding tool.

"""Host-representation resolution for the void/opening recut paths.

Files exported without representation subcontexts park Axis, BoundingBox and
Body on a single IfcGeometricRepresentationContext. Resolving a host's
representation from its active *context* is therefore ambiguous and returns
whichever representation happens to be first, so a wall recut after adding a
door could re-tessellate the wall from its Axis polyline and empty the mesh.
``get_host_representation_to_recut`` resolves from the active representation
instead."""

from unittest.mock import Mock, patch

import ifcopenshell
import pytest

pytestmark = pytest.mark.geometry


@pytest.fixture
def single_context_wall():
    """A wall whose Axis, BoundingBox and Body all sit on one context, Axis first."""
    ifc = ifcopenshell.file(schema="IFC2X3")
    context = ifc.create_entity(
        "IfcGeometricRepresentationContext",
        ContextType="Model",
        ContextIdentifier="Plan",
        CoordinateSpaceDimension=3,
    )
    axis = ifc.create_entity(
        "IfcShapeRepresentation",
        ContextOfItems=context,
        RepresentationIdentifier="Axis",
        RepresentationType="Curve2D",
        Items=[],
    )
    bbox = ifc.create_entity(
        "IfcShapeRepresentation",
        ContextOfItems=context,
        RepresentationIdentifier="BoundingBox",
        RepresentationType="BoundingBox",
        Items=[],
    )
    body = ifc.create_entity(
        "IfcShapeRepresentation",
        ContextOfItems=context,
        RepresentationIdentifier="Body",
        RepresentationType="Brep",
        Items=[],
    )
    wall = ifc.create_entity("IfcWall", GlobalId=ifcopenshell.guid.new())
    wall.Representation = ifc.create_entity("IfcProductDefinitionShape", Representations=[axis, bbox, body])
    return {"ifc": ifc, "context": context, "wall": wall, "axis": axis, "body": body}


def _run(single_context_wall, active_representation):
    from bonsai import tool

    obj = Mock()
    with (
        patch.object(tool.Geometry, "get_active_representation", return_value=active_representation),
        patch.object(tool.Geometry, "get_active_representation_context", return_value=single_context_wall["context"]),
        patch.object(tool.Ifc, "get_entity", return_value=single_context_wall["wall"]),
        patch.object(tool.Ifc, "get", return_value=single_context_wall["ifc"]),
    ):
        return tool.Geometry.get_host_representation_to_recut(obj)


def test_context_lookup_alone_is_ambiguous(single_context_wall):
    from bonsai import tool

    with patch.object(tool.Ifc, "get", return_value=single_context_wall["ifc"]):
        resolved = tool.Geometry.get_representation_by_context(
            single_context_wall["wall"], single_context_wall["context"]
        )
    assert resolved == single_context_wall["axis"]


def test_returns_active_representation_not_first_in_context(single_context_wall):
    assert _run(single_context_wall, single_context_wall["body"]) == single_context_wall["body"]


def test_falls_back_to_context_lookup_without_active_representation(single_context_wall):
    assert _run(single_context_wall, None) == single_context_wall["axis"]


def test_falls_back_to_context_lookup_for_an_active_item(single_context_wall):
    item = single_context_wall["ifc"].create_entity("IfcFacetedBrep")
    assert _run(single_context_wall, item) == single_context_wall["axis"]
