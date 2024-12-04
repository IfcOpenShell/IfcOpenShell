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

import bonsai.core.root as subject
import test.core.test_geometry
from test.core.bootstrap import ifc, collector, geometry, root


class TestCopyClass:
    def test_doing_nothing_if_not_an_ifc_element(self, ifc, collector, root):
        ifc.get_entity("obj").should_be_called().will_return(None)
        subject.copy_class(ifc, collector, geometry, root, obj="obj")

    def test_copy_with_new_geometry_derived_from_the_type(self, ifc, collector, root):
        ifc.get_entity("obj").should_be_called().will_return("original_element")
        root.is_element_a("original_element", "IfcRelSpaceBoundary").should_be_called().will_return(False)
        root.get_object_representation("obj").should_be_called().will_return("representation")
        ifc.run("root.copy_class", product="original_element").should_be_called().will_return("element")
        ifc.link("element", "obj").should_be_called()
        root.get_element_type("element").should_be_called().will_return("type")
        root.does_type_have_representations("type").should_be_called().will_return(True)
        ifc.run("type.map_type_representations", related_object="element", relating_type="type").should_be_called()
        ifc.get_object("type").should_be_called().will_return("type_obj")
        root.link_object_data("type_obj", "obj").should_be_called()
        collector.assign("obj").should_be_called()
        root.is_element_a("element", "IfcOpeningElement").should_be_called().will_return(False)
        subject.copy_class(ifc, collector, geometry, root, obj="obj")

    def test_copy_with_new_geometry_copied_from_the_old(self, ifc, collector, geometry, root):
        # Originally, geometry was added fresh from the Blender mesh instead of
        # copied. This was faster (though I cannot recreate it now) but had the
        # bigger problem of not preserving non-mesh geometry and openings.
        ifc.get_entity("obj").should_be_called().will_return("original_element")
        root.is_element_a("original_element", "IfcRelSpaceBoundary").should_be_called().will_return(False)
        root.get_object_representation("obj").should_be_called().will_return("representation")
        ifc.run("root.copy_class", product="original_element").should_be_called().will_return("element")
        ifc.link("element", "obj").should_be_called()
        root.get_element_type("element").should_be_called().will_return("type")
        root.does_type_have_representations("type").should_be_called().will_return(False)
        root.copy_representation("original_element", "element").should_be_called()
        root.get_representation_context("representation").should_be_called().will_return("context")
        root.get_element_representation("element", "context").should_be_called().will_return("new_representation")
        geometry.change_object_data("obj", "data", is_global=True).should_be_called()
        geometry.get_representation_name("new_representation").should_be_called().will_return("name")
        geometry.rename_object("data", "name").should_be_called()
        geometry.link("new_representation", "data").should_be_called()
        geometry.reload_representation_item_ids("new_representation", "data").should_be_called()
        root.assign_body_styles("element", "obj").should_be_called()
        geometry.duplicate_object_data("obj").should_be_called().will_return("data")
        collector.assign("obj").should_be_called()
        root.is_element_a("element", "IfcOpeningElement").should_be_called().will_return(False)
        subject.copy_class(ifc, collector, geometry, root, obj="obj")

    def test_copy_with_no_new_geometry(self, ifc, collector, geometry, root):
        ifc.get_entity("obj").should_be_called().will_return("original_element")
        root.is_element_a("original_element", "IfcRelSpaceBoundary").should_be_called().will_return(False)
        root.get_object_representation("obj").should_be_called().will_return(None)
        ifc.run("root.copy_class", product="original_element").should_be_called().will_return("element")
        ifc.link("element", "obj").should_be_called()
        root.get_element_type("element").should_be_called().will_return("type")
        root.does_type_have_representations("type").should_be_called().will_return(False)
        collector.assign("obj").should_be_called()
        root.is_element_a("element", "IfcOpeningElement").should_be_called().will_return(False)
        subject.copy_class(ifc, collector, geometry, root, obj="obj")

    def test_copied_openings_are_tracked_for_special_visualiation(self, ifc, collector, geometry, root):
        ifc.get_entity("obj").should_be_called().will_return("original_element")
        root.is_element_a("original_element", "IfcRelSpaceBoundary").should_be_called().will_return(False)
        root.get_object_representation("obj").should_be_called().will_return(None)
        ifc.run("root.copy_class", product="original_element").should_be_called().will_return("element")
        ifc.link("element", "obj").should_be_called()
        root.get_element_type("element").should_be_called().will_return("type")
        root.does_type_have_representations("type").should_be_called().will_return(True)
        ifc.run("type.map_type_representations", related_object="element", relating_type="type").should_be_called()
        ifc.get_object("type").should_be_called().will_return("type_obj")
        root.link_object_data("type_obj", "obj").should_be_called()
        collector.assign("obj").should_be_called()
        root.is_element_a("element", "IfcOpeningElement").should_be_called().will_return(True)
        root.add_tracked_opening("obj").should_be_called()
        subject.copy_class(ifc, collector, geometry, root, obj="obj")

    def test_copying_boundaries_are_dealt_with_specially(self, ifc, collector, geometry, root):
        ifc.get_entity("obj").should_be_called().will_return("original_element")
        root.is_element_a("original_element", "IfcRelSpaceBoundary").should_be_called().will_return(True)
        ifc.run("boundary.copy_boundary", boundary="original_element").should_be_called().will_return("element")
        ifc.link("element", "obj").should_be_called()
        assert subject.copy_class(ifc, collector, geometry, root, obj="obj") == "element"


