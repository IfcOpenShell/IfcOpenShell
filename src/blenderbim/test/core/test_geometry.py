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

import blenderbim.core.geometry as subject
import test.core.test_style
from test.core.bootstrap import ifc, surveyor, geometry, style


class TestEditObjectPlacement:
    def predict(self, ifc, surveyor):
        ifc.get_entity("obj").should_be_called().will_return("element")
        surveyor.get_absolute_matrix("obj").should_be_called().will_return("matrix")
        ifc.run("geometry.edit_object_placement", product="element", matrix="matrix").should_be_called()

    def test_run(self, ifc, surveyor):
        self.predict(ifc, surveyor)
        subject.edit_object_placement(ifc, surveyor, obj="obj")


class TestAddRepresentation:
    def test_run(self, ifc, geometry, style, surveyor):
        TestEditObjectPlacement.predict(self, ifc, surveyor)

        # Add representation
        geometry.get_object_data("obj").should_be_called().will_return("data")
        geometry.get_cartesian_point_coordinate_offset("obj").should_be_called().will_return("coordinate_offset")
        geometry.get_total_representation_items("obj").should_be_called().will_return(1)
        geometry.should_force_faceted_brep().should_be_called().will_return(False)
        geometry.should_force_triangulation().should_be_called().will_return(True)
        ifc.run(
            "geometry.add_representation",
            context="context",
            blender_object="obj",
            geometry="data",
            coordinate_offset="coordinate_offset",
            total_items=1,
            should_force_faceted_brep=False,
            should_force_triangulation=True,
            ifc_representation_class="ifc_representation_class",
            profile_set_usage="profile_set_usage",
        ).should_be_called().will_return("representation")

        # Styles are relevant for meshes with faces only
        geometry.does_object_have_mesh_with_faces("obj").should_be_called().will_return(True)

        # Add styles
        geometry.get_object_materials_without_styles("obj").should_be_called().will_return(["material"])
        test.core.test_style.TestAddStyle.predict(self, ifc, style, obj="material")

        # Link style to representation items
        geometry.should_use_presentation_style_assignment().should_be_called().will_return(False)
        ifc.run(
            "style.assign_representation_styles",
            shape_representation="representation",
            styles=["style"],
            should_use_presentation_style_assignment=False,
        ).should_be_called()

        # Assign representation to product
        ifc.run("geometry.assign_representation", product="element", representation="representation").should_be_called()

        # Update mesh
        geometry.duplicate_object_data("obj").should_be_called().will_return("data")
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

    def test_not_handling_styles_if_representation_has_no_faces(self, ifc, geometry, style, surveyor):
        TestEditObjectPlacement.predict(self, ifc, surveyor)

        # Add representation
        geometry.get_object_data("obj").should_be_called().will_return("data")
        geometry.get_cartesian_point_coordinate_offset("obj").should_be_called().will_return("coordinate_offset")
        geometry.get_total_representation_items("obj").should_be_called().will_return(1)
        geometry.should_force_faceted_brep().should_be_called().will_return(False)
        geometry.should_force_triangulation().should_be_called().will_return(True)
        ifc.run(
            "geometry.add_representation",
            context="context",
            blender_object="obj",
            geometry="data",
            coordinate_offset="coordinate_offset",
            total_items=1,
            should_force_faceted_brep=False,
            should_force_triangulation=True,
            ifc_representation_class="ifc_representation_class",
            profile_set_usage="profile_set_usage",
        ).should_be_called().will_return("representation")

        # Styles are relevant for meshes with faces only
        geometry.does_object_have_mesh_with_faces("obj").should_be_called().will_return(False)

        # Assign representation to product
        ifc.run("geometry.assign_representation", product="element", representation="representation").should_be_called()

        # Update mesh
        geometry.duplicate_object_data("obj").should_be_called().will_return("data")
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
        TestEditObjectPlacement.predict(self, ifc, surveyor)

        # Add representation
        geometry.get_object_data("obj").should_be_called().will_return(None)
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
    def test_switching_to_a_freshly_loaded_representation(self, geometry):
        geometry.resolve_mapped_representation("mapped_rep").should_be_called().will_return("representation")
        geometry.get_representation_data("representation").should_be_called().will_return(None)
        geometry.import_representation(
            "obj", "representation", enable_dynamic_voids=True
        ).should_be_called().will_return("new_data")
        geometry.get_representation_name("representation").should_be_called().will_return("name")
        geometry.rename_object("new_data", "name").should_be_called()
        geometry.link("representation", "new_data").should_be_called()
        geometry.change_object_data("obj", "new_data", is_global=True).should_be_called()
        geometry.clear_modifiers("obj").should_be_called()
        geometry.is_body_representation("representation").should_be_called().will_return(True)
        geometry.create_dynamic_voids("obj").should_be_called()
        subject.switch_representation(
            geometry,
            obj="obj",
            representation="mapped_rep",
            should_reload=True,
            enable_dynamic_voids=True,
            is_global=True,
        )

    def test_switching_to_a_reloaded_representation_and_deleting_the_existing_data(self, geometry):
        geometry.resolve_mapped_representation("mapped_rep").should_be_called().will_return("representation")
        geometry.get_representation_data("representation").should_be_called().will_return("existing_data")
        geometry.import_representation(
            "obj", "representation", enable_dynamic_voids=True
        ).should_be_called().will_return("new_data")
        geometry.get_representation_name("representation").should_be_called().will_return("name")
        geometry.rename_object("new_data", "name").should_be_called()
        geometry.link("representation", "new_data").should_be_called()
        geometry.change_object_data("obj", "new_data", is_global=True).should_be_called()
        geometry.delete_data("existing_data").should_be_called()
        geometry.clear_modifiers("obj").should_be_called()
        geometry.is_body_representation("representation").should_be_called().will_return(True)
        geometry.create_dynamic_voids("obj").should_be_called()
        subject.switch_representation(
            geometry,
            obj="obj",
            representation="mapped_rep",
            should_reload=True,
            enable_dynamic_voids=True,
            is_global=True,
        )

    def test_switching_to_an_existing_representation(self, geometry):
        geometry.resolve_mapped_representation("mapped_rep").should_be_called().will_return("representation")
        geometry.get_representation_data("representation").should_be_called().will_return("data")
        geometry.change_object_data("obj", "data", is_global=True).should_be_called()
        geometry.clear_modifiers("obj").should_be_called()
        geometry.is_body_representation("representation").should_be_called().will_return(True)
        geometry.create_dynamic_voids("obj").should_be_called()
        subject.switch_representation(
            geometry,
            obj="obj",
            representation="mapped_rep",
            should_reload=False,
            enable_dynamic_voids=True,
            is_global=True,
        )

    def test_switching_to_non_dynamic_baked_voids(self, geometry):
        geometry.resolve_mapped_representation("mapped_rep").should_be_called().will_return("representation")
        geometry.get_representation_data("representation").should_be_called().will_return("data")
        geometry.change_object_data("obj", "data", is_global=False).should_be_called()
        geometry.clear_modifiers("obj").should_be_called()
        subject.switch_representation(
            geometry,
            obj="obj",
            representation="mapped_rep",
            should_reload=False,
            enable_dynamic_voids=False,
            is_global=False,
        )
