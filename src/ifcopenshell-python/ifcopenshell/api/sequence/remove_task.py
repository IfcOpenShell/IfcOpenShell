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
        self.settings = {"task": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        # TODO: do a deep purge
        ifcopenshell.api.run(
            "project.unassign_declaration",
            self.file,
            definition=self.settings["task"],
            relating_context=self.file.by_type("IfcContext")[0],
        )
        for inverse in self.file.get_inverse(self.settings["task"]):
            if inverse.is_a("IfcRelSequence"):
                self.file.remove(inverse)
            elif inverse.is_a("IfcRelNests"):
                if inverse.RelatingObject == self.settings["task"]:
                    for related_object in inverse.RelatedObjects:
                        ifcopenshell.api.run(
                            "sequence.remove_task", self.file, task=related_object
                        )
                elif inverse.RelatedObjects == tuple(self.settings["task"]):
                    self.file.remove(inverse)
            elif inverse.is_a("IfcRelAssignsToControl"):
                if len(inverse.RelatedObjects) == 1:
                    self.file.remove(inverse)
                else:
                    related_objects = list(inverse.RelatedObjects)
                    related_objects.remove(self.settings["task"])
                    inverse.RelatedObjects = related_objects
        self.file.remove(self.settings["task"])
