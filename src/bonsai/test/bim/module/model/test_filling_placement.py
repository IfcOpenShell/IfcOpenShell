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
import ifcopenshell
import ifcopenshell.api.aggregate
import ifcopenshell.api.root
import ifcopenshell.util.placement
import numpy as np
import pytest
from mathutils import Vector

import bonsai.tool as tool
from bonsai.bim.module.model import opening as model_opening
from bonsai.bim.module.model.wall import DumbWallGenerator
from test.bim.bootstrap import NewFile

pytestmark = pytest.mark.model


def _set_blender_offset():
    props = tool.Georeference.get_georeference_props()
    props.has_blender_offset = True
    props.blender_offset_x = "1000"
    props.blender_offset_y = "2000"
    props.blender_offset_z = "0"
    props.blender_x_axis_abscissa = "1"
    props.blender_x_axis_ordinate = "0"


def _add_wall(start, end):
    ifc = tool.Ifc.get()
    bpy.ops.bim.add_default_type(ifc_element_type="IfcWallType")
    wall_type = ifc.by_type("IfcWallType")[-1]
    polyline_props = tool.Model.get_polyline_props()
    polyline_data = polyline_props.insertion_polyline.add()
    for co in (start, end):
        point = polyline_data.polyline_points.add()
        point.x, point.y, point.z = co
    walls, _ = DumbWallGenerator(wall_type).generate(insertion_type="POLYLINE")
    polyline_props.insertion_polyline.clear()
    bpy.context.view_layer.update()
    return walls[0]["obj"] if isinstance(walls[0], dict) else walls[0]


def _add_door_type():
    rprops = tool.Root.get_root_props()
    rprops.ifc_product = "IfcElementType"
    rprops.ifc_class = "IfcDoorType"
    rprops.ifc_predefined_type = "DOOR"
    rprops.representation_template = "DOOR"
    bpy.ops.bim.add_element()
    return tool.Ifc.get().by_type("IfcDoorType")[-1]


def _place_door(wall_obj, door_type, location):
    tool.Blender.select_and_activate_single_object(bpy.context, wall_obj)
    bpy.context.scene.cursor.location = location
    bpy.ops.bim.add_occurrence(relating_type_id=door_type.id())
    return tool.Ifc.get().by_type("IfcDoor")[-1]


class TestOpeningPlacementWithBlenderOffset(NewFile):
    def test_opening_is_written_where_the_door_is(self):
        bpy.ops.bim.create_project()
        _set_blender_offset()
        wall_obj = _add_wall(Vector((0.0, 0.0, 0.0)), Vector((5.0, 0.0, 0.0)))
        door = _place_door(wall_obj, _add_door_type(), Vector((2.0, 0.0, 0.0)))

        opening = door.FillsVoids[0].RelatingOpeningElement
        door_matrix = ifcopenshell.util.placement.get_local_placement(door.ObjectPlacement)
        opening_matrix = ifcopenshell.util.placement.get_local_placement(opening.ObjectPlacement)
        np.testing.assert_allclose(opening_matrix, door_matrix, atol=1e-6)

    @pytest.mark.parametrize("operator", ["recalculate_fill", "flip_fill"])
    def test_opening_follows_the_door_after_an_edit(self, operator):
        bpy.ops.bim.create_project()
        _set_blender_offset()
        wall_obj = _add_wall(Vector((0.0, 0.0, 0.0)), Vector((5.0, 0.0, 0.0)))
        door = _place_door(wall_obj, _add_door_type(), Vector((2.0, 0.0, 0.0)))
        door_obj = tool.Ifc.get_object(door)
        tool.Blender.select_and_activate_single_object(bpy.context, door_obj)
        getattr(bpy.ops.bim, operator)()

        opening = door.FillsVoids[0].RelatingOpeningElement
        opening_matrix = ifcopenshell.util.placement.get_local_placement(opening.ObjectPlacement)
        np.testing.assert_allclose(opening_matrix, tool.Surveyor.get_absolute_matrix(door_obj), atol=1e-6)


