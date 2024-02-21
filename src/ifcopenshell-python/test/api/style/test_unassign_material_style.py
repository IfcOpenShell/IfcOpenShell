# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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

import pytest
import test.bootstrap
import ifcopenshell
import ifcopenshell.api


class TestAssignMaterialStyle(test.bootstrap.IFC4):
    def test_run(self):
        material = ifcopenshell.api.run("material.add_material", self.file)
        context = self.file.createIfcGeometricRepresentationContext()
        style = self.file.createIfcSurfaceStyle()
        ifcopenshell.api.run("style.assign_material_style", self.file, material=material, style=style, context=context)

        # unassign 1 style
        style2 = self.file.createIfcSurfaceStyle()
        item = self.file.by_type("IfcStyledItem")[0]
        item.Styles = item.Styles + (style2,)
        ifcopenshell.api.run(
            "style.unassign_material_style", self.file, material=material, style=style2, context=context
        )
        assert item.Styles == (style,)

        # unassign last style
        ifcopenshell.api.run(
            "style.unassign_material_style", self.file, material=material, style=style, context=context
        )
        assert len(self.file.by_type("IfcMaterialDefinitionRepresentation")) == 0
        assert len(self.file.by_type("IfcStyledRepresentation")) == 0
        assert len(self.file.by_type("IfcStyledItem")) == 0
