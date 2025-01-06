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
import ifcopenshell.api.pset
import ifcopenshell.util.element


class TestAssignPset(test.bootstrap.IFC4):
    def test_assign_pset_to_occurrence(self):
        elements = [self.file.create_entity("IfcWall") for _ in range(3)]
        pset = self.file.create_entity("IfcPropertySet")
        rel = ifcopenshell.api.pset.assign_pset(self.file, elements, pset)
        assert rel

        assert len(self.file.by_type("IfcRelDefinesByProperties")) == 1
        assert rel.RelatingPropertyDefinition == pset
        assert set(rel.RelatedObjects) == set(elements)

    def test_assign_pset_to_occurrence_preexisting_rel(self):
        elements = [self.file.create_entity("IfcWall") for _ in range(3)]
        pset = self.file.create_entity("IfcPropertySet")
        rel = ifcopenshell.api.pset.assign_pset(self.file, elements[:1], pset)
        assert rel

        rel_updated = ifcopenshell.api.pset.assign_pset(self.file, elements[1:], pset)
        assert rel_updated == rel
        assert len(self.file.by_type("IfcRelDefinesByProperties")) == 1
        assert rel.RelatingPropertyDefinition == pset
        assert set(rel.RelatedObjects) == set(elements)

    def test_assign_pset_to_type(self):
        elements = [self.file.create_entity("IfcWallType") for _ in range(3)]
        pset = self.file.create_entity("IfcPropertySet")
        ret = ifcopenshell.api.pset.assign_pset(self.file, elements, pset)
        assert ret is None

        assert len(self.file.by_type("IfcRelDefinesByProperties")) == 0
        assert set(pset.DefinesType) == set(elements)


class TestAssignPsetIFC2X3(test.bootstrap.IFC2X3, TestAssignPset):
    pass
