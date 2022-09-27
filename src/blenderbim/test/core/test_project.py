# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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


import blenderbim.core.project as subject
from test.core.bootstrap import ifc, project


class TestCreateProject:
    def test_do_nothing_if_a_project_already_exists(self, ifc, project):
        ifc.get().should_be_called().will_return("ifc")
        subject.create_project(ifc, project, schema="IFC4", template=None)

    def test_create_an_ifc4_project(self, ifc, project):
        ifc.get().should_be_called().will_return(None)
        ifc.run("project.create_file", version="IFC4").should_be_called().will_return("ifc")
        ifc.set("ifc").should_be_called()

        project.create_empty("My Project").should_be_called().will_return("project")
        project.create_empty("My Site").should_be_called().will_return("site")
        project.create_empty("My Building").should_be_called().will_return("building")
        project.create_empty("My Storey").should_be_called().will_return("storey")
        project.run_root_assign_class(obj="project", ifc_class="IfcProject").should_be_called()
        project.run_unit_assign_scene_units().should_be_called()

        project.run_context_add_context(
            context_type="Model", context_identifier="", target_view="", parent=0
        ).should_be_called().will_return("model")
        project.run_context_add_context(
            context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent="model"
        ).should_be_called().will_return("body")
        project.run_context_add_context(
            context_type="MODEL", context_identifier="Axis", target_view="GRAPH_VIEW", parent="model"
        ).should_be_called()
        project.run_context_add_context(
            context_type="Model", context_identifier="Box", target_view="MODEL_VIEW", parent="model"
        ).should_be_called()
        project.run_context_add_context(
            context_type="Plan", context_identifier="", target_view="", parent=0
        ).should_be_called().will_return("plan")
        project.run_context_add_context(
            context_type="Plan", context_identifier="Axis", target_view="GRAPH_VIEW", parent="plan"
        ).should_be_called()
        project.run_context_add_context(
            context_type="Plan", context_identifier="Annotation", target_view="PLAN_VIEW", parent="plan"
        ).should_be_called()
        project.run_context_add_context(
            context_type="Plan", context_identifier="Annotation", target_view="SECTION_VIEW", parent="plan"
        ).should_be_called()
        project.run_context_add_context(
            context_type="Plan", context_identifier="Annotation", target_view="ELEVATION_VIEW", parent="plan"
        ).should_be_called()

        project.run_root_assign_class(obj="site", ifc_class="IfcSite", context="body").should_be_called()
        project.run_root_assign_class(obj="building", ifc_class="IfcBuilding", context="body").should_be_called()
        project.run_root_assign_class(obj="storey", ifc_class="IfcBuildingStorey", context="body").should_be_called()

        project.run_aggregate_assign_object(relating_obj="project", related_obj="site").should_be_called()
        project.run_aggregate_assign_object(relating_obj="site", related_obj="building").should_be_called()
        project.run_aggregate_assign_object(relating_obj="building", related_obj="storey").should_be_called()

        project.set_context("body").should_be_called()
        project.set_active_spatial_element("storey").should_be_called()

        subject.create_project(ifc, project, schema="IFC4", template=None)

    def test_appending_project_template_types_if_specified(self, ifc, project):
        ifc.get().should_be_called().will_return(None)
        ifc.run("project.create_file", version="IFC4").should_be_called().will_return("ifc")
        ifc.set("ifc").should_be_called()

        project.create_empty("My Project").should_be_called().will_return("project")
        project.create_empty("My Site").should_be_called().will_return("site")
        project.create_empty("My Building").should_be_called().will_return("building")
        project.create_empty("My Storey").should_be_called().will_return("storey")
        project.run_root_assign_class(obj="project", ifc_class="IfcProject").should_be_called()
        project.run_unit_assign_scene_units().should_be_called()

        project.run_context_add_context(
            context_type="Model", context_identifier="", target_view="", parent=0
        ).should_be_called().will_return("model")
        project.run_context_add_context(
            context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent="model"
        ).should_be_called().will_return("body")
        project.run_context_add_context(
            context_type="Model", context_identifier="Axis", target_view="GRAPH_VIEW", parent="model"
        ).should_be_called()
        project.run_context_add_context(
            context_type="Model", context_identifier="Box", target_view="MODEL_VIEW", parent="model"
        ).should_be_called()
        project.run_context_add_context(
            context_type="Plan", context_identifier="", target_view="", parent=0
        ).should_be_called().will_return("plan")
        project.run_context_add_context(
            context_type="Plan", context_identifier="Axis", target_view="GRAPH_VIEW", parent="plan"
        ).should_be_called()
        project.run_context_add_context(
            context_type="Plan", context_identifier="Annotation", target_view="PLAN_VIEW", parent="plan"
        ).should_be_called()
        project.run_context_add_context(
            context_type="Plan", context_identifier="Annotation", target_view="SECTION_VIEW", parent="plan"
        ).should_be_called()
        project.run_context_add_context(
            context_type="Plan", context_identifier="Annotation", target_view="ELEVATION_VIEW", parent="plan"
        ).should_be_called()

        project.run_root_assign_class(obj="site", ifc_class="IfcSite", context="body").should_be_called()
        project.run_root_assign_class(obj="building", ifc_class="IfcBuilding", context="body").should_be_called()
        project.run_root_assign_class(obj="storey", ifc_class="IfcBuildingStorey", context="body").should_be_called()

        project.run_aggregate_assign_object(relating_obj="project", related_obj="site").should_be_called()
        project.run_aggregate_assign_object(relating_obj="site", related_obj="building").should_be_called()
        project.run_aggregate_assign_object(relating_obj="building", related_obj="storey").should_be_called()

        project.set_context("body").should_be_called()
        project.set_active_spatial_element("storey").should_be_called()

        project.append_all_types_from_template("template").should_be_called()

        subject.create_project(ifc, project, schema="IFC4", template="template")

    def test_create_an_ifc2x3_project_with_owner_defaults(self, ifc, project):
        ifc.get().should_be_called().will_return(None)
        ifc.run("project.create_file", version="IFC2X3").should_be_called().will_return("ifc")
        ifc.set("ifc").should_be_called()

        project.run_owner_add_person().should_be_called().will_return("person")
        project.run_owner_add_organisation().should_be_called().will_return("organisation")
        project.run_owner_add_person_and_organisation(
            person="person", organisation="organisation"
        ).should_be_called().will_return("user")
        project.run_owner_set_user(user="user").should_be_called()

        project.create_empty("My Project").should_be_called().will_return("project")
        project.create_empty("My Site").should_be_called().will_return("site")
        project.create_empty("My Building").should_be_called().will_return("building")
        project.create_empty("My Storey").should_be_called().will_return("storey")
        project.run_root_assign_class(obj="project", ifc_class="IfcProject").should_be_called()
        project.run_unit_assign_scene_units().should_be_called()

        project.run_context_add_context(
            context_type="Model", context_identifier="", target_view="", parent=0
        ).should_be_called().will_return("model")
        project.run_context_add_context(
            context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent="model"
        ).should_be_called().will_return("body")
        project.run_context_add_context(
            context_type="Model", context_identifier="Axis", target_view="GRAPH_VIEW", parent="model"
        ).should_be_called()
        project.run_context_add_context(
            context_type="Model", context_identifier="Box", target_view="MODEL_VIEW", parent="model"
        ).should_be_called()
        project.run_context_add_context(
            context_type="Plan", context_identifier="", target_view="", parent=0
        ).should_be_called().will_return("plan")
        project.run_context_add_context(
            context_type="Plan", context_identifier="Axis", target_view="GRAPH_VIEW", parent="plan"
        ).should_be_called()
        project.run_context_add_context(
            context_type="Plan", context_identifier="Annotation", target_view="PLAN_VIEW", parent="plan"
        ).should_be_called()
        project.run_context_add_context(
            context_type="Plan", context_identifier="Annotation", target_view="SECTION_VIEW", parent="plan"
        ).should_be_called()
        project.run_context_add_context(
            context_type="Plan", context_identifier="Annotation", target_view="ELEVATION_VIEW", parent="plan"
        ).should_be_called()

        project.run_root_assign_class(obj="site", ifc_class="IfcSite", context="body").should_be_called()
        project.run_root_assign_class(obj="building", ifc_class="IfcBuilding", context="body").should_be_called()
        project.run_root_assign_class(obj="storey", ifc_class="IfcBuildingStorey", context="body").should_be_called()

        project.run_aggregate_assign_object(relating_obj="project", related_obj="site").should_be_called()
        project.run_aggregate_assign_object(relating_obj="site", related_obj="building").should_be_called()
        project.run_aggregate_assign_object(relating_obj="building", related_obj="storey").should_be_called()

        project.set_context("body").should_be_called()
        project.set_active_spatial_element("storey").should_be_called()

        subject.create_project(ifc, project, schema="IFC2X3", template=None)
