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


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"pset_template": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        prop_template = self.file.create_entity(
            "IfcSimplePropertyTemplate",
            **{
                "GlobalId": ifcopenshell.guid.new(),
                "Name": "NewProperty",
                "PrimaryMeasureType": "IfcLabel",
                "TemplateType": "P_SINGLEVALUE",
                "AccessState": "READWRITE",
                "Enumerators": None
            }
        )
        has_property_templates = list(self.settings["pset_template"].HasPropertyTemplates or [])
        has_property_templates.append(prop_template)
        self.settings["pset_template"].HasPropertyTemplates = has_property_templates
        return prop_template
