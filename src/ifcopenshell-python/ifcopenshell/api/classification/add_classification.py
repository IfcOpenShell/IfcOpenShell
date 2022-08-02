# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021, 2022 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell.util.schema
import ifcopenshell.util.date


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "classification": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if isinstance(self.settings["classification"], str):
            classification = self.file.createIfcClassification(Name=self.settings["classification"])
            self.relate_to_project(classification)
            return classification
        return self.add_from_library()

    def add_from_library(self):
        edition_date = None
        if self.settings["classification"].EditionDate:
            edition_date = ifcopenshell.util.date.ifc2datetime(self.settings["classification"].EditionDate)
            self.settings["classification"].EditionDate = None

        migrator = ifcopenshell.util.schema.Migrator()
        result = migrator.migrate(self.settings["classification"], self.file)

        # TODO: should auto date migration be part of the migrator?
        if self.file.schema == "IFC2X3" and edition_date:
            result.EditionDate = self.file.create_entity(
                "IfcCalendarDate", **ifcopenshell.util.date.datetime2ifc(edition_date, "IfcCalendarDate")
            )
        else:
            result.EditionDate = ifcopenshell.util.date.datetime2ifc(edition_date, "IfcDate")

        self.relate_to_project(result)

        return result  # See bug #1272

        try:
            result = self.file.add(self.settings["classification"])
        except:
            migrator = ifcopenshell.util.schema.Migrator()
            result = migrator.migrate(self.settings["classification"], self.file)

    def relate_to_project(self, classification):
        self.file.create_entity(
            "IfcRelAssociatesClassification",
            GlobalId=ifcopenshell.guid.new(),
            RelatedObjects=[self.file.by_type("IfcProject")[0]],
            RelatingClassification=classification,
        )
