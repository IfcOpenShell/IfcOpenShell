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
import ifcopenshell.api.root
import ifcopenshell.api.structural
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


class TestLoadsInATurnedModel(NewFile):
    """Global loads are given in their analysis model's axes, which RFEM points Z down, and drawn in Blender's"""

    def make_activity(self, item_class, activity_class, load_class, attributes, global_or_local="GLOBAL_COORDS"):
        ifc = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        model = ifcopenshell.api.structural.add_structural_analysis_model(ifc)
        model.SharedPlacement = ifc.createIfcLocalPlacement(
            None,
            ifc.createIfcAxis2Placement3D(
                ifc.createIfcCartesianPoint((0.0, 0.0, 0.0)),
                ifc.createIfcDirection((0.0, 0.0, -1.0)),
                ifc.createIfcDirection((1.0, 0.0, 0.0)),
            ),
        )
        item = ifcopenshell.api.root.create_entity(ifc, ifc_class=item_class)
        ifcopenshell.api.structural.assign_structural_analysis_model(
            ifc, products=[item], structural_analysis_model=model
        )
        load = ifcopenshell.api.structural.add_structural_load(ifc, ifc_class=load_class)
        ifcopenshell.api.structural.edit_structural_load(ifc, structural_load=load, attributes=attributes)
        activity = ifcopenshell.api.structural.add_structural_activity(
            ifc, ifc_class=activity_class, applied_load=load, structural_member=item, global_or_local=global_or_local
        )
        tool.Structural.get_structural_props().reference_frame = "GLOBAL_COORDS"
        return activity

    def test_a_line_load_down_in_the_model_is_drawn_down(self):
        activity = self.make_activity(
            "IfcStructuralCurveMember",
            "IfcStructuralLinearAction",
            "IfcStructuralLoadLinearForce",
            {"LinearForceZ": 5.0, "LinearMomentY": 1.0},
        )
        values = ShaderInfo().parse_linear_loads_to_dict([(activity, 1.0)], np.eye(3))["constant force"]
        assert np.allclose(values, (0.0, 0.0, -5.0, 0.0, -1.0, 0.0))

    def test_an_area_load_down_in_the_model_is_drawn_down(self):
        activity = self.make_activity(
            "IfcStructuralSurfaceMember",
            "IfcStructuralPlanarAction",
            "IfcStructuralLoadPlanarForce",
            {"PlanarForceZ": 5.0},
        )
        assert np.allclose(ShaderInfo().get_planar_loads_values([(activity, 1.0)], np.eye(3)), (0.0, 0.0, -5.0))

    def test_a_point_load_is_turned_once(self):
        activity = self.make_activity(
            "IfcStructuralPointConnection",
            "IfcStructuralPointAction",
            "IfcStructuralLoadSingleForce",
            {"ForceZ": 5.0},
        )
        values = ShaderInfo().get_point_loads_values([(activity, 1.0)], np.eye(3))
        assert np.allclose(values[:3], (0.0, 0.0, -5.0))

    def test_a_local_load_is_not_turned_into_the_model_axes(self):
        activity = self.make_activity(
            "IfcStructuralSurfaceMember",
            "IfcStructuralPlanarAction",
            "IfcStructuralLoadPlanarForce",
            {"PlanarForceZ": 5.0},
            global_or_local="LOCAL_COORDS",
        )
        tool.Structural.get_structural_props().reference_frame = "LOCAL_COORDS"
        assert np.allclose(ShaderInfo().get_planar_loads_values([(activity, 1.0)], np.eye(3)), (0.0, 0.0, 5.0))
