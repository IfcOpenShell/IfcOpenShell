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


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "relating_element": None,
            "related_element": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        incompatible_connections = []

        for rel in self.settings["relating_element"].ConnectedTo:
            if rel.is_a() == "IfcRelConnectsElements" and rel.RelatedElement == self.settings["related_element"]:
                incompatible_connections.append(rel)

        for rel in self.settings["relating_element"].ConnectedFrom:
            if rel.is_a() == "IfcRelConnectsElements" and rel.RelatingElement == self.settings["related_element"]:
                incompatible_connections.append(rel)

        for rel in self.settings["related_element"].ConnectedTo:
            if rel.is_a() == "IfcRelConnectsElements" and rel.RelatedElement == self.settings["relating_element"]:
                incompatible_connections.append(rel)

        for rel in self.settings["related_element"].ConnectedFrom:
            if rel.is_a() == "IfcRelConnectsElements" and rel.RelatingElement == self.settings["relating_element"]:
                incompatible_connections.append(rel)

        if incompatible_connections:
            for connection in set(incompatible_connections):
                self.file.remove(connection)
