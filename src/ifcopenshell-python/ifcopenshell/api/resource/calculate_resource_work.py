import math
import ifcopenshell.api
import ifcopenshell.util.date
import ifcopenshell.util.element


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"resource": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        self.productivity = ifcopenshell.util.element.get_psets(self.settings["resource"]).get(
            "EPset_Productivity", None
        )
        if not self.productivity:
            return
        unit_consumed = self.get_unit_consumed()
        self.unit_produced_name = self.productivity.get("BaseQuantityProducedName", None)
        unit_produced = self.productivity.get("BaseQuantityProducedValue", None)
        total_produced = self.get_total_produced()
        if not unit_consumed or not unit_produced or not total_produced:
            return
        seconds_worked = total_produced / unit_produced * unit_consumed
        self.set_schedule_work(seconds_worked)

    def get_unit_consumed(self):
        duration = self.productivity.get("BaseQuantityConsumed", None)
        if not duration:
            return
        return ifcopenshell.util.date.ifc2datetime(duration).seconds

    def get_total_produced(self):
        total = 0
        for rel in self.settings["resource"].HasAssignments or []:
            if not rel.is_a("IfcRelAssignsToProcess"):
                continue
            for rel2 in rel.RelatingProcess.HasAssignments or []:
                if not rel2.is_a("IfcRelAssignsToProduct"):
                    continue
                psets = ifcopenshell.util.element.get_psets(rel2.RelatingProduct)
                for pset in psets.values():
                    for name, value in pset.items():
                        if name == self.unit_produced_name:
                            try:
                                total += float(value)
                            except:
                                pass
        return total

    def set_schedule_work(self, seconds):
        if not self.settings["resource"].Usage:
            ifcopenshell.api.run("resource.add_resource_time", self.file, resource=self.settings["resource"])
        self.settings["resource"].Usage.ScheduleWork = f"PT{seconds / 60 / 60}H"
