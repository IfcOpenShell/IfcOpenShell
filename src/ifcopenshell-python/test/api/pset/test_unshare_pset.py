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
import ifcopenshell.api.root
import ifcopenshell.util.element
import ifcopenshell.guid


class TestUnsharePset(test.bootstrap.IFC4):
    def test_unshare_pset_for_occurrence(self):
        elements = [self.file.create_entity("IfcWall") for _ in range(3)]

        pset = ifcopenshell.api.pset.add_pset(self.file, elements[0], "Foo")
        rel = self.file.by_type("IfcRelDefinesByProperties")[0]
        rel.RelatedObjects = elements

        new_psets = ifcopenshell.api.pset.unshare_pset(self.file, elements[:2], pset)
        assert isinstance(new_psets, list)
        assert len(new_psets) == 2

        assert len(psets := self.file.by_type("IfcPropertySet")) == 3
        assert len(self.file.by_type("IfcRelDefinesByProperties")) == 3

        used_elements = set()
        for pset in psets:
            pset_elements = ifcopenshell.util.element.get_elements_by_pset(pset)
            assert len(pset_elements) == 1
            used_elements.update(pset_elements)

        assert used_elements == set(elements)

    def test_unshare_pset_for_type(self):
        elements = [self.file.create_entity("IfcWallType") for _ in range(3)]

        pset = ifcopenshell.api.pset.add_pset(self.file, elements[0], "Foo")
        elements[1].HasPropertySets = (pset,)
        elements[2].HasPropertySets = (pset,)

        new_psets = ifcopenshell.api.pset.unshare_pset(self.file, elements[:2], pset)
        assert isinstance(new_psets, list)
        assert len(new_psets) == 2

        assert len(psets := self.file.by_type("IfcPropertySet")) == 3
        assert len(self.file.by_type("IfcRelDefinesByProperties")) == 0

        used_psets: set[ifcopenshell.entity_instance] = set()
        for element in elements:
            element_psets = element.HasPropertySets
            assert len(element_psets) == 1
            used_psets.add(element_psets[0])

        assert used_psets == set(psets)

    def test_unshare_pset_for_all_pset_elements(self):
        elements = [self.file.create_entity("IfcWall") for _ in range(3)]

        pset = ifcopenshell.api.pset.add_pset(self.file, elements[0], "Foo")
        pset_id = pset.id()
        rel = self.file.by_type("IfcRelDefinesByProperties")[0]
        rel.RelatedObjects = elements

        new_psets = ifcopenshell.api.pset.unshare_pset(self.file, elements, pset)
        # Original pset still exists and it's not orphaned.
        pset = self.file.by_id(pset_id)

        assert isinstance(new_psets, list)
        assert len(new_psets) == 2

        assert len(psets := self.file.by_type("IfcPropertySet")) == 3
        assert len(self.file.by_type("IfcRelDefinesByProperties")) == 3

        used_elements = set()
        for pset in psets:
            pset_elements = ifcopenshell.util.element.get_elements_by_pset(pset)
            assert len(pset_elements) == 1
            used_elements.update(pset_elements)

        assert used_elements == set(elements)


class TestUnsharePsetIFC2X3(test.bootstrap.IFC2X3, TestUnsharePset):
    pass
