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

import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "ifc_class": "IfcStructuralPlanarAction",
            "predefined_type": "CONST",
            "global_or_local": "GLOBAL_COORDS",
            "applied_load": None,
            "structural_member": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        activity = ifcopenshell.api.run(
            "root.create_entity",
            self.file,
            ifc_class=self.settings["ifc_class"],
            predefined_type=self.settings["predefined_type"],
        )
        activity.AppliedLoad = self.settings["applied_load"]
        activity.GlobalOrLocal = self.settings["global_or_local"]

        rel = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcRelConnectsStructuralActivity")
        rel.RelatingElement = self.settings["structural_member"]
        rel.RelatedStructuralActivity = activity
        return activity
