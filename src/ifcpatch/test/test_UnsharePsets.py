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

import ifcpatch
import ifcopenshell
import ifcopenshell.api.pset
import ifcopenshell.geom
import ifcopenshell.util.element
import test.bootstrap


class TestUnsharePsets(test.bootstrap.IFC4):
    def test_unshare_all_psets(self):
        elements = [self.file.create_entity("IfcWall") for _ in range(3)]

        ifcopenshell.api.pset.add_pset(self.file, elements[0], "Foo")
        rel = self.file.by_type("IfcRelDefinesByProperties")[0]
        rel.RelatedObjects = elements

        ifcpatch.execute({"file": self.file, "recipe": "UnsharePsets"})
        assert len(psets := self.file.by_type("IfcPropertySet")) == 3
        assert len(self.file.by_type("IfcRelDefinesByProperties")) == 3

        used_elements = set()
        for pset in psets:
            pset_elements = ifcopenshell.util.element.get_elements_by_pset(pset)
            assert len(pset_elements) == 1
            used_elements.update(pset_elements)

        assert used_elements == set(elements)

    def test_unshare_all_psets_include_types(self):
        elements = [self.file.create_entity("IfcWallType") for _ in range(3)]

        pset = ifcopenshell.api.pset.add_pset(self.file, elements[0], "Foo")
        elements[1].HasPropertySets = (pset,)
        elements[2].HasPropertySets = (pset,)

        ifcpatch.execute({"file": self.file, "recipe": "UnsharePsets"})
        assert len(psets := self.file.by_type("IfcPropertySet")) == 3
        assert len(self.file.by_type("IfcRelDefinesByProperties")) == 0

        used_psets: set[ifcopenshell.entity_instance] = set()
        for element in elements:
            element_psets = element.HasPropertySets
            assert len(element_psets) == 1
            used_psets.add(element_psets[0])

        assert used_psets == set(psets)

    def test_unshare_psets_for_elements_from_query(self):
        shared_pset_elements = [self.file.create_entity("IfcSlab") for _ in range(3)]
        shared_pset = ifcopenshell.api.pset.add_pset(self.file, shared_pset_elements[0], "Foo")
        rel = self.file.by_type("IfcRelDefinesByProperties")[0]
        rel.RelatedObjects = shared_pset_elements

        elements = [self.file.create_entity("IfcWall") for _ in range(3)]
        ifcopenshell.api.pset.add_pset(self.file, elements[0], "Foo")
        rel = self.file.by_type("IfcRelDefinesByProperties")[1]
        rel.RelatedObjects = elements

        ifcpatch.execute({"file": self.file, "recipe": "UnsharePsets", "arguments": ["IfcWall"]})
        assert len(psets := self.file.by_type("IfcPropertySet")) == 4
        assert len(self.file.by_type("IfcRelDefinesByProperties")) == 4

        psets.remove(shared_pset)
        used_elements = set()
        for pset in psets:
            pset_elements = ifcopenshell.util.element.get_elements_by_pset(pset)
            assert len(pset_elements) == 1
            used_elements.update(pset_elements)

        assert used_elements == set(elements)
        # Leave shared pset untouched as it's not part of the provided query.
        assert ifcopenshell.util.element.get_elements_by_pset(shared_pset) == set(shared_pset_elements)


class TestUnsharePsetsIFC2X3(test.bootstrap.IFC2X3, TestUnsharePsets):
    pass
