# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult, Yassine Oualid <dion@thinkmoult.com>
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

# ############################################################################ #

from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Union, Iterable

if TYPE_CHECKING:
    import bpy
    import ifcopenshell
    import bonsai.tool as tool


def load_resources(resource: tool.Resource) -> None:
    resource.load_resources()


def add_resource(
    tool_ifc: tool.Ifc,
    resource_tool: tool.Resource,
    ifc_class,
    parent_resource: Optional[ifcopenshell.entity_instance] = None,
) -> None:
    tool_ifc.run("resource.add_resource", ifc_class=ifc_class, parent_resource=parent_resource)
    resource_tool.load_resources()


def disable_editing_resource(resource_tool: tool.Resource) -> None:
    resource_tool.disable_editing_resource()


def disable_resource_editing_ui(resource_tool: tool.Resource) -> None:
    resource_tool.disable_resource_editing_ui()


def enable_editing_resource(resource_tool: tool.Resource, resource) -> None:
    resource_tool.enable_editing_resource(resource)
    resource_tool.load_resource_attributes(resource)


def edit_resource(ifc: tool.Ifc, resource_tool: tool.Resource, resource: ifcopenshell.entity_instance) -> None:
    attributes = resource_tool.get_resource_attributes()
    ifc.run("resource.edit_resource", resource=resource, attributes=attributes)
    resource_tool.load_resource_properties()
    resource_tool.disable_editing_resource()


def remove_resource(ifc: tool.Ifc, resource_tool: tool.Resource, resource: ifcopenshell.entity_instance) -> None:
    ifc.run("resource.remove_resource", resource=resource)
    resource_tool.load_resources()


def enable_editing_resource_time(
    ifc_tool, resource_tool: tool.Resource, resource: ifcopenshell.entity_instance
) -> None:
    resource_time = resource_tool.get_resource_time(resource)
    if resource_time is None:
        resource_time = ifc_tool.run("resource.add_resource_time", resource=resource)
    resource_tool.enable_editing_resource_time(resource)
    resource_tool.load_resource_time_attributes(resource_time)


def edit_resource_time(
    ifc: tool.Ifc, resource_tool: tool.Resource, resource_time: ifcopenshell.entity_instance
) -> None:
    attributes = resource_tool.get_resource_time_attributes()
    ifc.run("resource.edit_resource_time", resource_time=resource_time, attributes=attributes)
    resource_tool.disable_editing_resource()


def disable_editing_resource_time(resource_tool: tool.Resource) -> None:
    resource_tool.disable_editing_resource()


def calculate_resource_work(
    ifc: tool.Ifc, resource_tool: tool.Resource, resource: ifcopenshell.entity_instance
) -> None:
    if resource_tool.get_task_assignments(resource):
        ifc.run("resource.calculate_resource_work", resource=resource)
    else:
        nested_resources = resource_tool.get_nested_resources(resource)
        for nested_resource in nested_resources or []:
            ifc.run("resource.calculate_resource_work", resource=nested_resource)
    resource_tool.load_resources()


def enable_editing_resource_costs(resource_tool: tool.Resource, resource: ifcopenshell.entity_instance) -> None:
    resource_tool.enable_editing_resource_costs(resource)
    resource_tool.disable_editing_resource_cost_value()


def disable_editing_resource_cost_value(resource_tool: tool.Resource) -> None:
    resource_tool.disable_editing_resource_cost_value()


def enable_editing_resource_cost_value(resource_tool: tool.Resource, cost_value: ifcopenshell.entity_instance) -> None:
    resource_tool.enable_editing_cost_value_attributes(cost_value)
    resource_tool.load_cost_value_attributes(cost_value)


def enable_editing_resource_cost_value_formula(
    resource_tool: tool.Resource, cost_value: ifcopenshell.entity_instance
) -> None:
    resource_tool.enable_editing_resource_cost_value_formula(cost_value)


def edit_resource_cost_value_formula(
    ifc: tool.Ifc, resource_tool: tool.Resource, cost_value: ifcopenshell.entity_instance
) -> None:
    formula = resource_tool.get_resource_cost_value_formula()
    ifc.run("cost.edit_cost_value_formula", cost_value=cost_value, formula=formula)
    resource_tool.disable_editing_resource_cost_value()


def edit_resource_cost_value(
    ifc: tool.Ifc, resource_tool: tool.Resource, cost_value: ifcopenshell.entity_instance
) -> None:
    attributes = resource_tool.get_resource_cost_value_attributes()
    ifc.run("cost.edit_cost_value", cost_value=cost_value, attributes=attributes)
    resource_tool.disable_editing_resource_cost_value()


def enable_editing_resource_base_quantity(resource_tool: tool.Resource, resource: ifcopenshell.entity_instance) -> None:
    resource_tool.enable_editing_resource_base_quantity(resource)


def add_resource_quantity(ifc: tool.Ifc, ifc_class: str, resource: ifcopenshell.entity_instance) -> None:
    ifc.run("resource.add_resource_quantity", resource=resource, ifc_class=ifc_class)


