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

import bpy
import ifcopenshell
import ifcopenshell.api
import bonsai.core.tool
import bonsai.tool as tool
from test.bim.bootstrap import NewFile
from bonsai.tool.document import Document as subject


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.Document)


class TestAddBreadcrumb(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        document = ifc.createIfcDocumentInformation()
        subject.add_breadcrumb(document)
        props = bpy.context.scene.BIMDocumentProperties
        assert props.breadcrumbs[0].name == str(document.id())


class TestClearBreadcrumbs(NewFile):
    def test_run(self):
        props = bpy.context.scene.BIMDocumentProperties
        props.breadcrumbs.add()
        subject.clear_breadcrumbs()
        assert len(props.breadcrumbs) == 0


class TestClearDocumentTree(NewFile):
    def test_run(self):
        props = bpy.context.scene.BIMDocumentProperties
        new = props.documents.add()
        subject.clear_document_tree()
        assert len(props.documents) == 0


class TestDisableEditingDocument(NewFile):
    def test_run(self):
        bpy.context.scene.BIMDocumentProperties.active_document_id = 1
        subject.disable_editing_document()
        assert bpy.context.scene.BIMDocumentProperties.active_document_id == 0


class TestDisableEditingUI(NewFile):
    def test_run(self):
        bpy.context.scene.BIMDocumentProperties.is_editing = True
        subject.disable_editing_ui()
        assert bpy.context.scene.BIMDocumentProperties.is_editing == False


class TestEnableEditingUI(NewFile):
    def test_run(self):
        bpy.context.scene.BIMDocumentProperties.is_editing = False
        subject.enable_editing_ui()
        assert bpy.context.scene.BIMDocumentProperties.is_editing == True


class TestExportDocumentAttributes(NewFile):
    def test_exporting_information(self):
        TestImportDocumentAttributes().test_importing_information()
        assert subject.export_document_attributes() == {
            "Identification": "Identification",
            "Name": "Name",
            "Description": "Description",
            "Location": "Location",
            "Purpose": "Purpose",
            "IntendedUse": "IntendedUse",
            "Scope": "Scope",
            "Revision": "Revision",
            "CreationTime": "CreationTime",
            "LastRevisionTime": "LastRevisionTime",
            "ElectronicFormat": "ElectronicFormat",
            "ValidFrom": "ValidFrom",
            "ValidUntil": "ValidUntil",
            "Confidentiality": "CONFIDENTIAL",
            "Status": "DRAFT",
        }


class TestGetActiveBreadcrumb(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        document = ifc.createIfcDocumentInformation()
        subject.add_breadcrumb(document)
        assert subject.get_active_breadcrumb() == document


class TestImportDocumentAttributes(NewFile):
    def test_importing_information(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        document = ifc.createIfcDocumentInformation()
        document.Identification = "Identification"
        document.Name = "Name"
        document.Description = "Description"
        document.Location = "Location"
        document.Purpose = "Purpose"
        document.IntendedUse = "IntendedUse"
        document.Scope = "Scope"
        document.Revision = "Revision"
        document.CreationTime = "CreationTime"
        document.LastRevisionTime = "LastRevisionTime"
        document.ElectronicFormat = "ElectronicFormat"
        document.ValidFrom = "ValidFrom"
        document.ValidUntil = "ValidUntil"
        document.Confidentiality = "CONFIDENTIAL"
        document.Status = "DRAFT"
        subject().import_document_attributes(document)
        props = bpy.context.scene.BIMDocumentProperties
        assert props.document_attributes.get("Identification").string_value == "Identification"
        assert props.document_attributes.get("Name").string_value == "Name"
        assert props.document_attributes.get("Description").string_value == "Description"
        assert props.document_attributes.get("Location").string_value == "Location"
        assert props.document_attributes.get("Purpose").string_value == "Purpose"
        assert props.document_attributes.get("IntendedUse").string_value == "IntendedUse"
        assert props.document_attributes.get("Scope").string_value == "Scope"
        assert props.document_attributes.get("Revision").string_value == "Revision"
        assert props.document_attributes.get("CreationTime").string_value == "CreationTime"
        assert props.document_attributes.get("LastRevisionTime").string_value == "LastRevisionTime"
        assert props.document_attributes.get("ElectronicFormat").string_value == "ElectronicFormat"
        assert props.document_attributes.get("ValidFrom").string_value == "ValidFrom"
        assert props.document_attributes.get("ValidUntil").string_value == "ValidUntil"
        assert props.document_attributes.get("Confidentiality").enum_value == "CONFIDENTIAL"
        assert props.document_attributes.get("Status").enum_value == "DRAFT"

    def test_importing_reference(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        document = ifc.createIfcDocumentInformation()
        document.Location = "Location"
        document.Identification = "Identification"
        document.Name = "Name"
        document.Description = "Description"
        subject().import_document_attributes(document)
        props = bpy.context.scene.BIMDocumentProperties
        assert props.document_attributes.get("Location").string_value == "Location"
        assert props.document_attributes.get("Identification").string_value == "Identification"
        assert props.document_attributes.get("Name").string_value == "Name"
        assert props.document_attributes.get("Description").string_value == "Description"


class TestImportProjectDocuments(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        ifc.createIfcProject()
        document = ifcopenshell.api.run("document.add_information", ifc)
        subject.import_project_documents()
        props = bpy.context.scene.BIMDocumentProperties
        assert len(props.documents) == 1
        assert props.documents[0].ifc_definition_id == document.id()
        assert props.documents[0].name == "Unnamed"
        assert props.documents[0].identification == "X"
        assert props.documents[0].is_information is True


class TestImportReferences(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        ifc.createIfcProject()
        document = ifcopenshell.api.run("document.add_information", ifc)
        reference = ifcopenshell.api.run("document.add_reference", ifc, information=document)
        subject.import_references(document)
        props = bpy.context.scene.BIMDocumentProperties
        assert len(props.documents) == 1
        assert props.documents[0].ifc_definition_id == reference.id()
        assert props.documents[0].name == "Unnamed"
        assert props.documents[0].identification == "X"
        assert props.documents[0].is_information is False


class TestImportSubdocuments(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        ifc.createIfcProject()
        document = ifcopenshell.api.run("document.add_information", ifc)
        subdocument = ifcopenshell.api.run("document.add_information", ifc, parent=document)
        subject.import_subdocuments(document)
        props = bpy.context.scene.BIMDocumentProperties
        assert len(props.documents) == 1
        assert props.documents[0].ifc_definition_id == subdocument.id()
        assert props.documents[0].name == "Unnamed"
        assert props.documents[0].identification == "X"
        assert props.documents[0].is_information is True


class TestIsDocumentInformation(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        information = ifc.createIfcDocumentInformation()
        reference = ifc.createIfcDocumentReference()
        assert subject.is_document_information(information) is True
        assert subject.is_document_information(reference) is False


class TestRemoveLatestBreadcrumb(NewFile):
    def test_run(self):
        props = bpy.context.scene.BIMDocumentProperties
        props.breadcrumbs.add()
        props.breadcrumbs.add()
        subject.remove_latest_breadcrumb()
        assert len(props.breadcrumbs) == 1


class TestSetActiveDocument(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        document = ifc.createIfcDocumentInformation()
        subject.set_active_document(document)
        assert bpy.context.scene.BIMDocumentProperties.active_document_id == document.id()
