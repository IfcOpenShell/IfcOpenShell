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

import bonsai.core.spatial as subject
from test.core.bootstrap import ifc, collector, spatial


class TestReferenceStructure:
    def test_run(self, ifc, spatial):
        spatial.can_reference("structure", "element").should_be_called().will_return(True)
        ifc.run("spatial.reference_structure", products=["element"], relating_structure="structure").should_be_called()
        subject.reference_structure(ifc, spatial, structure="structure", element="element")


class TestDereferenceStructure:
    def test_run(self, ifc, spatial):
        spatial.can_reference("structure", "element").should_be_called().will_return(True)
        ifc.run(
            "spatial.dereference_structure", products=["element"], relating_structure="structure"
        ).should_be_called()
        subject.dereference_structure(ifc, spatial, structure="structure", element="element")


class TestAssignContainer:
    def test_run(self, ifc, collector, spatial):
        spatial.can_contain("container", "element_obj").should_be_called().will_return(True)
        ifc.get_entity("element_obj").should_be_called().will_return("element")
        ifc.run(
            "spatial.assign_container", products=["element"], relating_structure="container"
        ).should_be_called().will_return("rel")
        spatial.disable_editing("element_obj").should_be_called()
        collector.assign("element_obj").should_be_called()
        assert (
            subject.assign_container(ifc, collector, spatial, container="container", element_obj="element_obj") == "rel"
        )


class TestEnableEditingContainer:
    def test_run(self, spatial):
        spatial.set_target_container_as_default().should_be_called()
        spatial.enable_editing("obj").should_be_called()
        subject.enable_editing_container(spatial, obj="obj")


class TestDisableEditingContainer:
    def test_run(self, spatial):
        spatial.disable_editing("obj").should_be_called()
        subject.disable_editing_container(spatial, obj="obj")


class TestRemoveContainer:
    def test_run(self, ifc, collector):
        ifc.get_entity("obj").should_be_called().will_return("element")
        ifc.run("spatial.unassign_container", products=["element"]).should_be_called()
        collector.assign("obj").should_be_called()
        subject.remove_container(ifc, collector, obj="obj")


class TestCopyToContainer:
    def test_run(self, ifc, collector, spatial):
        ifc.get_entity("obj").should_be_called().will_return("element")
        spatial.get_container("element").should_be_called().will_return("container")
        ifc.get_object("container").should_be_called().will_return("container_obj")
        spatial.get_relative_object_matrix("obj", "container_obj").should_be_called().will_return("matrix")

        ifc.get_object("to_container").should_be_called().will_return("to_container_obj")
        spatial.duplicate_object_and_data("obj").should_be_called().will_return("new_obj")
        spatial.set_relative_object_matrix("new_obj", "to_container_obj", "matrix").should_be_called()
        spatial.run_root_copy_class(obj="new_obj").should_be_called()
        spatial.run_spatial_assign_container(container="to_container", element_obj="new_obj").should_be_called()

        spatial.disable_editing("obj").should_be_called()

        subject.copy_to_container(ifc, collector, spatial, obj="obj", containers=["to_container"])

    def test_using_an_absolute_matrix_if_there_is_no_from_container(self, ifc, collector, spatial):
        ifc.get_entity("obj").should_be_called().will_return("element")
        spatial.get_container("element").should_be_called().will_return(None)
        spatial.get_object_matrix("obj").should_be_called().will_return("matrix")

        ifc.get_object("to_container").should_be_called().will_return("to_container_obj")
        spatial.duplicate_object_and_data("obj").should_be_called().will_return("new_obj")
        spatial.set_relative_object_matrix("new_obj", "to_container_obj", "matrix").should_be_called()
        spatial.run_root_copy_class(obj="new_obj").should_be_called()
        spatial.run_spatial_assign_container(container="to_container", element_obj="new_obj").should_be_called()

        spatial.disable_editing("obj").should_be_called()

        subject.copy_to_container(ifc, collector, spatial, obj="obj", containers=["to_container"])


class TestSelectContainer:
    def test_run(self, ifc, spatial):
        ifc.get_object("container").should_be_called().will_return("container_obj")
        spatial.set_active_object("container_obj", selection_mode="ADD").should_be_called()
        subject.select_container(ifc, spatial, container="container", selection_mode="ADD")


class TestSelectSimilarContainer:
    def test_run(self, ifc, spatial):
        ifc.get_entity("obj").should_be_called().will_return("element")
        spatial.get_container("element").should_be_called().will_return("container")
        spatial.get_decomposed_elements("container").should_be_called().will_return(["contained_element"])
        spatial.select_products(["contained_element"]).should_be_called()
        subject.select_similar_container(ifc, spatial, obj="obj")
