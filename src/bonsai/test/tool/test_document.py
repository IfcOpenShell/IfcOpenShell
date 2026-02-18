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

import json

import bpy
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.api.document

import bonsai.core.tool
import bonsai.tool as tool
from bonsai.tool.document import Document as subject
from test.bim.bootstrap import NewFile


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.Document)


class TestClearDocumentTree(NewFile):
    def test_run(self):
        props = tool.Document.get_document_props()
        new = props.documents.add()
        subject.clear_document_tree()
        assert len(props.documents) == 0


class TestDisableEditingDocument(NewFile):
    def test_run(self):
        props = tool.Document.get_document_props()
        props.active_document_id = 1
        subject.disable_editing_document()
        assert props.active_document_id == 0


class TestDisableEditingUI(NewFile):
    def test_run(self):
        props = tool.Document.get_document_props()
        props.is_editing = True
        subject.disable_editing_ui()
        assert props.is_editing == False


class TestEnableEditingUI(NewFile):
    def test_run(self):
        props = tool.Document.get_document_props()
        props.is_editing = False
        subject.enable_editing_ui()
        assert props.is_editing == True


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
        props = tool.Document.get_document_props()
        assert props.document_attributes["Identification"].string_value == "Identification"
        assert props.document_attributes["Name"].string_value == "Name"
        assert props.document_attributes["Description"].string_value == "Description"
        assert props.document_attributes["Location"].string_value == "Location"
        assert props.document_attributes["Purpose"].string_value == "Purpose"
        assert props.document_attributes["IntendedUse"].string_value == "IntendedUse"
        assert props.document_attributes["Scope"].string_value == "Scope"
        assert props.document_attributes["Revision"].string_value == "Revision"
        assert props.document_attributes["CreationTime"].string_value == "CreationTime"
        assert props.document_attributes["LastRevisionTime"].string_value == "LastRevisionTime"
        assert props.document_attributes["ElectronicFormat"].string_value == "ElectronicFormat"
        assert props.document_attributes["ValidFrom"].string_value == "ValidFrom"
        assert props.document_attributes["ValidUntil"].string_value == "ValidUntil"
        assert props.document_attributes["Confidentiality"].enum_value == "CONFIDENTIAL"
        assert props.document_attributes["Status"].enum_value == "DRAFT"

    def test_importing_reference(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        document = ifc.createIfcDocumentInformation()
        document.Location = "Location"
        document.Identification = "Identification"
        document.Name = "Name"
        document.Description = "Description"
        subject().import_document_attributes(document)
        props = tool.Document.get_document_props()
        assert props.document_attributes["Location"].string_value == "Location"
        assert props.document_attributes["Identification"].string_value == "Identification"
        assert props.document_attributes["Name"].string_value == "Name"
        assert props.document_attributes["Description"].string_value == "Description"


class TestImportProjectDocumentsExpanded(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        project = ifc.createIfcProject()
        document = ifcopenshell.api.document.add_information(ifc)
        reference = ifcopenshell.api.document.add_reference(ifc, information=document)

        props = tool.Document.get_document_props()
        expanded_docs = [document.id()]  # Mark document as expanded
        props.json_string = json.dumps(expanded_docs)

        subject.import_project_documents()
        props = tool.Document.get_document_props()

        # Should have project root + document + reference = 3 total
        assert len(props.documents) == 3

        assert props.documents[0].ifc_definition_id == -project.id()
        assert props.documents[0].document_type == "PROJECT"

        doc_info = next((d for d in props.documents if d.ifc_definition_id == document.id()), None)
        assert doc_info is not None
        assert doc_info.document_type == "INFORMATION"

        doc_ref = next((d for d in props.documents if d.ifc_definition_id == reference.id()), None)
        assert doc_ref is not None
        assert doc_ref.location == ""
        assert doc_ref.identification == "X"
        assert doc_ref.document_type == "REFERENCE"


class TestImportProjectDocumentsCollapsed(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        project = ifc.createIfcProject()
        document = ifcopenshell.api.document.add_information(ifc)
        reference = ifcopenshell.api.document.add_reference(ifc, information=document)

        props = tool.Document.get_document_props()
        props.json_string = json.dumps([])  # Empty expanded list

        subject.import_project_documents()
        props = tool.Document.get_document_props()

        # Should have project root + document = 2 total (reference not imported because parent is collapsed)
        assert len(props.documents) == 2

        assert props.documents[0].ifc_definition_id == -project.id()
        assert props.documents[0].document_type == "PROJECT"

        doc_info = next((d for d in props.documents if d.ifc_definition_id == document.id()), None)
        assert doc_info is not None
        assert doc_info.document_type == "INFORMATION"

        doc_ref = next((d for d in props.documents if d.ifc_definition_id == reference.id()), None)
        assert doc_ref is None


class TestIsDocumentInformation(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        information = ifc.createIfcDocumentInformation()
        reference = ifc.createIfcDocumentReference()
        assert subject.is_document_information(information) is True
        assert subject.is_document_information(reference) is False


class TestSetActiveDocument(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        document = ifc.createIfcDocumentInformation()
        subject.set_active_document(document)
        props = tool.Document.get_document_props()
        assert props.active_document_id == document.id()
