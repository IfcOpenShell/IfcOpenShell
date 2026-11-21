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

import bonsai.tool as tool
from bonsai.bim.module.model.profile import DumbProfileRecalculator
from test.bim.bootstrap import NewIfc


class TestDumbProfileRecalculator(NewIfc):
    def test_manual_half_space_cut_is_still_tracked_after_regenerating(self):
        bpy.ops.bim.select_library_file(filepath="./bonsai/bim/data/libraries/IFC4 Demo Library.ifc", append_all=True)
        ifc = tool.Ifc.get()
        props = bpy.context.scene.BIMModelProperties
        props.ifc_class = "IfcBeamType"
        props.relating_type_id = str(next(e for e in ifc.by_type("IfcBeamType") if e.Name == "B1").id())
        bpy.ops.bim.add_occurrence()
        obj = bpy.data.objects["IfcBeam/Beam"]
        element = tool.Ifc.get_entity(obj)
        body = tool.Geometry.get_body_representation(element)
        position = ifc.createIfcAxis2Placement3D(ifc.createIfcCartesianPoint((0.0, 0.0, 1.5)))
        half_space = ifc.createIfcHalfSpaceSolid(ifc.createIfcPlane(position), False)
        boolean = ifc.createIfcBooleanClippingResult("DIFFERENCE", tool.Model.get_extrusion(body), half_space)
        body.Items = [boolean]
        tool.Model.mark_manual_booleans(element, [boolean])
        DumbProfileRecalculator().recalculate([obj])
        assert len(tool.Model.get_manual_booleans(element)) == 1
