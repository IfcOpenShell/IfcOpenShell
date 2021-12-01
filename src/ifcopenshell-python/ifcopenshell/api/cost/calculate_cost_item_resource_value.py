import ifcopenshell.api
import ifcopenshell.util.date


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"cost_item": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        for cost_value in self.settings["cost_item"].CostValues or []:
            ifcopenshell.api.run(
                "cost.remove_cost_value", self.file, parent=self.settings["cost_item"], cost_value=cost_value
            )

        resources = []
        for rel in self.settings["cost_item"].Controls or []:
            for related_object in rel.RelatedObjects:
                if related_object.is_a("IfcConstructionResource"):
                    resources.append(related_object)
                elif related_object.is_a("IfcTask"):
                    for rel2 in related_object.OperatesOn or []:
                        for related_object2 in rel2.RelatedObjects:
                            if related_object2.is_a("IfcConstructionResource"):
                                resources.append(related_object2)

        total_cost = 0
        for resource in resources:
            cost = self.get_cost(resource)
            quantity = self.get_quantity(resource)
            if not cost or not quantity:
                continue
            total_cost += cost * quantity

        if total_cost:
            cost_value = ifcopenshell.api.run("cost.add_cost_value", self.file, parent=self.settings["cost_item"])
            cost_value.AppliedValue = self.file.createIfcMonetaryMeasure(total_cost)

    def get_cost(self, resource):
        total = 0
        for cost_value in resource.BaseCosts or []:
            total += cost_value.AppliedValue.wrappedValue if cost_value.AppliedValue else 0
        return total

    def get_quantity(self, resource):
        total = 0
        if resource.BaseQuantity:
            return resource.BaseQuantity[3]
        if resource.Usage and resource.Usage.ScheduleWork:
            # For now we assume either hourly or daily depending on how duration is stored
            duration = ifcopenshell.util.date.ifc2datetime(resource.Usage.ScheduleWork)
            if duration.days:
                return duration.days
            return duration.seconds / 60 / 60
