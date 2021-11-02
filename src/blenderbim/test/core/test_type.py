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

import blenderbim.core.type as subject
from test.core.bootstrap import ifc, type


class TestAssignType:
    def test_assigning_and_switching_preferably_to_a_body_representation(self, ifc, type):
        ifc.run("type.assign_type", related_object="element", relating_type="type").should_be_called()
        type.has_material_usage("element").should_be_called().will_return(False)
        type.get_body_representation("element").should_be_called().will_return("mapped_rep")
        ifc.get_object("element").should_be_called().will_return("obj")
        type.has_dynamic_voids("obj").should_be_called().will_return(False)
        type.run_geometry_switch_representation(
            obj="obj", representation="mapped_rep", should_reload=False, enable_dynamic_voids=False, is_global=False
        ).should_be_called()
        type.disable_editing("obj").should_be_called()
        subject.assign_type(ifc, type, element="element", type="type")

    def test_assigning_and_switching_to_any_representation_as_a_fallback(self, ifc, type):
        ifc.run("type.assign_type", related_object="element", relating_type="type").should_be_called()
        type.has_material_usage("element").should_be_called().will_return(False)
        type.get_body_representation("element").should_be_called().will_return(None)
        type.get_any_representation("element").should_be_called().will_return("mapped_rep")
        ifc.get_object("element").should_be_called().will_return("obj")
        type.has_dynamic_voids("obj").should_be_called().will_return(False)
        type.run_geometry_switch_representation(
            obj="obj", representation="mapped_rep", should_reload=False, enable_dynamic_voids=False, is_global=False
        ).should_be_called()
        type.disable_editing("obj").should_be_called()
        subject.assign_type(ifc, type, element="element", type="type")

    def test_assigning_and_not_changing_representation_if_there_is_no_representation_to_change_to(self, ifc, type):
        ifc.run("type.assign_type", related_object="element", relating_type="type").should_be_called()
        type.has_material_usage("element").should_be_called().will_return(False)
        type.get_body_representation("element").should_be_called().will_return(None)
        type.get_any_representation("element").should_be_called().will_return(None)
        ifc.get_object("element").should_be_called().will_return("obj")
        type.disable_editing("obj").should_be_called()
        subject.assign_type(ifc, type, element="element", type="type")

    def test_updating_an_existing_body_if_there_is_a_parametric_material_usage(self, ifc, type):
        ifc.run("type.assign_type", related_object="element", relating_type="type").should_be_called()

        type.has_material_usage("element").should_be_called().will_return(True)
        type.get_body_representation("element").should_be_called().will_return("representation")
        type.get_representation_context("representation").should_be_called().will_return("context")
        ifc.run(
            "geometry.unassign_representation", product="element", representation="representation"
        ).should_be_called()
        ifc.run("geometry.remove_representation", representation="representation").should_be_called()
        type.get_ifc_representation_class("element").should_be_called().will_return("class")
        type.get_profile_set_usage("element").should_be_called().will_return("usage")
        type.run_geometry_add_representation(
            obj="obj", context="context", ifc_representation_class="class", profile_set_usage="usage"
        ).should_be_called().will_return("mapped_rep")

        ifc.get_object("element").should_be_called().will_return("obj")
        type.has_dynamic_voids("obj").should_be_called().will_return(False)
        type.run_geometry_switch_representation(
            obj="obj", representation="mapped_rep", should_reload=True, enable_dynamic_voids=False, is_global=False
        ).should_be_called()
        type.disable_editing("obj").should_be_called()
        subject.assign_type(ifc, type, element="element", type="type")

    def test_creating_a_new_body_if_there_is_a_parametric_material_usage(self, ifc, type):
        ifc.run("type.assign_type", related_object="element", relating_type="type").should_be_called()

        type.has_material_usage("element").should_be_called().will_return(True)
        type.get_body_representation("element").should_be_called().will_return(None)
        type.get_body_context().should_be_called().will_return("context")
        type.get_ifc_representation_class("element").should_be_called().will_return("class")
        type.get_profile_set_usage("element").should_be_called().will_return("usage")
        type.run_geometry_add_representation(
            obj="obj", context="context", ifc_representation_class="class", profile_set_usage="usage"
        ).should_be_called().will_return("mapped_rep")

        ifc.get_object("element").should_be_called().will_return("obj")
        type.has_dynamic_voids("obj").should_be_called().will_return(False)
        type.run_geometry_switch_representation(
            obj="obj", representation="mapped_rep", should_reload=True, enable_dynamic_voids=False, is_global=False
        ).should_be_called()
        type.disable_editing("obj").should_be_called()
        subject.assign_type(ifc, type, element="element", type="type")
