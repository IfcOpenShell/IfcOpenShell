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
import ifcopenshell.api


class Usecase:
    def __init__(self, file, product=None, system=None):
        """Unassigns a product from a system

        :param product: The IfcDistributionElement to unassign from the system.
        :type product: ifcopenshell.entity_instance.entity_instance
        :param system: The IfcSystem you want to unassign the element from.
        :type system: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

        Example:

        .. code:: python

            # A completely empty distribution system
            system = ifcopenshell.api.run("system.add_system", model)

            # Create a duct
            duct = ifcopenshell.api.run("root.create_entity", model,
                ifc_class="IfcDuctSegment", predefined_type="RIGIDSEGMENT")

            # This duct is part of the system
            ifcopenshell.api.run("system.assign_system", model, product=duct, system=system)

            # Not anymore!
            ifcopenshell.api.run("system.unassign_system", model, product=duct, system=system)
        """
        self.file = file
        self.settings = {
            "product": product,
            "system": system,
        }

    def execute(self):
        if not self.settings["system"].IsGroupedBy:
            return
        rel = self.settings["system"].IsGroupedBy[0]
        related_objects = set(rel.RelatedObjects) or set()
        related_objects.remove(self.settings["product"])
        if len(related_objects):
            rel.RelatedObjects = list(related_objects)
            ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": rel})
        else:
            self.file.remove(rel)
