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


class Usecase:
    def __init__(self, file, cost_item=None, products=None):
        """Removes quantities of a cost item that are calculated on products

        A cost item may have quantities that are parametrically calculated on
        physical products. This lets you remove those quantities. This means
        that any future changes in the physical product's dimensions will not
        have any impact on the cost item.

        :param cost_item: The IfcCostItem to remove quantities from
        :type cost_item: ifcopenshell.entity_instance.entity_instance
        :param products: A list of IfcProducts that may have parametrically
            connected quantities to the cost item
        :type products: list[ifcopenshell.entity_instance.entity_instance]
        :return: None
        :rtype: None

        Example:

        .. code:: python

            schedule = ifcopenshell.api.run("cost.add_cost_schedule", model)
            item = ifcopenshell.api.run("cost.add_cost_item", model, cost_schedule=schedule)

            # Let's imagine a unit cost of 5.0 per unit volume
            value = ifcopenshell.api.run("cost.add_cost_value", model, parent=item)
            ifcopenshell.api.run("cost.edit_cost_value", model, cost_value=value,
                attributes={"AppliedValue": 5.0})

            slab = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcSlab")
            # Usually the quantity would be automatically calculated via a
            # graphical authoring application but let's assign a manual quantity
            # for now.
            qto = ifcopenshell.api.run("pset.add_qto", model, product=slab, name="Qto_SlabBaseQuantities")
            ifcopenshell.api.run("pset.edit_qto", model, qto=qto, properties={"NetVolume": 42.0})

            # Now let's parametrically link the slab's quantity to the cost
            # item. If the slab is edited in the future and 42.0 changes, then
            # the updated value will also automatically be applied to the cost
            # item.
            ifcopenshell.api.run("cost.assign_cost_item_quantity", model,
                cost_item=item, products=[slab], prop_name="NetVolume")

            # Let's change our mind and remove the parametric connection
            ifcopenshell.api.run("cost.unassign_cost_item_quantity", model,
                cost_item=item, products=[slab])
        """
        self.file = file
        self.settings = {"cost_item": cost_item, "products": products or []}

    def execute(self):
        self.quantities = set(self.settings["cost_item"].CostQuantities or [])
        for quantity in self.settings["cost_item"].CostQuantities or []:
            for inverse in self.file.get_inverse(quantity):
                if not inverse.is_a("IfcElementQuantity"):
                    continue
                for rel in inverse.DefinesOccurrence or []:
                    for related_object in rel.RelatedObjects:
                        if related_object in self.settings["products"]:
                            self.quantities.remove(quantity)
        self.settings["cost_item"].CostQuantities = list(self.quantities)
        for product in self.settings["products"]:
            ifcopenshell.api.run(
                "control.unassign_control",
                self.file,
                related_object=product,
                relating_control=self.settings["cost_item"],
            )
        self.update_cost_item_count()

    def update_cost_item_count(self):
        # This is a bold assumption
        # https://forums.buildingsmart.org/t/how-does-a-cost-item-know-that-it-is-counting-a-controlled-product/3564
        if len(self.settings["cost_item"].CostQuantities) == 1:
            quantity = self.settings["cost_item"].CostQuantities[0]
            if quantity.is_a("IfcQuantityCount"):
                count = 0
                for rel in self.settings["cost_item"].Controls:
                    count += len(rel.RelatedObjects)
                quantity[3] = count
