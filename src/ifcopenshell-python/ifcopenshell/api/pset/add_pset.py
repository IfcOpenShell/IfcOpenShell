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
        self.settings = {"product": None, "name": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if self.settings["product"].is_a("IfcObject") or self.settings["product"].is_a("IfcContext"):
            for rel in self.settings["product"].IsDefinedBy or []:
                if (
                    rel.is_a("IfcRelDefinesByProperties")
                    and rel.RelatingPropertyDefinition.Name == self.settings["name"]
                ):
                    return rel.RelatingPropertyDefinition

            pset = self.file.create_entity(
                "IfcPropertySet",
                **{
                    "GlobalId": ifcopenshell.guid.new(),
                    "OwnerHistory": ifcopenshell.api.run("owner.create_owner_history", self.file),
                    "Name": self.settings["name"],
                }
            )
            self.file.create_entity(
                "IfcRelDefinesByProperties",
                **{
                    "GlobalId": ifcopenshell.guid.new(),
                    "OwnerHistory": ifcopenshell.api.run("owner.create_owner_history", self.file),
                    "RelatedObjects": [self.settings["product"]],
                    "RelatingPropertyDefinition": pset,
                }
            )
            return pset
        elif self.settings["product"].is_a("IfcTypeObject"):
            for definition in self.settings["product"].HasPropertySets or []:
                if definition.Name == self.settings["name"]:
                    return definition

            pset = self.file.create_entity(
                "IfcPropertySet",
                **{
                    "GlobalId": ifcopenshell.guid.new(),
                    "OwnerHistory": ifcopenshell.api.run("owner.create_owner_history", self.file),
                    "Name": self.settings["name"],
                }
            )
            has_property_sets = list(self.settings["product"].HasPropertySets or [])
            has_property_sets.append(pset)
            self.settings["product"].HasPropertySets = has_property_sets
            return pset
        elif self.settings["product"].is_a("IfcMaterialDefinition"):
            for definition in self.settings["product"].HasProperties or []:
                if definition.Name == self.settings["name"]:
                    return definition

            return self.file.create_entity(
                "IfcMaterialProperties",
                **{
                    "Name": self.settings["name"],
                    "Material": self.settings["product"],
                }
            )
        elif self.settings["product"].is_a("IfcProfileDef"):
            for definition in self.settings["product"].HasProperties or []:
                if definition.Name == self.settings["name"]:
                    return definition

            return self.file.create_entity(
                "IfcProfileProperties",
                **{
                    "Name": self.settings["name"],
                    "ProfileDefinition": self.settings["product"],
                }
            )
