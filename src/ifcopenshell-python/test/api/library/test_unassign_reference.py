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
import ifcopenshell.api.library
import ifcopenshell.util.element


class TestUnassignReference(test.bootstrap.IFC4):
    def test_unassigning_a_reference(self):
        reference = self.file.createIfcLibraryReference()
        products = [self.file.createIfcWall() for i in range(3)]
        ifcopenshell.api.library.assign_reference(self.file, products=products, reference=reference)
        ifcopenshell.api.library.unassign_reference(self.file, products=products[:1], reference=reference)
        assert ifcopenshell.util.element.get_referenced_elements(reference) == set(products[1:])

        ifcopenshell.api.library.unassign_reference(self.file, products=products[1:], reference=reference)
        assert ifcopenshell.util.element.get_referenced_elements(reference) == set()
        assert len(self.file.by_type("IfcRelAssociatesLibrary")) == 0


class TestUnassignReferenceIFC2X3(test.bootstrap.IFC2X3, TestUnassignReference):
    pass
