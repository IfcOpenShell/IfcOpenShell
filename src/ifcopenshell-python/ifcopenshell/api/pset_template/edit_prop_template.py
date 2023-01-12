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
    def __init__(self, file, prop_template=None, attributes=None):
        """Edits the attributes of an IfcSimplePropertyTemplate

        For more information about the attributes and data types of an
        IfcSimplePropertyTemplate, consult the IFC documentation.

        :param prop_template: The IfcSimplePropertyTemplate entity you want to edit
        :type prop_template: ifcopenshell.entity_instance.entity_instance
        :param attributes: a dictionary of attribute names and values.
        :type attributes: dict, optional
        :return: None
        :rtype: None

        Example:

        .. code:: python

            template = ifcopenshell.api.run("pset_template.add_pset_template", model, name="ABC_RiskFactors")

            # Here's a property with just default values.
            prop = ifcopenshell.api.run("pset_template.add_prop_template", model, pset_template=template)

            # Let's edit it to give the actual values we need.
            ifcopenshell.api.run("pset_template.edit_prop_template", model,
                prop_template=prop, attributes={"Name": "DemoA", "PrimaryMeasureType": "IfcLengthMeasure"})
        """
        self.file = file
        self.settings = {"prop_template": prop_template, "attributes": attributes or {}}

    def execute(self):
        for name, value in self.settings["attributes"].items():
            setattr(self.settings["prop_template"], name, value)
