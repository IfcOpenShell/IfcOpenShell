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

"""Regression tests for deleting a type object through the Outliner (#6560).

Type objects live in the ``IfcTypeProduct`` collection, whose layer collection
is hidden in the viewport, so they cannot be picked or deleted in the 3D view.
The Outliner is the only route: ``bim.override_outliner_delete`` collects
``context.selected_ids`` and hands them to ``bim.override_object_delete`` under
``temp_override(selected_objects=...)``, which bypasses the visibility gate.

Before the fix that generic path called ``tool.Geometry.delete_ifc_object`` on
the type, which removed the type's representation maps and then blanked every
occurrence's Blender data. The occurrence survived in the IFC with
``Representation`` set to ``None``, so reopening the file showed it as an empty.

The tests drive the same ``temp_override`` hand-off the Outliner operator uses.
"""

import bpy
import pytest

import bonsai.tool as tool

pytestmark = pytest.mark.geometry


def _door_type_with_occurrences(count: int = 1):
    """Build an empty project holding one IfcDoorType with `count` occurrences."""
    bpy.ops.wm.read_homefile(use_empty=True)
    bpy.ops.bim.create_project()
    ifc_file = tool.Ifc.get()

    root_props = tool.Root.get_root_props()
    root_props.ifc_product = "IfcElementType"
    root_props.ifc_class = "IfcDoorType"
    root_props.ifc_predefined_type = "DOOR"
    root_props.representation_template = "DOOR"
    root_props.name = "DT01"
    bpy.ops.bim.add_element()

    element_type = ifc_file.by_type("IfcDoorType")[0]
    model_props = tool.Model.get_model_props()
    model_props.ifc_class = "IfcDoorType"
    model_props.relating_type_id = str(element_type.id())
    for _ in range(count):
        bpy.ops.bim.add_occurrence()
    return ifc_file, element_type


def _outliner_delete(objs):
    """Reproduce OverrideOutlinerDelete._execute's hand-off for `objs`."""
    with bpy.context.temp_override(selected_objects=list(objs)):
        bpy.ops.bim.override_object_delete(is_batch=False, confirm=False)


def test_type_objects_are_not_selectable_in_the_viewport():
    """The premise of the bug: the Outliner is the only way to reach a type
    object, because its collection is hidden in the viewport."""
    _, element_type = _door_type_with_occurrences()
    obj = tool.Ifc.get_object(element_type)
    obj.select_set(True)
    assert obj not in bpy.context.selected_objects


def test_deleting_a_type_keeps_its_occurrence_geometry():
    ifc_file, element_type = _door_type_with_occurrences()
    door = ifc_file.by_type("IfcDoor")[0]
    door_id = door.id()

    _outliner_delete([tool.Ifc.get_object(element_type)])

    assert not ifc_file.by_type("IfcDoorType")
    door = ifc_file.by_id(door_id)
    assert door.Representation is not None, "occurrence was left without a representation"
    assert not door.IsTypedBy
    assert tool.Ifc.get_object(door).type == "MESH"


def test_deleting_a_type_leaves_no_unresolved_mapped_items():
    """The occurrence must own its geometry outright once the type is gone."""
    ifc_file, element_type = _door_type_with_occurrences()
    door_id = ifc_file.by_type("IfcDoor")[0].id()

    _outliner_delete([tool.Ifc.get_object(element_type)])

    door = ifc_file.by_id(door_id)
    for representation in door.Representation.Representations:
        for item in representation.Items:
            assert not item.is_a("IfcMappedItem")


def test_deleting_a_type_and_its_occurrence_together_removes_both():
    """Blanking the occurrence's Blender data used to invalidate the very
    data-block still queued in the same delete batch, so the occurrence was
    skipped and its IfcDoor survived."""
    ifc_file, element_type = _door_type_with_occurrences()
    door = ifc_file.by_type("IfcDoor")[0]

    _outliner_delete([tool.Ifc.get_object(element_type), tool.Ifc.get_object(door)])

    assert not ifc_file.by_type("IfcDoorType")
    assert not ifc_file.by_type("IfcDoor")


def test_deleting_an_occurrence_still_keeps_its_type():
    ifc_file, element_type = _door_type_with_occurrences()
    door = ifc_file.by_type("IfcDoor")[0]

    _outliner_delete([tool.Ifc.get_object(door)])

    assert not ifc_file.by_type("IfcDoor")
    assert len(ifc_file.by_type("IfcDoorType")) == 1
