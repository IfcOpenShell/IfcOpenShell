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

import bonsai.core.geometry as subject
import test.core.test_style
from test.core.bootstrap import ifc, surveyor, geometry, style


class TestEditObjectPlacement:
    def predict(self, ifc, geometry, surveyor):
        ifc.get_entity("obj").should_be_called().will_return("element")
        geometry.clear_cache("element").should_be_called()
        geometry.clear_scale("obj").should_be_called()
        geometry.get_blender_offset_type("obj").should_be_called()
        surveyor.get_absolute_matrix("obj").should_be_called().will_return("matrix")
        ifc.run("geometry.edit_object_placement", product="element", matrix="matrix").should_be_called()
        geometry.record_object_position("obj").should_be_called()

    def test_run(self, ifc, geometry, surveyor):
        self.predict(ifc, geometry, surveyor)
        subject.edit_object_placement(ifc, geometry, surveyor, obj="obj")


class TestAddRepresentation:
    def test_run(self, ifc, geometry, style, surveyor):
        TestEditObjectPlacement.predict(self, ifc, geometry, surveyor)

        # Add representation
        geometry.get_object_data("obj").should_be_called().will_return("data")
        geometry.is_data_supported_for_adding_representation("data").should_be_called().will_return(True)
        geometry.get_cartesian_point_offset("obj").should_be_called().will_return("coordinate_offset")
        geometry.get_total_representation_items("obj").should_be_called().will_return(1)
        geometry.should_force_faceted_brep().should_be_called().will_return(False)
        geometry.should_force_triangulation().should_be_called().will_return(True)
        geometry.should_generate_uvs("obj").should_be_called().will_return(True)
        ifc.run(
            "geometry.add_representation",
            context="context",
            blender_object="obj",
            geometry="data",
            coordinate_offset="coordinate_offset",
            total_items=1,
            should_force_faceted_brep=False,
            should_force_triangulation=True,
            should_generate_uvs=True,
            ifc_representation_class="ifc_representation_class",
            profile_set_usage="profile_set_usage",
        ).should_be_called().will_return("representation")

        # Styles are relevant for body representations only (as a simplification)
        geometry.is_body_representation("representation").should_be_called().will_return(True)

        # Add styles
        geometry.get_object_materials_without_styles("obj").should_be_called().will_return(["material"])
        geometry.run_style_add_style(obj="material").should_be_called()
        geometry.get_styles("obj").should_be_called().will_return(["style"])

        # Link style to representation items
        geometry.should_use_presentation_style_assignment().should_be_called().will_return(False)
        ifc.run(
            "style.assign_representation_styles",
            shape_representation="representation",
            styles=["style"],
            should_use_presentation_style_assignment=False,
        ).should_be_called()
        geometry.record_object_materials("obj").should_be_called()

        # Assign representation to product
        ifc.run("geometry.assign_representation", product="element", representation="representation").should_be_called()

        # Update mesh
        geometry.duplicate_object_data("obj").should_be_called().will_return("data")
        geometry.change_object_data("obj", "data", is_global=True).should_be_called()
        geometry.get_representation_name("representation").should_be_called().will_return("name")
        geometry.rename_object("data", "name").should_be_called()
        geometry.link("representation", "data").should_be_called()

        assert (
            subject.add_representation(
                ifc,
                geometry,
                style,
                surveyor,
                obj="obj",
                context="context",
                ifc_representation_class="ifc_representation_class",
                profile_set_usage="profile_set_usage",
            )
            == "representation"
        )

    def test_not_handling_styles_if_not_a_body_representation(self, ifc, geometry, style, surveyor):
        TestEditObjectPlacement.predict(self, ifc, geometry, surveyor)

        # Add representation
        geometry.get_object_data("obj").should_be_called().will_return("data")
        geometry.is_data_supported_for_adding_representation("data").should_be_called().will_return(True)
        geometry.get_cartesian_point_offset("obj").should_be_called().will_return("coordinate_offset")
        geometry.get_total_representation_items("obj").should_be_called().will_return(1)
        geometry.should_force_faceted_brep().should_be_called().will_return(False)
        geometry.should_force_triangulation().should_be_called().will_return(True)
        geometry.should_generate_uvs("obj").should_be_called().will_return(True)
        ifc.run(
            "geometry.add_representation",
            context="context",
            blender_object="obj",
            geometry="data",
            coordinate_offset="coordinate_offset",
            total_items=1,
            should_force_faceted_brep=False,
            should_force_triangulation=True,
            should_generate_uvs=True,
            ifc_representation_class="ifc_representation_class",
            profile_set_usage="profile_set_usage",
        ).should_be_called().will_return("representation")

        # Styles are relevant for body representations only (as a simplification)
        geometry.is_body_representation("representation").should_be_called().will_return(False)

        # Assign representation to product
        ifc.run("geometry.assign_representation", product="element", representation="representation").should_be_called()

        # Update mesh
        geometry.duplicate_object_data("obj").should_be_called().will_return("data")
        geometry.change_object_data("obj", "data", is_global=True).should_be_called()
        geometry.get_representation_name("representation").should_be_called().will_return("name")
        geometry.rename_object("data", "name").should_be_called()
        geometry.link("representation", "data").should_be_called()

        assert (
            subject.add_representation(
                ifc,
                geometry,
                style,
                surveyor,
                obj="obj",
                context="context",
                ifc_representation_class="ifc_representation_class",
                profile_set_usage="profile_set_usage",
            )
            == "representation"
        )

    def test_only_updating_the_placement_if_there_is_no_object_data(self, ifc, geometry, style, surveyor):
        TestEditObjectPlacement.predict(self, ifc, geometry, surveyor)

        # Add representation
        geometry.get_object_data("obj").should_be_called().will_return("data")
        geometry.is_data_supported_for_adding_representation("data").should_be_called().will_return(False)
        assert (
            subject.add_representation(
                ifc,
                geometry,
                style,
                surveyor,
                obj="obj",
                context="context",
                ifc_representation_class="ifc_representation_class",
                profile_set_usage="profile_set_usage",
            )
            is None
        )

    def test_doing_nothing_if_not_an_ifc_element(self, ifc, geometry, style, surveyor):
        ifc.get_entity("obj").should_be_called().will_return(None)
        assert (
            subject.add_representation(
                ifc,
                geometry,
                style,
                surveyor,
                obj="obj",
                context="context",
                ifc_representation_class="ifc_representation_class",
                profile_set_usage="profile_set_usage",
            )
            is None
        )


