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
from blenderbim.tool.collector import Collector as subject
from test.bim.bootstrap import NewFile


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), blenderbim.core.tool.Collector)


class TestAssign(NewFile):
    def test_in_decomposition_mode_walls_are_placed_in_its_spatial_collection(self):
        bpy.ops.bim.create_project()
        wall_obj = bpy.data.objects.new("Object", None)
        wall_element = tool.Ifc.get().createIfcWall()
        tool.Ifc.link(wall_element, wall_obj)
        bpy.context.scene.collection.objects.link(wall_obj)
        ifcopenshell.api.run(
            "spatial.assign_container",
            tool.Ifc.get(),
            product=wall_element,
            relating_structure=tool.Ifc.get().by_type("IfcSite")[0],
        )
        subject.assign(wall_obj)
        assert len(wall_obj.users_collection) == 1
        assert "IfcSite" in wall_obj.users_collection[0].name

    def test_in_decomposition_mode_walls_are_placed_in_the_project_if_not_decomposes(self):
        bpy.ops.bim.create_project()
        wall_obj = bpy.data.objects.new("Object", None)
        wall_element = tool.Ifc.get().createIfcWall()
        tool.Ifc.link(wall_element, wall_obj)
        bpy.context.scene.collection.objects.link(wall_obj)
        subject.assign(wall_obj)
        assert len(wall_obj.users_collection) == 1
        assert "IfcProject" in wall_obj.users_collection[0].name

    def test_in_decomposition_mode_spatial_elements_are_placed_in_a_collection_of_the_same_name(self):
        bpy.ops.bim.create_project()
        space_obj = bpy.data.objects.new("IfcSpace/Name", None)
        space_element = tool.Ifc.get().createIfcSpace()
        tool.Ifc.link(space_element, space_obj)
        bpy.context.scene.collection.objects.link(space_obj)
        ifcopenshell.api.run(
            "aggregate.assign_object",
            tool.Ifc.get(),
            relating_object=tool.Ifc.get().by_type("IfcSite")[0],
            product=space_element,
        )
        subject.assign(space_obj)
        assert len(space_obj.users_collection) == 1
        assert space_obj.users_collection[0].name == space_obj.name

    def test_in_decomposition_mode_aggregates_are_placed_in_a_collection_of_the_same_name(self):
        bpy.ops.bim.create_project()
        element_obj = bpy.data.objects.new("IfcElementAssembly/Name", None)
        element = tool.Ifc.get().createIfcElementAssembly()
        subelement_obj = bpy.data.objects.new("IfcBeam/Name", None)
        subelement = tool.Ifc.get().createIfcBeam()
        tool.Ifc.link(element, element_obj)
        bpy.context.scene.collection.objects.link(element_obj)
        ifcopenshell.api.run(
            "aggregate.assign_object",
            tool.Ifc.get(),
            relating_object=element,
            product=subelement,
        )
        subject.assign(element_obj)
        assert len(element_obj.users_collection) == 1
        assert element_obj.users_collection[0].name == element_obj.name

    def test_in_decomposition_mode_projects_are_placed_in_a_collection_of_the_same_name(self):
        tool.Ifc.set(ifcopenshell.file())
        element_obj = bpy.data.objects.new("IfcProject/Name", None)
        element = tool.Ifc.get().createIfcProject()
        tool.Ifc.link(element, element_obj)
        bpy.context.scene.collection.objects.link(element_obj)
        subject.assign(element_obj)
        assert len(element_obj.users_collection) == 1
        assert element_obj.users_collection[0].name == element_obj.name

    def test_in_decomposition_mode_existing_collections_are_reassigned_to_the_correct_place_in_the_hierarchy(self):
        bpy.ops.bim.create_project()
        space_obj = bpy.data.objects.new("IfcSpace/Name", None)
        space_element = tool.Ifc.get().createIfcSpace()
        tool.Ifc.link(space_element, space_obj)
        space_collection = bpy.data.collections.new("IfcSpace/Name")
        bpy.context.scene.collection.children.link(space_collection)
        space_collection.objects.link(space_obj)
        ifcopenshell.api.run(
            "aggregate.assign_object",
            tool.Ifc.get(),
            relating_object=tool.Ifc.get().by_type("IfcSite")[0],
            product=space_element,
        )
        subject.assign(space_obj)
        assert bpy.context.scene.collection.children.find(space_collection.name) == -1
        assert bpy.data.collections.get("IfcSite/My Site").children.find(space_collection.name) != -1

    def test_in_decomposition_mode_aggregates_subelements_are_placed_in_the_aggregates_collection(self):
        bpy.ops.bim.create_project()
        element_obj = bpy.data.objects.new("IfcElementAssembly/Name", None)
        element = tool.Ifc.get().createIfcElementAssembly()
        subelement_obj = bpy.data.objects.new("IfcBeam/Name", None)
        subelement = tool.Ifc.get().createIfcBeam()
        tool.Ifc.link(element, element_obj)
        tool.Ifc.link(subelement, subelement_obj)
        bpy.context.scene.collection.objects.link(element_obj)
        ifcopenshell.api.run(
            "aggregate.assign_object",
            tool.Ifc.get(),
            relating_object=element,
            product=subelement,
        )
        subject.assign(element_obj)
        subject.assign(subelement_obj)
        assert subelement_obj.users_collection[0].name == element_obj.name

    def test_in_decomposition_mode_aggregates_subelements_are_placed_in_the_spatial_collection_as_a_fallback(self):
        # The aggregate object may not exist in all scenarios, such as when it is filtered out
        bpy.ops.bim.create_project()
        element = tool.Ifc.get().createIfcElementAssembly()
        subelement_obj = bpy.data.objects.new("IfcBeam/Name", None)
        subelement = tool.Ifc.get().createIfcBeam()
        tool.Ifc.link(subelement, subelement_obj)
        ifcopenshell.api.run(
            "spatial.assign_container",
            tool.Ifc.get(),
            product=element,
            relating_structure=tool.Ifc.get().by_type("IfcSite")[0],
        )
        ifcopenshell.api.run(
            "aggregate.assign_object",
            tool.Ifc.get(),
            relating_object=element,
            product=subelement,
        )
        subject.assign(subelement_obj)
        assert subelement_obj.users_collection[0].name == "IfcSite/My Site"

    def test_in_decomposition_mode_types_are_placed_in_the_types_collection(self):
        bpy.ops.bim.create_project()
        element_obj = bpy.data.objects.new("IfcWallType/Name", None)
        element = tool.Ifc.get().createIfcWallType()
        tool.Ifc.link(element, element_obj)
        bpy.context.scene.collection.objects.link(element_obj)
        subject.assign(element_obj)
        assert element_obj.users_collection[0].name == "Types"
        assert bpy.data.collections.get("IfcProject/My Project").children.get("Types")

    def test_in_decomposition_mode_openings_are_placed_in_the_openings_collection(self):
        bpy.ops.bim.create_project()
        element_obj = bpy.data.objects.new("IfcOpeningElement/Name", None)
        element = tool.Ifc.get().createIfcOpeningElement()
        tool.Ifc.link(element, element_obj)
        bpy.context.scene.collection.objects.link(element_obj)
        subject.assign(element_obj)
        assert element_obj.users_collection[0].name == "IfcOpeningElements"
        assert bpy.data.collections.get("IfcProject/My Project").children.get("IfcOpeningElements")
