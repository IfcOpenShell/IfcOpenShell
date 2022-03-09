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

import bpy
import ifcopenshell
import blenderbim.core.tool
import blenderbim.tool as tool
from test.bim.bootstrap import NewFile
from blenderbim.tool.document import Document as subject


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), blenderbim.core.tool.Document)


class TestDisableDocumentAssignmentUI(NewFile):
    def test_run(self):
        obj = bpy.data.objects.new("Object", None)
        obj.BIMObjectDocumentProperties.is_adding = "foo"
        subject.disable_document_assignment_ui(obj)
        assert obj.BIMObjectDocumentProperties.is_adding == ""


class TestDisableEditingDocument(NewFile):
    def test_run(self):
        bpy.context.scene.BIMDocumentProperties.active_document_id = 1
        subject.disable_editing_document()
        assert bpy.context.scene.BIMDocumentProperties.active_document_id == 0


class TestDisableEditingUI(NewFile):
    def test_run(self):
        bpy.context.scene.BIMDocumentProperties.is_editing = "is_editing"
        subject.disable_editing_ui()
        assert bpy.context.scene.BIMDocumentProperties.is_editing == ""


class TestEnableDocumentAssignmentUI(NewFile):
    def test_run(self):
        obj = bpy.data.objects.new("Object", None)
        obj.BIMObjectDocumentProperties.is_adding = ""
        subject.enable_document_assignment_ui(obj)
        assert obj.BIMObjectDocumentProperties.is_adding == "IfcDocumentReference"


class TestEnableInformationEditingUI(NewFile):
    def test_run(self):
        bpy.context.scene.BIMDocumentProperties.is_editing = ""
        subject.enable_information_editing_ui()
        assert bpy.context.scene.BIMDocumentProperties.is_editing == "information"


class TestEnableReferenceEditingUI(NewFile):
    def test_run(self):
        bpy.context.scene.BIMDocumentProperties.is_editing = ""
        subject.enable_reference_editing_ui()
        assert bpy.context.scene.BIMDocumentProperties.is_editing == "reference"


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


class TestImportInformation(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        document = ifc.createIfcDocumentInformation()
        subject.import_information()
        props = bpy.context.scene.BIMDocumentProperties
        assert len(props.documents) == 1
        assert props.documents[0].ifc_definition_id == document.id()
        assert props.documents[0].name == "Unnamed"
        assert props.documents[0].identification == "*"


class TestImportReference(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        document = ifc.createIfcDocumentReference()
        subject.import_references()
        props = bpy.context.scene.BIMDocumentProperties
        assert len(props.documents) == 1
        assert props.documents[0].ifc_definition_id == document.id()
        assert props.documents[0].name == "Unnamed"
        assert props.documents[0].identification == "*"


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
        assert bpy.context.scene.BIMDocumentProperties.active_document_id == document.id()
