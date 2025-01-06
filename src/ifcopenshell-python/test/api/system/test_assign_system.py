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
import ifcopenshell.api.root
import ifcopenshell.api.system
import ifcopenshell.util.system


class TestAssignSystem(test.bootstrap.IFC4):
    def test_assign_system(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcFlowSegment")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcFlowSegment")
        system = ifcopenshell.api.system.add_system(self.file)
        ifcopenshell.api.system.assign_system(self.file, products=[element, element2], system=system)
        assert len(self.file.by_type("IfcRelAssignsToGroup")) == 1
        assert set(ifcopenshell.util.system.get_system_elements(system)) == set(self.file.by_type("IfcFlowSegment"))

    def test_exception_on_unassignable_elements(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcFlowSegment")
        proj = self.file.createIfcProject()
        system = ifcopenshell.api.system.add_system(self.file)
        with pytest.raises(TypeError):
            ifcopenshell.api.system.assign_system(self.file, products=[element, proj], system=system)
        with pytest.raises(TypeError):
            ifcopenshell.api.system.assign_system(self.file, products=[element], system=proj)


class TestAssignSystemIFC2X3(test.bootstrap.IFC2X3, TestAssignSystem):
    pass
