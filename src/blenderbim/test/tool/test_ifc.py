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
from blenderbim.tool.ifc import Ifc as subject


class TestImplementsTool(test.bim.bootstrap.NewFile):
    def test_run(self):
        assert isinstance(subject(), blenderbim.core.tool.Ifc)


class TestSet(test.bim.bootstrap.NewFile):
    def test_setting_an_ifc_data(self):
        ifc = ifcopenshell.file()
        subject.set(ifc)
        assert subject.get() == ifc


class TestGet(test.bim.bootstrap.NewFile):
    def test_getting_an_ifc_dataset_from_a_ifc_spf_filepath(self):
        assert subject.get() is None
        bpy.context.scene.BIMProperties.ifc_file = "test/files/basic.ifc"
        result = subject.get()
        assert isinstance(result, ifcopenshell.file)

    def test_getting_the_active_ifc_dataset_regardless_of_ifc_path(self):
        bpy.context.scene.BIMProperties.ifc_file = "test/files/basic.ifc"
        ifc = ifcopenshell.file()
        subject.set(ifc)
        assert subject.get() == ifc


class TestRun(test.bim.bootstrap.NewFile):
    def test_running_a_command_on_the_active_ifc_dataset(self):
        ifc = ifcopenshell.file()
        subject.set(ifc)
        wall = subject.run("root.create_entity", ifc_class="IfcWall")
        assert subject.get().by_type("IfcWall")[0] == wall


class TestGetSchema(test.bim.bootstrap.NewFile):
    def test_getting_the_schema_version_identifier(self):
        ifc = ifcopenshell.file(schema="IFC4")
        subject.set(ifc)
        assert subject.get_schema() == "IFC4"


class TestGetEntity(test.bim.bootstrap.NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        subject.set(ifc)
        obj = bpy.data.objects.new("Object", None)
        element = ifc.createIfcWall()
        obj.BIMObjectProperties.ifc_definition_id = element.id()
        assert subject.get_entity(obj) == element

    def test_attempting_to_get_an_unlinked_object(self):
        obj = bpy.data.objects.new("Object", None)
        assert subject.get_entity(obj) is None

    def test_attempting_without_a_file(self):
        obj = bpy.data.objects.new("Object", None)
        obj.BIMObjectProperties.ifc_definition_id = 1
        assert subject.get_entity(obj) is None

    def test_attempting_to_get_an_invalidly_linked_object(self):
        ifc = ifcopenshell.file()
        subject.set(ifc)
        obj = bpy.data.objects.new("Object", None)
        obj.BIMObjectProperties.ifc_definition_id = 1
        assert subject.get_entity(obj) is None


class TestGetObject(test.bim.bootstrap.NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        subject.set(ifc)
        element = ifc.createIfcWall()
        obj = bpy.data.objects.new("Object", None)
        subject.link(element, obj)
        assert subject.get_object(element) == obj


class TestLink(test.bim.bootstrap.NewFile):
    def test_link_an_object(self):
        ifc = ifcopenshell.file()
        subject.set(ifc)
        element = ifc.createIfcWall()
        obj = bpy.data.objects.new("Object", None)
        subject.link(element, obj)
        assert subject.get_entity(obj) == element
        assert subject.get_object(element) == obj

    def test_link_a_material(self):
        ifc = ifcopenshell.file()
        subject.set(ifc)
        element = ifc.createIfcMaterial()
        obj = bpy.data.materials.new("Material")
        subject.link(element, obj)
        assert subject.get_entity(obj) == element
        assert subject.get_object(element) == obj


class TestUnlink(test.bim.bootstrap.NewFile):
    def test_unlink_an_object(self):
        ifc = ifcopenshell.file()
        subject.set(ifc)
        element = ifc.createIfcWall()
        obj = bpy.data.objects.new("Object", None)
        subject.link(element, obj)
        subject.unlink(element, obj)
        assert subject.get_entity(obj) is None
        assert subject.get_object(element) is None

    def test_unlink_a_material(self):
        ifc = ifcopenshell.file()
        subject.set(ifc)
        element = ifc.createIfcMaterial()
        obj = bpy.data.materials.new("Material")
        subject.link(element, obj)
        subject.unlink(element, obj)
        assert subject.get_entity(obj) is None
        assert subject.get_object(element) is None

    def test_unlinking_using_an_object(self):
        ifc = ifcopenshell.file()
        subject.set(ifc)
        element = ifc.createIfcWall()
        obj = bpy.data.objects.new("Object", None)
        subject.link(element, obj)
        subject.unlink(obj=obj)
        assert subject.get_entity(obj) is None
        assert subject.get_object(element) is None

    def test_unlinking_using_an_element(self):
        ifc = ifcopenshell.file()
        subject.set(ifc)
        element = ifc.createIfcWall()
        obj = bpy.data.objects.new("Object", None)
        subject.link(element, obj)
        subject.unlink(element=element)
        assert subject.get_entity(obj) is None
        assert subject.get_object(element) is None
