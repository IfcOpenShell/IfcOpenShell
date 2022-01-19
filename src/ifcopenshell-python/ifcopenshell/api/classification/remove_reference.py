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

import ifcopenshell.util.schema


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"reference": None, "product": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        total_related_objects = 0
        for association in self.file.by_type("IfcRelAssociatesClassification"):
            if association.RelatingClassification == self.settings["reference"] and association.RelatedObjects:
                total_related_objects += len(association.RelatedObjects)
                related_objects = list(association.RelatedObjects)
                try:
                    related_objects.remove(self.settings["product"])
                except:
                    continue
                if len(related_objects):
                    association.RelatedObjects = related_objects
                else:
                    self.file.remove(association)

        # TODO: we only handle lightweight classifications here
        if total_related_objects == 1:
            self.file.remove(self.settings["reference"])
