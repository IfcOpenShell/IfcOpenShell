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
import ifcopenshell.util.pset


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"qto": None, "name": None, "properties": {}}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        self.qto_idx = 5
        if self.settings["qto"].is_a("IfcPhysicalComplexQuantity"):
            self.qto_idx = 2

        self.update_qto_name()
        self.load_qto_template()
        self.update_existing_properties()
        new_properties = self.add_new_properties()
        self.extend_qto_with_new_properties(new_properties)

    def update_qto_name(self):
        if self.settings["name"]:
            self.settings["qto"].Name = self.settings["name"]

    def load_qto_template(self):
        # TODO: add IFC2X3 PsetQto template support
        self.psetqto = ifcopenshell.util.pset.get_template("IFC4")
        self.qto_template = self.psetqto.get_by_name(self.settings["qto"].Name)

    def update_existing_properties(self):
        for prop in self.settings["qto"][self.qto_idx] or []:
            self.update_existing_property(prop)

    def update_existing_property(self, prop):
        if prop.Name not in self.settings["properties"]:
            return
        value = self.settings["properties"][prop.Name]
        name = prop.Name
        if value is None:
            self.file.remove(prop)
        elif prop.is_a("IfcPhysicalSimpleQuantity"):
            value = value.wrappedValue if isinstance(value, ifcopenshell.entity_instance) else value
            prop[3] = float(value)
        del self.settings["properties"][name]

    def add_new_properties(self):
        properties = []
        for name, value in self.settings["properties"].items():
            if value is None:
                continue
            property_type = self.get_canonical_property_type(name, value)
            value = value.wrappedValue if isinstance(value, ifcopenshell.entity_instance) else value
            properties.append(
                self.file.create_entity(
                    "IfcQuantity{}".format(property_type),
                    **{"Name": name, "{}Value".format(property_type): value},
                )
            )
        return properties

    def extend_qto_with_new_properties(self, new_properties):
        props = list(self.settings["qto"][self.qto_idx]) if self.settings["qto"][self.qto_idx] else []
        props.extend(new_properties)
        self.settings["qto"][self.qto_idx] = props

    def get_canonical_property_type(self, name, value):
        if isinstance(value, ifcopenshell.entity_instance):
            result = value.is_a().replace("Ifc", "").replace("Measure", "")
            # Sigh, IFC inconsistencies
            if result == "Numeric":
                result = "Number"
            elif result == "Mass":
                result = "Weight"
            return result
        if self.qto_template:
            for prop_template in self.qto_template.HasPropertyTemplates:
                if prop_template.Name != name:
                    continue
                return prop_template.TemplateType[2:].lower().capitalize()
        return "Length"

    def get_primary_measure_type(self, name, previous_value=None):
        if not self.qto_template:
            return previous_value.is_a() if previous_value else "IfcLabel"
        for prop_template in self.qto_template.HasPropertyTemplates:
            if prop_template.Name != name:
                continue
            return prop_template.PrimaryMeasureType or "IfcLabel"
        return previous_value.is_a() if previous_value else "IfcLabel"
