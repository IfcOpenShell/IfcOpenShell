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
    def __init__(self, file, definition=None, relating_context=None):
        """Unassigns an object to a project or project library

        Typically used to remove an asset from a project library.

        :param definition: The object you want to undeclare. Typically an asset.
        :type definition: ifcopenshell.entity_instance.entity_instance
        :param relating_context: The IfcProject, or more commonly the
            IfcProjectLibrary that you want the object to no longer be part of.
        :type relating_context: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

        Example:

        .. code:: python

            # Programmatically generate a library. You could do this visually too.
            library = ifcopenshell.api.run("project.create_file")
            root = ifcopenshell.api.run("root.create_entity", library, ifc_class="IfcProject", name="Demo Library")
            context = ifcopenshell.api.run("root.create_entity", library,
                ifc_class="IfcProjectLibrary", name="Demo Library")

            # It's necessary to say our library is part of our project.
            ifcopenshell.api.run("project.assign_declaration", library, definition=context, relating_context=root)

            # Remove the library from our project
            ifcopenshell.api.run("project.unassign_declaration", library, definition=context, relating_context=root)
        """
        self.file = file
        self.settings = {
            "definition": definition,
            "relating_context": relating_context,
        }

    def execute(self):
        if not self.settings["definition"].HasContext:
            return
        rel = self.settings["definition"].HasContext[0]
        related_definitions = set(rel.RelatedDefinitions) or set()
        related_definitions.remove(self.settings["definition"])
        if len(related_definitions):
            rel.RelatedDefinitions = list(related_definitions)
            ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": rel})
        else:
            self.file.remove(rel)
