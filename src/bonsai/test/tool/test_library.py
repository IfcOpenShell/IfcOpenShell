# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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
import bonsai.core.tool
import bonsai.tool as tool
from test.bim.bootstrap import NewFile
from bonsai.tool.library import Library as subject


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.Library)


class TestClearEditingMode(NewFile):
    def test_run(self):
        props = bpy.context.scene.BIMLibraryProperties
        props.editing_mode = "foo"
        subject.clear_editing_mode()
        assert props.editing_mode == ""


class TestExportLibraryAttributes(NewFile):
    def test_run(self):
        TestImportLibraryAttributes().test_run()
        assert subject.export_library_attributes() == {
            "Name": "Name",
            "Version": "Version",
            "VersionDate": "VersionDate",
            "Location": "Location",
            "Description": "Description",
        }


class TestExportReferenceAttributes(NewFile):
    def test_run(self):
        TestImportReferenceAttributes().test_run()
        assert subject.export_reference_attributes() == {
            "Location": "Location",
            "Identification": "Identification",
            "Name": "Name",
            "Description": "Description",
            "Language": "Language",
        }


class TestGetActiveLibrary(NewFile):
    def test_run(self):
        TestSetActiveLibrary().test_run()
        assert subject.get_active_library().is_a("IfcLibraryInformation")


class TestGetActiveReference(NewFile):
    def test_run(self):
        TestSetActiveReference().test_run()
        assert subject.get_active_reference().is_a("IfcLibraryReference")


class TestImportLibraryAttributes(NewFile):
    def test_run(self):
        tool.Ifc.set(ifc := ifcopenshell.file())
        library = ifc.createIfcLibraryInformation("Name", "Version", None, "VersionDate", "Location", "Description")
        subject.import_library_attributes(library)
        props = bpy.context.scene.BIMLibraryProperties
        assert props.library_attributes.get("Name").string_value == "Name"
        assert props.library_attributes.get("Version").string_value == "Version"
        assert props.library_attributes.get("VersionDate").string_value == "VersionDate"
        assert props.library_attributes.get("Location").string_value == "Location"
        assert props.library_attributes.get("Description").string_value == "Description"


class TestImportReferenceAttributes(NewFile):
    def test_run(self):
        tool.Ifc.set(ifc := ifcopenshell.file())
        reference = ifc.createIfcLibraryReference("Location", "Identification", "Name", "Description", "Language")
        subject.import_reference_attributes(reference)
        props = bpy.context.scene.BIMLibraryProperties
        assert props.reference_attributes.get("Location").string_value == "Location"
        assert props.reference_attributes.get("Identification").string_value == "Identification"
        assert props.reference_attributes.get("Name").string_value == "Name"
        assert props.reference_attributes.get("Description").string_value == "Description"
        assert props.reference_attributes.get("Language").string_value == "Language"


class TestImportReferences(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        library = ifc.createIfcLibraryInformation()
        reference = ifc.createIfcLibraryReference(Name="Reference", ReferencedLibrary=library)
        subject.import_references(library)
        props = bpy.context.scene.BIMLibraryProperties
        assert props.references[0].ifc_definition_id == reference.id()
        assert props.references[0].name == "Reference"


class TestSetActiveLibrary(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        library = ifc.createIfcLibraryInformation()
        subject.set_active_library(library)
        assert bpy.context.scene.BIMLibraryProperties.active_library_id == library.id()


class TestSetActiveReference(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        reference = ifc.createIfcLibraryReference()
        subject.set_active_reference(reference)
        assert bpy.context.scene.BIMLibraryProperties.active_reference_id == reference.id()


class TestSetEditingMode(NewFile):
    def test_run(self):
        subject.set_editing_mode("FOO")
        assert bpy.context.scene.BIMLibraryProperties.editing_mode == "FOO"
