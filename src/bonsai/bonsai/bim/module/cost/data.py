# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell
import ifcopenshell.util.cost
import ifcopenshell.util.date
import ifcopenshell.util.element
import ifcopenshell.util.unit
import bonsai.tool as tool
from ifcopenshell.util.doc import get_entity_doc, get_predefined_type_doc
from typing import Any, Union


def refresh():
    CostSchedulesData.is_loaded = False
    CostItemRatesData.is_loaded = False
    CostItemQuantitiesData.is_loaded = False


CostItem = dict[str, Any]
CostQuantity = dict[str, Any]
CostSchedule = dict[str, Any]
Currency = dict[str, Any]


class CostSchedulesData:
    data = {}
    is_loaded = False
    _cost_values: dict[int, dict[str, Any]]

    @classmethod
    def load(cls) -> None:
        cls.data = {
            "predefined_types": cls.get_cost_schedule_types(),
            "total_cost_schedules": cls.total_cost_schedules(),
            "schedules": cls.schedules(),
            "is_editing_rates": cls.is_editing_rates(),
            "cost_items": cls.cost_items(),
            "cost_quantities": cls.cost_quantities(),
            "cost_values": cls.cost_values(),
            "quantity_types": cls.quantity_types(),
            "currency": cls.currency(),
        }
        cls.is_loaded = True

    @classmethod
    def currency(cls) -> Union[Currency, None]:
        unit = tool.Unit.get_project_currency_unit()
        if unit:
            return {"id": unit.id(), "name": unit.Currency}

    @classmethod
    def total_cost_schedules(cls) -> int:
        return len(tool.Ifc.get().by_type("IfcCostSchedule"))

    @classmethod
    def schedules(cls) -> list[CostSchedule]:
        results: list[CostSchedule] = []
        props = tool.Cost.get_cost_props()
        if props.active_cost_schedule_id:
            schedule = tool.Ifc.get().by_id(props.active_cost_schedule_id)
            results.append(
                {
                    "id": schedule.id(),
                    "name": schedule.Name or "Unnamed",
                    "predefined_type": ifcopenshell.util.element.get_predefined_type(schedule),
                }
            )
        else:
            for schedule in tool.Ifc.get().by_type("IfcCostSchedule"):
                results.append(
                    {
                        "id": schedule.id(),
                        "name": schedule.Name or "Unnamed",
                        "predefined_type": ifcopenshell.util.element.get_predefined_type(schedule),
                    }
                )
        return results

    @classmethod
    def is_editing_rates(cls) -> bool:
        props = tool.Cost.get_cost_props()
        ifc_id = props.active_cost_schedule_id
        if not ifc_id:
            return False
        return tool.Ifc.get().by_id(ifc_id).PredefinedType == "SCHEDULEOFRATES"

    @classmethod
    def cost_items(cls) -> dict[int, CostItem]:
        cls._cost_values = {}
        results: dict[int, CostItem] = {}
        for cost_item in tool.Ifc.get().by_type("IfcCostItem"):
            data: CostItem = {}
            cls._load_cost_item_quantities(cost_item, data)
            cls._load_cost_values(cost_item, data)
            cls._load_nesting_index(cost_item, data)
            cls._load_assigned_cost_rate(cost_item, data)
            results[cost_item.id()] = data
        return results

    @classmethod
    def _load_nesting_index(cls, cost_item: ifcopenshell.entity_instance, data: CostItem) -> None:
        data["NestingIndex"] = None
        for rel in cost_item.Nests or []:
            data["NestingIndex"] = rel.RelatedObjects.index(cost_item)

    @classmethod
    def _load_cost_values(cls, root_element: ifcopenshell.entity_instance, data: CostItem) -> None:
        # data["CostValues"] = []
        data["CategoryValues"] = {}
        data["UnitBasisValueComponent"] = None
        data["UnitBasisUnitSymbol"] = None
        data["TotalAppliedValue"] = 0.0
        data["TotalCost"] = 0.0
        has_unit_basis = False
        is_sum = False
        values: list[ifcopenshell.entity_instance]
        if root_element.is_a("IfcCostItem"):
            values = root_element.CostValues
        elif root_element.is_a("IfcConstructionResource"):
            values = root_element.BaseCosts
        for cost_value in values or []:
            cls._load_cost_value(root_element, data, cost_value)
            # data["CostValues"].append(cost_value.id())
            data["TotalAppliedValue"] += cls._cost_values[cost_value.id()]["AppliedValue"]
            if cost_value.UnitBasis:
                cost_value_data = cls._cost_values[cost_value.id()]
                data["UnitBasisValueComponent"] = cost_value_data["UnitBasis"]["ValueComponent"]
                data["UnitBasisUnitSymbol"] = cost_value_data["UnitBasis"]["UnitSymbol"]
                has_unit_basis = True
            else:
                data["UnitBasisValueComponent"] = 1
                data["UnitBasisUnitSymbol"] = "U"
            if cost_value.Category == "*":
                is_sum = True
        cost_quantity = 1 if data["TotalCostQuantity"] is None else data["TotalCostQuantity"]
        if has_unit_basis:
            data["TotalCost"] = data["TotalAppliedValue"] * cost_quantity / data["UnitBasisValueComponent"]
        else:
            data["TotalCost"] = data["TotalAppliedValue"] * cost_quantity
        if is_sum:
            pass  # If it is None it doesn't allow me to assign a cost rate composed by sum
            # data["TotalAppliedValue"] = None

    @classmethod
    def _load_assigned_cost_rate(cls, cost_item: ifcopenshell.entity_instance, data: CostItem) -> None:
        data["AssignedCostRate"] = tool.Cost.get_assigned_rate_cost_item(cost_item)

    @classmethod
    def _load_cost_item_quantities(cls, cost_item: ifcopenshell.entity_instance, data: CostItem) -> None:
        # parametric_quantities = []
        # for rel in cost_item.Controls:
        #     for related_object in rel.RelatedObjects or []:
        #         quantities = cls._get_object_quantities(cost_item, related_object)
        #         parametric_quantities.extend(quantities)
        data["TotalCostQuantity"] = ifcopenshell.util.cost.get_total_quantity(cost_item)
        data["UnitSymbol"] = "-"
        quantities: list[ifcopenshell.entity_instance] = cost_item.CostQuantities
        if quantities:
            quantity = quantities[0]
            data["QuantityType"] = quantity.is_a()
            unit = ifcopenshell.util.unit.get_property_unit(quantity, tool.Ifc.get())
            if unit:
                data["UnitSymbol"] = ifcopenshell.util.unit.get_unit_symbol(unit)
            if quantity.is_a("IfcPhysicalSimpleQuantity"):
                measure_class = (
                    quantity.wrapped_data.declaration()
                    .as_entity()
                    .attribute_by_index(3)
                    .type_of_attribute()
                    .declared_type()
                    .name()
                )
                if "Count" in measure_class:
                    data["UnitSymbol"] = "U"

        # same_unit_nested_cost_item = set()
        # data["DerivedTotalCostQuantity"] = None
        # if cost_item.IsNestedBy:
        #     data["TotalCostQuantity"] = 0.0
        #     derived_quantity = 0
        #     derived_unit = None
        #     should_sum = False
        #     for rel in cost_item.IsNestedBy:
        #         for related_object in rel.RelatedObjects or []:
        #             for quantity in related_object.CostQuantities or []:
        #                 nested_unit = ifcopenshell.util.unit.get_property_unit(quantity, tool.Ifc.get())
        #                 if derived_unit is None:
        #                     derived_unit = nested_unit
        #                 elif nested_unit and nested_unit.id() == derived_unit.id():
        #                     same_unit_nested_cost_item.add(related_object)
        #                 else:
        #                     derived_unit = None
        #                     break
        #     for cost in same_unit_nested_cost_item:
        #         qto = ifcopenshell.util.cost.get_total_quantity(cost)
        #         derived_quantity += qto
        #         print(derived_quantity)
        #     if derived_quantity not in [0, None]:
        #         data["DerivedTotalCostQuantity"] = derived_quantity
        #         if derived_unit:
        #             data["DerivedUnitSymbol"] = ifcopenshell.util.unit.get_unit_symbol(derived_unit)
        #         else:
        #             data["DerivedUnitSymbol"] = "?"
        #         print("Total Cost", data["DerivedTotalCostQuantity"], cost_item.Name)

    # TODO: dead code?
    @classmethod
    def _get_object_quantities(
        cls, cost_item: ifcopenshell.entity_instance, element: ifcopenshell.entity_instance
    ) -> list[int]:
        if not element.is_a("IfcObject"):
            return []
        cost_quantities: list[ifcopenshell.entity_instance] = cost_item.CostQuantities
        if not cost_quantities:
            return []

        results: list[int] = []
        relationship: ifcopenshell.entity_instance
        for relationship in element.IsDefinedBy:
            if not relationship.is_a("IfcRelDefinesByProperties"):
                continue
            qto: ifcopenshell.entity_instance = relationship.RelatingPropertyDefinition
            if not qto.is_a("IfcElementQuantity"):
                continue
            prop: ifcopenshell.entity_instance
            for prop in qto.Quantities:
                if prop in cost_quantities:
                    results.append(prop.id())
        return results

    @classmethod
    def _load_cost_value(
        cls,
        root_element: ifcopenshell.entity_instance,
        root_element_data: CostItem,
        cost_value: ifcopenshell.entity_instance,
    ) -> None:
        value_data = cost_value.get_info()
        del value_data["AppliedValue"]
        if tool.Cost.get_assigned_rate_cost_item(root_element):
            root_element = tool.Cost.get_assigned_rate_cost_item(root_element)
        if value_data["UnitBasis"]:
            data = cost_value.UnitBasis.get_info()
            data["ValueComponent"] = data["ValueComponent"].wrappedValue
            data["UnitComponent"] = data["UnitComponent"].id()
            data["UnitSymbol"] = ifcopenshell.util.unit.get_unit_symbol(cost_value.UnitBasis.UnitComponent)
            value_data["UnitBasis"] = data
        if value_data["ApplicableDate"]:
            value_data["ApplicableDate"] = ifcopenshell.util.date.ifc2datetime(value_data["ApplicableDate"])
        if value_data["FixedUntilDate"]:
            value_data["FixedUntilDate"] = ifcopenshell.util.date.ifc2datetime(value_data["FixedUntilDate"])
        value_data["Components"] = [c.id() for c in value_data["Components"] or []]
        value_data["AppliedValue"] = ifcopenshell.util.cost.calculate_applied_value(root_element, cost_value)

        if cost_value.Category not in [None, "*"]:
            root_element_data["CategoryValues"].setdefault(cost_value.Category, 0)
            root_element_data["CategoryValues"][cost_value.Category] += value_data["AppliedValue"]

        value_data["Formula"] = ifcopenshell.util.cost.serialise_cost_value(cost_value)

        cls._cost_values[cost_value.id()] = value_data
        for component in cost_value.Components or []:
            cls._load_cost_value(root_element, root_element_data, component)

    @classmethod
    def cost_quantities(cls) -> list[CostQuantity]:
        results: list[CostQuantity] = []
        props = tool.Cost.get_cost_props()
        ifc_id = props.active_cost_item_id
        if not ifc_id:
            return results
        for quantity in tool.Ifc.get().by_id(ifc_id).CostQuantities or []:
            results.append({"id": quantity.id(), "name": quantity.Name, "value": "{0:.2f}".format(quantity[3])})
        return results

    @classmethod
    def cost_values(cls) -> list[dict[str, str]]:
        props = tool.Cost.get_cost_props()
        ifc_id = props.active_cost_item_id
        if not ifc_id:
            return []
        return ifcopenshell.util.cost.get_cost_values(tool.Ifc.get().by_id(ifc_id))

    @classmethod
    def quantity_types(cls) -> list[tuple[str, str, str]]:
        return [
            (t.name(), t.name(), "")
            for t in tool.Ifc.schema().declaration_by_name("IfcPhysicalSimpleQuantity").subtypes()
        ]

    @classmethod
    def get_cost_schedule_types(cls) -> list[tuple[str, str, str]]:
        types = ifcopenshell.util.cost.get_cost_schedule_types(tool.Ifc.get())
        return [(t["name"], t["name"], t["description"]) for t in types]