class TestUnhostableFilling(NewFile):
    def test_a_host_without_faces_reports_instead_of_raising(self):
        bpy.ops.bim.create_project()
        wall_obj = _add_wall(Vector((0.0, 0.0, 0.0)), Vector((5.0, 0.0, 0.0)))
        wall_obj.data = bpy.data.meshes.new("Empty")
        door_type = _add_door_type()
        with pytest.raises(RuntimeError, match="Could not host the door"):
            _place_door(wall_obj, door_type, Vector((2.0, 0.0, 1.0)))
        assert not tool.Ifc.get().by_type("IfcDoor")

    def test_a_door_too_far_from_the_host_is_not_left_behind(self):
        bpy.ops.bim.create_project()
        wall_obj = _add_wall(Vector((0.0, 0.0, 0.0)), Vector((5.0, 0.0, 0.0)))
        door_type = _add_door_type()
        with pytest.raises(RuntimeError, match="Could not host the door"):
            _place_door(wall_obj, door_type, Vector((500.0, 500.0, 0.0)))
        assert not tool.Ifc.get().by_type("IfcDoor")
        assert not tool.Ifc.get().by_type("IfcOpeningElement")

    def test_adding_a_far_door_to_a_wall_as_an_opening_reports_why(self):
        bpy.ops.bim.create_project()
        wall_obj = _add_wall(Vector((0.0, 0.0, 0.0)), Vector((5.0, 0.0, 0.0)))
        bpy.ops.object.select_all(action="DESELECT")
        bpy.context.scene.cursor.location = Vector((500.0, 500.0, 0.0))
        bpy.ops.bim.add_occurrence(relating_type_id=_add_door_type().id())
        door = tool.Ifc.get().by_type("IfcDoor")[-1]
        door_obj = tool.Ifc.get_object(door)
        bpy.ops.object.select_all(action="DESELECT")
        wall_obj.select_set(True)
        door_obj.select_set(True)
        bpy.context.view_layer.objects.active = wall_obj
        with pytest.raises(RuntimeError, match="Could not host"):
            bpy.ops.bim.add_opening()
        assert not door.FillsVoids


class TestFillingHostFromPart(NewFile):
    def test_a_door_picked_on_a_part_of_the_wall_is_hosted_in_the_wall(self):
        bpy.ops.bim.create_project()
        wall_obj = _add_wall(Vector((0.0, 0.0, 0.0)), Vector((5.0, 0.0, 0.0)))
        ifc = tool.Ifc.get()
        wall = tool.Ifc.get_entity(wall_obj)
        part_obj = bpy.data.objects.new("Part", bpy.data.meshes.new("Part"))
        bpy.context.scene.collection.objects.link(part_obj)
        bpy.ops.bim.assign_class(obj=part_obj.name, ifc_class="IfcBuildingElementPart")
        part = ifc.by_type("IfcBuildingElementPart")[0]
        part_obj = tool.Ifc.get_object(part)
        ifcopenshell.api.aggregate.assign_object(ifc, products=[part], relating_object=wall)
        door = _place_door(part_obj, _add_door_type(), Vector((2.0, 0.0, 1.0)))
        assert door.FillsVoids
        assert door.FillsVoids[0].RelatingOpeningElement.VoidsElements[0].RelatingBuildingElement == wall

    def test_the_host_is_found_through_nested_parts(self):
        ifc = ifcopenshell.file()
        wall = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
        part = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcBuildingElementPart")
        annotation = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcAnnotation")
        ifcopenshell.api.aggregate.assign_object(ifc, products=[part], relating_object=wall)
        ifcopenshell.api.aggregate.assign_object(ifc, products=[annotation], relating_object=part)
        assert model_opening.get_filling_host(annotation) == wall

    def test_an_element_outside_any_host_has_no_host(self):
        ifc = ifcopenshell.file()
        beam = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcBeam")
        assert model_opening.get_filling_host(beam) is None
        assert model_opening.get_filling_host(None) is None
