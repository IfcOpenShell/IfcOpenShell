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

import lark
import ifcopenshell
from typing import Optional, Union, Literal, Generator, Any


arithmetic_operator_symbols = {"ADD": "+", "DIVIDE": "/", "MULTIPLY": "*", "SUBTRACT": "-"}
symbol_arithmetic_operators = {"+": "ADD", "/": "DIVIDE", "*": "MULTIPLY", "-": "SUBTRACT"}
FILTER_BY_TYPE = Literal["PRODUCT", "RESOURCE", "PROCESS"]


def get_primitive_applied_value(applied_value: Union[ifcopenshell.entity_instance, float, None]) -> float:
    if not applied_value:
        return 0.0
    elif isinstance(applied_value, float):
        return applied_value
    elif hasattr(applied_value, "wrappedValue") and isinstance(applied_value.wrappedValue, float):
        return applied_value.wrappedValue
    elif applied_value.is_a("IfcMeasureWithUnit"):
        return applied_value.ValueComponent
    assert False, f"Applied value {applied_value} not implemented"


def get_total_quantity(root_element: ifcopenshell.entity_instance) -> Union[float, None]:
    # 3 IfcPhysicalQuantity Value
    if root_element.is_a("IfcCostItem"):
        # Different output for no quantities and zero quantites
        # as they have different meaning in IFC.
        quantities = root_element.CostQuantities
        if not quantities:
            return None
        return sum([q[3] for q in quantities])
    elif root_element.is_a("IfcConstructionResource"):
        quantity = root_element.BaseQuantity
        return quantity[3] if quantity else 1.0


def calculate_applied_value(
    root_element: ifcopenshell.entity_instance, cost_value: ifcopenshell.entity_instance, category_filter=None
) -> float:
    if cost_value.ArithmeticOperator and cost_value.Components:
        component_values = []
        for component in cost_value.Components:
            component_values.append(calculate_applied_value(root_element, component, category_filter))
        if cost_value.ArithmeticOperator == "ADD":
            return sum(component_values)
        result = component_values.pop(0)
        if cost_value.ArithmeticOperator == "DIVIDE":
            for value in component_values:
                try:
                    result /= value
                except ZeroDivisionError:
                    pass
        elif cost_value.ArithmeticOperator == "MULTIPLY":
            for value in component_values:
                result *= value
        elif cost_value.ArithmeticOperator == "SUBTRACT":
            for value in component_values:
                result -= value
        return result
    if cost_value.Category is None:
        return get_primitive_applied_value(cost_value.AppliedValue)
    elif cost_value.Category == "*":
        if root_element.IsNestedBy:
            return sum_child_root_elements(root_element)
        else:
            return get_primitive_applied_value(cost_value.AppliedValue)
    elif cost_value.Category:
        if root_element.IsNestedBy:
            return sum_child_root_elements(root_element, category_filter=cost_value.Category)
        else:
            return get_primitive_applied_value(cost_value.AppliedValue)
    return 0.0


def sum_child_root_elements(root_element: ifcopenshell.entity_instance, category_filter: Optional[str] = None) -> float:
    result = 0.0
    for rel in root_element.IsNestedBy:
        for child_root_element in rel.RelatedObjects:
            if root_element.is_a("IfcCostItem"):
                values = child_root_element.CostValues
            elif root_element.is_a("IfcConstructionResource"):
                values = child_root_element.BaseCosts
            for child_cost_value in values or []:
                if category_filter and child_cost_value.Category != category_filter:
                    continue
                child_applied_value = calculate_applied_value(child_root_element, child_cost_value)
                child_quantity = get_total_quantity(child_root_element)
                child_quantity = 1.0 if child_quantity is None else child_quantity
                if child_cost_value.UnitBasis:
                    value_component = child_cost_value.UnitBasis.ValueComponent.wrappedValue
                    result += child_quantity / value_component * child_applied_value
                else:
                    result += child_quantity * child_applied_value
    return result


def serialise_cost_value(cost_value: ifcopenshell.entity_instance) -> str:
    result = _serialise_cost_value(cost_value)
    if result and result[0] == "(" and result[-1] == ")":
        return result[1:-1]
    return result


