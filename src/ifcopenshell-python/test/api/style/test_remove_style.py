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
import ifcopenshell.api


class TestRemoveStyle(test.bootstrap.IFC4):
    def test_removing_a_style(self):
        shading = self.file.createIfcSurfaceStyleShading()
        style = self.file.createIfcSurfaceStyle(Styles=[shading])
        ifcopenshell.api.run("style.remove_style", self.file, style=style)
        assert len(list(self.file)) == 0

    def test_removing_any_styled_items_referencing_the_style(self):
        shading = self.file.createIfcSurfaceStyleShading()
        style = self.file.createIfcSurfaceStyle(Styles=[shading])
        styled_item = self.file.createIfcStyledItem(Styles=[style])
        ifcopenshell.api.run("style.remove_style", self.file, style=style)
        assert len(list(self.file)) == 0


class TestRemoveStyleIFC2X3(test.bootstrap.IFC2X3, TestRemoveStyle):
    pass
