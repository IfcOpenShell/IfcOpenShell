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
from ifcopenshell.util.shape_builder import ShapeBuilder


class TestAddBoolean(test.bootstrap.IFC4):
    def test_returning_ifc_boolean_result(self):
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

        builder = ShapeBuilder(self.file)
        extrusion = builder.extrude(builder.rectangle())
        rep = builder.get_representation(body, extrusion)
        ifcopenshell.api.run("geometry.assign_representation", self.file, product=wall, representation=rep)

        ifcopenshell.api.run("geometry.add_boolean", self.file, representation=rep, matrix=np.eye(4))
        assert rep.Items[0].is_a() == "IfcBooleanResult"
        assert rep.RepresentationType == "CSG"
