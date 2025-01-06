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


class TestAssignReference(test.bootstrap.IFC4):
    def test_assigning_a_reference(self):
        reference = self.file.createIfcLibraryReference()
        product = self.file.createIfcWall()
        product2 = self.file.createIfcWall()
        product3 = self.file.createIfcWall()
        ifcopenshell.api.library.assign_reference(self.file, products=[product], reference=reference)
        rel = self.file.by_type("IfcRelAssociatesLibrary")[0]
        assert rel.RelatedObjects == (product,)
        ifcopenshell.api.library.assign_reference(self.file, products=[product2, product3], reference=reference)
        assert set(rel.RelatedObjects) == set((product, product2, product3))

    def test_not_assigning_twice(self):
        reference = self.file.createIfcLibraryReference()
        product = self.file.createIfcWall()
        ifcopenshell.api.library.assign_reference(self.file, products=[product], reference=reference)
        ifcopenshell.api.library.assign_reference(self.file, products=[product], reference=reference)
        rel = self.file.by_type("IfcRelAssociatesLibrary")[0]
        assert rel.RelatedObjects == (product,)


class TestAssignReferenceIFC2X3(test.bootstrap.IFC2X3, TestAssignReference):
    pass
