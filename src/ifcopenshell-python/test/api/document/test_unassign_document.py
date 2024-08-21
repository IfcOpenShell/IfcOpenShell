# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell.api.root
import ifcopenshell.api.document
import ifcopenshell.util.element


class TestUnassignDocument(test.bootstrap.IFC4):
    def test_unassigning_a_document(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        reference = ifcopenshell.api.document.add_reference(self.file, information=None)
        ifcopenshell.api.document.assign_document(self.file, products=[element], document=reference)
        ifcopenshell.api.document.unassign_document(self.file, products=[element], document=reference)
        assert not element.HasAssociations
        assert not len(self.file.by_type("IfcRelAssociatesDocument"))

    def test_unassigning_a_document_used_by_multiple_entities(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element3 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        reference = ifcopenshell.api.document.add_reference(self.file, information=None)
        ifcopenshell.api.document.assign_document(self.file, products=[element, element2, element3], document=reference)
        ifcopenshell.api.document.unassign_document(self.file, products=[element, element2], document=reference)
        assert ifcopenshell.util.element.get_referenced_elements(reference) == {element3}


class TestUnassignDocumentIFC2X3(test.bootstrap.IFC2X3, TestUnassignDocument):
    pass
