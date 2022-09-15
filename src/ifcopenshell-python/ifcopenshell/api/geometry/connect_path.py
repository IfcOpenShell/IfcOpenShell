# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "relating_element": None,
            "related_element": None,
            "relating_connection": "NOTDEFINED",
            "related_connection": "NOTDEFINED",
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        existing_connection = [
            r
            for r in self.settings["relating_element"].ConnectedTo
            if r.RelatedElement == self.settings["related_element"]
        ]

        if existing_connection:
            existing_connection = existing_connection[0]
            if existing_connection.RelatingConnectionType != self.settings["relating_connection"]:
                existing_connection.RelatingConnectionType = self.settings["relating_connection"]
            if existing_connection.RelatedConnectionType != self.settings["related_connection"]:
                existing_connection.RelatedConnectionType = self.settings["related_connection"]
            return existing_connection[0]

        if [
            r
            for r in self.settings["related_element"].ConnectedTo
            if r.RelatedElement == self.settings["relating_element"]
        ]:
            # No cyclical connections allowed, I assume
            return

        return self.file.createIfcRelConnectsPathElements(
            ifcopenshell.guid.new(),
            OwnerHistory=ifcopenshell.api.run("owner.create_owner_history", self.file),
            RelatingElement=self.settings["relating_element"],
            RelatedElement=self.settings["related_element"],
            RelatingConnectionType=self.settings["relating_connection"],
            RelatedConnectionType=self.settings["related_connection"],
        )
