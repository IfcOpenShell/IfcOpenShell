# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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

from __future__ import annotations
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    import bpy
    import ifcopenshell
    import bonsai.tool as tool


def create_project(
    ifc: tool.Ifc,
    georeference: tool.Georeference,
    project: tool.Project,
    spatial: tool.Spatial,
    schema: str,
    template: Optional[str] = None,
) -> None:
    if ifc.get():
        return

    ifc.set(ifc.run("project.create_file", version=schema))

    if schema == "IFC2X3":
        person = project.run_owner_add_person()
        organisation = project.run_owner_add_organisation()
        user = project.run_owner_add_person_and_organisation(person=person, organisation=organisation)
        project.run_owner_set_user(user=user)

    project_obj = project.create_empty("My Project")
    site = project.create_empty("My Site")
    building = project.create_empty("My Building")
    storey = project.create_empty("My Storey")

    project.run_root_assign_class(obj=project_obj, ifc_class="IfcProject", should_add_representation=False)
    project.run_unit_assign_scene_units()

    model = project.run_context_add_context(context_type="Model", context_identifier="", target_view="", parent=0)
    body = project.run_context_add_context(
        context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
    )
    project.run_context_add_context(
        context_type="Model", context_identifier="Axis", target_view="GRAPH_VIEW", parent=model
    )
    project.run_context_add_context(
        context_type="Model", context_identifier="Box", target_view="MODEL_VIEW", parent=model
    )
    project.run_context_add_context(
        context_type="Model", context_identifier="Annotation", target_view="SECTION_VIEW", parent=model
    )
    project.run_context_add_context(
        context_type="Model", context_identifier="Annotation", target_view="ELEVATION_VIEW", parent=model
    )
    project.run_context_add_context(
        context_type="Model", context_identifier="Annotation", target_view="MODEL_VIEW", parent=model
    )
    project.run_context_add_context(
        context_type="Model", context_identifier="Annotation", target_view="PLAN_VIEW", parent=model
    )
    project.run_context_add_context(
        context_type="Model", context_identifier="Profile", target_view="ELEVATION_VIEW", parent=model
    )
    plan = project.run_context_add_context(context_type="Plan", context_identifier="", target_view="", parent=0)
    project.run_context_add_context(
        context_type="Plan", context_identifier="Axis", target_view="GRAPH_VIEW", parent=plan
    )
    project.run_context_add_context(
        context_type="Plan", context_identifier="Body", target_view="PLAN_VIEW", parent=plan
    )
    project.run_context_add_context(
        context_type="Plan", context_identifier="Annotation", target_view="PLAN_VIEW", parent=plan
    )
    project.run_context_add_context(
        context_type="Plan", context_identifier="Annotation", target_view="REFLECTED_PLAN_VIEW", parent=plan
    )

    project.run_root_assign_class(obj=site, ifc_class="IfcSite", context=body)
    project.run_root_assign_class(obj=building, ifc_class="IfcBuilding", context=body)
    project.run_root_assign_class(obj=storey, ifc_class="IfcBuildingStorey", context=body)

    project.run_aggregate_assign_object(relating_obj=project_obj, related_obj=site)
    project.run_aggregate_assign_object(relating_obj=site, related_obj=building)
    project.run_aggregate_assign_object(relating_obj=building, related_obj=storey)

    project.set_context(body)
    spatial.run_spatial_import_spatial_decomposition()
    if default_container := spatial.guess_default_container():
        spatial.set_default_container(default_container)

    if template:
        project.append_all_types_from_template(template)

    project.load_default_thumbnails()
    project.set_default_context()
    project.set_default_modeling_dimensions()
    project.run_root_reload_grid_decorator()
    georeference.set_model_origin()
