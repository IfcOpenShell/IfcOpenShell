# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.


import bonsai.core.document as subject
from test.core.bootstrap import ifc, document


class TestLoadProjectDocuments:
    def test_run(self, document):
        document.clear_document_tree().should_be_called()
        document.import_project_documents().should_be_called()
        document.clear_breadcrumbs().should_be_called()
        document.enable_editing_ui().should_be_called()
        subject.load_project_documents(document)


class TestLoadDocument:
    def test_run(self, document):
        document.clear_document_tree().should_be_called()
        document.import_subdocuments("document").should_be_called()
        document.import_references("document").should_be_called()
        document.disable_editing_document().should_be_called()
        document.add_breadcrumb("document").should_be_called()
        subject.load_document(document, document="document")


class TestDisableDocumentEditingUi:
    def test_run(self, document):
        document.disable_editing_ui().should_be_called()
        document.disable_editing_document().should_be_called()
        subject.disable_document_editing_ui(document)


class TestEnableEditingDocument:
    def test_run(self, document):
        document.import_document_attributes("document").should_be_called()
        document.set_active_document("document").should_be_called()
        subject.enable_editing_document(document, document="document")


class TestDisableEditingDocument:
    def test_run(self, document):
        document.disable_editing_document().should_be_called()
        subject.disable_editing_document(document)


class TestAddInformation:
    def test_add_and_reload_tree_at_project_root(self, ifc, document):
        document.clear_document_tree().should_be_called()
        document.get_active_breadcrumb().should_be_called().will_return(None)
        ifc.run("document.add_information", parent=None).should_be_called().will_return("information")
        ifc.run("document.add_reference", information="information").should_be_called()
        document.import_project_documents().should_be_called()
        subject.add_information(ifc, document)

    def test_add_and_reload_tree_at_current_parent(self, ifc, document):
        document.clear_document_tree().should_be_called()
        document.get_active_breadcrumb().should_be_called().will_return("parent")
        ifc.run("document.add_information", parent="parent").should_be_called().will_return("information")
        ifc.run("document.add_reference", information="information").should_be_called()
        document.import_subdocuments("parent").should_be_called()
        document.import_references("parent").should_be_called()
        subject.add_information(ifc, document)


class TestAddReference:
    def test_run(self, ifc, document):
        document.get_active_breadcrumb().should_be_called().will_return("parent")
        ifc.run("document.add_reference", information="parent").should_be_called()
        document.clear_document_tree().should_be_called()
        document.import_subdocuments("parent").should_be_called()
        document.import_references("parent").should_be_called()
        subject.add_reference(ifc, document)


class TestEditDocument:
    def test_edit_information(self, ifc, document):
        document.export_document_attributes().should_be_called().will_return("attributes")
        document.is_document_information("document").should_be_called().will_return(True)
        ifc.run("document.edit_information", information="document", attributes="attributes").should_be_called()
        document.disable_editing_document().should_be_called()
        document.clear_document_tree().should_be_called()
        document.get_active_breadcrumb().should_be_called().will_return(None)
        document.import_project_documents().should_be_called()
        subject.edit_document(ifc, document, document="document")

    def test_edit_reference(self, ifc, document):
        document.export_document_attributes().should_be_called().will_return("attributes")
        document.is_document_information("document").should_be_called().will_return(False)
        ifc.run("document.edit_reference", reference="document", attributes="attributes").should_be_called()
        document.disable_editing_document().should_be_called()
        document.clear_document_tree().should_be_called()
        document.get_active_breadcrumb().should_be_called().will_return("parent")
        document.import_subdocuments("parent").should_be_called()
        document.import_references("parent").should_be_called()
        subject.edit_document(ifc, document, document="document")


class TestRemoveDocument:
    def test_remove_information(self, ifc, document):
        document.clear_document_tree().should_be_called()
        document.is_document_information("document").should_be_called().will_return(True)
        ifc.run("document.remove_information", information="document").should_be_called()
        document.get_active_breadcrumb().should_be_called().will_return(None)
        document.import_project_documents().should_be_called()
        subject.remove_document(ifc, document, document="document")

    def test_remove_reference(self, ifc, document):
        document.clear_document_tree().should_be_called()
        document.is_document_information("document").should_be_called().will_return(False)
        ifc.run("document.remove_reference", reference="document").should_be_called()
        document.get_active_breadcrumb().should_be_called().will_return("parent")
        document.import_subdocuments("parent").should_be_called()
        document.import_references("parent").should_be_called()
        subject.remove_document(ifc, document, document="document")


class TestAssignDocument:
    def test_run(self, ifc):
        ifc.run("document.assign_document", products=["product"], document="document").should_be_called()
        subject.assign_document(ifc, product="product", document="document")


class TestUnassignDocument:
    def test_run(self, ifc):
        ifc.run("document.unassign_document", products=["product"], document="document").should_be_called()
        subject.unassign_document(ifc, product="product", document="document")
