# This file was generated with the assistance of an AI coding tool.

import bpy
import ifcopenshell
from mathutils import Vector

import bonsai.tool as tool
from bonsai.bim.module.model.profile import DumbProfileJoiner
from test.bim.bootstrap import NewFile


class TestJoinDirection(NewFile):
    def test_join_is_refused_when_the_crossing_point_is_outside_the_other_profile(self, monkeypatch):
        tool.Ifc.set(ifcopenshell.file())
        through = bpy.data.objects.new("Through", None)
        crossing = bpy.data.objects.new("Crossing", None)
        axes = {
            "Through": [Vector((0, 0, 0)), Vector((0, 5, 0))],
            "Crossing": [Vector((1, 2, 0)), Vector((3, 2, 0))],
        }
        monkeypatch.setattr(DumbProfileJoiner, "get_profile_axis", lambda self, obj: axes[obj.name])
        joiner = DumbProfileJoiner.__new__(DumbProfileJoiner)
        joiner.axis = list(axes["Through"])
        assert joiner.join(through, crossing, "ATEND", "ATSTART") is False
        assert joiner.axis == axes["Through"]
