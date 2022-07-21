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
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"product": None, "pset": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        to_purge = []
        should_remove_pset = True
        for inverse in self.file.get_inverse(self.settings["pset"]):
            if inverse.is_a("IfcRelDefinesByProperties"):
                if not inverse.RelatedObjects or len(inverse.RelatedObjects) == 1:
                    to_purge.append(inverse)
                else:
                    related_objects = list(inverse.RelatedObjects)
                    related_objects.remove(self.settings["product"])
                    inverse.RelatedObjects = related_objects
                    should_remove_pset = False
        if should_remove_pset:
            if self.settings["pset"].is_a("IfcPropertySet"):
                properties = self.settings["pset"].HasProperties or []
            elif self.settings["pset"].is_a("IfcQuantitySet"):
                properties = self.settings["pset"].Quantities or []
            elif self.settings["pset"].is_a() in ("IfcMaterialProperties", "IfcProfileProperties"):
                properties = self.settings["pset"].Properties or []
            for prop in properties:
                self.file.remove(prop)
            self.file.remove(self.settings["pset"])
        for element in to_purge:
            self.file.remove(element)
