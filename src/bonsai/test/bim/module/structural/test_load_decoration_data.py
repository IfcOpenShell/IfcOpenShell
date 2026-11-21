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
import ifcopenshell.guid

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


class TestTemperatureLoads(NewFile):
    def test_curve_member_temperature_load(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        member = ifc.createIfcStructuralCurveMember(
            GlobalId=ifcopenshell.guid.new(), PredefinedType="RIGID_JOINED_MEMBER"
        )
        load = ifc.createIfcStructuralLoadTemperature(DeltaTConstant=25.0, DeltaTY=-5.0, DeltaTZ=0.0)
        action = ifc.createIfcStructuralLinearAction(
            GlobalId=ifcopenshell.guid.new(), AppliedLoad=load, PredefinedType="CONST"
        )
        mesh = bpy.data.meshes.new("Member")
        mesh.from_pydata([(0.0, 0.0, 0.0), (4.0, 0.0, 0.0)], [(0, 1)], [])
        obj = bpy.data.objects.new("Member", mesh)
        tool.Ifc.link(member, obj)

        info = ShaderInfo()
        info.temperature_unit = "K"
        info.curve_members = {"1": {"member": member, "activities": [(action, 1.0)]}}
        info.get_temperature_loads()

        assert len(info.info) == 1
        assert len(info.text_info) == 1
        assert "ΔT=+25.00 K" in info.text_info[0]["text"]
        assert "ΔTy=-5.00 K" in info.text_info[0]["text"]

    def test_member_without_mesh_skips_cleanly(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        member = ifcopenshell.create_entity("IfcStructuralCurveMember", GlobalId=ifcopenshell.guid.new())
        load = ifc.createIfcStructuralLoadTemperature(DeltaTConstant=10.0)
        action = ifc.createIfcStructuralLinearAction(GlobalId=ifcopenshell.guid.new(), AppliedLoad=load)
        info = ShaderInfo()
        info.curve_members = {"1": {"member": member, "activities": [(action, 1.0)]}}
        info.get_temperature_loads()
        assert info.info == []
        assert info.text_info == []
