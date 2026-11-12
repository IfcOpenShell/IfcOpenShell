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

import ifcopenshell.api
import ifcopenshell.util.unit


def add_cost_item_quantity(
    file: ifcopenshell.file,
    cost_item: ifcopenshell.entity_instance,
    ifc_class: ifcopenshell.util.unit.QUANTITY_CLASS = "IfcQuantityCount",
) -> ifcopenshell.entity_instance:
    """Adds a new quantity associated with a cost item

    Cost items calculate their subtotal by multiplying the sum of the cost
    item's "values" by the sum of the cost item's "quantities". The
    quantities may be either parametrically linked to quantities measured on
    physical product, or manually specified.

    The quantity must be of a particular type, common examples are:

    - IfcQuantityCount: to count the total occurrences of a product, useful
      for things like doors, windows, and furniture
    - IfcQuantityNumber: any other generic numeric quantity
    - IfcQuantityLength
    - IfcQuantityArea
    - IfcQuantityVolume
    - IfcQuantityWeight
    - IfcQuantityTime

    A cost item must not mix quantities of different types.

    If an IfcQuantityCount is used, then this API will automatically count
    all products that this cost item controls (see
    ifcopenshell.api.controls.assign_control) and prefill that quantity.

    For all other quantity types, the quantity is left as zero and the user
    must either manually specify the quantity or parametrically link it
    using another API call.

    :param cost_item: The IfcCostItem to add the quantity to
    :param ifc_class: The type of quantity to add
    :return: The newly created quantity entity, chosen from the ifc_class
        parameter

    Example:

    .. code:: python

        chair = ifcopenshell.api.root.create_entity(model, ifc_class="IfcFurniture")
        schedule = ifcopenshell.api.cost.add_cost_schedule(model)
        item = ifcopenshell.api.cost.add_cost_item(model, cost_schedule=schedule)
        ifcopenshell.api.control.assign_control(model,
            relating_control=item, related_objects=[chair])

        # Let's assume we want to count the amount of chairs to calculate our cost item
        # Because this is an IfcQuantityCount the count will be automatically set to "1" chair
        ifcopenshell.api.cost.add_cost_item_quantity(model,
            cost_item=item, ifc_class="IfcQuantityCount")
    """
    quantity = file.create_entity(ifc_class, Name="Unnamed")
    # 3 IfcPhysicalSimpleQuantity Value
    # This is a bold assumption
    # https://forums.buildingsmart.org/t/how-does-a-cost-item-know-that-it-is-counting-a-controlled-product/3564
    if ifc_class == "IfcQuantityCount":
        count = 0
        for rel in cost_item.Controls:
            count += len(rel.RelatedObjects)
        quantity[3] = count
    else:
        quantity[3] = 0.0
    quantities = list(cost_item.CostQuantities or [])
    quantities.append(quantity)
    cost_item.CostQuantities = quantities
    return quantity
