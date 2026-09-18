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

import ifcopenshell.api.document
import ifcopenshell.util.document as subject
import test.bootstrap


class TestGetRevisionHistory(test.bootstrap.IFC4):
    def test_a_document_with_no_history(self):
        self.file.createIfcProject()
        document = ifcopenshell.api.document.add_information(self.file, parent=None)
        assert subject.get_revision_history(document) == []

    def test_a_linear_chain_of_revisions(self):
        self.file.createIfcProject()
        latest = ifcopenshell.api.document.add_information(self.file, parent=None)
        rev_b = ifcopenshell.api.document.add_information(self.file, parent=latest)
        rev_a = ifcopenshell.api.document.add_information(self.file, parent=rev_b)
        assert subject.get_revision_history(latest) == [rev_b, rev_a]
        # An older revision only sees its own, even older, history.
        assert subject.get_revision_history(rev_b) == [rev_a]
        assert subject.get_revision_history(rev_a) == []

    def test_branching_history_is_flattened(self):
        self.file.createIfcProject()
        latest = ifcopenshell.api.document.add_information(self.file, parent=None)
        rev_b1 = ifcopenshell.api.document.add_information(self.file, parent=latest)
        rev_b2 = ifcopenshell.api.document.add_information(self.file, parent=latest)
        rev_a = ifcopenshell.api.document.add_information(self.file, parent=rev_b1)
        results = subject.get_revision_history(latest)
        assert set(results) == {rev_b1, rev_b2, rev_a}
        assert results.index(rev_b1) < results.index(rev_a)

    def test_a_cyclic_relationship_does_not_infinitely_recurse(self):
        self.file.createIfcProject()
        latest = ifcopenshell.api.document.add_information(self.file, parent=None)
        child = ifcopenshell.api.document.add_information(self.file, parent=latest)
        self.file.createIfcDocumentInformationRelationship(RelatingDocument=child, RelatedDocuments=[latest])
        results = subject.get_revision_history(latest)
        assert set(results) == {child, latest}


class TestGetRevisionHistoryIFC2X3(test.bootstrap.IFC2X3, TestGetRevisionHistory):
    pass