def remove_resource_quantity(ifc: tool.Ifc, resource: ifcopenshell.entity_instance) -> None:
    ifc.run("resource.remove_resource_quantity", resource=resource)


def enable_editing_resource_quantity(
    resource_tool: tool.Resource, resource_quantity: ifcopenshell.entity_instance
) -> None:
    resource_tool.enable_editing_resource_quantity(resource_quantity)


def disable_editing_resource_quantity(resource_tool: tool.Resource) -> None:
    resource_tool.disable_editing_resource_quantity()


def edit_resource_quantity(
    resource_tool: tool.Resource, ifc: tool.Ifc, physical_quantity: ifcopenshell.entity_instance
) -> None:
    attributes = resource_tool.get_resource_quantity_attributes()
    ifc.run("resource.edit_resource_quantity", physical_quantity=physical_quantity, attributes=attributes)
    resource_tool.disable_editing_resource_quantity()


def import_resources(resource_tool: tool.Resource, file_path: str) -> None:
    resource_tool.import_resources(file_path)
    resource_tool.load_resources()


def expand_resource(resource_tool: tool.Resource, resource: ifcopenshell.entity_instance) -> None:
    resource_tool.expand_resource(resource)
    resource_tool.load_resources()


def contract_resource(resource_tool: tool.Resource, resource: ifcopenshell.entity_instance) -> None:
    resource_tool.contract_resource(resource)
    resource_tool.load_resources()


def assign_resource(
    ifc: tool.Ifc,
    spatial: tool.Spatial,
    resource: ifcopenshell.entity_instance,
    products: Optional[Iterable[ifcopenshell.entity_instance]] = None,
) -> None:
    if not products:
        products = spatial.get_selected_products()
    for product in products:
        rel = ifc.run("resource.assign_resource", relating_resource=resource, related_object=product)


def unassign_resource(
    ifc: tool.Ifc,
    spatial: tool.Spatial,
    resource: ifcopenshell.entity_instance,
    products: Optional[Iterable[ifcopenshell.entity_instance]] = None,
) -> None:
    if not products:
        products = spatial.get_selected_products()
    for product in products:
        ifc.run("resource.unassign_resource", relating_resource=resource, related_object=product)


def edit_productivity_pset(ifc: tool.Ifc, resource_tool: tool.Resource) -> None:
    resource = resource_tool.get_highlighted_resource()
    if resource is None:
        return
    productivity = resource_tool.get_productivity(resource)
    if productivity:
        pset = ifc.get().by_id(productivity["id"])
    else:
        pset = ifc.run("pset.add_pset", product=resource, name="EPset_Productivity")
    ifc.run("pset.edit_pset", pset=pset, properties=resource_tool.get_productivity_attributes())


def add_usage_constraint(
    ifc: tool.Ifc, resource_tool: tool.Resource, resource: ifcopenshell.entity_instance, reference_path: str
) -> None:
    metric = resource_tool.has_metric_constraint(resource, "Usage")
    if metric:
        return print("Must remove existing metric first")

    objective = ifc.run("constraint.add_objective")
    ifc.run("constraint.edit_objective", objective=objective, attributes={"ObjectiveQualifier": "PARAMETER"})
    metric = ifc.run("constraint.add_metric", objective=objective)
    ifc.run(
        "constraint.edit_metric",
        metric=metric,
        attributes={
            "ConstraintGrade": "HARD",
            "Benchmark": "EQUALTO",
        },
    )
    ifc.run("constraint.add_metric_reference", metric=metric, reference_path=reference_path)
    ifc.run("constraint.assign_constraint", products=[resource], constraint=objective)


def remove_usage_constraint(
    ifc: tool.Ifc, resource_tool: tool.Resource, resource: ifcopenshell.entity_instance, reference_path: str
) -> None:
    constraints = resource_tool.get_constraints(resource)
    for constraint in constraints:
        metrics = resource_tool.get_metrics(constraint)
        for metric in metrics:
            reference = resource_tool.get_metric_reference(metric, is_deep=True)
            if reference == reference_path:
                ifc.run("constraint.remove_metric", metric=metric)
                ifc.run("constraint.unassign_constraint", products=[resource], constraint=constraint)
                ifc.run("constraint.remove_constraint", constraint=constraint)


def go_to_resource(resource_tool: tool.Resource, resource: ifcopenshell.entity_instance) -> None:
    resource_tool.go_to_resource(resource)


def calculate_resource_usage(
    ifc: tool.Resource, resource_tool: tool.Resource, resource: ifcopenshell.entity_instance
) -> None:
    ifc.run("resource.calculate_resource_usage", resource=resource)
    resource_tool.load_resources()


def calculate_resource_quantity(resource_tool: tool.Resource, resource: ifcopenshell.entity_instance) -> None:
    resource_tool.calculate_resource_quantity(resource)
