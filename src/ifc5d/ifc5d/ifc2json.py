import ifcopenshell
import ifcopenshell.util.unit
from typing import Any
import ifcopenshell.util.cost
import ifcopenshell.util.date
from ifcopenshell.util.classification import get_references


CostItem = dict[str, Any]


class ifc5D2json:
    def __init__(self):
        self.json: str = None
        self.file_path: str = None
        self.file: ifcopenshell.file = None
        self.cost_schedule: ifcopenshell.entity_instance = None
        self.units: dict[str, ifcopenshell.entity_instance] = {}
        self._cost_values = {}
        self.data: list[dict[str, Any]] = []

    def convert_ifc_to_json(self):
        self.data = []
        if not isinstance(self.file_path, str):
            self.file = self.file_path
        else:
            self.file = ifcopenshell.open(self.file_path)
        if not self.cost_schedule:
            self.extract_cost_schedules()
        else:
            self.extract_cost_schedule()
        return self.data

    def extract_cost_schedule(self):
        data = self.cost_schedule.get_info(recursive=True)
        data["cost_items"] = self.build_schedule_tree(self.cost_schedule)
        self.data.append(data)

    def extract_cost_schedules(self):
        for cost_schedule in self.file.by_type("IfcCostSchedule"):
            data = cost_schedule.get_info(recursive=True)
            data["cost_items"] = self.build_schedule_tree(cost_schedule)
            self.data.append(data)

    def build_schedule_tree(self, cost_schedule: ifcopenshell.entity_instance) -> dict[str, Any]:
        schedule_data = []
        self._cost_values = {}
        for rel in cost_schedule.Controls or []:
            for cost_item in rel.RelatedObjects:
                self.extract_cost_item_data(cost_item, schedule_data)
        return schedule_data

    def extract_cost_item_data(self, cost_item: ifcopenshell.entity_instance, json_data):
        data = {}
        self.extract_cost_item_quantities(cost_item, data)
        self.populate_cost_values(cost_item, data)
        self.populate_nesting_index(cost_item, data)
        cost_rate = ifcopenshell.util.cost.get_cost_rate(self.file, cost_item)
        data = {**data, **cost_item.get_info(recursive=True)}
        data["id"] = cost_item.id()
        data["IsNestedBy"] = []
        data["IsSum"] = self.check_if_cost_item_is_sum(cost_item)
        data["Classification"] = self.get_cost_classifications(cost_item)
        data["CostRate"] = {
            "id": cost_rate.id() if cost_rate else None,
            "Identification": cost_rate.Identification if cost_rate else None,
            "Name": cost_rate.Name if cost_rate else None,
        }
        json_data.append(data)
        for rel in cost_item.IsNestedBy or []:
            for sub_cost in rel.RelatedObjects:
                self.extract_cost_item_data(sub_cost, data["IsNestedBy"])

    def get_cost_classifications(self, cost_item: ifcopenshell.entity_instance) -> list:
        results = []
        if cost_item:
            for reference in get_references(cost_item):
                data = reference.get_info()
                del data["ReferencedSource"]
                results.append(data)
        return results

    def check_if_cost_item_is_sum(self, cost_item: ifcopenshell.entity_instance) -> bool:
        cost_values = []
        if cost_item.is_a("IfcCostItem"):
            cost_values = cost_item.CostValues
        elif cost_item.is_a("IfcCostValue"):
            cost_values = cost_item.Components
        for cost_value in cost_values or []:
            if cost_value.Category == "*":
                return True
        return False

    def populate_nesting_index(self, cost_item, data):
        data["NestingIndex"] = None
        for rel in cost_item.Nests or []:
            data["NestingIndex"] = rel.RelatedObjects.index(cost_item)

    def populate_cost_values(self, root_element, data):
        # data["CostValues"] = []
        data["CategoryValues"] = {}
        data["UnitBasisValueComponent"] = None
        data["UnitBasisUnitSymbol"] = None
        data["TotalAppliedValue"] = 0.0
        data["TotalCost"] = 0.0
        has_unit_basis = False
        is_sum = False
        if root_element.is_a("IfcCostItem"):
            values = root_element.CostValues
        elif root_element.is_a("IfcConstructionResource"):
            values = root_element.BaseCosts
        for cost_value in values or []:
            self.extract_cost_value(root_element, data, cost_value)
            # data["CostValues"].append(cost_value.id())
            data["TotalAppliedValue"] += self._cost_values[cost_value.id()]["AppliedValue"]
            if cost_value.UnitBasis:
                cost_value_data = self._cost_values[cost_value.id()]
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
            data["TotalAppliedValue"] = None

    def extract_cost_value(self, root_element, root_element_data, cost_value):
        value_data = cost_value.get_info()
        del value_data["AppliedValue"]
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

        self._cost_values[cost_value.id()] = value_data
        for component in cost_value.Components or []:
            self.extract_cost_value(root_element, root_element_data, component)

    def extract_cost_item_quantities(self, cost_item, data):
        data["TotalCostQuantity"] = ifcopenshell.util.cost.get_total_quantity(cost_item)
        data["UnitSymbol"] = "-"
        if cost_item.CostQuantities:
            quantity = cost_item.CostQuantities[0]
            data["QuantityType"] = quantity.is_a()
            unit = ifcopenshell.util.unit.get_property_unit(quantity, self.file)
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
