# This file was generated with the assistance of an AI coding tool.

import bpy
import ifcopenshell
import ifcopenshell.api.geometry
import ifcopenshell.api.root
import pytest
from mathutils import Vector

import bonsai.tool as tool
from bonsai.bim.module.model.wall import DumbWallJoiner
from test.bim.bootstrap import NewFile

pytestmark = pytest.mark.wall


class TestUnjoin(NewFile):
    def test_joined_neighbours_are_regenerated(self, monkeypatch):
        ifc = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc)
        walls = [ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall") for _ in range(3)]
        objs = [bpy.data.objects.new(f"Wall{i}", None) for i in range(3)]
        for wall, obj in zip(walls, objs):
            tool.Ifc.link(wall, obj)
        for relating, related in ((walls[0], walls[1]), (walls[1], walls[2])):
            ifcopenshell.api.geometry.connect_path(
                ifc,
                relating_element=relating,
                related_element=related,
                relating_connection="ATEND",
                related_connection="ATSTART",
            )
        recreated = []
        monkeypatch.setattr(tool.Model, "recreate_wall", lambda element, obj: recreated.append(element))
        monkeypatch.setattr(tool.Model, "get_wall_axis", lambda obj: {"reference": [Vector(), Vector((1, 0, 0))]})
        DumbWallJoiner.__new__(DumbWallJoiner).unjoin(objs[1])
        assert set(recreated) == set(walls)