class CostItemRatesData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "schedule_of_rates": cls.schedule_of_rates(),
            "cost_schedules": cls.cost_schedules(),
        }
        cls.is_loaded = True

    @classmethod
    def schedule_of_rates(cls) -> list[tuple[str, str, str]]:
        return [
            (str(s.id()), s.Name or "Unnamed", "")
            for s in tool.Ifc.get().by_type("IfcCostSchedule")
            if s.PredefinedType == "SCHEDULEOFRATES"
        ]

    @classmethod
    def cost_schedules(cls) -> list[tuple[str, str, str]]:
        return [(str(s.id()), s.Name or "Unnamed", "") for s in tool.Ifc.get().by_type("IfcCostSchedule")]


class CostItemQuantitiesData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "product_quantity_names": cls.product_quantity_names(),
            "process_quantity_names": cls.process_quantity_names(),
            "resource_quantity_names": cls.resource_quantity_names(),
        }
        cls.is_loaded = True

    @classmethod
    def product_quantity_names(cls):
        elements = tool.Spatial.get_selected_products()
        names = ifcopenshell.util.cost.get_product_quantity_names(elements)
        return [(n, n, "") for n in names]

    @classmethod
    def process_quantity_names(cls):
        props = tool.Sequence.get_work_schedule_props()
        active_task_index = props.active_task_index
        tprops = tool.Sequence.get_task_tree_props()
        total_tasks = len(tprops.tasks)
        if not total_tasks or active_task_index >= total_tasks:
            return []
        ifc_definition_id = tprops.tasks[active_task_index].ifc_definition_id
        element = tool.Ifc.get().by_id(ifc_definition_id)
        names = set()
        qtos = ifcopenshell.util.element.get_psets(element, qtos_only=True)
        for qset, quantities in qtos.items():
            names = set(quantities.keys())
        return [(n, n, "") for n in names if n != "id"]

    @classmethod
    def resource_quantity_names(cls):
        active_resource_index = bpy.context.scene.BIMResourceProperties.active_resource_index
        total_resources = len(bpy.context.scene.BIMResourceTreeProperties.resources)
        if not total_resources or active_resource_index >= total_resources:
            return []
        ifc_definition_id = bpy.context.scene.BIMResourceTreeProperties.resources[
            active_resource_index
        ].ifc_definition_id
        element = tool.Ifc.get().by_id(ifc_definition_id)
        names = set()
        qtos = ifcopenshell.util.element.get_psets(element, qtos_only=True)
        for qset, quantities in qtos.items():
            names = set(quantities.keys())
        return [(n, n, "") for n in names if n != "id"]
