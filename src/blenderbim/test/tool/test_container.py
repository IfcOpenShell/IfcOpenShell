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
import blenderbim.core.tool
import blenderbim.tool as tool
from blenderbim.tool.container import Container as subject
from test.bim.bootstrap import NewFile


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), blenderbim.core.tool.Container)


class TestCanContain(NewFile):
    def test_a_spatial_element_can_contain_an_element(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        structure = ifc.createIfcSite()
        structure_obj = bpy.data.objects.new("Object", None)
        tool.Ifc.link(structure, structure_obj)
        element = ifc.createIfcWall()
        element_obj = bpy.data.objects.new("Object", None)
        tool.Ifc.link(element, element_obj)
        assert subject.can_contain(structure_obj, element_obj) is True

    def test_a_spatial_element_can_contain_an_element_ifc2x3(self):
        ifc = ifcopenshell.file(schema="IFC2X3")
        tool.Ifc.set(ifc)
        structure = ifc.createIfcSite()
        structure_obj = bpy.data.objects.new("Object", None)
        tool.Ifc.link(structure, structure_obj)
        element = ifc.createIfcWall()
        element_obj = bpy.data.objects.new("Object", None)
        tool.Ifc.link(element, element_obj)
        assert subject.can_contain(structure_obj, element_obj) is True

    def test_unlinked_elements_cannot_contain_anything(self):
        structure_obj = bpy.data.objects.new("Object", None)
        element_obj = bpy.data.objects.new("Object", None)
        assert subject.can_contain(structure_obj, element_obj) is False

    def test_a_non_spatial_element_cannot_contain_anything(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        structure = ifc.createIfcWall()
        structure_obj = bpy.data.objects.new("Object", None)
        tool.Ifc.link(structure, structure_obj)
        element = ifc.createIfcWall()
        element_obj = bpy.data.objects.new("Object", None)
        tool.Ifc.link(element, element_obj)
        assert subject.can_contain(structure_obj, element_obj) is False

    def test_a_non_element_cannot_be_contained(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        structure = ifc.createIfcSite()
        structure_obj = bpy.data.objects.new("Object", None)
        tool.Ifc.link(structure, structure_obj)
        element = ifc.createIfcTask()
        element_obj = bpy.data.objects.new("Object", None)
        tool.Ifc.link(element, element_obj)
        assert subject.can_contain(structure_obj, element_obj) is False


class TestEnableEditing(NewFile):
    def test_run(self):
        obj = bpy.data.objects.new("Object", None)
        subject.enable_editing(obj)
        assert obj.BIMObjectSpatialProperties.is_editing is True


class TestDisableEditing(NewFile):
    def test_run(self):
        obj = bpy.data.objects.new("Object", None)
        subject.enable_editing(obj)
        subject.disable_editing(obj)
        assert obj.BIMObjectSpatialProperties.is_editing is False


class TestImportContainers(NewFile):
    def test_run(self):
        bpy.ops.bim.create_project()
        subject.import_containers()
        props = bpy.context.scene.BIMSpatialProperties
        assert len(props.containers) == 1
        assert props.containers[0].name == "My Site"
        assert props.containers[0].long_name == ""
        assert props.containers[0].has_decomposition is True
        assert props.containers[0].ifc_definition_id == tool.Ifc.get().by_type("IfcSite")[0].id()
        assert props.active_container_id == tool.Ifc.get().by_type("IfcProject")[0].id()

    def test_importing_with_a_specified_parent(self):
        bpy.ops.bim.create_project()
        site = tool.Ifc.get().by_type("IfcSite")[0]
        subject.import_containers(site)
        props = bpy.context.scene.BIMSpatialProperties
        assert len(props.containers) == 1
        assert props.containers[0].name == "My Building"
        assert props.containers[0].long_name == ""
        assert props.containers[0].has_decomposition is True
        assert props.containers[0].ifc_definition_id == tool.Ifc.get().by_type("IfcBuilding")[0].id()
        assert props.active_container_id == site.id()

    def test_importing_sorted_by_z_placement(self):
        bpy.ops.bim.create_project()
        building = tool.Ifc.get().by_type("IfcBuilding")[0]
        storey1 = tool.Ifc.get().by_type("IfcBuildingStorey")[0]
        storey1.Name = "Higher"
        bpy.ops.bim.copy_class(obj=tool.Ifc.get_object(storey1).name)
        storey2 = tool.Ifc.get().by_type("IfcBuildingStorey")[1]
        storey2.Name = "Lower"
        storey2.ObjectPlacement.RelativePlacement.Location.Coordinates = (0.0, 0.0, -100.0)
        subject.import_containers(building)
        props = bpy.context.scene.BIMSpatialProperties
        assert len(props.containers) == 2
        assert props.containers[0].name == "Lower"
        assert props.containers[1].name == "Higher"
