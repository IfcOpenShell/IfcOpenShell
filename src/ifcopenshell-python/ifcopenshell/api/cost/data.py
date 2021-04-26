import ifcopenshell.util.date


class Data:
    is_loaded = False
    cost_schedules = {}
    cost_items = {}
    physical_quantities = {}
    cost_values = {}

    @classmethod
    def purge(cls):
        cls.is_loaded = False
        cls.cost_schedules = {}
        cls.cost_items = {}
        cls.physical_quantities = {}
        cls.cost_values = {}

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
            data["Controls"] = []
            for rel in cost_item.IsNestedBy:
                [data["IsNestedBy"].append(o.id()) for o in rel.RelatedObjects if o.is_a("IfcCostItem")]
            for rel in cost_item.Controls:
                [data["Controls"].append(o.id()) for o in rel.RelatedObjects or []]
            cls.cost_items[cost_item.id()] = data
            cls.load_cost_item_quantities(cost_item, data)
            cls.load_cost_item_values(cost_item, data)
        cls.is_loaded = True

    @classmethod
    def load_cost_item_quantities(cls, cost_item, data):
        data["CostQuantities"] = []
        data["TotalCostQuantity"] = cls.get_total_quantity(cost_item)
        for quantity in cost_item.CostQuantities or []:
            quantity_data = quantity.get_info()
            del quantity_data["Unit"]
            cls.physical_quantities[quantity.id()] = quantity_data
            data["CostQuantities"].append(quantity.id())

    @classmethod
    def load_cost_item_values(cls, cost_item, data):
        data["CostValues"] = []
        data["TotalCostValue"] = 0.0
        data["TotalAppliedValue"] = 0.0
        for cost_value in cost_item.CostValues or []:
            cls.load_cost_item_value(cost_item, cost_value)
            data["CostValues"].append(cost_value.id())
            data["TotalAppliedValue"] += cls.cost_values[cost_value.id()]["AppliedValue"]
        data["TotalCostValue"] = data["TotalCostQuantity"] * data["TotalAppliedValue"]

    @classmethod
    def load_cost_item_value(cls, cost_item, cost_value):
        value_data = cost_value.get_info()
        del value_data["AppliedValue"]
        del value_data["UnitBasis"]
        if value_data["ApplicableDate"]:
            value_data["ApplicableDate"] = ifcopenshell.util.date.ifc2datetime(value_data["ApplicableDate"])
        if value_data["FixedUntilDate"]:
            value_data["FixedUntilDate"] = ifcopenshell.util.date.ifc2datetime(value_data["FixedUntilDate"])
        value_data["Components"] = [c.id() for c in value_data["Components"] or []]
        value_data["AppliedValue"] = cls.calculate_applied_value(cost_item, cost_value)
        cls.cost_values[cost_value.id()] = value_data

    @classmethod
    def calculate_applied_value(cls, cost_item, cost_value, category_filter=None):
        result = 0
        if cost_value.ArithmeticOperator and cost_value.Components:
            pass  # TODO
        if cost_value.Category is None:
            return cls.get_primitive_applied_value(cost_value.AppliedValue)
        elif cost_value.Category == "*":
            if cost_item.IsNestedBy:
                return cls.sum_child_cost_items(cost_item)
            else:
                return cls.get_primitive_applied_value(cost_value.AppliedValue)
        elif cost_value.Category:
            if cost_item.IsNestedBy:
                return cls.sum_child_cost_items(cost_item, category_filter=cost_value.Category)
            else:
                return cls.get_primitive_applied_value(cost_value.AppliedValue)
        return result

    @classmethod
    def sum_child_cost_items(cls, cost_item, category_filter=None):
        result = 0
        for rel in cost_item.IsNestedBy:
            for child_cost_item in rel.RelatedObjects:
                for child_cost_value in child_cost_item.CostValues or []:
                    if category_filter and child_cost_value.Category != category_filter:
                        continue
                    child_applied_value = cls.calculate_applied_value(child_cost_item, child_cost_value)
                    child_quantity = cls.get_total_quantity(child_cost_item)
                    result += child_applied_value * child_quantity
        return result

    @classmethod
    def get_total_quantity(cls, cost_item):
        return sum([q[3] for q in cost_item.CostQuantities or []]) or 1.0

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
