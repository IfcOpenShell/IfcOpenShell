# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell.api.root
import ifcopenshell.api.type
import ifcopenshell.util.brick as subject


class TestGetBrickTypeIFC4(test.bootstrap.IFC4):
    def test_run(self):
        element = self.file.createIfcAirTerminalBox()
        assert subject.get_brick_type(element) == "https://brickschema.org/schema/Brick#TerminalUnit"
        element.PredefinedType = "CONSTANTFLOW"
        assert subject.get_brick_type(element) == "https://brickschema.org/schema/Brick#CAV"
        element = self.file.createIfcEngine()
        assert subject.get_brick_type(element) == "https://brickschema.org/schema/Brick#Equipment"


class TestGetBrickTypeIFC2X3(test.bootstrap.IFC2X3):
    def test_run(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcFlowController")
        type_element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcAirTerminalBoxType")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element], relating_type=type_element)
        assert subject.get_brick_type(element) == "https://brickschema.org/schema/Brick#TerminalUnit"
