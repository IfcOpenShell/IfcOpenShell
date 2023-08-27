# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import ifcopenshell
import blenderbim.core.tool
import blenderbim.tool as tool
import numpy as np
from test.bim.bootstrap import NewFile
from blenderbim.tool.model import Model as subject


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), blenderbim.core.tool.Model)


class TestGenerateOccurrenceName(NewFile):
    def test_generating_based_on_class(self):
        ifc = ifcopenshell.file()
        element_type = ifc.createIfcWallType(Name="Foobar")
        bpy.context.scene.BIMModelProperties.occurrence_name_style = "CLASS"
        assert subject.generate_occurrence_name(element_type, "IfcWall") == "Wall"

    def test_generating_based_on_type_name(self):
        ifc = ifcopenshell.file()
        element_type = ifc.createIfcWallType()
        bpy.context.scene.BIMModelProperties.occurrence_name_style = "TYPE"
        assert subject.generate_occurrence_name(element_type, "IfcWall") == "Unnamed"
        element_type.Name = "Foobar"
        assert subject.generate_occurrence_name(element_type, "IfcWall") == "Foobar"

    def test_generating_based_on_a_custom_function(self):
        ifc = ifcopenshell.file()
        element_type = ifc.createIfcWallType()
        bpy.context.scene.BIMModelProperties.occurrence_name_style = "CUSTOM"
        bpy.context.scene.BIMModelProperties.occurrence_name_function = '"Foobar"'
        assert subject.generate_occurrence_name(element_type, "IfcWall") == "Foobar"

class TestGetManualBooleans(NewFile):
    def test_run(self):
        assert isinstance(subject(), blenderbim.core.tool.Model)

    def test_len_returned_boolean(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcProject")
        length = ifcopenshell.api.run("unit.add_si_unit", ifc, unit_type="LENGTHUNIT")
        ifcopenshell.api.run("unit.assign_unit", ifc, units=[length])
        ifcopenshell.api.run("unit.assign_unit", ifc)
        element = ifc.createIfcColumn()
        hea100 = ifc.create_entity(
            "IfcIShapeProfileDef", ProfileName="HEA100", ProfileType="AREA",
            OverallWidth=100, OverallDepth=96, WebThickness=5, FlangeThickness=8, FilletRadius=12,
        )
        model3d = ifcopenshell.api.run("context.add_context", ifc, context_type="Model")
        body = ifcopenshell.api.run("context.add_context", ifc,context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model3d)
        representation = ifcopenshell.api.run("geometry.add_profile_representation", ifc, context=body, profile=hea100, depth=5)
        ifcopenshell.api.run("geometry.assign_representation", ifc, product=element, representation=representation)
        matrix = np.eye(4)
        matrix = ifcopenshell.util.placement.rotation(45,"X") @ matrix
        matrix[:,3][0:3] = (0, 0, 3)
        matrix = matrix.tolist()
        ifcopenshell.api.run("geometry.add_boolean", ifc, representation = representation, type = "IfcHalfSpaceSolid", matrix = matrix)
        assert len(subject.get_manual_booleans(element)) == 1

