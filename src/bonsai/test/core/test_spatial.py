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
from test.core.bootstrap import collector, ifc, spatial


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
        ifc.get_entity("obj").should_be_called().will_return("element")
        spatial.get_root_element("element").should_be_called().will_return("aggregate")
        spatial.get_decomposition("aggregate").should_be_called().will_return(["element", "element2"])
        spatial.can_contain("container", "aggregate").should_be_called().will_return(True)
        ifc.run("spatial.assign_container", products=["aggregate"], relating_structure="container").should_be_called()
        spatial.disable_editing("obj").should_be_called()
        ifc.get_object("aggregate").should_be_called().will_return("aggregate_obj")
        ifc.get_object("element").should_be_called().will_return("obj")
        ifc.get_object("element2").should_be_called().will_return("obj2")
        collector.assign("aggregate_obj").should_be_called()
        collector.assign("obj").should_be_called()
        collector.assign("obj2").should_be_called()
        subject.assign_container(ifc, collector, spatial, container="container", objs=["obj"])

    def test_root_resolves_to_self_for_a_filling(self, ifc, collector, spatial):
        ifc.get_entity("door_obj").should_be_called().will_return("door")
        spatial.get_root_element("door").should_be_called().will_return("door")
        spatial.disable_editing("door_obj").should_be_called()
        spatial.get_decomposition("door").should_be_called().will_return(["door"])
        spatial.can_contain("container", "door").should_be_called().will_return(True)
        ifc.run("spatial.assign_container", products=["door"], relating_structure="container").should_be_called()
        ifc.get_object("door").should_be_called().will_return("door_obj")
        collector.assign("door_obj").should_be_called()
        subject.assign_container(ifc, collector, spatial, container="container", objs=["door_obj"])

    def test_can_contain_is_evaluated_per_root_element(self, ifc, collector, spatial):
        ifc.get_entity("door_obj").should_be_called().will_return("door")
        spatial.get_root_element("door").should_be_called().will_return("door")
        spatial.disable_editing("door_obj").should_be_called()
        spatial.get_decomposition("door").should_be_called().will_return(["door"])
        ifc.get_entity("opening_obj").should_be_called().will_return("opening")
        spatial.get_root_element("opening").should_be_called().will_return("opening")
        spatial.disable_editing("opening_obj").should_be_called()
        spatial.get_decomposition("opening").should_be_called().will_return(["opening"])
        spatial.can_contain("container", "door").should_be_called().will_return(True)
        spatial.can_contain("container", "opening").should_be_called().will_return(False)
        ifc.run("spatial.assign_container", products=["door"], relating_structure="container").should_be_called()
        ifc.get_object("door").should_be_called().will_return("door_obj")
        ifc.get_object("opening").should_be_called().will_return("opening_obj")
        collector.assign("door_obj").should_be_called()
        collector.assign("opening_obj").should_be_called()
        subject.assign_container(ifc, collector, spatial, container="container", objs=["door_obj", "opening_obj"])


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
        spatial.run_spatial_assign_container(container="to_container", objs=["new_obj"]).should_be_called()

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
        spatial.run_spatial_assign_container(container="to_container", objs=["new_obj"]).should_be_called()

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
        spatial.get_decomposed_elements("container", True).should_be_called().will_return(["contained_element"])
        spatial.select_products(["contained_element"]).should_be_called()
        subject.select_similar_container(ifc, spatial, obj="obj")