class TestSwitchRepresentation:
    def test_switching_to_a_representation(self, ifc, geometry):
        ifc.is_edited("obj").should_be_called().will_return(False)
        geometry.get_object_data("obj").should_be_called().will_return("current_obj_data")
        geometry.reimport_element_representations("obj", "mapped_rep", apply_openings=True).should_be_called()
        subject.switch_representation(
            ifc,
            geometry,
            obj="obj",
            representation="mapped_rep",
            should_reload=True,
            is_global=True,
            should_sync_changes_first=True,
            apply_openings=True,
        )

    def test_updating_a_representation_if_the_blender_object_has_been_edited_prior_to_switching(self, ifc, geometry):
        ifc.is_edited("obj").should_be_called().will_return(True)
        geometry.is_box_representation("mapped_rep").should_be_called().will_return(False)
        geometry.get_representation_id("mapped_rep").should_be_called().will_return("representation_id")
        geometry.run_geometry_update_representation(obj="obj").should_be_called()
        geometry.does_representation_id_exist("representation_id").should_be_called().will_return(True)
        geometry.get_object_data("obj").should_be_called().will_return("current_obj_data")
        geometry.reimport_element_representations("obj", "mapped_rep", apply_openings=True).should_be_called()
        subject.switch_representation(
            ifc,
            geometry,
            obj="obj",
            representation="mapped_rep",
            should_reload=False,
            is_global=False,
            should_sync_changes_first=True,
        )

    def test_not_switching_if_an_updated_representation_is_the_same_one_we_were_going_to_switch_to(self, ifc, geometry):
        ifc.is_edited("obj").should_be_called().will_return(True)
        geometry.is_box_representation("mapped_rep").should_be_called().will_return(False)
        geometry.get_representation_id("mapped_rep").should_be_called().will_return("representation_id")
        geometry.run_geometry_update_representation(obj="obj").should_be_called()
        geometry.does_representation_id_exist("representation_id").should_be_called().will_return(False)
        subject.switch_representation(
            ifc,
            geometry,
            obj="obj",
            representation="mapped_rep",
            should_reload=False,
            is_global=False,
            should_sync_changes_first=True,
        )


class TestGetRepresentationIfcParameters:
    def test_run(self, geometry):
        geometry.get_object_data("obj").should_be_called().will_return("data")
        geometry.import_representation_parameters("data").should_be_called()
        subject.get_representation_ifc_parameters(geometry, obj="obj", should_sync_changes_first=False)


