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
import ifcopenshell.util.element


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"product": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if self.settings["product"].is_a("IfcTypeObject"):
            material = ifcopenshell.util.element.get_material(self.settings["product"])
            if material.is_a() in ["IfcMaterialLayerSet", "IfcMaterialProfileSet"]:
                for inverse in self.file.get_inverse(material):
                    if self.file.schema == "IFC2X3":
                        if not inverse.is_a("IfcMaterialLayerSetUsage"):
                            continue
                        for inverse2 in self.file.get_inverse(inverse):
                            if inverse2.is_a("IfcRelAssociatesMaterial"):
                                self.file.remove(inverse2)
                    else:
                        if not inverse.is_a("IfcMaterialUsageDefinition"):
                            continue
                        for rel in inverse.AssociatedTo:
                            self.file.remove(rel)
                    self.file.remove(inverse)

        for rel in self.settings["product"].HasAssociations:
            if rel.is_a("IfcRelAssociatesMaterial"):
                if rel.RelatingMaterial.is_a() in ["IfcMaterialLayerSetUsage", "IfcMaterialProfileSetUsage"]:
                    self.file.remove(rel.RelatingMaterial)
                if len(rel.RelatedObjects) == 1:
                    self.file.remove(rel)
                    continue
                related_objects = set(rel.RelatedObjects)
                related_objects.remove(self.settings["product"])
                rel.RelatedObjects = list(related_objects)
