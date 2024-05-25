# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

import test.bootstrap
import ifcopenshell.api
import numpy as np


class TestAddBoolean(test.bootstrap.IFC4):
    def test_returning_ifc_boolean_clipping_result(self):
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        model = ifcopenshell.api.run("context.add_context", self.file, context_type="Model")
        body = ifcopenshell.api.run(
            "context.add_context",
            self.file,
            context_type="Model",
            context_identifier="Body",
            target_view="MODEL_VIEW",
            parent=model,
        )
        wall = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")

        profile = self.file.create_entity(
            "IfcIShapeProfileDef",
            ProfileName="HEA100",
            ProfileType="AREA",
            OverallWidth=100,
            OverallDepth=96,
            WebThickness=5,
            FlangeThickness=8,
            FilletRadius=12,
        )
        rep = ifcopenshell.api.run(
            "geometry.add_profile_representation", self.file, context=body, profile=profile, depth=5
        )
        ifcopenshell.api.run("geometry.assign_representation", self.file, product=wall, representation=rep)

        ifcopenshell.api.run("geometry.add_boolean", self.file, representation=rep, matrix=np.eye(4))
        assert rep.Items[0].is_a() == "IfcBooleanClippingResult"
        assert rep.RepresentationType == "Clipping"


class TestAddBooleanIFC2X3(test.bootstrap.IFC2X3, TestAddBoolean):
    pass
