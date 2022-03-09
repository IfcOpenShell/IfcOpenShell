# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.


import blenderbim.core.document as subject
from test.core.bootstrap import ifc, document


class TestLoadInformation:
    def test_run(self, document):
        document.import_information().should_be_called()
        document.enable_information_editing_ui().should_be_called()
        document.disable_editing_document().should_be_called()
        subject.load_information(document)


class TestLoadReferences:
    def test_run(self, document):
        document.import_references().should_be_called()
        document.enable_reference_editing_ui().should_be_called()
        document.disable_editing_document().should_be_called()
        subject.load_references(document)


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
    def test_run(self, ifc, document):
        ifc.run("document.add_information").should_be_called().will_return("information")
        document.import_information().should_be_called()
        document.import_document_attributes("information").should_be_called()
        document.set_active_document("information").should_be_called()
        subject.add_information(ifc, document)


class TestAddReference:
    def test_run(self, ifc, document):
        ifc.run("document.add_reference").should_be_called().will_return("reference")
        document.import_references().should_be_called()
        document.import_document_attributes("reference").should_be_called()
        document.set_active_document("reference").should_be_called()
        subject.add_reference(ifc, document)


class TestEditInformation:
    def test_run(self, ifc, document):
        document.export_document_attributes().should_be_called().will_return("attributes")
        ifc.run("document.edit_information", information="information", attributes="attributes").should_be_called()
        document.disable_editing_document().should_be_called()
        document.import_information().should_be_called()
        subject.edit_information(ifc, document, information="information")


class TestEditInformation:
    def test_run(self, ifc, document):
        document.export_document_attributes().should_be_called().will_return("attributes")
        ifc.run("document.edit_reference", reference="reference", attributes="attributes").should_be_called()
        document.disable_editing_document().should_be_called()
        document.import_references().should_be_called()
        subject.edit_reference(ifc, document, reference="reference")


class TestRemoveDocument:
    def test_remove_information(self, ifc, document):
        document.is_document_information("document").should_be_called().will_return(True)
        ifc.run("document.remove_document", document="document").should_be_called()
        document.import_information().should_be_called()
        document.disable_editing_document().should_be_called()
        subject.remove_document(ifc, document, document="document")

    def test_remove_reference(self, ifc, document):
        document.is_document_information("document").should_be_called().will_return(False)
        ifc.run("document.remove_document", document="document").should_be_called()
        document.import_references().should_be_called()
        document.disable_editing_document().should_be_called()
        subject.remove_document(ifc, document, document="document")


class TestEnableAssigningDocument:
    def test_run(self, document):
        document.import_references().should_be_called()
        document.enable_reference_editing_ui().should_be_called()
        document.disable_editing_document().should_be_called()
        document.enable_document_assignment_ui("obj").should_be_called()
        subject.enable_assigning_document(document, obj="obj")


class TestDisableAssigningDocument:
    def test_run(self, document):
        document.disable_document_assignment_ui("obj").should_be_called()
        subject.disable_assigning_document(document, obj="obj")


class TestAssignDocument:
    def test_run(self, ifc):
        ifc.run("document.assign_document", product="product", document="document").should_be_called()
        subject.assign_document(ifc, product="product", document="document")


class TestUnassignDocument:
    def test_run(self, ifc):
        ifc.run("document.unassign_document", product="product", document="document").should_be_called()
        subject.unassign_document(ifc, product="product", document="document")
