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

import ifcopenshell.util.date


def add_resource_time(file: ifcopenshell.file, resource: ifcopenshell.entity_instance) -> ifcopenshell.entity_instance:
    """Adds the time that a resource is used for

    For labour and equipment resources, the total duration that the resource
    is used for may be stored. This may either be input manually or
    calculated parametrically. This is known as the resource time, and may
    be used to calculate other parameters like resource utilisation.

    :param resource: The IfcConstructionResource to record time for.
    :return: The newly created IfcResourceTime

    Example:

    .. code:: python

        # Add our own crew
        crew = ifcopenshell.api.resource.add_resource(model, ifc_class="IfcCrewResource")

        # Add some labour to our crew.
        labour = ifcopenshell.api.resource.add_resource(model,
            parent_resource=crew, ifc_class="IfcLaborResource")

        # Labour resource is quantified in terms of time.
        quantity = ifcopenshell.api.resource.add_resource_quantity(model,
            resource=labour, ifc_class="IfcQuantityTime")

        # Store the unit time used in hours
        ifcopenshell.api.resource.edit_resource_quantity(model,
            physical_quantity=quantity, attributes={"TimeValue": 8.0})

        # Let's imagine we've used the resource for 2 days.
        time = ifcopenshell.api.resource.add_resource_time(model, resource=labour)
        ifcopenshell.api.resource.edit_resource_time(model,
            resource_time=time, attributes={"ScheduleWork": "PT16H"})
    """
    resource_time = file.create_entity("IfcResourceTime")
    resource.Usage = resource_time
    return resource_time
