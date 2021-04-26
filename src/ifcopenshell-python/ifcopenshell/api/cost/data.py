import ifcopenshell.util.date


class Data:
    is_loaded = False
    cost_schedules = {}
    cost_items = {}
    physical_quantities = {}

    @classmethod
    def purge(cls):
        cls.is_loaded = False
        cls.cost_schedules = {}
        cls.cost_items = {}
        cls.physical_quantities = {}

    @classmethod
    def load(cls, file):
        cls.cost_schedules = {}
        cls.cost_items = {}
        cls.physical_quantities = {}

        for cost_schedule in file.by_type("IfcCostSchedule"):
            data = cost_schedule.get_info()
            del data["OwnerHistory"]
            if data["SubmittedOn"]:
                data["SubmittedOn"] = ifcopenshell.util.date.ifc2datetime(data["SubmittedOn"])
            if data["UpdateDate"]:
                data["UpdateDate"] = ifcopenshell.util.date.ifc2datetime(data["UpdateDate"])
            data["RelatedObjects"] = []
            for rel in cost_schedule.Controls:
                for related_object in rel.RelatedObjects:
                    if related_object.is_a("IfcCostItem"):
                        data["RelatedObjects"].append(related_object.id())
                        break # We are only allowed one summary cost item
            cls.cost_schedules[cost_schedule.id()] = data

        for cost_item in file.by_type("IfcCostItem"):
            data = cost_item.get_info()
            del data["OwnerHistory"]
            del data["CostValues"]
            data["RelatedObjects"] = []
            data["Controls"] = []
            for rel in cost_item.IsNestedBy:
                [data["RelatedObjects"].append(o.id()) for o in rel.RelatedObjects if o.is_a("IfcCostItem")]
            for rel in cost_item.Controls:
                [data["Controls"].append(o.id()) for o in rel.RelatedObjects or []]
            cls.cost_items[cost_item.id()] = data
            cls.load_cost_item_quantities(cost_item, data)
        cls.is_loaded=True

    @classmethod
    def load_cost_item_quantities(cls, cost_item, data):
        data["CostQuantities"] = []
        data["TotalCostQuantities"] = 0.0
        for quantity in cost_item.CostQuantities or []:
            quantity_data = quantity.get_info()
            del quantity_data["Unit"]
            cls.physical_quantities[quantity.id()] = quantity_data
            data["CostQuantities"].append(quantity.id())
            data["TotalCostQuantities"] += quantity[3]
