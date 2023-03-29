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
    def __init__(self, file, unit=None, attributes=None):
        """Edits the attributes of an IfcNamedUnit

        Named units include SI units, conversion based units (imperial units),
        and context dependent units.

        For more information about the attributes and data types of an
        IfcNamedUnit, consult the IFC documentation.

        :param unit: The IfcNamedUnit entity you want to edit
        :type unit: ifcopenshell.entity_instance.entity_instance
        :param attributes: a dictionary of attribute names and values.
        :type attributes: dict, optional
        :return: None
        :rtype: None

        Example:

        .. code:: python

            # Boxes of things
            unit = ifcopenshell.api.run("unit.add_context_dependent_unit", model, name="BOXES")

            # Uh, crates? Boxes? Whatever.
            ifcopenshell.api.run("unit.edit_named_unit", model, unit=unit, attibutes={"Name": "CRATES"})
        """
        self.file = file
        self.settings = {"unit": unit, "attributes": attributes or {}}

    def execute(self):
        for name, value in self.settings["attributes"].items():
            if name == "Dimensions":
                dimensions = self.settings["unit"].Dimensions
                if len(self.file.get_inverse(dimensions)) > 1:
                    self.settings["unit"].Dimensions = self.file.createIfcDimensionalExponents(*value)
                else:
                    for i, exponent in enumerate(value):
                        dimensions[i] = exponent
                continue
            setattr(self.settings["unit"], name, value)
