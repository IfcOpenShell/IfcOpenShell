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

# This file was generated with the assistance of an AI coding tool.

import bpy
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.unit
import pytest

import bonsai.tool as tool
from test.bim.bootstrap import NewFile

pytestmark = pytest.mark.project


class TestImportRepresentationsInOneContext(NewFile):
    def test_body_mesh_is_kept_when_an_axis_shares_its_context(self, tmp_path):
        ifc = ifcopenshell.api.project.create_file()
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(ifc)
        context = ifcopenshell.api.context.add_context(ifc, context_type="Model")
        wall = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall", name="Wall")
        body = ifcopenshell.api.geometry.add_wall_representation(
            ifc, context=context, length=2, height=3, thickness=0.2
        )
        curve = ifc.createIfcPolyline(
            [ifc.createIfcCartesianPoint((0.0, 0.0, 0.0)), ifc.createIfcCartesianPoint((2.0, 0.0, 0.0))]
        )
        axis = ifc.createIfcShapeRepresentation(context, "Axis", "Curve3D", [curve])
        ifcopenshell.api.geometry.assign_representation(ifc, product=wall, representation=body)
        ifcopenshell.api.geometry.assign_representation(ifc, product=wall, representation=axis)
        filepath = str(tmp_path / "shared_context.ifc")
        ifc.write(filepath)

        bpy.ops.bim.load_project(filepath=filepath)

        obj = tool.Ifc.get_object(tool.Ifc.get().by_type("IfcWall")[0])
        assert len(obj.data.polygons) > 0
        assert len([o for o in bpy.data.objects if o.name.startswith("IfcWall/")]) == 1
