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

"""Regression tests for #9353: editing one window/door occurrence must not
push its OverallWidth/OverallHeight onto sibling occurrences of the same
type when those siblings own their own Body representation.

The geometry path in ``update_window_modifier_representation`` /
``update_door_modifier_representation`` already leaves an occurrence's own
Body geometry alone (only type-mapped representations are shared); these
tests pin that the occurrence attribute loop follows the same rule, in both
directions:

- an occurrence with its own Body representation keeps its attributes;
- an occurrence whose Body resolves through the shared type map still
  receives the new attributes."""

import bpy
import ifcopenshell
import ifcopenshell.api.root
import ifcopenshell.api.type
import ifcopenshell.util.representation
import ifcopenshell.util.unit
import pytest

import bonsai.tool as tool
from bonsai.bim.module.model.door import update_door_modifier_representation
from bonsai.bim.module.model.window import update_window_modifier_representation
from test.bim.bootstrap import NewFile

pytestmark = pytest.mark.model


def _add_parametric(name: str, ifc_class: str, add_op) -> tuple[bpy.types.Object, ifcopenshell.entity_instance]:
    """Create a parametric window/door occurrence owning its own Body rep."""
    bpy.ops.mesh.primitive_cube_add()
    obj = bpy.context.active_object
    obj.name = name
    rprops = tool.Root.get_root_props()
    rprops.ifc_product = "IfcElement"
    bpy.ops.bim.assign_class(ifc_class=ifc_class, predefined_type="", userdefined_type="")
    add_op()
    return obj, tool.Ifc.get_entity(obj)


def _assign_bare_type(elements, ifc_class: str) -> ifcopenshell.entity_instance:
    """Type the occurrences without touching their own representations."""
    ifc_file = tool.Ifc.get()
    element_type = ifcopenshell.api.root.create_entity(ifc_file, ifc_class=ifc_class)
    ifcopenshell.api.type.assign_type(
        ifc_file, related_objects=elements, relating_type=element_type, should_map_representations=False
    )
    return element_type


def _get_body(element: ifcopenshell.entity_instance) -> ifcopenshell.entity_instance:
    representation = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
    assert representation is not None
    return representation


def _map_body_to_type(
    occurrence: ifcopenshell.entity_instance,
    element_type: ifcopenshell.entity_instance,
    source_representation: ifcopenshell.entity_instance,
) -> None:
    """Replace the occurrence's own Body with a mapped item of a type map
    wrapping ``source_representation`` (the shared-geometry layout)."""
    ifc_file = tool.Ifc.get()
    origin = ifc_file.createIfcAxis2Placement3D(ifc_file.createIfcCartesianPoint((0.0, 0.0, 0.0)))
    representation_map = ifc_file.create_entity(
        "IfcRepresentationMap", MappingOrigin=origin, MappedRepresentation=source_representation
    )
    element_type.RepresentationMaps = [representation_map]
    transform = ifc_file.createIfcCartesianTransformationOperator3D(
        None, None, ifc_file.createIfcCartesianPoint((0.0, 0.0, 0.0)), 1.0
    )
    mapped_item = ifc_file.createIfcMappedItem(representation_map, transform)
    mapped_representation = ifc_file.createIfcShapeRepresentation(
        source_representation.ContextOfItems, "Body", "MappedRepresentation", [mapped_item]
    )
    old_body = _get_body(occurrence)
    representations = list(occurrence.Representation.Representations)
    representations[representations.index(old_body)] = mapped_representation
    occurrence.Representation.Representations = representations


class TestWindowOccurrenceAttributes(NewFile):
    def _setup_two_windows(self):
        bpy.ops.bim.create_project()
        obj_a, win_a = _add_parametric("WindowA", "IfcWindow", bpy.ops.bim.add_window)
        obj_b, win_b = _add_parametric("WindowB", "IfcWindow", bpy.ops.bim.add_window)
        return obj_a, win_a, obj_b, win_b

    def _edit_width(self, obj, delta: float = 0.25) -> float:
        props = tool.Model.get_window_props(obj)
        props.overall_width = props.overall_width + delta
        bpy.context.view_layer.objects.active = obj
        update_window_modifier_representation(bpy.context)
        si_conversion = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        return props.overall_width / si_conversion

    def test_own_geometry_occurrence_keeps_attributes(self):
        obj_a, win_a, obj_b, win_b = self._setup_two_windows()
        _assign_bare_type([win_a, win_b], "IfcWindowType")
        width_b = win_b.OverallWidth
        assert width_b is not None

        new_width = self._edit_width(obj_a)

        assert win_a.OverallWidth == pytest.approx(new_width)
        assert win_b.OverallWidth == pytest.approx(width_b)

    def test_type_mapped_occurrence_still_gets_attributes(self):
        obj_a, win_a, obj_b, win_b = self._setup_two_windows()
        element_type = _assign_bare_type([win_a, win_b], "IfcWindowType")
        _map_body_to_type(win_b, element_type, _get_body(win_a))

        new_width = self._edit_width(obj_a)

        assert win_a.OverallWidth == pytest.approx(new_width)
        assert win_b.OverallWidth == pytest.approx(new_width)


class TestDoorOccurrenceAttributes(NewFile):
    def test_own_geometry_occurrence_keeps_attributes(self):
        bpy.ops.bim.create_project()
        obj_a, door_a = _add_parametric("DoorA", "IfcDoor", bpy.ops.bim.add_door)
        obj_b, door_b = _add_parametric("DoorB", "IfcDoor", bpy.ops.bim.add_door)
        _assign_bare_type([door_a, door_b], "IfcDoorType")
        width_b = door_b.OverallWidth
        assert width_b is not None

        props = tool.Model.get_door_props(obj_a)
        props.overall_width = props.overall_width + 0.25
        bpy.context.view_layer.objects.active = obj_a
        update_door_modifier_representation(obj_a)
        si_conversion = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())

        assert door_a.OverallWidth == pytest.approx(props.overall_width / si_conversion)
        assert door_b.OverallWidth == pytest.approx(width_b)
