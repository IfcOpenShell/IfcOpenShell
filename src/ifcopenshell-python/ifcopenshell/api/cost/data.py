import ifcopenshell.util.date
import ifcopenshell.util.unit
import ifcopenshell.util.cost


class CostValueTrait:
    @classmethod
    def load_cost_values(cls, root_element, data):
        data["CostValues"] = []
        data["CategoryValues"] = {}
        data["UnitBasisValueComponent"] = None
        data["UnitBasisUnitSymbol"] = None
        data["TotalAppliedValue"] = 0.0
        data["TotalCost"] = 0.0
        if root_element.is_a("IfcCostItem"):
            values = root_element.CostValues
        elif root_element.is_a("IfcConstructionResource"):
            values = root_element.BaseCosts
        for cost_value in values or []:
            cls.load_cost_value(root_element, data, cost_value)
            data["CostValues"].append(cost_value.id())
            data["TotalAppliedValue"] += cls.cost_values[cost_value.id()]["AppliedValue"]
            if cost_value.UnitBasis:
                cost_value_data = cls.cost_values[cost_value.id()]
                data["UnitBasisValueComponent"] = cost_value_data["UnitBasis"]["ValueComponent"]
                data["UnitBasisUnitSymbol"] = cost_value_data["UnitBasis"]["UnitSymbol"]
        if data["UnitBasisValueComponent"]:
            data["TotalCost"] = data["TotalCostQuantity"] / data["UnitBasisValueComponent"] * data["TotalAppliedValue"]
        else:
            data["TotalCost"] = data["TotalCostQuantity"] * data["TotalAppliedValue"]

    @classmethod
    def load_cost_value(cls, root_element, root_element_data, cost_value):
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
        value_data["AppliedValue"] = cls.calculate_applied_value(root_element, cost_value)

        if cost_value.Category not in [None, "*"]:
            root_element_data["CategoryValues"].setdefault(cost_value.Category, 0)
            root_element_data["CategoryValues"][cost_value.Category] += value_data["AppliedValue"]

        value_data["Formula"] = ifcopenshell.util.cost.serialise_cost_value(cost_value)

        cls.cost_values[cost_value.id()] = value_data
        for component in cost_value.Components or []:
            cls.load_cost_value(root_element, root_element_data, component)

    @classmethod
    def calculate_applied_value(cls, root_element, cost_value, category_filter=None):
        if cost_value.ArithmeticOperator and cost_value.Components:
            component_values = []
            for component in cost_value.Components:
                component_values.append(cls.calculate_applied_value(root_element, component, category_filter))
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
            return cls.get_primitive_applied_value(cost_value.AppliedValue)
        elif cost_value.Category == "*":
            if root_element.IsNestedBy:
                return cls.sum_child_root_elements(root_element)
            else:
                return cls.get_primitive_applied_value(cost_value.AppliedValue)
        elif cost_value.Category:
            if root_element.IsNestedBy:
                return cls.sum_child_root_elements(root_element, category_filter=cost_value.Category)
            else:
                return cls.get_primitive_applied_value(cost_value.AppliedValue)
        return 0

    @classmethod
    def sum_child_root_elements(cls, root_element, category_filter=None):
        result = 0
        for rel in root_element.IsNestedBy:
            for child_root_element in rel.RelatedObjects:
                if root_element.is_a("IfcCostItem"):
                    values = child_root_element.CostValues
                elif root_element.is_a("IfcConstructionResource"):
                    values = child_root_element.BaseCosts
                for child_cost_value in values or []:
                    if category_filter and child_cost_value.Category != category_filter:
                        continue
                    child_applied_value = cls.calculate_applied_value(child_root_element, child_cost_value)
                    child_quantity = cls.get_total_quantity(child_root_element)
                    if child_cost_value.UnitBasis:
                        value_component = child_cost_value.UnitBasis.ValueComponent.wrappedValue
                        result += child_quantity / value_component * child_applied_value
                    else:
                        result += child_quantity * child_applied_value
        return result

    @classmethod
    def get_total_quantity(cls, root_element):
        if root_element.is_a("IfcCostItem"):
            return sum([q[3] for q in root_element.CostQuantities or []]) or 1.0
        elif root_element.is_a("IfcConstructionResource"):
            return root_element.BaseQuantity[3] if root_element.BaseQuantity else 1.0

    @classmethod
    def get_primitive_applied_value(cls, applied_value):
        if not applied_value:
            return 0.0
        elif isinstance(applied_value, float):
            return applied_value
        elif hasattr(applied_value, "wrappedValue") and isinstance(applied_value.wrappedValue, float):
            return applied_value.wrappedValue
        elif applied_value.is_a("IfcMeasureWithUnit"):
            return applied_value.ValueComponent
        assert False, "Applied value {applied_value} not implemented"


