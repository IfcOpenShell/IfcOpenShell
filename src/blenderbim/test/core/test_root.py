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

import blenderbim.core.root as subject
import test.core.test_geometry
from test.core.bootstrap import ifc, collector, geometry, root


class TestCopyClass:
    def test_doing_nothing_if_not_an_ifc_element(self, ifc, collector, root):
        ifc.get_entity("obj").should_be_called().will_return(None)
        subject.copy_class(ifc, collector, geometry, root, obj="obj")

    def test_copy_with_new_geometry_derived_from_the_type(self, ifc, collector, root):
        ifc.get_entity("obj").should_be_called().will_return("original_element")
        ifc.run("root.copy_class", product="original_element").should_be_called().will_return("element")
        ifc.link("element", "obj").should_be_called()
        root.get_element_type("element").should_be_called().will_return("type")
        root.does_type_have_representations("type").should_be_called().will_return(True)
        ifc.run("type.map_type_representations", related_object="element", relating_type="type").should_be_called()
        ifc.get_object("type").should_be_called().will_return("type_obj")
        root.link_object_data("type_obj", "obj").should_be_called()
        collector.assign("obj").should_be_called()
        root.is_opening_element("element").should_be_called().will_return(False)
        subject.copy_class(ifc, collector, geometry, root, obj="obj")

    def test_copy_with_new_geometry_added_afresh_for_speed(self, ifc, collector, geometry, root):
        ifc.get_entity("obj").should_be_called().will_return("original_element")
        ifc.run("root.copy_class", product="original_element").should_be_called().will_return("element")
        ifc.link("element", "obj").should_be_called()
        root.get_element_type("element").should_be_called().will_return("type")
        root.does_type_have_representations("type").should_be_called().will_return(False)

        root.get_object_representation("obj").should_be_called().will_return("representation")
        root.get_representation_context("representation").should_be_called().will_return("context")
        geometry.get_ifc_representation_class("element", "representation").should_be_called().will_return(
            "ifc_representation_class"
        )
        geometry.get_profile_set_usage("element").should_be_called().will_return("profile_set_usage")
        root.run_geometry_add_representation(
            obj="obj",
            context="context",
            ifc_representation_class="ifc_representation_class",
            profile_set_usage="profile_set_usage",
        ).should_be_called()
        collector.assign("obj").should_be_called()
        root.is_opening_element("element").should_be_called().will_return(False)
        subject.copy_class(ifc, collector, geometry, root, obj="obj")

    def test_copy_with_no_new_geometry(self, ifc, collector, geometry, root):
        ifc.get_entity("obj").should_be_called().will_return("original_element")
        ifc.run("root.copy_class", product="original_element").should_be_called().will_return("element")
        ifc.link("element", "obj").should_be_called()
        root.get_element_type("element").should_be_called().will_return("type")
        root.does_type_have_representations("type").should_be_called().will_return(False)
        root.get_object_representation("obj").should_be_called().will_return(None)
        collector.assign("obj").should_be_called()
        root.is_opening_element("element").should_be_called().will_return(False)
        subject.copy_class(ifc, collector, geometry, root, obj="obj")

    def test_copied_openings_have_dynamic_voids_added(self, ifc, collector, root):
        ifc.get_entity("obj").should_be_called().will_return("original_element")
        ifc.run("root.copy_class", product="original_element").should_be_called().will_return("element")
        ifc.link("element", "obj").should_be_called()
        root.get_element_type("element").should_be_called().will_return("type")
        root.does_type_have_representations("type").should_be_called().will_return(True)
        ifc.run("type.map_type_representations", related_object="element", relating_type="type").should_be_called()
        ifc.get_object("type").should_be_called().will_return("type_obj")
        root.link_object_data("type_obj", "obj").should_be_called()
        collector.assign("obj").should_be_called()
        root.is_opening_element("element").should_be_called().will_return(True)
        root.add_dynamic_opening_voids("element", "obj").should_be_called()
        subject.copy_class(ifc, collector, geometry, root, obj="obj")
