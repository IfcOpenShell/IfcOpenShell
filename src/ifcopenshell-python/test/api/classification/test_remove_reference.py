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

import test.bootstrap
import ifcopenshell.api
import ifcopenshell.util.classification


class TestRemoveReference(test.bootstrap.IFC4):
    def test_removing_a_reference(self):
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        result = ifcopenshell.api.run("classification.add_classification", self.file, classification="Name")
        reference = ifcopenshell.api.run(
            "classification.add_reference",
            self.file,
            product=element,
            identification="X",
            name="Foobar",
            classification=result,
        )
        ifcopenshell.api.run("classification.remove_reference", self.file, product=element, reference=reference)
        assert len(ifcopenshell.util.classification.get_references(element)) == 0
        assert len(self.file.by_type("IfcClassificationReference")) == 0

    def test_removing_a_reference_from_a_resource(self):
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        element = self.file.createIfcMaterial()
        result = ifcopenshell.api.run("classification.add_classification", self.file, classification="Name")
        reference = ifcopenshell.api.run(
            "classification.add_reference",
            self.file,
            product=element,
            identification="X",
            name="Foobar",
            classification=result,
        )
        ifcopenshell.api.run("classification.remove_reference", self.file, product=element, reference=reference)
        assert len(ifcopenshell.util.classification.get_references(element)) == 0
        assert len(self.file.by_type("IfcClassificationReference")) == 0

    def test_retaining_the_reference_if_still_in_use(self):
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        element = self.file.createIfcMaterial()
        element2 = self.file.createIfcMaterial()
        result = ifcopenshell.api.run("classification.add_classification", self.file, classification="Name")
        reference = ifcopenshell.api.run(
            "classification.add_reference",
            self.file,
            product=element,
            identification="X",
            name="Foobar",
            classification=result,
        )
        reference2 = ifcopenshell.api.run(
            "classification.add_reference",
            self.file,
            product=element2,
            identification="X",
            name="Foobar",
            classification=result,
        )
        assert len(self.file.by_type("IfcClassificationReference")) == 1
        ifcopenshell.api.run("classification.remove_reference", self.file, product=element, reference=reference)
        assert len(self.file.by_type("IfcClassificationReference")) == 1
        ifcopenshell.api.run("classification.remove_reference", self.file, product=element2, reference=reference2)
        assert len(self.file.by_type("IfcClassificationReference")) == 0
