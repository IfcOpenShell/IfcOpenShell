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
import ifcopenshell.util.element


class Usecase:
    def __init__(self, file, material=None, element=None):
        """Copies a material to an element

        This convenience function exists to allow you to easily unassign any
        existing material an element has, and assign a new material to it.
        Essentially, it is a form a copy / pasting a material from one element
        to another.

        It's a bit out of place, and will likely be redesigned or removed in the
        future.  It's not recommended to use this function, and
        ifcopenshell.api.material.assign_material should be used instead.

        :param material: The IfcMaterial to assign to the element.
        :type material: ifcopenshell.entity_instance.entity_instance
        :param element: The IfcElement or IfcElementType to remove all previous
            materials from and assign the new material to.
        :type element: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

        Example:

        .. code:: python

            concrete = ifcopenshell.api.run("material.add_material", model, name="CON01", category="concrete")
            wood = ifcopenshell.api.run("material.add_material", model, name="TIM01", category="wood")

            # Let's imagine a concrete bench made out of concrete.
            bench = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcFurniture")
            ifcopenshell.api.run("material.assign_material", model,
                product=bench, type="IfcMaterial", material=concrete)

            # And some street furniture made from wood.
            street_furniture = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcFurniture")
            ifcopenshell.api.run("material.assign_material", model,
                product=street_furniture, type="IfcMaterial", material=wood)

            # Let's copy the concrete over to the street furniture.
            ifcopenshell.api.run("material.copy_material", model, material=wood, element=street_furniture)
        """
        self.file = file
        self.settings = {"material": material, "element": element}

    def execute(self):
        ifcopenshell.api.run("material.unassign_material", self.file, product=self.settings["element"])
        if self.settings["material"].is_a("IfcMaterial"):
            ifcopenshell.api.run(
                "material.assign_material",
                self.file,
                product=self.settings["element"],
                type="IfcMaterial",
                material=self.settings["material"],
            )
        # No other material type can be copied right now.
        # 1. Material lists and constituents may have shape aspects and I
        # haven't implemented it yet.
        # 2. Material layer and profile sets implicitly define parametric
        # geometry and we have no way of guaranteeing that this constraint is
        # satisfied.
        # 3. Material set usages follow an unofficial constraint that all
        # instances must have a usage of their type's material set. We cannot
        # guarantee that constraint.
