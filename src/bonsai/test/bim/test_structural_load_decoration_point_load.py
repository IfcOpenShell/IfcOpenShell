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
