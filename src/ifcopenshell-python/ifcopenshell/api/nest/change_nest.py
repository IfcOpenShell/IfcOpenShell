# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021-2022 Dion Moult <dion@thinkmoult.com>, Yassine Oualid <yassine@sigmadimensions.com>
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
import ifcopenshell.api

class Usecase:
    def __init__(self, file, item=None, new_parent=None):
        """Assigns a cost item to a new parent cost item"""
        self.file = file
        self.settings = {"item": item, "new_parent": new_parent}

    def execute(self):
        if not self.settings["item"].Nests:
            return
        nests = self.settings["item"].Nests[0]
        related_objects = list(nests.RelatedObjects)
        related_objects.remove(self.settings["item"])
        if related_objects:
            nests.RelatedObjects = related_objects
            ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": nests})
        else:
            self.file.remove(nests)
        ifcopenshell.api.run("nest.assign_object", self.file, related_object=self.settings["item"], relating_object=self.settings["new_parent"])