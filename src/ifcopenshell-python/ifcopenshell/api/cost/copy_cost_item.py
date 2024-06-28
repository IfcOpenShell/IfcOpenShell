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
import ifcopenshell.api.nest
import ifcopenshell.util.element
from typing import Union


def copy_cost_item(
    file: ifcopenshell.file, cost_item: ifcopenshell.entity_instance
) -> Union[ifcopenshell.entity_instance, list[ifcopenshell.entity_instance]]:
    # TODO: currently it never returns list of duplicated cost items
    # though it is stated in the docs
    """Copies all cost items and related relationships

    The following relationships are also duplicated:

    * The copy will have the same attributes and property sets as the original cost item
    * The copy will be assigned to the parent cost schedule
    * The copy will have duplicated nested cost items

    :param cost_item: The cost item to be duplicated
    :type cost_item: ifcopenshell.entity_instance
    :return: The duplicated cost item or the list of duplicated cost items if the latter has children
    :rtype: ifcopenshell.entity_instance or list[ifcopenshell.entity_instance]

    Example:
    .. code:: python

        # We have a cost item
        cost_item = CostItem(name="Design new feature", deadline="2023-03-01")

        # And now we have two
        duplicated_cost_item = project.duplicate_cost_item(cost_item)


    """
    usecase = Usecase()
    usecase.file = file
    usecase.settings = {"cost_item": cost_item}
    return usecase.execute()


class Usecase:
    def execute(self):
        self.new_cost_items = []
        return self.duplicate_cost_item(self.settings["cost_item"])

    def duplicate_cost_item(self, cost_item):
        new_cost_item = ifcopenshell.util.element.copy_deep(self.file, cost_item)
        self.new_cost_items.append(new_cost_item)
        self.copy_indirect_attributes(cost_item, new_cost_item)
        return new_cost_item

    def copy_indirect_attributes(self, from_element, to_element):
        for inverse in self.file.get_inverse(from_element):
            if inverse.is_a("IfcRelDefinesByProperties"):
                inverse = ifcopenshell.util.element.copy(self.file, inverse)
                inverse.RelatedObjects = [to_element]
                pset = ifcopenshell.util.element.copy_deep(self.file, inverse.RelatingPropertyDefinition)
                inverse.RelatingPropertyDefinition = pset
            elif inverse.is_a("IfcRelNests") and inverse.RelatingObject == from_element:
                nested_cost_items = [e for e in inverse.RelatedObjects]
                if nested_cost_items:
                    new_cost_items = []
                    for cost_item in nested_cost_items:
                        new_cost_item = self.duplicate_cost_item(cost_item)
                        new_cost_items.append(new_cost_item)
                    inverse = ifcopenshell.util.element.copy(self.file, inverse)
                    inverse.RelatingObject = to_element
                    inverse.RelatedObjects = new_cost_items
                    ifcopenshell.api.nest.unassign_object(self.file, related_objects=new_cost_items)
                    ifcopenshell.api.nest.assign_object(
                        self.file, related_objects=new_cost_items, relating_object=to_element
                    )
            # elif inverse.is_a("IfcRelAssignsToProduct"):
            #     continue
            #     to_element.IsDefinedBy = inverse.RelatingOrder
            # elif inverse.is_a("IfcRelAssignsToProcess"):
            #     to_element.IsDefinedBy = inverse.RelatingProcess
            # elif inverse.is_a("IfcRelAssignsToResource"):
            #     continue
            # elif inverse.is_a("IfcRelAssignsToControl"):
            #     continue
            # elif inverse.is_a("IfcRelDefinesByObject"):
            #     continue
            else:
                for i, value in enumerate(inverse):
                    if value == from_element:
                        new_inverse = ifcopenshell.util.element.copy(self.file, inverse)
                        new_inverse[i] = to_element
                    elif isinstance(value, (tuple, list)) and from_element in value:
                        new_value = list(value)
                        new_value.append(to_element)
                        inverse[i] = new_value
