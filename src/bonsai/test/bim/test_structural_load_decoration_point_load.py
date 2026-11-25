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

from unittest import mock

import bpy
import ifcopenshell.api.group
import ifcopenshell.api.structural
import pytest

import bonsai.tool as tool
from bonsai.bim.module.structural.data import LoadGroupDecorationData
from bonsai.bim.module.structural.load_decoration_data import ShaderInfo
from test.bim.bootstrap import NewIfc

pytestmark = pytest.mark.structural


def add_curve_member():
    props = tool.Root.get_root_props()
    props.ifc_product = "IfcStructuralItem"
    props.ifc_class = "IfcStructuralCurveMember"
    props.representation_template = "EDGE"
    bpy.ops.bim.add_element("INVOKE_DEFAULT", skip_dialog=True)
    return tool.Ifc.get_entity(bpy.context.active_object)


class TestShaderInfoUpdate(NewIfc):
    def test_member_with_distributed_and_point_load_is_decorated(self):
        ifc_file = tool.Ifc.get()
        member = add_curve_member()
        member.Axis = ifc_file.createIfcDirection((0.0, 0.0, 1.0))

        distributed = ifcopenshell.api.structural.add_structural_load(
            ifc_file, ifc_class="IfcStructuralLoadLinearForce"
        )
        distributed.LinearForceZ = -5000.0
        distributed_activity = ifcopenshell.api.structural.add_structural_activity(
            ifc_file,
            applied_load=distributed,
            structural_member=member,
            ifc_class="IfcStructuralLinearAction",
            predefined_type="CONST",
        )

        point_force = ifc_file.createIfcStructuralLoadSingleForce(ForceZ=-10000.0)
        configuration = ifc_file.createIfcStructuralLoadConfiguration(Values=[point_force], Locations=[(1.0,)])
        point_activity = ifcopenshell.api.structural.add_structural_activity(
            ifc_file,
            applied_load=configuration,
            structural_member=member,
            ifc_class="IfcStructuralLinearAction",
            predefined_type="DISCRETE",
        )

        load_group = ifcopenshell.api.structural.add_structural_load_group(ifc_file, name="Group")
        ifcopenshell.api.group.assign_group(ifc_file, products=[distributed_activity, point_activity], group=load_group)
        analysis_model = ifcopenshell.api.structural.add_structural_analysis_model(ifc_file)
        analysis_model.LoadedBy = [load_group]
        LoadGroupDecorationData.is_loaded = False
        props = tool.Structural.get_structural_props()
        props.activity_type = "Action"
        props.load_group_to_show = str(load_group.id())

        with (
            mock.patch("bonsai.bim.module.structural.load_decoration_data.DecorationShader"),
            mock.patch.object(ShaderInfo, "get_force_units"),
        ):
            info = ShaderInfo()
            info.update()

        distributed = [i for i in info.info if any(name == "maxload" for name, _ in i["uniforms"])]
        points = [i for i in info.info if i not in distributed]
        assert distributed
        assert points
        for entry in distributed:
            assert dict(entry["uniforms"])["maxload"] == 5000.0


def add_point_connection():
    props = tool.Root.get_root_props()
    props.ifc_product = "IfcStructuralItem"
    props.ifc_class = "IfcStructuralPointConnection"
    props.representation_template = "VERTEX"
    bpy.ops.bim.add_element("INVOKE_DEFAULT", skip_dialog=True)
    return tool.Ifc.get_entity(bpy.context.active_object)


class TestPointForcesArePickable(NewIfc):
    def apply_forces(self, *forces):
        ifc_file = tool.Ifc.get()
        point = add_point_connection()
        load_case = ifcopenshell.api.structural.add_structural_load_case(ifc_file, name="Case")
        analysis_model = ifcopenshell.api.structural.add_structural_analysis_model(ifc_file)
        analysis_model.LoadedBy = [load_case]
        activities = []
        for x, z in forces:
            load = ifcopenshell.api.structural.add_structural_load(ifc_file, ifc_class="IfcStructuralLoadSingleForce")
            load.ForceX, load.ForceZ = x, z
            activities.append(
                ifcopenshell.api.structural.add_structural_activity(
                    ifc_file, applied_load=load, structural_member=point, ifc_class="IfcStructuralPointAction"
                )
            )
        ifcopenshell.api.group.assign_group(ifc_file, products=activities, group=load_case)
        LoadGroupDecorationData.is_loaded = False
        props = tool.Structural.get_structural_props()
        props.activity_type = "Action"
        props.load_group_to_show = str(load_case.id())
        return point, activities

    def draw(self):
        with (
            mock.patch("bonsai.bim.module.structural.load_decoration_data.DecorationShader"),
            mock.patch.object(ShaderInfo, "get_force_units"),
        ):
            info = ShaderInfo()
            info.update()
        return info

    def test_each_of_several_forces_picks_its_own_load(self):
        _, activities = self.apply_forces((300.0, 400.0), (-200.0, 0.0))
        tool.Structural.get_structural_props().force_display = "PARALLELOGRAM"
        info = self.draw()
        # The resultant stands for no one load, so it is not pickable.
        assert sorted(p["activity"] for p in info.pickables) == sorted(a.id() for a in activities)

    def test_the_components_of_a_resultant_of_several_forces_are_not_pickable(self):
        self.apply_forces((300.0, 400.0), (-200.0, 0.0))
        tool.Structural.get_structural_props().force_display = "BOTH"
        assert self.draw().pickables == []

    def test_a_single_force_is_picked_by_its_components_and_itself(self):
        _, activities = self.apply_forces((300.0, 400.0))
        info = self.draw()
        assert len(info.pickables) == 3  # Its X and Z components and the force itself.
        assert {p["activity"] for p in info.pickables} == {activities[0].id()}

    def test_drawing_is_tagged_with_its_item_to_hide_with_it(self):
        point, _ = self.apply_forces((300.0, 400.0))
        info = self.draw()
        name = tool.Ifc.get_object(point).name
        assert info.info and all(entry.get("object") == name for entry in info.info + info.text_info)

    def test_a_previewed_load_is_drawn_with_its_dialog_values(self):
        _, activities = self.apply_forces((0.0, -100.0))
        ShaderInfo.preview = {activities[0].AppliedLoad.id(): {"ForceX": None, "ForceY": None, "ForceZ": -750.0}}
        try:
            info = self.draw()
        finally:
            ShaderInfo.preview = {}
        assert any(entry["text"].startswith("750.00") for entry in info.text_info)
        assert not any(entry["text"].startswith("100.00") for entry in info.text_info)
