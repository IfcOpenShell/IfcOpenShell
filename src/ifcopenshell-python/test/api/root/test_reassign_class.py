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

import test.bootstrap
import ifcopenshell.api


class TestReassignClass(test.bootstrap.IFC4):
    def test_reassigning_a_simple_class(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        new = ifcopenshell.api.run("root.reassign_class", self.file, product=element, ifc_class="IfcSlab")
        assert len([e for e in self.file]) == 1
        assert new.id() == 1
        assert new.is_a("IfcSlab")

    def test_reassigning_a_predefined_type(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        new = ifcopenshell.api.run(
            "root.reassign_class", self.file, product=element, ifc_class="IfcSlab", predefined_type="FLOOR"
        )
        assert new.PredefinedType == "FLOOR"

    def test_falling_back_to_userdefined_if_the_predefined_type_cannot_be_reassigned(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        new = ifcopenshell.api.run(
            "root.reassign_class", self.file, product=element, ifc_class="IfcSlab", predefined_type="FOO"
        )
        assert new.PredefinedType == "USERDEFINED"
        assert new.ObjectType == "FOO"
