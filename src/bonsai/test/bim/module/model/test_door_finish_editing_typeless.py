# This file was generated with the assistance of an AI coding tool.
import bpy
import ifcopenshell.api.geometry
import pytest

import bonsai.tool as tool
from test.bim.bootstrap import NewFile

pytestmark = pytest.mark.model


def _add_door_in_wall():
    tool.Project.get_project_props().template_file = "IFC4 Demo Template.ifc"
    bpy.ops.bim.create_project()
    ifc_file = tool.Ifc.get()
    wall_type = next(e for e in ifc_file.by_type("IfcWallType") if e.Name == "WAL100")
    bpy.ops.bim.add_occurrence(relating_type_id=wall_type.id())
    wall_obj = tool.Ifc.get_object(ifc_file.by_type("IfcWall")[0])
    tool.Blender.set_active_object(wall_obj)
    bpy.context.scene.cursor.location = (10, 0, 0)
    bpy.ops.bim.hotkey(hotkey="S_E")
    door_type = next(e for e in ifc_file.by_type("IfcDoorType") if e.Name == "DT01")
    bpy.context.scene.cursor.location = (7, 0, 0)
    bpy.ops.bim.add_occurrence(relating_type_id=door_type.id())
    door = ifc_file.by_type("IfcDoor")[0]
    door_obj = tool.Ifc.get_object(door)
    tool.Blender.set_active_object(door_obj)
    bpy.ops.bim.add_door()
    return ifc_file, door_type, door, door_obj


def _strip_type_representation(ifc_file, door_type):
    for rep_map in list(door_type.RepresentationMaps):
        ifcopenshell.api.geometry.unassign_representation(
            ifc_file, product=door_type, representation=rep_map.MappedRepresentation
        )
    type_obj = tool.Ifc.get_object(door_type)
    tool.Ifc.unlink(element=door_type)
    bpy.data.objects.remove(type_obj)
    empty = bpy.data.objects.new("DT01", None)
    bpy.context.scene.collection.objects.link(empty)
    tool.Ifc.link(door_type, empty)


class TestFinishEditingDoorTypeWithoutRepresentationMap(NewFile):
    def test_finishes_and_regenerates_the_opening_from_the_door(self):
        ifc_file, door_type, door, door_obj = _add_door_in_wall()
        _strip_type_representation(ifc_file, door_type)
        assert not door_type.RepresentationMaps
        tool.Blender.set_objects_selection(bpy.context, door_obj, (door_obj,))
        bpy.ops.bim.enable_editing_door()
        tool.Model.get_door_props(door_obj).overall_width = 1.2
        bpy.ops.bim.finish_editing_door()
        assert door.OverallWidth == pytest.approx(1.2)
        assert door.FillsVoids
        opening = door.FillsVoids[0].RelatingOpeningElement
        assert tool.Geometry.get_body_representation(opening)