def _serialise_cost_value(cost_value: ifcopenshell.entity_instance) -> str:
    value = ""
    if cost_value.ArithmeticOperator and cost_value.Components:
        operator = arithmetic_operator_symbols[cost_value.ArithmeticOperator]
        serialised_components = []
        for component in cost_value.Components:
            serialised_components.append(_serialise_cost_value(component))
        value = operator.join(serialised_components)
    elif cost_value.AppliedValue is not None:
        value = serialise_applied_value(cost_value.AppliedValue)

    category = ""
    if cost_value.Category == "*":
        category = "SUM"
    elif cost_value.Category:
        category = cost_value.Category

    if not category and not value:
        value = "0"

    if category:
        return f"{category}({value})"
    elif cost_value.Components:
        return f"({value})"
    return value


def serialise_applied_value(applied_value: ifcopenshell.entity_instance) -> str:
    if applied_value.is_a("IfcMonetaryMeasure"):
        return str(applied_value.wrappedValue)
    return "?"


def unserialise_cost_value(formula: str, cost_value: ifcopenshell.entity_instance) -> dict[str, Any]:
    unserialiser = CostValueUnserialiser()
    result = unserialiser.parse(formula)

    def map_element_to_result(element: ifcopenshell.entity_instance, result: dict):
        result["ifc"] = element
        for i, component in enumerate(result.get("Components", [])):
            if element.Components and i < len(element.Components):
                map_element_to_result(element.Components[i], result["Components"][i])

    map_element_to_result(cost_value, result)
    return result


