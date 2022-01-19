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
import ifcopenshell.util.cost
import ifcopenshell.util.unit
import ifcopenshell.util.element


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"cost_value": None, "formula": {}}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        try:
            data = ifcopenshell.util.cost.unserialise_cost_value(self.settings["formula"], self.settings["cost_value"])
        except:
            return
        self.edit_cost_value(data)

    def edit_cost_value(self, data, parent=None):
        ifc = data.get("ifc", None)
        if not ifc:
            ifc = ifcopenshell.api.run("cost.add_cost_value", self.file, parent=parent)
        if "AppliedValue" in data:
            if data["AppliedValue"]:
                ifc.AppliedValue = self.file.createIfcMonetaryMeasure(data["AppliedValue"])
            else:
                ifc.AppliedValue = None
        ifc.Category = data["Category"] if "Category" in data else None
        ifc.ArithmeticOperator = data["ArithmeticOperator"] if "ArithmeticOperator" in data else None
        if "Components" in data:
            for component in data["Components"]:
                self.edit_cost_value(component, ifc)