class TestRemoveRepresentation:
    def test_removing_an_actively_used_mapped_representation_by_remapping_usages_to_an_empty(self, ifc, geometry):
        ifc.get_entity("obj").should_be_called().will_return("element")
        geometry.get_element_type("element").should_be_called().will_return("type")
        geometry.is_mapped_representation("mapped_rep").should_be_called().will_return(False)
        geometry.is_type_product("element").should_be_called().will_return(True)
        geometry.resolve_mapped_representation("mapped_rep").should_be_called().will_return("representation")
        geometry.get_representation_data("representation").should_be_called().will_return("data")
        geometry.has_data_users("data").should_be_called().will_return(True)
        geometry.get_elements_of_type("type").should_be_called().will_return(["element"])
        ifc.get_object("element").should_be_called().will_return("obj")
        geometry.switch_from_representation("obj", "representation").should_be_called()
        ifc.get_object("type").should_be_called().will_return("type_obj")
        geometry.switch_from_representation("type_obj", "representation").should_be_called()
        ifc.run("geometry.unassign_representation", product="type", representation="representation").should_be_called()
        ifc.run("geometry.remove_representation", representation="representation").should_be_called()
        geometry.delete_data("data").should_be_called()
        subject.remove_representation(ifc, geometry, obj="obj", representation="mapped_rep")

    def test_removing_an_unused_mapped_representation(self, ifc, geometry):
        ifc.get_entity("obj").should_be_called().will_return("element")
        geometry.get_element_type("element").should_be_called().will_return("type")
        geometry.is_mapped_representation("mapped_rep").should_be_called().will_return(True)
        geometry.resolve_mapped_representation("mapped_rep").should_be_called().will_return("representation")
        geometry.get_representation_data("representation").should_be_called().will_return(None)
        ifc.run("geometry.unassign_representation", product="type", representation="representation").should_be_called()
        ifc.run("geometry.remove_representation", representation="representation").should_be_called()
        subject.remove_representation(ifc, geometry, obj="obj", representation="mapped_rep")

    def test_remove_a_mapped_representation_by_an_element_with_no_type(self, ifc, geometry):
        ifc.get_entity("obj").should_be_called().will_return("element")
        geometry.get_element_type("element").should_be_called().will_return(None)
        geometry.get_representation_data("representation").should_be_called().will_return("data")
        geometry.has_data_users("data").should_be_called().will_return(True)
        geometry.switch_from_representation("obj", "representation").should_be_called()
        ifc.run(
            "geometry.unassign_representation", product="element", representation="representation"
        ).should_be_called()
        ifc.run("geometry.remove_representation", representation="representation").should_be_called()
        geometry.delete_data("data").should_be_called()
        subject.remove_representation(ifc, geometry, obj="obj", representation="representation")

    def test_removing_an_actively_used_representation(self, ifc, geometry):
        ifc.get_entity("obj").should_be_called().will_return("element")
        geometry.get_element_type("element").should_be_called().will_return("type")
        geometry.is_mapped_representation("representation").should_be_called().will_return(False)
        geometry.is_type_product("element").should_be_called().will_return(False)
        geometry.get_representation_data("representation").should_be_called().will_return("data")
        geometry.has_data_users("data").should_be_called().will_return(True)
        geometry.switch_from_representation("obj", "representation").should_be_called()
        ifc.run(
            "geometry.unassign_representation", product="element", representation="representation"
        ).should_be_called()
        ifc.run("geometry.remove_representation", representation="representation").should_be_called()
        geometry.delete_data("data").should_be_called()
        subject.remove_representation(ifc, geometry, obj="obj", representation="representation")

    def test_removing_an_unused_representation(self, ifc, geometry):
        ifc.get_entity("obj").should_be_called().will_return("element")
        geometry.get_element_type("element").should_be_called().will_return("type")
        geometry.is_mapped_representation("representation").should_be_called().will_return(False)
        geometry.is_type_product("element").should_be_called().will_return(False)
        geometry.get_representation_data("representation").should_be_called().will_return(None)
        ifc.run(
            "geometry.unassign_representation", product="element", representation="representation"
        ).should_be_called()
        ifc.run("geometry.remove_representation", representation="representation").should_be_called()
        subject.remove_representation(ifc, geometry, obj="obj", representation="representation")


class TestSelectConnection:
    def test_run(self, geometry):
        geometry.select_connection("connection").should_be_called()
        subject.select_connection(geometry, connection="connection")


class TestRemoveConnection:
    def test_run(self, geometry):
        geometry.remove_connection("connection").should_be_called()
        subject.remove_connection(geometry, connection="connection")
