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
import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "definition": None,
            "relating_context": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        declares = None
        if self.settings["relating_context"].Declares:
            declares = self.settings["relating_context"].Declares[0]

        if not hasattr(self.settings["definition"], "HasContext"):
            return

        has_context = None
        if self.settings["definition"].HasContext:
            has_context = self.settings["definition"].HasContext[0]

        if has_context and has_context == declares:
            return

        if has_context:
            related_definitions = list(has_context.RelatedDefinitions)
            related_definitions.remove(self.settings["definition"])
            if related_definitions:
                has_context.RelatedDefinitions = related_definitions
                ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": has_context})
            else:
                self.file.remove(has_context)

        if declares:
            related_definitions = set(declares.RelatedDefinitions)
            related_definitions.add(self.settings["definition"])
            declares.RelatedDefinitions = list(related_definitions)
            ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": declares})
        else:
            declares = self.file.create_entity(
                "IfcRelDeclares",
                **{
                    "GlobalId": ifcopenshell.guid.new(),
                    "OwnerHistory": ifcopenshell.api.run("owner.create_owner_history", self.file),
                    "RelatedDefinitions": [self.settings["definition"]],
                    "RelatingContext": self.settings["relating_context"],
                }
            )
        return declares
