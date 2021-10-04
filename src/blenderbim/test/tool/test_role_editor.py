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
from blenderbim.tool.role_editor import RoleEditor as subject


class TestImplementsTool(test.bim.bootstrap.NewFile):
    def test_run(self):
        assert isinstance(subject(), blenderbim.core.tool.RoleEditor)


class TestSetRole(test.bim.bootstrap.NewFile):
    def test_run(self):
        role = ifcopenshell.file().createIfcActorRole()
        subject().set_role(role)
        assert bpy.context.scene.BIMOwnerProperties.active_role_id == role.id()


class TestImportAttributes(test.bim.bootstrap.NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        role = ifc.createIfcActorRole()
        role.Role = "USERDEFINED"
        role.UserDefinedRole = "UserDefinedRole"
        role.Description = "Description"
        subject().set_role(role)
        subject().import_attributes()
        props = bpy.context.scene.BIMOwnerProperties
        assert props.role_attributes.get("Role").enum_value == "USERDEFINED"
        assert props.role_attributes.get("UserDefinedRole").string_value == "UserDefinedRole"
        assert props.role_attributes.get("Description").string_value == "Description"

    def test_importing_twice(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        role = ifc.createIfcActorRole()
        role.Role = "USERDEFINED"
        subject().set_role(role)
        subject().import_attributes()
        role.Role = "ARCHITECT"
        subject().import_attributes()
        props = bpy.context.scene.BIMOwnerProperties
        assert props.role_attributes.get("Role").enum_value == "ARCHITECT"


class TestClearRole(test.bim.bootstrap.NewFile):
    def test_run(self):
        role = ifcopenshell.file().createIfcActorRole()
        subject().set_role(role)
        subject().clear_role()
        assert bpy.context.scene.BIMOwnerProperties.active_role_id == 0


class TestGetRole(test.bim.bootstrap.NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        role = ifc.createIfcActorRole()
        subject().set_role(role)
        assert subject().get_role() == role


class TestExportAttributes(test.bim.bootstrap.NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        role = ifc.createIfcActorRole()
        role.Role = "USERDEFINED"
        role.UserDefinedRole = "UserDefinedRole"
        role.Description = "Description"
        subject().set_role(role)
        subject().import_attributes()
        assert subject().export_attributes() == {
            "Role": "USERDEFINED",
            "UserDefinedRole": "UserDefinedRole",
            "Description": "Description",
        }
