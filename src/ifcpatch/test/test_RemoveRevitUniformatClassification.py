# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Petru Conduraru <petru@bimvoice.com>
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
#
# Written with the assistance of an AI coding tool.


import ifcopenshell
import ifcopenshell.api.root

import ifcpatch
import test.bootstrap


class TestRemoveRevitUniformatClassification(test.bootstrap.IFC4):
    def add_reference(
        self, identification: str, name: str, source: ifcopenshell.entity_instance
    ) -> ifcopenshell.entity_instance:
        attributes = {"Location": "", "Name": name, "ReferencedSource": source}
        if self.file.schema == "IFC2X3":
            attributes["ItemReference"] = identification
        else:
            attributes["Identification"] = identification
        return self.file.create_entity("IfcClassificationReference", **attributes)

    def associate(self, reference: ifcopenshell.entity_instance, element: ifcopenshell.entity_instance) -> None:
        self.file.create_entity(
            "IfcRelAssociatesClassification",
            GlobalId=ifcopenshell.guid.new(),
            RelatedObjects=[element],
            RelatingClassification=reference,
        )

    def test_run(self):
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        uniformat = self.file.create_entity("IfcClassification", Source="Uniformat", Edition="1998", Name="Uniformat")
        self.associate(self.add_reference("B2010", "Exterior Walls", uniformat), wall)

        ifcpatch.execute({"file": self.file, "recipe": "RemoveRevitUniformatClassification", "arguments": []})

        assert not self.file.by_type("IfcClassification")
        assert not self.file.by_type("IfcClassificationReference")
        assert not self.file.by_type("IfcRelAssociatesClassification")

    def test_other_classifications_are_kept(self):
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        uniformat = self.file.create_entity("IfcClassification", Source="Uniformat", Edition="1998", Name="Uniformat")
        self.associate(self.add_reference("B2010", "Exterior Walls", uniformat), wall)
        omniclass = self.file.create_entity("IfcClassification", Source="Omniclass", Edition="2012", Name="Omniclass")
        self.associate(self.add_reference("23-13", "Walls", omniclass), wall)

        ifcpatch.execute({"file": self.file, "recipe": "RemoveRevitUniformatClassification", "arguments": []})

        assert [c.Name for c in self.file.by_type("IfcClassification")] == ["Omniclass"]
        assert len(self.file.by_type("IfcClassificationReference")) == 1
        assert len(self.file.by_type("IfcRelAssociatesClassification")) == 1

    def test_nested_references_are_removed(self):
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        uniformat = self.file.create_entity("IfcClassification", Source="Uniformat", Edition="1998", Name="Uniformat")
        parent = self.add_reference("B2010", "Exterior Walls", uniformat)
        self.associate(self.add_reference("B2010.10", "Exterior Wall Construction", parent), wall)

        ifcpatch.execute({"file": self.file, "recipe": "RemoveRevitUniformatClassification", "arguments": []})

        assert not self.file.by_type("IfcClassification")
        assert not self.file.by_type("IfcClassificationReference")
        assert not self.file.by_type("IfcRelAssociatesClassification")


class TestRemoveRevitUniformatClassificationIFC2X3(test.bootstrap.IFC2X3, TestRemoveRevitUniformatClassification):
    def test_classification_items_are_removed(self):
        uniformat = self.file.create_entity("IfcClassification", Source="Uniformat", Edition="1998", Name="Uniformat")
        facet = self.file.create_entity("IfcClassificationNotationFacet", NotationValue="B2010")
        notation = self.file.create_entity("IfcClassificationNotation", NotationFacets=[facet])
        self.file.create_entity("IfcClassificationItem", Notation=notation, ItemOf=uniformat, Title="Exterior Walls")

        ifcpatch.execute({"file": self.file, "recipe": "RemoveRevitUniformatClassification", "arguments": []})

        assert not self.file.by_type("IfcClassification")
        assert not self.file.by_type("IfcClassificationItem")