def get_cost_items_for_product(product: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
    """
    Returns a list of cost items related to the given product.

    Args:
        product: An object of class IfcProduct representing a product.

    Returns:
        A list of IfcCostItem objects representing the cost items related to the product.
    """
    cost_items = []
    for assignment in product.HasAssignments:
        if assignment.is_a("IfcRelAssignsToControl") and assignment.RelatingControl.is_a("IfcCostItem"):
            cost_items.append(assignment.RelatingControl)
    return cost_items


def get_root_cost_items(cost_schedule: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
    return [
        related_object
        for rel in cost_schedule.Controls or []
        for related_object in rel.RelatedObjects
        if related_object.is_a("IfcCostItem")
    ]


def get_all_nested_cost_items(
    cost_item: ifcopenshell.entity_instance,
) -> Generator[ifcopenshell.entity_instance, None, None]:
    for cost_item in get_nested_cost_items(cost_item):
        yield cost_item
        yield from get_all_nested_cost_items(cost_item)


def get_nested_cost_items(cost_item: ifcopenshell.entity_instance, is_deep=False) -> list[ifcopenshell.entity_instance]:
    if is_deep:
        return list(get_all_nested_cost_items(cost_item))
    else:
        return [obj for rel in cost_item.IsNestedBy for obj in rel.RelatedObjects]


def get_schedule_cost_items(
    cost_schedule: ifcopenshell.entity_instance,
) -> Generator[ifcopenshell.entity_instance, None, None]:
    for cost_item in get_root_cost_items(cost_schedule):
        yield cost_item
        yield from get_all_nested_cost_items(cost_item)


def get_cost_assignments_by_type(
    cost_item: ifcopenshell.entity_instance, filter_by_type: Optional[FILTER_BY_TYPE] = None
) -> list[ifcopenshell.entity_instance]:
    if filter_by_type is not None:
        if filter_by_type == "PRODUCT":
            filter_by_type = "IfcElement"
        elif filter_by_type == "RESOURCE":
            filter_by_type = "IfcResource"
        elif filter_by_type == "PROCESS":
            filter_by_type = "IfcProcess"
    return [
        related_object
        for r in cost_item.Controls or []
        for related_object in r.RelatedObjects
        if not filter_by_type or related_object.is_a(filter_by_type)
    ]


def get_cost_item_assignments(
    cost_item: ifcopenshell.entity_instance, filter_by_type: Optional[FILTER_BY_TYPE] = None, is_deep: bool = False
) -> list[ifcopenshell.entity_instance]:
    if not is_deep:
        return get_cost_assignments_by_type(cost_item, filter_by_type)
    else:
        return [
            product
            for nested_cost_item in get_all_nested_cost_items(cost_item)
            for product in get_cost_assignments_by_type(nested_cost_item, filter_by_type)
        ]


def get_cost_values(cost_item: ifcopenshell.entity_instance) -> list[dict[str, str]]:
    results = []
    for cost_value in cost_item.CostValues or []:
        label = "{0:.2f}".format(calculate_applied_value(cost_item, cost_value))
        label += " = {}".format(serialise_cost_value(cost_value))
        results.append(
            {
                "id": cost_value.id(),
                "label": label,
                "name": cost_value.Name,
                "category": cost_value.Category,
                "applied_value": (
                    get_primitive_applied_value(cost_value.AppliedValue) if cost_value.AppliedValue else None
                ),
            }
        )
    print(results)
    return results


class CostValueUnserialiser:
    def parse(self, formula: str):
        l = lark.Lark(
            """start: formula
                    formula: operand (operator operand)*
                    operand: value | category "(" formula ")"
                    value: NUMBER?
                    category: WORD?
                    operator: add | divide | multiply | subtract
                    add: "+"
                    divide: "/"
                    multiply: "*"
                    subtract: "-"

                    // Embed common.lark for packaging
                    DIGIT: "0".."9"
                    HEXDIGIT: "a".."f"|"A".."F"|DIGIT
                    INT: DIGIT+
                    SIGNED_INT: ["+"|"-"] INT
                    DECIMAL: INT "." INT? | "." INT
                    _EXP: ("e"|"E") SIGNED_INT
                    FLOAT: INT _EXP | DECIMAL _EXP?
                    SIGNED_FLOAT: ["+"|"-"] FLOAT
                    NUMBER: FLOAT | INT
                    SIGNED_NUMBER: ["+"|"-"] NUMBER
                    _STRING_INNER: /.*?/
                    _STRING_ESC_INNER: _STRING_INNER /(?<!\\\\)(\\\\\\\\)*?/
                    ESCAPED_STRING : "\\"" _STRING_ESC_INNER "\\""
                    LCASE_LETTER: "a".."z"
                    UCASE_LETTER: "A".."Z"
                    LETTER: UCASE_LETTER | LCASE_LETTER
                    WORD: LETTER+
                    CNAME: ("_"|LETTER) ("_"|LETTER|DIGIT)*
                    WS_INLINE: (" "|/\\t/)+
                    WS: /[ \\t\\f\\r\\n]/+
                    CR : /\\r/
                    LF : /\\n/
                    NEWLINE: (CR? LF)+

                    %ignore WS // Disregard spaces in text
                 """
        )
        start = l.parse(formula)
        return self.get_formula(start.children[0])

    def get_formula(self, formula):
        if len(formula.children) == 1:
            return self.get_operand(formula.children[0])
        results = {"Components": []}
        for child in formula.children:
            if child.data == "operand":
                results["Components"].append(self.get_operand(child))
            elif child.data == "operator":
                results["ArithmeticOperator"] = self.get_operator(child)
        return results

    def get_operand(self, operand):
        child = operand.children[0]
        if child.data == "value":
            value = self.get_value(child)
            return {"AppliedValue": float(value) if value else None}
        elif child.data == "category":
            data = {}
            category = self.get_category(child)
            if category:
                if category.lower() == "sum":
                    category = "*"
                data["Category"] = category
            formula = self.get_formula(operand.children[1])
            if formula.get("Components"):
                data["Components"] = formula["Components"]
                data["ArithmeticOperator"] = formula["ArithmeticOperator"]
            else:
                data["AppliedValue"] = formula["AppliedValue"]
            return data

    def get_value(self, value):
        if value.children:
            return value.children[0].value

    def get_category(self, category):
        if category.children:
            return category.children[0].value

    def get_operator(self, operator):
        return operator.children[0].data.upper()
