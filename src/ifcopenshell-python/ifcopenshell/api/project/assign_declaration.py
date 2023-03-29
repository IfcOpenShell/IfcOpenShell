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
        """Declares an element to the project

        All data in a model must be directly or indirectly related to the
        project. Most data is indirectly related, existing instead within the
        spatial decomposition tree. Other data, such as types, may be declared
        at the top level.

        Most of the time, the API handles declaration automatically for you.
        There is one scenario where you might want to explicitly declare objects
        to the project, and that's when you want to organise objects into
        project libraries for future use (such as an assets library). Assigning
        a declaration lets you say that an object belongs to a library.

        :param definition: The object you want to declare. Typically an asset.
        :type definition: ifcopenshell.entity_instance.entity_instance
        :param relating_context: The IfcProject, or more commonly the
            IfcProjectLibrary that you want the object to be part of.
        :type relating_context: ifcopenshell.entity_instance.entity_instance
        :return: The new IfcRelDeclares relationship
        :rtype: ifcopenshell.entity_instance.entity_instance

        Example:

        .. code:: python

            # Programmatically generate a library. You could do this visually too.
            library = ifcopenshell.api.run("project.create_file")
            root = ifcopenshell.api.run("root.create_entity", library, ifc_class="IfcProject", name="Demo Library")
            context = ifcopenshell.api.run("root.create_entity", library,
                ifc_class="IfcProjectLibrary", name="Demo Library")

            # It's necessary to say our library is part of our project.
            ifcopenshell.api.run("project.assign_declaration", library, definition=context, relating_context=root)

            # Assign units for our example library
            unit = ifcopenshell.api.run("unit.add_si_unit", library,
                unit_type="LENGTHUNIT", name="METRE", prefix="MILLI")
            ifcopenshell.api.run("unit.assign_unit", library, units=[unit])

            # Let's create a single asset of a 200mm thick concrete wall
            wall_type = ifcopenshell.api.run("root.create_entity", library, ifc_class="IfcWallType", name="WAL01")
            concrete = ifcopenshell.api.run("material.add_material", self.file, name="CON", category="concrete")
            rel = ifcopenshell.api.run("material.assign_material", library,
                product=wall_type, type="IfcMaterialLayerSet")
            layer = ifcopenshell.api.run("material.add_layer", library,
                layer_set=rel.RelatingMaterial, material=concrete)
            layer.Name = "Structure"
            layer.LayerThickness = 200

            # Mark our wall type as a reusable asset in our library.
            ifcopenshell.api.run("project.assign_declaration", library,
                definition=wall_type, relating_context=context)

            # All done, just for fun let's save our asset library to disk for later use.
            library.write("/path/to/my-library.ifc")
        """
        self.file = file
        self.settings = {
            "definition": definition,
            "relating_context": relating_context,
        }

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
