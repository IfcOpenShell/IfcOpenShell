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
        self.settings = {"material_set": None, "old_index": 0, "new_index": 0}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if self.settings["material_set"].is_a("IfcMaterialConstituentSet"):
            set_name = "MaterialConstituents"
        elif self.settings["material_set"].is_a("IfcMaterialLayerSet"):
            set_name = "MaterialLayers"
        elif self.settings["material_set"].is_a("IfcMaterialProfileSet"):
            set_name = "MaterialProfiles"
        elif self.settings["material_set"].is_a("IfcMaterialList"):
            set_name = "Materials"
        items = list(getattr(self.settings["material_set"], set_name) or [])
        items.insert(self.settings["new_index"], items.pop(self.settings["old_index"]))
        setattr(self.settings["material_set"], set_name, items)
