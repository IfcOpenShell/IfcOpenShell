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
            "element": None,
            "connection_type": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if self.settings["connection_type"] and self.settings["element"]:
            connections = [
                r
                for r in self.settings["element"].ConnectedTo
                if r.RelatingConnectionType == self.settings["connection_type"]
            ] + [
                r
                for r in self.settings["element"].ConnectedFrom
                if r.RelatedConnectionType == self.settings["connection_type"]
            ]
        else:
            connections = [
                r
                for r in self.settings["relating_element"].ConnectedTo
                if r.RelatedElement == self.settings["related_element"]
            ]

        for connection in set(connections):
            self.file.remove(connection)
