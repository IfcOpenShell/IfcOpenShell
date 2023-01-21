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
    def __init__(self, file, product=None, attributes=None):
        """Edit the attributes of a product

        All IFC entities have attributes. Normally they can be edited directly,
        by simply assigning a new value to them. In some scenarios, you may wish
        to also ensure that ownership history is updated. This function provides
        that convenience.

        :param product: The product you want to edit. This may be any rooted IFC
            entity.
        :type product: ifcopenshell.entity_instance.entity_instance
        :param attributes: a dictionary of attribute names and values.
        :type attributes: dict, optional
        :return: None
        :rtype: None

        Example:

        .. code:: python

            element = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcWall")
            ifcopenshell.api.run("attribute.edit_attributes", model,
                product=element, attributes={"Name": "Waldo"})
        """
        self.file = file
        self.settings = {"product": product, "attributes": attributes or {}}

    def execute(self):
        for name, value in self.settings["attributes"].items():
            setattr(self.settings["product"], name, value)
        if hasattr(self.settings["product"], "OwnerHistory"):
            ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": self.settings["product"]})
