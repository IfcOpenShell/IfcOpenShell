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

import ifcopenshell.api.control


def unassign_cost_item_quantity(
    file: ifcopenshell.file, cost_item: ifcopenshell.entity_instance, products: list[ifcopenshell.entity_instance]
) -> None:
    """Removes quantities of a cost item that are calculated on products

    A cost item may have quantities that are parametrically calculated on
    physical products. This lets you remove those quantities. This means
    that any future changes in the physical product's dimensions will not
    have any impact on the cost item.

    :param cost_item: The IfcCostItem to remove quantities from
    :param products: A list of IfcProducts that may have parametrically
        connected quantities to the cost item
    :return: None

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

        # Let's change our mind and remove the parametric connection
        ifcopenshell.api.cost.unassign_cost_item_quantity(model,
            cost_item=item, products=[slab])
    """
    usecase = Usecase()
    usecase.file = file
    return usecase.execute(cost_item, products or [])


class Usecase:
    file: ifcopenshell.file

    def execute(self, cost_item: ifcopenshell.entity_instance, products: list[ifcopenshell.entity_instance]) -> None:
        quantities = set(cost_item.CostQuantities or [])
        for quantity in cost_item.CostQuantities or []:
            for inverse in self.file.get_inverse(quantity):
                if not inverse.is_a("IfcElementQuantity"):
                    continue
                for rel in inverse.DefinesOccurrence or []:
                    for related_object in rel.RelatedObjects:
                        if related_object in products:
                            quantities.remove(quantity)
        cost_item.CostQuantities = list(quantities)
        for product in products:
            ifcopenshell.api.control.unassign_control(
                self.file,
                related_objects=[product],
                relating_control=cost_item,
            )
        self.update_cost_item_count(cost_item)

    def update_cost_item_count(self, cost_item: ifcopenshell.entity_instance) -> None:
        # This is a bold assumption
        # https://forums.buildingsmart.org/t/how-does-a-cost-item-know-that-it-is-counting-a-controlled-product/3564
        if len(cost_item.CostQuantities) == 1:
            quantity = cost_item.CostQuantities[0]
            if quantity.is_a("IfcQuantityCount"):
                count = 0
                for rel in cost_item.Controls:
                    count += len(rel.RelatedObjects)
                if count:
                    quantity[3] = count
                else:
                    self.file.remove(quantity)
