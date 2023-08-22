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


class Usecase:
    def __init__(self, file, product=None, pset=None):
        """Removes a property set from a product

        All properties that are part of this property set are also removed.

        :param product: The IfcObject to remove the property set from.
        :type product: ifcopenshell.entity_instance.entity_instance
        :param pset: The IfcPropertySet or IfcElementQuantity to remove.
        :type pset: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

        Example:

        .. code:: python

            # Let's imagine we have a new wall type with a property set.
            wall_type = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcWallType")
            pset = ifcopenshell.api.run("pset.add_pset", model, product=wall_type, name="Pset_WallCommon")

            # Remove it!
            ifcopenshell.api.run("pset.remove_pset", model, product=wall_type, pset=pset)
        """
        self.file = file
        self.settings = {"product": product, "pset": pset}

    def execute(self):
        to_purge = []
        should_remove_pset = True
        for inverse in self.file.get_inverse(self.settings["pset"]):
            if inverse.is_a("IfcRelDefinesByProperties"):
                if not inverse.RelatedObjects or len(inverse.RelatedObjects) == 1:
                    to_purge.append(inverse)
                else:
                    related_objects = list(inverse.RelatedObjects)
                    related_objects.remove(self.settings["product"])
                    inverse.RelatedObjects = related_objects
                    should_remove_pset = False
        if should_remove_pset:
            properties = []  # Predefined psets have no properties
            if self.settings["pset"].is_a("IfcPropertySet"):
                properties = self.settings["pset"].HasProperties or []
            elif self.settings["pset"].is_a("IfcQuantitySet"):
                properties = self.settings["pset"].Quantities or []
            elif self.settings["pset"].is_a() in ("IfcMaterialProperties", "IfcProfileProperties"):
                properties = self.settings["pset"].Properties or []
            for prop in properties:
                if self.file.get_total_inverses(prop) == 1:
                    self.file.remove(prop)
            self.file.remove(self.settings["pset"])
        for element in to_purge:
            self.file.remove(element)
