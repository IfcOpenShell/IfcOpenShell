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
    def __init__(self, file, opening=None):
        """Remove an opening

        Fillings are retained as orphans. Voided elements remain. Openings
        cannot exist by themselves, so not only is the opening relationship
        removed, the opening is also removed.

        :param opening: The IfcOpeningElement to remove.
        :type opening: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

        Example:

        .. code:: python

            # Create an oprhaned opening. Note that an orphaned opening is
            # invalid, as an opening can only exist when voiding another
            # element.
            opening = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcOpeningElement")

            # Remove it. This brings us back to a valid model.
            ifcopenshell.api.run("void.remove_opening", model, opening=opening)
        """
        self.file = file
        self.settings = {"opening": opening}

    def execute(self):
        for rel in self.settings["opening"].VoidsElements:
            self.file.remove(rel)
        for rel in self.settings["opening"].HasFillings:
            self.file.remove(rel)
        ifcopenshell.api.run("root.remove_product", self.file, product=self.settings["opening"])
