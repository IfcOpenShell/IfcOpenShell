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
import ifcopenshell.api.classification
import ifcopenshell.util.classification


class TestRemoveReference(test.bootstrap.IFC4):
    def test_removing_a_reference(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        result = ifcopenshell.api.classification.add_classification(self.file, classification="Name")
        reference = ifcopenshell.api.classification.add_reference(
            self.file,
            products=[element, element2],
            identification="X",
            name="Foobar",
            classification=result,
        )
        ifcopenshell.api.classification.remove_reference(self.file, products=[element, element2], reference=reference)
        assert len(ifcopenshell.util.classification.get_references(element)) == 0
        assert len(ifcopenshell.util.classification.get_references(element2)) == 0
        assert len(self.file.by_type("IfcClassificationReference")) == 0

    def test_removing_a_reference_from_a_resource_and_from_a_root(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        element = self.file.createIfcMaterial()
        element2 = self.file.createIfcCostValue()
        element3 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        result = ifcopenshell.api.classification.add_classification(self.file, classification="Name")
        if self.file.schema == "IFC2X3":
            with pytest.raises(TypeError):
                reference = ifcopenshell.api.classification.add_reference(
                    self.file,
                    products=[element, element2, element3],
                    identification="X",
                    name="Foobar",
                    classification=result,
                )
            return
        else:
            reference = ifcopenshell.api.classification.add_reference(
                self.file,
                products=[element, element2, element3],
                identification="X",
                name="Foobar",
                classification=result,
            )

        ifcopenshell.api.classification.remove_reference(
            self.file, products=[element, element2, element3], reference=reference
        )
        assert len(ifcopenshell.util.classification.get_references(element)) == 0
        assert len(ifcopenshell.util.classification.get_references(element2)) == 0
        assert len(ifcopenshell.util.classification.get_references(element3)) == 0
        assert len(self.file.by_type("IfcClassificationReference")) == 0

    def test_retaining_the_reference_if_still_in_use(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element3 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        result = ifcopenshell.api.classification.add_classification(self.file, classification="Name")
        reference = ifcopenshell.api.classification.add_reference(
            self.file,
            products=[element, element2, element3],
            identification="X",
            name="Foobar",
            classification=result,
        )
        assert len(self.file.by_type("IfcClassificationReference")) == 1
        ifcopenshell.api.classification.remove_reference(self.file, products=[element, element2], reference=reference)
        assert len(self.file.by_type("IfcClassificationReference")) == 1
        ifcopenshell.api.classification.remove_reference(self.file, products=[element3], reference=reference)
        assert len(self.file.by_type("IfcClassificationReference")) == 0


class TestRemoveReferenceIFC2X3(test.bootstrap.IFC2X3, TestRemoveReference):
    pass
