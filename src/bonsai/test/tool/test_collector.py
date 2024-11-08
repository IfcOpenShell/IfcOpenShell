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
import ifcopenshell.api
import ifcopenshell.util.element
import bonsai.core.tool
import bonsai.tool as tool
from bonsai.tool.collector import Collector as subject
from test.bim.bootstrap import NewFile, NewIfc, NewIfc4X3


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.Collector)


class TestAssign(NewIfc):
    def test_walls_are_placed_in_its_spatial_collection(self):
        wall_obj = bpy.data.objects.new("Object", None)
        wall_element = tool.Ifc.get().createIfcWall()
        tool.Ifc.link(wall_element, wall_obj)
        bpy.context.scene.collection.objects.link(wall_obj)
        ifcopenshell.api.run(
            "spatial.assign_container",
            tool.Ifc.get(),
            products=[wall_element],
            relating_structure=tool.Ifc.get().by_type("IfcSite")[0],
        )
        subject.assign(wall_obj)
        assert len(wall_obj.users_collection) == 2
        assert "IfcSite" in wall_obj.users_collection[0].name

    def test_walls_are_unsorted_if_not_decomposes(self):
        wall_obj = bpy.data.objects.new("Object", None)
        wall_element = tool.Ifc.get().createIfcWall()
        tool.Ifc.link(wall_element, wall_obj)
        bpy.context.scene.collection.objects.link(wall_obj)
        subject.assign(wall_obj)
        assert len(wall_obj.users_collection) == 2
        assert "Unsorted" in wall_obj.users_collection[0].name

    def test_spatial_structure_elements_are_placed_in_a_collection_of_the_same_name(self):
        space_obj = bpy.data.objects.new("IfcSpace/Name", None)
        space_element = tool.Ifc.get().createIfcSpace()
        tool.Ifc.link(space_element, space_obj)
        bpy.context.scene.collection.objects.link(space_obj)
        ifcopenshell.api.run(
            "aggregate.assign_object",
            tool.Ifc.get(),
            relating_object=tool.Ifc.get().by_type("IfcSite")[0],
            products=[space_element],
        )
        subject.assign(space_obj)
        assert len(space_obj.users_collection) == 2
        assert space_obj.users_collection[0].name == space_obj.name

    def test_multiple_assigns_do_not_create_duplicate_spatial_structure_collections(self):
        space_obj = bpy.data.objects.new("IfcSpace/Name", None)
        space_element = tool.Ifc.get().createIfcSpace()
        tool.Ifc.link(space_element, space_obj)
        bpy.context.scene.collection.objects.link(space_obj)
        ifcopenshell.api.run(
            "aggregate.assign_object",
            tool.Ifc.get(),
            relating_object=tool.Ifc.get().by_type("IfcSite")[0],
            products=[space_element],
        )
        subject.assign(space_obj)
        subject.assign(space_obj)
        assert bpy.data.collections.get("IfcSpace/Name")
        assert bpy.data.collections.get("IfcSite/My Site")
        assert not bpy.data.collections.get("IfcSpace/Name.001")
        assert not bpy.data.collections.get("IfcSite/My Site.001")

    def test_spatial_zone_elements_are_not_placed_in_a_collection_of_the_same_name(self):
        space_obj = bpy.data.objects.new("IfcSpaceZone/Name", None)
        space_element = tool.Ifc.get().createIfcSpatialZone()
        tool.Ifc.link(space_element, space_obj)
        bpy.context.scene.collection.objects.link(space_obj)
        ifcopenshell.api.run(
            "aggregate.assign_object",
            tool.Ifc.get(),
            relating_object=tool.Ifc.get().by_type("IfcSite")[0],
            products=[space_element],
        )
        subject.assign(space_obj)
        assert len(space_obj.users_collection) == 2
        assert space_obj.users_collection[0].name != space_obj.name

    def test_aggregates_are_also_placed_in_their_container(self):
        element_obj = bpy.data.objects.new("IfcElementAssembly/Name", None)
        element = tool.Ifc.get().createIfcElementAssembly()
        subelement_obj = bpy.data.objects.new("IfcBeam/Name", None)
        subelement = tool.Ifc.get().createIfcBeam()
        tool.Ifc.link(element, element_obj)
        tool.Ifc.link(subelement, subelement_obj)
        bpy.context.scene.collection.objects.link(element_obj)
        bpy.context.scene.collection.objects.link(subelement_obj)
        ifcopenshell.api.run(
            "aggregate.assign_object",
            tool.Ifc.get(),
            relating_object=element,
            products=[subelement],
        )
        ifcopenshell.api.run(
            "spatial.assign_container",
            tool.Ifc.get(),
            products=[element],
            relating_structure=tool.Ifc.get().by_type("IfcSite")[0],
        )
        subject.assign(element_obj)
        subject.assign(subelement_obj)
        assert len(element_obj.users_collection) == 2
        assert len(subelement_obj.users_collection) == 2
        assert "IfcSite" in element_obj.users_collection[0].name
        assert "IfcSite" in subelement_obj.users_collection[0].name

    def test_projects_are_placed_in_a_collection_of_the_same_name(self):
        tool.Ifc.set(ifcopenshell.file())
        element_obj = bpy.data.objects.new("IfcProject/Name", None)
        element = tool.Ifc.get().createIfcProject()
        tool.Ifc.link(element, element_obj)
        bpy.context.scene.collection.objects.link(element_obj)
        subject.assign(element_obj)
        assert len(element_obj.users_collection) == 2
        assert element_obj.users_collection[0].name == element_obj.name

    def test_multiple_assigns_do_not_create_duplicate_collections(self):
        tool.Ifc.set(ifcopenshell.file())
        element_obj = bpy.data.objects.new("IfcProject/Name", None)
        element = tool.Ifc.get().createIfcProject()
        tool.Ifc.link(element, element_obj)
        bpy.context.scene.collection.objects.link(element_obj)
        subject.assign(element_obj)
        subject.assign(element_obj)
        assert bpy.data.collections.get("IfcProject/Name")
        assert not bpy.data.collections.get("IfcProject/Name.001")

    def test_own_collections_are_retained_and_name_synced(self):
        space_obj = bpy.data.objects.new("IfcSpace/Name", None)
        space_element = tool.Ifc.get().createIfcSpace()
        tool.Ifc.link(space_element, space_obj)
        space_collection = bpy.data.collections.new("Foobar")
        bpy.context.scene.collection.children.link(space_collection)
        space_obj.BIMObjectProperties.collection = space_collection
        space_collection.objects.link(space_obj)
        ifcopenshell.api.run(
            "aggregate.assign_object",
            tool.Ifc.get(),
            relating_object=tool.Ifc.get().by_type("IfcSite")[0],
            products=[space_element],
        )
        subject.assign(space_obj)
        assert bpy.context.scene.collection.children.find(space_collection.name) != -1
        assert bpy.data.collections.get("IfcSite/My Site").children.find(space_collection.name) == -1
        assert bpy.data.collections.get("IfcProject/My Project").children.find(space_collection.name) == -1
        assert bpy.context.scene.collection.children.find(space_collection.name) != -1
        assert space_collection.objects.find(space_obj.name) != -1
        assert space_collection.name == "IfcSpace/Name"

    def test_types_are_placed_in_the_types_collection(self):
        element_obj = bpy.data.objects.new("IfcWallType/Name", None)
        element = tool.Ifc.get().createIfcWallType()
        tool.Ifc.link(element, element_obj)
        bpy.context.scene.collection.objects.link(element_obj)
        subject.assign(element_obj)
        assert element_obj.users_collection[0].name == "IfcTypeProduct"
        assert bpy.data.collections.get("IfcProject/My Project").children.get("IfcTypeProduct")

    def test_openings_are_placed_in_the_openings_collection(self):
        element_obj = bpy.data.objects.new("IfcOpeningElement/Name", None)
        element = tool.Ifc.get().createIfcOpeningElement()
        tool.Ifc.link(element, element_obj)
        bpy.context.scene.collection.objects.link(element_obj)
        subject.assign(element_obj)
        assert element_obj.users_collection[0].name == "IfcOpeningElement"
        assert bpy.data.collections.get("IfcProject/My Project").children.get("IfcOpeningElement")

    def test_grids_are_placed_in_their_container(self):
        element_obj = bpy.data.objects.new("IfcGrid/Name", None)
        element = tool.Ifc.get().createIfcGrid()
        tool.Ifc.link(element, element_obj)
        ifcopenshell.api.run(
            "spatial.assign_container",
            tool.Ifc.get(),
            products=[element],
            relating_structure=tool.Ifc.get().by_type("IfcSite")[0],
        )
        bpy.context.scene.collection.objects.link(element_obj)
        subject.assign(element_obj)
        assert element_obj.users_collection[0].name == "IfcSite/My Site"

    def test_grids_axes_are_placed_in_the_grids_container(self):
        element_obj = bpy.data.objects.new("IfcGrid/Name", None)
        axis_obj = bpy.data.objects.new("IfcGrid/Name", None)
        axis = tool.Ifc.get().createIfcGridAxis()
        element = tool.Ifc.get().createIfcGrid(UAxes=[axis])
        tool.Ifc.link(element, element_obj)
        tool.Ifc.link(axis, axis_obj)
        ifcopenshell.api.run(
            "spatial.assign_container",
            tool.Ifc.get(),
            products=[element],
            relating_structure=tool.Ifc.get().by_type("IfcSite")[0],
        )
        bpy.context.scene.collection.objects.link(element_obj)
        subject.assign(element_obj)
        subject.assign(axis_obj)
        assert axis_obj.users_collection[0].name == "IfcSite/My Site"

    def test_drawings_are_placed_in_their_own_collection(self):
        element_obj = bpy.data.objects.new("IfcAnnotation/DRAWING", None)
        element = tool.Ifc.get().createIfcAnnotation(ObjectType="DRAWING")
        tool.Ifc.link(element, element_obj)

        group = ifcopenshell.api.run("group.add_group", tool.Ifc.get())
        group.ObjectType = "DRAWING"
        ifcopenshell.api.run("group.assign_group", tool.Ifc.get(), products=[element], group=group)

        subject.assign(element_obj)
        assert element_obj.users_collection[0].name == "IfcAnnotation/DRAWING"
        assert bpy.data.collections.get("IfcProject/My Project").children.get("IfcAnnotation/DRAWING")

    def test_annotations_are_placed_in_their_drawings_collection(self):
        self.test_drawings_are_placed_in_their_own_collection()
        ifc_file = tool.Ifc.get()

        element_obj = bpy.data.objects.new("IfcAnnotation/Name", None)
        element = ifc_file.createIfcAnnotation()
        tool.Ifc.link(element, element_obj)

        group = ifc_file.by_type("IfcGroup")[0]
        ifcopenshell.api.run("group.assign_group", ifc_file, products=[element], group=group)

        subject.assign(element_obj)
        assert element_obj.users_collection[0].name == "IfcAnnotation/DRAWING"

    def test_structural_members_are_placed_in_a_members_collection(self):
        element_obj = bpy.data.objects.new("IfcStructuralCurveMember/Name", None)
        element = tool.Ifc.get().createIfcStructuralCurveMember()
        tool.Ifc.link(element, element_obj)
        subject.assign(element_obj)
        assert element_obj.users_collection[0].name == "IfcStructuralItem"
        assert bpy.data.collections.get("IfcProject/My Project").children.get("IfcStructuralItem")

    def test_structural_connections_are_placed_in_a_connections_collection(self):
        element_obj = bpy.data.objects.new("IfcStructuralCurveConnection/Name", None)
        element = tool.Ifc.get().createIfcStructuralCurveConnection()
        tool.Ifc.link(element, element_obj)
        subject.assign(element_obj)
        assert element_obj.users_collection[0].name == "IfcStructuralItem"
        assert bpy.data.collections.get("IfcProject/My Project").children.get("IfcStructuralItem")


class TestAssignIFC4X3(NewIfc4X3):
    def test_linear_positioning_elements_are_placed_in_a_special_collection(self):
        element_obj = bpy.data.objects.new("Name", None)
        element = tool.Ifc.get().createIfcAlignment()
        tool.Ifc.link(element, element_obj)
        subject.assign(element_obj)
        assert element_obj.users_collection[0].name == "IfcLinearPositioningElement"
        assert bpy.data.collections.get("IfcProject/My Project").children.get("IfcLinearPositioningElement")

    def test_referents_are_placed_in_a_special_collection(self):
        element_obj = bpy.data.objects.new("Name", None)
        element = tool.Ifc.get().createIfcReferent()
        tool.Ifc.link(element, element_obj)
        subject.assign(element_obj)
        assert element_obj.users_collection[0].name == "IfcReferent"
        assert bpy.data.collections.get("IfcProject/My Project").children.get("IfcReferent")
