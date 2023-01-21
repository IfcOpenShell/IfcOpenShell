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

import ifcopenshell.util.element


class Usecase:
    def __init__(self, file, prop_template=None):
        """Removes a property template

        Note that a property set template should always have at least one
        property template to be valid, so take care when removing property
        templates.

        :param prop_template: The IfcSimplePropertyTemplate to remove.
        :type prop_template: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

        Example:

        .. code:: python

            template = ifcopenshell.api.run("pset_template.add_pset_template", model, name="ABC_RiskFactors")

            # Here's two propertes with just default values.
            prop1 = ifcopenshell.api.run("pset_template.add_prop_template", model, pset_template=template)
            prop2 = ifcopenshell.api.run("pset_template.add_prop_template", model, pset_template=template)

            # Let's remove the second one.
            ifcopenshell.api.run("pset_template.remove_prop_template", model, prop_template=prop2)
        """
        self.file = file
        self.settings = {"prop_template": prop_template}

    def execute(self):
        for inverse in self.file.get_inverse(self.settings["prop_template"]):
            if len(inverse.HasPropertyTemplates) == 1:
                inverse.HasPropertyTemplates = []
            else:
                has_property_templates = list(inverse.HasPropertyTemplates)
                has_property_templates.remove(self.settings["prop_template"])
                inverse.HasPropertyTemplates = has_property_templates
        ifcopenshell.util.element.remove_deep(self.file, self.settings["prop_template"])
