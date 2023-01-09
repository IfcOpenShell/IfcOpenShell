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

import datetime
import ifcopenshell.util.date


class Usecase:
    def __init__(self, file, resource_time=None, attributes=None):
        """Edits the attributes of an IfcResourceTime

        For more information about the attributes and data types of an
        IfcResourceTime, consult the IFC documentation.

        :param resource_time: The IfcResourceTime entity you want to edit
        :type resource_time: ifcopenshell.entity_instance.entity_instance
        :param attributes: a dictionary of attribute names and values.
        :type attributes: dict, optional
        :return: None
        :rtype: None

        Example:

        .. code:: python

            # Add our own crew
            crew = ifcopenshell.api.run("resource.add_resource", model, ifc_class="IfcCrewResource")

            # Add some labour to our crew.
            labour = ifcopenshell.api.run("resource.add_resource", model,
                parent_resource=crew, ifc_class="IfcLaborResource")

            # Labour resource is quantified in terms of time.
            ifcopenshell.api.run("resource.add_resource_quantity", model,
                resource=labour, ifc_class="IfcQuantityTime")

            # Store the unit time used in hours
            ifcopenshell.api.run("resource.edit_resource_quantity", model,
                physical_quantity=time, attributes={"TimeValue": 8.0})

            # Let's imagine we've used the resource for 2 days.
            time = ifcopenshell.api.run("resource.add_resource_time", model, resource=labour)
            ifcopenshell.api.run("resource.edit_resource_time", model,
                resource_time=time, attributes={"ScheduleWork": "P16H"})
        """
        self.file = file
        self.settings = {"resource_time": resource_time, "attributes": attributes or {}}

    def execute(self):
        self.resource = self.get_resource()

        # If the user specifies both an end date and a duration, the duration takes priority
        if (
            self.settings["attributes"].get("ScheduleWork", None)
            and "ScheduleFinish" in self.settings["attributes"].keys()
        ):
            del self.settings["attributes"]["ScheduleFinish"]
        if (
            self.settings["attributes"].get("ActualWork", None)
            and "ActualFinish" in self.settings["attributes"].keys()
        ):
            del self.settings["attributes"]["ActualFinish"]

        for name, value in self.settings["attributes"].items():
            if value:
                if "Start" in name or "Finish" in name or name == "StatusTime":
                    value = ifcopenshell.util.date.datetime2ifc(value, "IfcDateTime")
                elif (
                    name == "ScheduleWork"
                    or name == "ActualWork"
                    or name == "RemainingTime"
                ):
                    value = ifcopenshell.util.date.datetime2ifc(value, "IfcDuration")
            setattr(self.settings["resource_time"], name, value)

    def get_resource(self):
        return [
            e
            for e in self.file.get_inverse(self.settings["resource_time"])
            if e.is_a("IfcResource")
        ][0]
