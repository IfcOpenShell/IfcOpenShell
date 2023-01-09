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
    def __init__(self, file, style=None, attributes=None):
        """Edits the attributes of an IfcPresentationStyle

        For more information about the attributes and data types of an
        IfcPresentationStyle, consult the IFC documentation.

        :param style: The IfcPresentationStyle entity you want to edit
        :type style: ifcopenshell.entity_instance.entity_instance
        :param attributes: a dictionary of attribute names and values.
        :type attributes: dict, optional
        :return: None
        :rtype: None

        Example:

        .. code:: python

            # Create a new surface style
            style = ifcopenshell.api.run("style.add_style", model)

            # Change the name of the style to "Foo"
            ifcopenshell.api.run("style.edit_presentation_style", model, style=style, attributes={"Name": "Foo"})
        """
        self.file = file
        self.settings = {"style": style, "attributes": attributes or {}}

    def execute(self):
        for name, value in self.settings["attributes"].items():
            setattr(self.settings["style"], name, value)
