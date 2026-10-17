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

import bpy
import ifcopenshell.api.geometry
import ifcopenshell.util.representation
import pytest

import bonsai.tool as tool
from test.bim.bootstrap import NewIfc

pytestmark = pytest.mark.model


def select_only(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def add_door_in_wall():
    bpy.ops.bim.select_library_file(filepath="./bonsai/bim/data/libraries/IFC4 Demo Library.ifc", append_all=True)
    ifc_file = tool.Ifc.get()
    props = tool.Model.get_model_props()
    props.ifc_class = "IfcWallType"
    props.relating_type_id = str(next(e for e in ifc_file.by_type("IfcWallType") if e.Name == "WAL100").id())
    bpy.ops.bim.add_occurrence()
    select_only(bpy.data.objects["IfcWall/Wall"])
    bpy.context.scene.cursor.location = (10, 0, 0)
    bpy.ops.bim.hotkey(hotkey="S_E")
    props.ifc_class = "IfcDoorType"
    props.relating_type_id = str(next(e for e in ifc_file.by_type("IfcDoorType") if e.Name == "DT01").id())
    bpy.context.scene.cursor.location = (7, 0, 0)
    bpy.ops.bim.add_occurrence()
    return bpy.data.objects["IfcDoor/Door"]


def add_wide_plan_representation(element):
    ifc_file = tool.Ifc.get()
    context = ifcopenshell.util.representation.get_context(ifc_file, "Plan", "Body", "PLAN_VIEW")
    profile = ifc_file.createIfcRectangleProfileDef("AREA", None, None, 1.6, 1.0)
    representation = ifcopenshell.api.geometry.add_profile_representation(
        ifc_file, context=context, profile=profile, depth=0.01
    )
    ifcopenshell.api.geometry.assign_representation(ifc_file, product=element, representation=representation)
    return representation


class TestFlipFill(NewIfc):
    def test_flip_ignores_a_wide_2d_representation_being_shown(self):
        door = add_door_in_wall()
        origin = door.matrix_world.translation.copy()
        width, depth, _ = door.dimensions
        plan_representation = add_wide_plan_representation(tool.Ifc.get_entity(door))
        select_only(door)
        bpy.ops.bim.switch_representation(obj=door.name, ifc_definition_id=plan_representation.id())

        bpy.ops.bim.flip_fill()

        assert tuple(door.matrix_world.translation) == pytest.approx(
            (origin.x + width, origin.y + depth, origin.z), abs=1e-3
        )
        assert tool.Geometry.get_active_representation(door) == plan_representation
