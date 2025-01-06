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


def add_cost_value(file: ifcopenshell.file, parent: ifcopenshell.entity_instance) -> ifcopenshell.entity_instance:
    """Adds a new value or subvalue to a cost item

    A cost item's subtotal can be specified in two ways.

    Option 1 is by simply manually specifying the subtotal value, which
    represents the full cost of that cost item. This option occurs when a
    cost item has no quantities associated with it.

    Option 2 is by specifying a unit cost value of the cost item, which is
    then multiplied by the associated quantity of the cost item, to give us
    the subtotal. This option occurs when a cost item has quantities
    associated with it.

    For either option 1 (full cost value) or option 2 (unit cost value), the
    cost value may be specified as a single number, or as a sum of
    subcomponents or formulas (e.g. multiplication by wastage factor, or
    adding taxes or other adjustments).

    This function lets you add a single top level unit value to a cost item,
    or alternatively price subcomponents by using the "parent" parameter.

    More advanced usage, which involves summing, subcategory-filtered costs,
    and formulas are possible but not yet documented.

    :param parent: A parent IfcCostItem, if specifying a price directly to a
        cost item, or a top-level price component. Alternatively, this can
        be set to a IfcCostValue, if specifying price subcomponents.
    :type parent: ifcopenshell.entity_instance
    :return: The newly created IfcCostValue
    :rtype: ifcopenshell.entity_instance

    Example:

    .. code:: python

        # We always need a schedule first prior to adding any cost items
        schedule = ifcopenshell.api.cost.add_cost_schedule(model)

        # Option 1: This cost item will have a full cost of 42.0
        item1 = ifcopenshell.api.cost.add_cost_item(model, cost_schedule=schedule)
        value = ifcopenshell.api.cost.add_cost_value(model, parent=item1)
        ifcopenshell.api.cost.edit_cost_value(model, cost_value=value,
            attributes={"AppliedValue": 42.0})

        # Option 2: This cost item will have a unit cost of 5.0 per unit
        # area, multiplied by the quantity of area specified explicitly as
        # 3.0, giving us a subtotal cost of 15.0.
        item2 = ifcopenshell.api.cost.add_cost_item(model, cost_schedule=schedule)
        value = ifcopenshell.api.cost.add_cost_value(model, parent=item2)
        ifcopenshell.api.cost.edit_cost_value(model, cost_value=value,
            attributes={"AppliedValue": 5.0})
        quantity = ifcopenshell.api.cost.add_cost_item_quantity(model,
            cost_item=item2, ifc_class="IfcQuantityVolume")
        ifcopenshell.api.cost.edit_cost_item_quantity(model,
            physical_quantity=quantity, "attributes": {"VolumeValue": 3.0})

        # A cost value may also be specified in terms of the sum of its
        # subcomponents. In this case, it's broken down into 2 subvalues.
        item1 = ifcopenshell.api.cost.add_cost_item(model, cost_schedule=schedule)
        value = ifcopenshell.api.cost.add_cost_value(model, parent=item1)
        subvalue1 = ifcopenshell.api.cost.add_cost_value(model, parent=value)
        subvalue2 = ifcopenshell.api.cost.add_cost_value(model, parent=value)

        # This specifies that the value is the sum of all subitems
        # regardless of their cost category. The first subvalue is 2.0 and
        # the second is 3.0, giving a total value of 5.0.
        ifcopenshell.api.cost.edit_cost_value(model, cost_value=value, attributes={"Category": "*"})
        ifcopenshell.api.cost.edit_cost_value(model,
            cost_value=subvalue1, attributes={"AppliedValue": 2.0})
        ifcopenshell.api.cost.edit_cost_value(model,
            cost_value=subvalue2, attributes={"AppliedValue": 3.0})
    """
    settings = {"parent": parent}

    value = file.create_entity("IfcCostValue")
    if settings["parent"].is_a("IfcCostItem"):
        values = list(settings["parent"].CostValues or [])
        values.append(value)
        settings["parent"].CostValues = values
    elif settings["parent"].is_a("IfcConstructionResource"):
        values = list(settings["parent"].BaseCosts or [])
        values.append(value)
        settings["parent"].BaseCosts = values
    elif settings["parent"].is_a("IfcCostValue"):
        values = list(settings["parent"].Components or [])
        values.append(value)
        settings["parent"].Components = values
    return value
