# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

import ifcopenshell.util.element
import ifcopenshell.util.date


def get_productivity(resource, should_inherit=True):
    productivity = ifcopenshell.util.element.get_psets(resource).get("EPset_Productivity", None)
    if should_inherit and not productivity:
        #Note: This is not part of the Schema - but it makes sense to inherit from parent
        productivity = get_parent_productivity(resource)
    return productivity

def get_parent_productivity(resource):
    if not resource.Nests:
        return
    else:
        parent_resource = resource.Nests[0].RelatingObject
        productivity = ifcopenshell.util.element.get_psets(parent_resource).get("EPset_Productivity", None)
        return productivity


def get_unit_consumed(productivity):
    duration = productivity.get("BaseQuantityConsumed", None)
    if not duration:
        return
    return ifcopenshell.util.date.ifc2datetime(duration)


def get_quantity_produced(productivity):
    if not productivity:
        return 0
    return productivity.get("BaseQuantityProducedValue", 0)


def get_quantity_produced_name(productivity):
    if not productivity:
        return ""
    return productivity.get("BaseQuantityProducedName", "")


def get_total_quantity_produced(resource, quantity_name_in_process):
    def get_product_quantity(product, quantity_name):
        psets = ifcopenshell.util.element.get_psets(product)
        for pset in psets.values():
            for name, value in pset.items():
                if name == quantity_name:
                    return float(value)

    total = 0
    products = get_parametric_resource_products(resource)
    if quantity_name_in_process == "Count":
        total = len(products)
    else:
        for product in products:
            total += get_product_quantity(product, quantity_name_in_process) or 0
    return total


def get_parametric_resource_products(resource):
    products = []
    for rel in resource.HasAssignments or []:
        if not rel.is_a("IfcRelAssignsToProcess"):
            continue
        for rel2 in rel.RelatingProcess.HasAssignments or []:
            if not rel2.is_a("IfcRelAssignsToProduct"):
                continue
            products.append(rel2.RelatingProduct)
    return products

def get_task_assignments(resource):
    for rel in resource.HasAssignments or []:
        if not rel.is_a("IfcRelAssignsToProcess"):
            continue
        return rel.RelatingProcess


def get_resource_required_work(resource):
    productivity = get_productivity(resource)
    if productivity:
        quantity_produced = get_quantity_produced(productivity)
        time_consumed = get_unit_consumed(productivity)
        quantity_name_in_process = get_quantity_produced_name(productivity)
        total_quantity_to_produce = get_total_quantity_produced(resource, quantity_name_in_process)
        if not time_consumed or not quantity_produced or not total_quantity_to_produce:
            return
        iso_string = ""
        if "T" in productivity.get("BaseQuantityConsumed", ""):
            seconds = (time_consumed.days * 24 * 60 * 60) + time_consumed.seconds
            productivity_ratio = seconds / quantity_produced
            required_work = total_quantity_to_produce * productivity_ratio
            iso_string = f"PT{required_work / 60 / 60}H"
        else:
            days = time_consumed.days + (time_consumed.seconds / (24 * 60 * 60))
            productivity_ratio = days / quantity_produced
            required_work = total_quantity_to_produce * productivity_ratio
            iso_string = f"P{required_work}D"
        return iso_string

def get_nested_resources(resource):
    return [object for rel in resource.IsNestedBy or [] for object in rel.RelatedObjects]
