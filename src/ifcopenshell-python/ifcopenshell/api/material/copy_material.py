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
        self.settings = {"material": None, "element": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        ifcopenshell.api.run("material.unassign_material", self.file, product=self.settings["element"])
        if self.settings["material"].is_a("IfcMaterial"):
            ifcopenshell.api.run(
                "material.assign_material",
                self.file,
                product=self.settings["element"],
                type="IfcMaterial",
                material=self.settings["material"],
            )
        # No other material type can be copied right now.
        # 1. Material lists and constituents may have shape aspects and I
        # haven't implemented it yet.
        # 2. Material layer and profile sets implicitly define parametric
        # geometry and we have no way of guaranteeing that this constraint is
        # satisfied.
        # 3. Material set usages follow an unofficial constraint that all
        # instances must have a usage of their type's material set. We cannot
        # guarantee that constraint.
