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

import blenderbim.core.spatial as subject
from test.core.bootstrap import ifc, collector, spatial


class TestReferenceStructure:
    def test_run(self, ifc, spatial):
        spatial.can_reference("structure", "element").should_be_called().will_return(True)
        ifc.run("spatial.reference_structure", product="element", relating_structure="structure").should_be_called()
        subject.reference_structure(ifc, spatial, structure="structure", element="element")


class TestDereferenceStructure:
    def test_run(self, ifc, spatial):
        spatial.can_reference("structure", "element").should_be_called().will_return(True)
        ifc.run("spatial.dereference_structure", product="element", relating_structure="structure").should_be_called()
        subject.dereference_structure(ifc, spatial, structure="structure", element="element")


class TestAssignContainer:
    def test_run(self, ifc, collector, spatial):
        spatial.can_contain("structure_obj", "element_obj").should_be_called().will_return(True)
        ifc.get_entity("structure_obj").should_be_called().will_return("structure")
        ifc.get_entity("element_obj").should_be_called().will_return("element")
        ifc.run(
            "spatial.assign_container", product="element", relating_structure="structure"
        ).should_be_called().will_return("rel")
        spatial.disable_editing("element_obj").should_be_called()
        collector.assign("element_obj").should_be_called()
        assert (
            subject.assign_container(ifc, collector, spatial, structure_obj="structure_obj", element_obj="element_obj")
            == "rel"
        )


class TestEnableEditingContainer:
    def test_run(self, spatial):
        spatial.enable_editing("obj").should_be_called()
        spatial.import_containers().should_be_called()
        subject.enable_editing_container(spatial, obj="obj")


class TestDisableEditingContainer:
    def test_run(self, spatial):
        spatial.disable_editing("obj").should_be_called()
        subject.disable_editing_container(spatial, obj="obj")


class TestChangeSpatialLevel:
    def test_run(self, spatial):
        spatial.import_containers(parent="parent").should_be_called()
        subject.change_spatial_level(spatial, parent="parent")


class TestRemoveContainer:
    def test_run(self, ifc, collector):
        ifc.get_entity("obj").should_be_called().will_return("element")
        ifc.run("spatial.remove_container", product="element").should_be_called()
        collector.assign("obj").should_be_called()
        subject.remove_container(ifc, collector, obj="obj")


class TestCopyToContainer:
    def test_run(self, ifc, spatial):
        ifc.get_entity("obj").should_be_called().will_return("element")
        spatial.get_container("element").should_be_called().will_return("container")
        ifc.get_object("container").should_be_called().will_return("container_obj")
        spatial.get_relative_object_matrix("obj", "container_obj").should_be_called().will_return("matrix")

        ifc.get_object("to_container").should_be_called().will_return("to_container_obj")
        spatial.duplicate_object_and_data("obj").should_be_called().will_return("new_obj")
        spatial.set_relative_object_matrix("new_obj", "to_container_obj", "matrix").should_be_called()
        spatial.run_root_copy_class(obj="new_obj").should_be_called()
        spatial.run_spatial_assign_container(structure_obj="to_container_obj", element_obj="new_obj").should_be_called()

        spatial.disable_editing("obj").should_be_called()

        subject.copy_to_container(ifc, spatial, obj="obj", containers=["to_container"])

    def test_using_an_absolute_matrix_if_there_is_no_from_container(self, ifc, spatial):
        ifc.get_entity("obj").should_be_called().will_return("element")
        spatial.get_container("element").should_be_called().will_return(None)
        spatial.get_object_matrix("obj").should_be_called().will_return("matrix")

        ifc.get_object("to_container").should_be_called().will_return("to_container_obj")
        spatial.duplicate_object_and_data("obj").should_be_called().will_return("new_obj")
        spatial.set_relative_object_matrix("new_obj", "to_container_obj", "matrix").should_be_called()
        spatial.run_root_copy_class(obj="new_obj").should_be_called()
        spatial.run_spatial_assign_container(structure_obj="to_container_obj", element_obj="new_obj").should_be_called()

        spatial.disable_editing("obj").should_be_called()

        subject.copy_to_container(ifc, spatial, obj="obj", containers=["to_container"])


class TestSelectContainer:
    def test_run(self, ifc, spatial):
        ifc.get_entity("obj").should_be_called().will_return("element")
        spatial.get_container("element").should_be_called().will_return("container")
        ifc.get_object("container").should_be_called().will_return("container_obj")
        spatial.set_active_object("container_obj").should_be_called()
        subject.select_container(ifc, spatial, obj="obj")


class TestSelectSimilarContainer:
    def test_run(self, ifc, spatial):
        ifc.get_entity("obj").should_be_called().will_return("element")
        spatial.get_container("element").should_be_called().will_return("container")
        spatial.get_decomposed_elements("container").should_be_called().will_return(["contained_element"])
        ifc.get_object("contained_element").should_be_called().will_return("contained_obj")
        spatial.select_object("contained_obj").should_be_called()
        subject.select_similar_container(ifc, spatial, obj="obj")