class TestAssignClass:
    def test_do_nothing_if_already_assigned(self, ifc, collector, root):
        ifc.get_entity("obj").should_be_called().will_return("entity")
        subject.assign_class(
            ifc,
            collector,
            root,
            obj="obj",
            ifc_class="ifc_class",
            predefined_type="predefined_type",
            should_add_representation=True,
            context="context",
            ifc_representation_class="ifc_representation_class",
        )

    def test_assign_a_class_with_geometry_and_autodetected_spatial_container_spatial_element(
        self, ifc, collector, root
    ):
        ifc.get_entity("obj").should_be_called().will_return(None)
        root.get_object_name("obj").should_be_called().will_return("name")
        ifc.run(
            "root.create_entity", ifc_class="ifc_class", predefined_type="predefined_type", name="name"
        ).should_be_called().will_return("element")
        root.set_object_name("obj", "element").should_be_called()
        ifc.link("element", "obj").should_be_called()
        root.run_geometry_add_representation(
            obj="obj", context="context", ifc_representation_class="ifc_representation_class", profile_set_usage=None
        ).should_be_called()

        root.is_drawing_annotation("element").should_be_called().will_return(False)
        root.get_default_container().should_be_called().will_return("default_container")
        root.is_spatial_element("element").should_be_called().will_return(True)
        ifc.run("aggregate.assign_object", products=["element"], relating_object="default_container").should_be_called()

        collector.assign("obj").should_be_called()
        subject.assign_class(
            ifc,
            collector,
            root,
            obj="obj",
            ifc_class="ifc_class",
            predefined_type="predefined_type",
            should_add_representation=True,
            context="context",
            ifc_representation_class="ifc_representation_class",
        )

    def test_assign_a_class_with_geometry_and_autodetected_spatial_container_non_spatial_containable(
        self, ifc, collector, root
    ):
        ifc.get_entity("obj").should_be_called().will_return(None)
        root.get_object_name("obj").should_be_called().will_return("name")
        ifc.run(
            "root.create_entity", ifc_class="ifc_class", predefined_type="predefined_type", name="name"
        ).should_be_called().will_return("element")
        root.set_object_name("obj", "element").should_be_called()
        ifc.link("element", "obj").should_be_called()
        root.run_geometry_add_representation(
            obj="obj", context="context", ifc_representation_class="ifc_representation_class", profile_set_usage=None
        ).should_be_called()

        root.is_drawing_annotation("element").should_be_called().will_return(False)
        root.get_default_container().should_be_called().will_return("default_container")
        root.is_spatial_element("element").should_be_called().will_return(False)
        root.is_containable("element").should_be_called().will_return(True)
        ifc.run(
            "spatial.assign_container", products=["element"], relating_structure="default_container"
        ).should_be_called()

        collector.assign("obj").should_be_called()
        subject.assign_class(
            ifc,
            collector,
            root,
            obj="obj",
            ifc_class="ifc_class",
            predefined_type="predefined_type",
            should_add_representation=True,
            context="context",
            ifc_representation_class="ifc_representation_class",
        )

    def test_assign_a_class_to_drawing_annotation_without_assigning_container(self, ifc, collector, root):
        ifc.get_entity("obj").should_be_called().will_return(None)
        root.get_object_name("obj").should_be_called().will_return("name")
        ifc.run(
            "root.create_entity", ifc_class="ifc_class", predefined_type="predefined_type", name="name"
        ).should_be_called().will_return("element")
        root.set_object_name("obj", "element").should_be_called()
        ifc.link("element", "obj").should_be_called()
        root.run_geometry_add_representation(
            obj="obj", context="context", ifc_representation_class="ifc_representation_class", profile_set_usage=None
        ).should_be_called()

        root.is_drawing_annotation("element").should_be_called().will_return(True)

        collector.assign("obj").should_be_called()
        subject.assign_class(
            ifc,
            collector,
            root,
            obj="obj",
            ifc_class="ifc_class",
            predefined_type="predefined_type",
            should_add_representation=True,
            context="context",
            ifc_representation_class="ifc_representation_class",
        )

    def test_not_adding_a_representation_if_requested_no_default_container(self, ifc, collector, root):
        ifc.get_entity("obj").should_be_called().will_return(None)
        root.get_object_name("obj").should_be_called().will_return("name")
        ifc.run(
            "root.create_entity", ifc_class="ifc_class", predefined_type="predefined_type", name="name"
        ).should_be_called().will_return("element")
        root.set_object_name("obj", "element").should_be_called()
        ifc.link("element", "obj").should_be_called()
        root.is_drawing_annotation("element").should_be_called().will_return(False)
        root.get_default_container().should_be_called().will_return(None)
        collector.assign("obj").should_be_called()
        subject.assign_class(
            ifc,
            collector,
            root,
            obj="obj",
            ifc_class="ifc_class",
            predefined_type="predefined_type",
            should_add_representation=False,
            context="context",
            ifc_representation_class="ifc_representation_class",
        )
