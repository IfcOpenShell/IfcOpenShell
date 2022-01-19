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
        self.settings = {"cost_item": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        # TODO: do a deep purge
        for inverse in self.file.get_inverse(self.settings["cost_item"]):
            if inverse.is_a("IfcRelNests"):
                if inverse.RelatingObject == self.settings["cost_item"]:
                    for related_object in inverse.RelatedObjects:
                        ifcopenshell.api.run("cost.remove_cost_item", self.file, cost_item=related_object)
                elif inverse.RelatedObjects == tuple(self.settings["cost_item"]):
                    self.file.remove(inverse)
            elif inverse.is_a("IfcRelAssignsToControl"):
                self.file.remove(inverse)
        self.file.remove(self.settings["cost_item"])
