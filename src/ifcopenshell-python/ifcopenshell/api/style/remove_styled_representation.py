# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
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
    def __init__(self, file, representation=None):
        """Removes a styled representation

        Styled representations are typically associated with materials. This
        removes the representation but not the underlying styles.

        :param representation: The IfcStyledRepresentation to remove.
        :type representation: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

        Example:

        .. code:: python

            # Remove a styled representation
            ifcopenshell.api.run("style.remove_styled_representation", model, representation=representation)
        """
        self.file = file
        self.settings = {"representation": representation}

    def execute(self):
        for inverse in self.file.get_inverse(self.settings["representation"]):
            if inverse.is_a("IfcMaterialDefinitionRepresentation") and len(inverse.Representations) == 1:
                self.file.remove(inverse)

        for item in self.settings["representation"].Items:
            if item.is_a("IfcStyledItem") and self.file.get_total_inverses(item) == 1:
                for style in item.Styles:
                    if style.is_a("IfcPresentationStyleAssignment"):
                        self.file.remove(style)
                self.file.remove(item)

        self.file.remove(self.settings["representation"])
