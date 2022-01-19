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
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"source": None, "destination": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        for cost_value in self.settings["destination"].CostValues or []:
            ifcopenshell.api.run("cost.remove_cost_item_value", self.file, cost_value=cost_value)
        copied_cost_values = []
        for cost_value in self.settings["source"].CostValues or []:
            copied_cost_values.append(ifcopenshell.util.element.copy_deep(self.file, cost_value))
        self.settings["destination"].CostValues = copied_cost_values