class Data(CostValueTrait):
    is_loaded = False
    cost_schedules = {}
    cost_items = {}
    physical_quantities = {}
    cost_values = {}
    categories = []

    @classmethod
    def purge(cls):
        cls.is_loaded = False
        cls.cost_schedules = {}
        cls.cost_items = {}
        cls.physical_quantities = {}
        cls.cost_values = {}
        cls.categories = []

    @classmethod
    def set_categories(cls, categories):
        cls.categories = categories

    @classmethod
    def load(cls, file):
        cls.file = file
        cls.cost_schedules = {}
        cls.cost_items = {}
        cls.physical_quantities = {}
        cls.cost_values = {}

        for cost_schedule in cls.file.by_type("IfcCostSchedule"):
            data = cost_schedule.get_info()
            del data["OwnerHistory"]
            if data["SubmittedOn"]:
                data["SubmittedOn"] = ifcopenshell.util.date.ifc2datetime(data["SubmittedOn"])
            if data["UpdateDate"]:
                data["UpdateDate"] = ifcopenshell.util.date.ifc2datetime(data["UpdateDate"])
            data["Controls"] = []
            for rel in cost_schedule.Controls:
                for related_object in rel.RelatedObjects:
                    if related_object.is_a("IfcCostItem"):
                        data["Controls"].append(related_object.id())
                        break  # We are only allowed one summary cost item
            cls.cost_schedules[cost_schedule.id()] = data

        for cost_item in cls.file.by_type("IfcCostItem"):
            data = cost_item.get_info()
            del data["OwnerHistory"]
            del data["CostValues"]
            data["IsNestedBy"] = []
            data["Controls"] = {}
            for rel in cost_item.IsNestedBy:
                [data["IsNestedBy"].append(o.id()) for o in rel.RelatedObjects if o.is_a("IfcCostItem")]
            parametric_quantities = []
            for rel in cost_item.Controls:
                for related_object in rel.RelatedObjects or []:
                    quantities = cls.get_object_quantities(cost_item, related_object)
                    data["Controls"][related_object.id()] = quantities
                    parametric_quantities.extend(quantities)
            cls.cost_items[cost_item.id()] = data
            cls.load_cost_item_quantities(cost_item, data, parametric_quantities)
            cls.load_cost_values(cost_item, data)
        cls.is_loaded = True

    @classmethod
    def get_object_quantities(cls, cost_item, element):
        if not element.is_a("IfcObject"):
            return []
        results = []
        for relationship in element.IsDefinedBy:
            if not relationship.is_a("IfcRelDefinesByProperties"):
                continue
            qto = relationship.RelatingPropertyDefinition
            if not qto.is_a("IfcElementQuantity"):
                continue
            for prop in qto.Quantities:
                if prop in cost_item.CostQuantities or []:
                    results.append(prop.id())
        return results

    @classmethod
    def load_cost_item_quantities(cls, cost_item, data, parametric_quantities):
        data["CostQuantities"] = []
        data["TotalCostQuantity"] = cls.get_total_quantity(cost_item)
        for quantity in cost_item.CostQuantities or []:
            if quantity.id() in parametric_quantities:
                continue
            quantity_data = quantity.get_info()
            del quantity_data["Unit"]
            cls.physical_quantities[quantity.id()] = quantity_data
            data["CostQuantities"].append(quantity.id())
        data["Unit"] = None
        data["UnitSymbol"] = "?"
        if cost_item.CostQuantities:
            quantity = cost_item.CostQuantities[0]
            unit = ifcopenshell.util.unit.get_property_unit(quantity, cls.file)
            if unit:
                data["Unit"] = unit.id()
                data["UnitSymbol"] = ifcopenshell.util.unit.get_unit_symbol(unit)
            else:
                data["Unit"] = None
                data["UnitSymbol"] = None
