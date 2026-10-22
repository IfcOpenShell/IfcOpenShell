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

from types import SimpleNamespace
from unittest.mock import MagicMock

import bpy

import bonsai.tool as tool
from bonsai.bim.module.material.data import ObjectMaterialData
from bonsai.bim.module.material.operator import AddProfile
from test.bim.bootstrap import NewIfc


def make_beam_with_profile_set():
    obj = bpy.data.objects.new("Beam", None)
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    root_props = tool.Root.get_root_props()
    root_props.ifc_product = "IfcElement"
    root_props.ifc_class = "IfcBeam"
    bpy.ops.bim.assign_class()
    bpy.ops.bim.add_material()
    obj.BIMObjectMaterialProperties.material_type = "IfcMaterialProfileSet"
    bpy.ops.bim.assign_material()
    bpy.ops.bim.enable_editing_assigned_material()
    profile_set = tool.Ifc.get().by_type("IfcMaterialProfileSet")[0]
    return obj, profile_set


def add_profile(obj, profile_set):
    bpy.ops.bim.add_profile_def()
    profile = tool.Ifc.get().by_type("IfcProfileDef")[-1]
    tool.Material.refresh()
    tool.Material.get_material_props().profiles = str(profile.id())
    report = MagicMock()
    AddProfile._execute(SimpleNamespace(obj=obj.name, profile_set=profile_set.id(), report=report), bpy.context)
    return report


class TestAddProfileWarnsWithoutCompositeProfile(NewIfc):
    def test_second_profile_reports_a_warning(self):
        obj, profile_set = make_beam_with_profile_set()
        assert len(profile_set.MaterialProfiles) == 1
        report = add_profile(obj, profile_set)
        assert len(profile_set.MaterialProfiles) == 2
        report.assert_called_once()
        assert report.call_args.args[0] == {"WARNING"}

    def test_panel_data_flags_a_missing_composite_profile(self):
        obj, profile_set = make_beam_with_profile_set()
        add_profile(obj, profile_set)
        ObjectMaterialData.load()
        assert ObjectMaterialData.data["set"]["has_composite_profile"] is False
        profile_set.CompositeProfile = tool.Ifc.get().createIfcCompositeProfileDef("AREA")
        ObjectMaterialData.load()
        assert ObjectMaterialData.data["set"]["has_composite_profile"] is True
