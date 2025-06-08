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

import ifcopenshell
import ifcopenshell.api.cost
import ifcopenshell.util.element


def remove_cost_item(file: ifcopenshell.file, cost_item: ifcopenshell.entity_instance) -> None:
    """Removes a cost item

    All associated relationships with the cost item are also removed,
    however the related resources, products, and tasks themselves are
    retained.

    :param cost_item: The IfcCostItem entity you want to remove
    :return: None

    Example:

    .. code:: python

        schedule = ifcopenshell.api.cost.add_cost_schedule(model)
        item = ifcopenshell.api.cost.add_cost_item(model, cost_schedule=schedule)
        ifcopenshell.api.cost.remove_cost_item(model, cost_item=item)
    """
    # TODO: do a deep purge
    for inverse in file.get_inverse(cost_item):
        if inverse.is_a("IfcRelNests"):
            if inverse.RelatingObject == cost_item:
                for related_object in inverse.RelatedObjects:
                    ifcopenshell.api.cost.remove_cost_item(file, cost_item=related_object)
            elif inverse.RelatedObjects == (cost_item,):
                history = inverse.OwnerHistory
                file.remove(inverse)
                if history:
                    ifcopenshell.util.element.remove_deep2(file, history)
        elif inverse.is_a("IfcRelAssignsToControl"):
            if len(inverse.RelatedObjects) >= 2 or inverse.RelatingControl == cost_item:
                continue
            history = inverse.OwnerHistory
            file.remove(inverse)
            if history:
                ifcopenshell.util.element.remove_deep2(file, history)
    history = cost_item.OwnerHistory
    file.remove(cost_item)
    if history:
        ifcopenshell.util.element.remove_deep2(file, history)
