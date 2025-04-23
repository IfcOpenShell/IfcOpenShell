# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021-2022 Dion Moult <dion@thinkmoult.com>, Yassine Oualid <yassine@sigmadimensions.com>
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

import bpy
import bonsai.tool as tool
import ifcopenshell
import ifcopenshell.util.constraint
import ifcopenshell.util.cost
import ifcopenshell.util.date
import ifcopenshell.util.resource
from typing import Any


def refresh():
    ResourceData.is_loaded = False


class ResourceData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "total_resources": cls.total_resources(),
            "resources": cls.resources(),
            "active_resource_ids": cls.active_resource_ids(),
            "cost_values": cls.cost_values(),
        }
        cls.is_loaded = True

    @classmethod
    def total_resources(cls) -> int:
        return len(tool.Ifc.get().by_type("IfcResource"))

    @classmethod
    def resources(cls) -> dict[int, dict[str, Any]]:
        results = {}
        for resource in tool.Ifc.get().by_type("IfcResource"):
            base_quantity = None
            if resource.BaseQuantity:
                base_quantity = resource.BaseQuantity.get_info()
                del base_quantity["Unit"]
            results[resource.id()] = {
                "type": resource.is_a(),
                "BaseQuantity": base_quantity,
            }
            results[resource.id()]["Benchmarks"] = cls.get_resource_benchmarks(resource)
            if resource.is_a() in ["IfcLaborResource", "IfcConstructionEquipmentResource"]:
                results[resource.id()]["Productivity"] = {}
                results[resource.id()]["InheritedProductivity"] = {}
                productivity = ifcopenshell.util.resource.get_productivity(resource, should_inherit=False)
                if productivity:
                    results[resource.id()]["Productivity"] = {
                        "id": productivity.get("id"),
                        "QuantityProduced": ifcopenshell.util.resource.get_quantity_produced(productivity),
                        "TimeConsumed": ifcopenshell.util.resource.get_unit_consumed(productivity),
                        "QuantityProducedName": ifcopenshell.util.resource.get_quantity_produced_name(productivity),
                    }
                inherited_productivity = ifcopenshell.util.resource.get_parent_productivity(resource)
                if inherited_productivity:
                    results[resource.id()]["InheritedProductivity"] = {
                        "QuantityProduced": ifcopenshell.util.resource.get_quantity_produced(inherited_productivity),
                        "TimeConsumed": ifcopenshell.util.resource.get_unit_consumed(inherited_productivity),
                        "QuantityProducedName": ifcopenshell.util.resource.get_quantity_produced_name(
                            inherited_productivity
                        ),
                    }
                if resource.Usage:
                    results[resource.id()]["ScheduleWork"] = (
                        ifcopenshell.util.date.readable_ifc_duration(resource.Usage.ScheduleWork)
                        if resource.Usage.ScheduleWork
                        else None
                    )
                    results[resource.id()]["ScheduleUsage"] = (
                        resource.Usage.ScheduleUsage if resource.Usage.ScheduleUsage else None
                    )
                if resource.IsNestedBy:
                    results[resource.id()]["DerivedScheduleWork"] = cls.sum_person_hours(resource)
        return results

    @classmethod
    def sum_person_hours(cls, resource: ifcopenshell.entity_instance) -> float:
        sum = 0
        nested_resources = ifcopenshell.util.resource.get_nested_resources(resource)
        for nested_resource in nested_resources or []:
            if not nested_resource.Usage or not nested_resource.Usage.ScheduleWork:
                continue
            duration = ifcopenshell.util.date.ifc2datetime(nested_resource.Usage.ScheduleWork)
            sum += duration.total_seconds() / 3600
        return round(float(sum), 2) if sum else 0

    @classmethod
    def get_resource_benchmarks(cls, resource: ifcopenshell.entity_instance) -> list[dict[str, Any]]:
        constraints = []
        for constraint in ifcopenshell.util.constraint.get_constraints(resource) or []:
            metrics = []
            for metric in ifcopenshell.util.constraint.get_metrics(constraint) or []:
                metrics.append(
                    {
                        "reference": ifcopenshell.util.constraint.get_metric_reference(metric),
                        "Benchmark": metric.Benchmark,
                        "ConstraintGrade": metric.ConstraintGrade,
                    }
                )
            constraints.append({"ObjectiveQualifier": constraint.ObjectiveQualifier, "metrics": metrics})
        return constraints

    @classmethod
    def cost_values(cls) -> list[dict[str, Any]]:
        results = []
        ifc_id = bpy.context.scene.BIMResourceProperties.active_resource_id
        if not ifc_id:
            return results
        resource = tool.Ifc.get().by_id(ifc_id)
        for cost_value in resource.BaseCosts or []:
            label = "{0:.2f}".format(ifcopenshell.util.cost.calculate_applied_value(resource, cost_value))
            label += " = {}".format(ifcopenshell.util.cost.serialise_cost_value(cost_value))
            results.append({"id": cost_value.id(), "label": label})
        return results

    @classmethod
    def active_resource_ids(cls) -> list[int]:
        obj = bpy.context.active_object
        element = tool.Ifc.get_entity(obj)
        if not element:
            return []
        results = []
        for rel in getattr(element, "HasAssignments", []) or []:
            if rel.is_a("IfcRelAssignsToResource"):
                results.append(rel.RelatingResource.id())
        return results
