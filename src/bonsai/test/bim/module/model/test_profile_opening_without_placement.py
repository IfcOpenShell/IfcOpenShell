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
import ifcopenshell.api.material
import ifcopenshell.api.root
import ifcopenshell.guid

import bonsai.tool as tool
from bonsai.bim.module.model.profile import DumbProfileJoiner
from test.bim.bootstrap import NewFile


class TestMoveProfileOriginWithOpeningWithoutPlacement(NewFile):
    def test_run(self):
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()
        profile = ifc.create_entity("IfcRectangleProfileDef", ProfileType="AREA", XDim=0.2, YDim=0.3)
        beam_type = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcBeamType", name="Beam")
        material = ifcopenshell.api.material.add_material(ifc, name="Steel")
        profile_set = ifcopenshell.api.material.add_material_set(ifc, name="Beam", set_type="IfcMaterialProfileSet")
        ifcopenshell.api.material.add_profile(ifc, profile_set=profile_set, material=material, profile=profile)
        ifcopenshell.api.material.assign_material(
            ifc, products=[beam_type], type="IfcMaterialProfileSet", material=profile_set
        )
        bpy.ops.bim.add_occurrence(relating_type_id=beam_type.id())
        obj = bpy.context.active_object
        beam = tool.Ifc.get_entity(obj)

        opening = ifc.createIfcOpeningElement(GlobalId=ifcopenshell.guid.new())
        ifc.createIfcRelVoidsElement(
            GlobalId=ifcopenshell.guid.new(), RelatingBuildingElement=beam, RelatedOpeningElement=opening
        )
        assert opening.ObjectPlacement is None

        joiner = DumbProfileJoiner()
        start, end = joiner.get_profile_axis(obj)
        joiner.join_E(obj, start + (end - start) * 0.5, "ATSTART")
        assert (joiner.get_profile_axis(obj)[0] - start).length > 0.1
