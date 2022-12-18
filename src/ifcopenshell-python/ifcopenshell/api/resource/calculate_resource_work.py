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
    def __init__(self, file, resource=None):
        """Calculates the work that a resource is used for

        This is an unofficial parametric calculation that may be done on a
        resource based on careful analysis of the relationships between the
        costing, scheduling, and resource domains in IFC.

        A resource may store a productivity rate in a property set called
        EPset_Productivity. This stores three properties:

        * BaseQuantityConsumed - a duration that the resource is consumed for.
        * BaseQuantityProducedName - what quantity the resource can produce,
            such as area or volume.
        * BaseQuantityProducedValue - what value of that quantity the resource
            can produce during that duration.

        For example, a labour or equipment resource might produce 100m3 of
        NetVolume every day (i.e. 8 hours are consumed).

        Then, if a resource is assigned to a construction task, and that
        construction task is assigned to concrete slabs totalling 200m3, we can
        calculate that the resource consumes 16 hours of work.

        This calculated work is stored against the resource as scheduled work
        under the resource time data.

        :param resource: The IfcConstructionResource that you want to calculate
            the work performed.
        :type resource: ifcopenshell.entity_instance.entity_instance
        :return None:
        :rtype None:
        """
        self.file = file
        self.settings = {"resource": resource}

    def execute(self):
        self.productivity = ifcopenshell.util.element.get_psets(
            self.settings["resource"]
        ).get("EPset_Productivity", None)
        if not self.productivity:
            # Proposal for Schema - If instance doesn't have any productivity, use the parent's productivity - if any.
            if not self.settings["resource"].Nests:
                return
            else:
                parent_resource = self.settings["resource"].Nests[0].RelatingObject
                self.productivity = ifcopenshell.util.element.get_psets(
                    parent_resource
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
