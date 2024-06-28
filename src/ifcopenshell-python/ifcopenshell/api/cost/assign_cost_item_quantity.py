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

import ifcopenshell.api.cost
import ifcopenshell.api.control
from typing import Any


def assign_cost_item_quantity(
    file: ifcopenshell.file,
    cost_item: ifcopenshell.entity_instance,
    products: list[ifcopenshell.entity_instance],
    prop_name: str = "",
) -> None:
    """Adds a cost item quantity that is parametrically connected to a product

    A cost item may have its subtotal calculated by multiplying a unit value
    by a quantity associated with the cost item. That quantity may be either
    manually specified or parametrically connected to a quantity on a
    product. This API function lets you create that parametric connection.

    For example, you may wish to have a cost item linked to the "NetVolume"
    quantity on all IfcSlabs. Each quantity has a name which you can
    specify. If the quantity is updated in-place (which should occur for
    Native IFC applications) then the quantity for the cost item will
    automatically update as well. If the quantity is deleted and then
    re-added, then the parametric relationship is also lost.

    This API also automatically assigns a control relationship between the
    cost item and the product, so it is not necessary to use
    ifcopenshell.api.control.assign_control.

    If cost item has just 1 quantity and it's IfcQuantityCount, API will
    assume that quantity is used for counting controlled objects
    and it will recalculate the quantity value at the end of the API call.

    :param cost_item: The IfcCostItem to assign parametric quantities to
    :type cost_item: ifcopenshell.entity_instance
    :param products: The IfcObjects to assign parametric quantities to
    :type products: list[ifcopenshell.entity_instance]
    :param prop_name: The name of the quantity. If this is not specified,
        then it is assumed that there is no calculated quantity, and the
        number of objects are counted instead.
    :type prop_name: str, optional
    :return: None
    :rtype: None

    Example:

    .. code:: python

        schedule = ifcopenshell.api.cost.add_cost_schedule(model)
        item = ifcopenshell.api.cost.add_cost_item(model, cost_schedule=schedule)

        # Let's imagine a unit cost of 5.0 per unit volume
        value = ifcopenshell.api.cost.add_cost_value(model, parent=item)
        ifcopenshell.api.cost.edit_cost_value(model, cost_value=value,
            attributes={"AppliedValue": 5.0})

        slab = ifcopenshell.api.root.create_entity(model, ifc_class="IfcSlab")
        # Usually the quantity would be automatically calculated via a
        # graphical authoring application but let's assign a manual quantity
        # for now.
        qto = ifcopenshell.api.pset.add_qto(model, product=slab, name="Qto_SlabBaseQuantities")
        ifcopenshell.api.pset.edit_qto(model, qto=qto, properties={"NetVolume": 42.0})

        # Now let's parametrically link the slab's quantity to the cost
        # item. If the slab is edited in the future and 42.0 changes, then
        # the updated value will also automatically be applied to the cost
        # item.
        ifcopenshell.api.cost.assign_cost_item_quantity(model,
            cost_item=item, products=[slab], prop_name="NetVolume")
    """
    usecase = Usecase()
    usecase.file = file
    usecase.settings = {
        "cost_item": cost_item,
        "products": products or [],
        "prop_name": prop_name,
    }
    return usecase.execute()


class Usecase:
    file: ifcopenshell.file
    settings: dict[str, Any]

    def execute(self):
        if self.settings["prop_name"]:
            self.quantities = set(self.settings["cost_item"].CostQuantities or [])
        for product in self.settings["products"]:
            self.assign_cost_control(related_object=product, cost_item=self.settings["cost_item"])
            if self.settings["prop_name"]:
                if (
                    self.settings["cost_item"].CostQuantities
                    and self.settings["cost_item"].CostQuantities[0].Name.lower() != self.settings["prop_name"].lower()
                ) or not product.is_a("IfcObject"):
                    continue
                self.add_quantity_from_related_object(product)
        if self.settings["prop_name"]:
            self.settings["cost_item"].CostQuantities = list(self.quantities)
        else:
            self.update_cost_item_count()

    def assign_cost_control(
        self, related_object: ifcopenshell.entity_instance, cost_item: ifcopenshell.entity_instance
    ) -> ifcopenshell.entity_instance:
        return ifcopenshell.api.control.assign_control(
            self.file,
            related_object=related_object,
            relating_control=cost_item,
        )

    def add_quantity_from_related_object(self, element: ifcopenshell.entity_instance) -> None:
        for relationship in element.IsDefinedBy:
            if relationship.is_a("IfcRelDefinesByProperties"):
                self.add_quantity_from_qto(relationship.RelatingPropertyDefinition)

    def add_quantity_from_qto(self, qto: ifcopenshell.entity_instance) -> None:
        if not qto.is_a("IfcElementQuantity"):
            return
        for prop in qto.Quantities:
            if prop.is_a("IfcPhysicalSimpleQuantity") and prop.Name.lower() == self.settings["prop_name"].lower():
                self.quantities.add(prop)

    def update_cost_item_count(self):
        # This is a bold assumption
        # https://forums.buildingsmart.org/t/how-does-a-cost-item-know-that-it-is-counting-a-controlled-product/3564
        if not self.settings["cost_item"].CostQuantities:
            ifcopenshell.api.cost.add_cost_item_quantity(
                self.file,
                cost_item=self.settings["cost_item"],
                ifc_class="IfcQuantityCount",
            )
        if len(self.settings["cost_item"].CostQuantities) == 1:
            quantity = self.settings["cost_item"].CostQuantities[0]
            if quantity.is_a("IfcQuantityCount"):
                count = 0
                for rel in self.settings["cost_item"].Controls:
                    count += len(rel.RelatedObjects)
                quantity[3] = count
