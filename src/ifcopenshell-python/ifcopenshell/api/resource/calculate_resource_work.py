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
        self.productivity = ifcopenshell.util.element.get_psets(
            self.settings["resource"]
        ).get("EPset_Productivity", None)
        if not self.productivity:
            return
        unit_consumed = self.get_unit_consumed()
        self.unit_produced_name = self.productivity.get(
            "BaseQuantityProducedName", None
        )
        unit_produced = self.productivity.get("BaseQuantityProducedValue", None)
        total_produced = self.get_total_produced()
        if not unit_consumed or not unit_produced or not total_produced:
            return
        if not self.settings["resource"].Usage:
            ifcopenshell.api.run(
                "resource.add_resource_time",
                self.file,
                resource=self.settings["resource"],
            )
        if "T" in self.productivity.get("BaseQuantityConsumed", None):
            seconds = (unit_consumed.days * 24 * 60 * 60) + unit_consumed.seconds
            amount_worked = total_produced / unit_produced * seconds
            self.settings[
                "resource"
            ].Usage.ScheduleWork = f"PT{amount_worked / 60 / 60}H"
        else:
            days = unit_consumed.days + (unit_consumed.seconds / (24 * 60 * 60))
            amount_worked = total_produced / unit_produced * days
            self.settings["resource"].Usage.ScheduleWork = f"P{amount_worked}D"

    def get_unit_consumed(self):
        duration = self.productivity.get("BaseQuantityConsumed", None)
        if not duration:
            return
        return ifcopenshell.util.date.ifc2datetime(duration)

    def get_total_produced(self):
        total = 0
        for rel in self.settings["resource"].HasAssignments or []:
            if not rel.is_a("IfcRelAssignsToProcess"):
                continue
            for rel2 in rel.RelatingProcess.HasAssignments or []:
                if not rel2.is_a("IfcRelAssignsToProduct"):
                    continue
                if self.unit_produced_name == "Count":
                    total += 1
                else:
                    psets = ifcopenshell.util.element.get_psets(rel2.RelatingProduct)
                    for pset in psets.values():
                        for name, value in pset.items():
                            if name == self.unit_produced_name:
                                total += float(value)
        return total
