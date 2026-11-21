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

import math
from types import SimpleNamespace

import bpy
import ifcopenshell
import ifcopenshell.guid
import numpy as np

import bonsai.tool as tool
from bonsai.bim.module.structural.load_decoration_data import ShaderInfo
from test.bim.bootstrap import NewFile


class TestLinearLoadsForMemberWithoutMesh(NewFile):
    def _shader_info(self, ifc):
        member = ifc.createIfcStructuralCurveMember(
            GlobalId=ifcopenshell.guid.new(), PredefinedType="RIGID_JOINED_MEMBER"
        )
        action = ifc.createIfcStructuralLinearAction(GlobalId=ifcopenshell.guid.new(), PredefinedType="CONST")
        info = ShaderInfo()
        info.curve_members = {"1": {"member": member, "activities": [(action, 1.0)]}}
        return info, member

    def test_member_without_object(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        info, _ = self._shader_info(ifc)
        info.get_linear_loads()
        assert info.info == []

    def test_member_with_empty_mesh(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        info, member = self._shader_info(ifc)
        tool.Ifc.link(member, bpy.data.objects.new("Member", bpy.data.meshes.new("Member")))
        info.get_linear_loads()
        assert info.info == []


class TestArrowThickness(NewFile):
    def get_spacing(self) -> float:
        info = ShaderInfo()
        info.shader = SimpleNamespace(new=lambda name: None)  # Headless, there is no GPU to make shaders with.
        info.add_force_arrow(np.zeros(3), np.array((0.0, 0.0, 1.0)), (1, 0, 0, 1), "1 kN", 1.0)
        return dict(info.info[-1]["uniforms"])["spacing"]

    def test_scaling_the_shaft_and_head_together(self):
        tool.Ifc.set(ifcopenshell.file())
        default = self.get_spacing()
        tool.Structural.get_structural_props().arrow_thickness = 2.0
        assert math.isclose(self.get_spacing(), 2 * default)
