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

import ifcopenshell.api.resource
import ifcopenshell.util.constraint
import ifcopenshell.util.date
import ifcopenshell.util.element
import ifcopenshell.util.resource


def calculate_resource_work(file: ifcopenshell.file, resource: ifcopenshell.entity_instance) -> None:
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
    :type resource: ifcopenshell.entity_instance
    :return None:
    :rtype: None:
    """
    if ifcopenshell.util.constraint.is_attribute_locked(resource, "Usage.ScheduleWork"):
        return
    amount_worked = ifcopenshell.util.resource.get_resource_required_work(resource)
    if not amount_worked:
        return
    if not resource.Usage:
        ifcopenshell.api.resource.add_resource_time(file, resource=resource)
    resource.Usage.ScheduleWork = amount_worked
