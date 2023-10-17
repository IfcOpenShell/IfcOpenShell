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
    def test_get_manual_booleans(self):
        clippings = [
            {
                "type": "IfcBooleanClippingResult",
                "operand_type": "IfcHalfSpaceSolid",
                "matrix": np.eye(4).tolist(),
            },
            {
                "type": "IfcBooleanResult",
                "operand_type": "IfcHalfSpaceSolid",
                "matrix": np.eye(4).tolist(),
            },
        ]

        ifc = ifcopenshell.file()
        self.ifc = ifc
        tool.Ifc.set(ifc)
        ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcProject")
        length = ifcopenshell.api.run("unit.add_si_unit", ifc, unit_type="LENGTHUNIT")
        ifcopenshell.api.run("unit.assign_unit", ifc, units=[length])
        ifcopenshell.api.run("unit.assign_unit", ifc)
        element = ifc.createIfcColumn()
        hea100 = ifc.create_entity(
            "IfcIShapeProfileDef",
            ProfileName="HEA100",
            ProfileType="AREA",
            OverallWidth=100,
            OverallDepth=96,
            WebThickness=5,
            FlangeThickness=8,
            FilletRadius=12,
        )
        model3d = ifcopenshell.api.run("context.add_context", ifc, context_type="Model")
        body = ifcopenshell.api.run(
            "context.add_context",
            ifc,
            context_type="Model",
            context_identifier="Body",
            target_view="MODEL_VIEW",
            parent=model3d,
        )
        representation = ifcopenshell.api.run(
            "geometry.add_profile_representation", ifc, context=body, profile=hea100, depth=5, clippings=clippings
        )
        ifcopenshell.api.run("geometry.assign_representation", ifc, product=element, representation=representation)

        booleans = subject.get_booleans(element)
        assert len(booleans) == 2
        assert len(subject.get_manual_booleans(element)) == 0
        subject.mark_manual_booleans(element, booleans)
        assert len(subject.get_manual_booleans(element)) == 2
