# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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
import test.bim.bootstrap
import blenderbim.core.tool
import blenderbim.tool as tool
from blenderbim.tool.organisation_editor import OrganisationEditor as subject


class TestImplementsTool(test.bim.bootstrap.NewFile):
    def test_run(self):
        assert isinstance(subject(), blenderbim.core.tool.OrganisationEditor)


class TestSetOrganisation(test.bim.bootstrap.NewFile):
    def test_run(self):
        organisation = ifcopenshell.file().createIfcOrganization()
        subject().set_organisation(organisation)
        assert bpy.context.scene.BIMOwnerProperties.active_organisation_id == organisation.id()


class TestImportAttributes(test.bim.bootstrap.NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        organisation = ifc.createIfcOrganization()
        organisation.Identification = "Identification"
        organisation.Name = "Name"
        organisation.Description = "Description"
        subject().set_organisation(organisation)
        subject().import_attributes()
        props = bpy.context.scene.BIMOwnerProperties
        assert props.organisation_attributes.get("Identification").string_value == "Identification"
        assert props.organisation_attributes.get("Name").string_value == "Name"
        assert props.organisation_attributes.get("Description").string_value == "Description"

    def test_overwriting_a_previous_import(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        organisation = ifc.createIfcOrganization()
        organisation.Identification = "Identification"
        organisation.Description = "Description"
        subject().set_organisation(organisation)
        subject().import_attributes()
        organisation.Identification = "Identification2"
        organisation.Description = None
        subject().import_attributes()
        props = bpy.context.scene.BIMOwnerProperties
        assert props.organisation_attributes.get("Identification").string_value == "Identification2"
        assert props.organisation_attributes.get("Description").string_value == ""


class TestClearOrganisation(test.bim.bootstrap.NewFile):
    def test_run(self):
        props = bpy.context.scene.BIMOwnerProperties
        props.active_organisation_id = 1
        subject().clear_organisation()
        assert props.active_organisation_id == 0


class TestExportAttributes(test.bim.bootstrap.NewFile):
    def test_run(self):
        TestImportAttributes().test_run()
        assert subject().export_attributes() == {
            "Identification": "Identification",
            "Name": "Name",
            "Description": "Description",
        }


class TestGetOrganisation(test.bim.bootstrap.NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        organisation = ifc.createIfcOrganization()
        subject().set_organisation(organisation)
        assert subject().get_organisation() == organisation
