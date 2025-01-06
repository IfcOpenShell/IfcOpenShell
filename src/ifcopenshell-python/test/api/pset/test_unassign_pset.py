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


class TestUnassignPset(test.bootstrap.IFC4):
    def test_unassign_pset_from_last_occurrence_and_remove_rel(self):
        elements = [self.file.create_entity("IfcWall") for _ in range(3)]
        pset = self.file.create_entity("IfcPropertySet")
        ifcopenshell.api.pset.assign_pset(self.file, elements, pset)

        ifcopenshell.api.pset.unassign_pset(self.file, elements, pset)
        assert len(self.file.by_type("IfcRelDefinesByProperties")) == 0

    def test_unassign_pset_from_non_last_occurrence_and_reuse_rel(self):
        elements = [self.file.create_entity("IfcWall") for _ in range(3)]
        pset = self.file.create_entity("IfcPropertySet")
        rel = ifcopenshell.api.pset.assign_pset(self.file, elements, pset)
        assert rel

        ifcopenshell.api.pset.unassign_pset(self.file, elements[1:], pset)
        assert rel.RelatedObjects == (elements[0],)

    def test_unassign_non_last_pset_from_type(self):
        elements = [self.file.create_entity("IfcWallType") for _ in range(3)]
        pset = self.file.create_entity("IfcPropertySet")
        pset2 = self.file.create_entity("IfcPropertySet")
        ifcopenshell.api.pset.assign_pset(self.file, elements, pset)
        ifcopenshell.api.pset.assign_pset(self.file, elements, pset2)

        ifcopenshell.api.pset.unassign_pset(self.file, elements, pset)
        assert pset.DefinesType == tuple()
        assert set(pset2.DefinesType) == set(elements)
        for element in elements:
            assert element.HasPropertySets == (pset2,)

    def test_unassign_last_pset_from_type_and_set_prop_to_none(self):
        elements = [self.file.create_entity("IfcWallType") for _ in range(3)]
        pset = self.file.create_entity("IfcPropertySet")
        ifcopenshell.api.pset.assign_pset(self.file, elements, pset)
        ifcopenshell.api.pset.unassign_pset(self.file, elements, pset)
        assert pset.DefinesType == tuple()
        for element in elements:
            assert element.HasPropertySets is None


class TestUnassignPsetIFC2X3(test.bootstrap.IFC2X3, TestUnassignPset):
    pass
