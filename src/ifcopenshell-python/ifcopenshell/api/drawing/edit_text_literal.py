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
    def __init__(self, file, text_literal=None, attributes=None):
        """Edits the attributes of an IfcTextLiteral

        For more information about the attributes and data types of an
        IfcTextLiteral, consult the IFC documentation.

        :param reference: The IfcTextLiteral entity you want to edit
        :type reference: ifcopenshell.entity_instance.entity_instance
        :param attributes: a dictionary of attribute names and values.
        :type attributes: dict, optional
        :return: None
        :rtype: None

        Example:

        .. code:: python

            text = model.createIfcTextLiteral()
            ifcopenshell.api.run("drawing.edit_text_literal", model,
                text_literal=text, attributes={"Literal": "MY ANNOTATION"})
        """
        self.file = file
        self.settings = {"text_literal": text_literal, "attributes": attributes or {}}

    def execute(self):
        for name, value in self.settings["attributes"].items():
            setattr(self.settings["text_literal"], name, value)
