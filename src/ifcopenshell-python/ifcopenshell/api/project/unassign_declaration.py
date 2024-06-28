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
import ifcopenshell.api.owner
import ifcopenshell.util.element


def unassign_declaration(
    file: ifcopenshell.file,
    definitions: list[ifcopenshell.entity_instance],
    relating_context: ifcopenshell.entity_instance,
) -> None:
    """Unassigns a list of objects from a project or project library

    Typically used to remove an asset from a project library.

    :param definitions: The list of objects you want to undeclare.
        Typically a list of assets.
    :type definitions: list[ifcopenshell.entity_instance]
    :param relating_context: The IfcProject, or more commonly the
        IfcProjectLibrary that you want the object to no longer be part of.
    :type relating_context: ifcopenshell.entity_instance
    :return: None
    :rtype: None

    Example:

    .. code:: python

        # Programmatically generate a library. You could do this visually too.
        library = ifcopenshell.api.project.create_file()
        root = ifcopenshell.api.root.create_entity(library, ifc_class="IfcProject", name="Demo Library")
        context = ifcopenshell.api.root.create_entity(library,
            ifc_class="IfcProjectLibrary", name="Demo Library")

        # It's necessary to say our library is part of our project.
        ifcopenshell.api.project.assign_declaration(library, definitions=[context], relating_context=root)

        # Remove the library from our project
        ifcopenshell.api.project.unassign_declaration(library, definitions=[context], relating_context=root)
    """
    settings = {
        "definitions": definitions,
        "relating_context": relating_context,
    }

    definitions = set(settings["definitions"])
    rels = {rel for obj in definitions if (rel := next(iter(obj.HasContext), None))}

    for rel in rels:
        related_definitions = set(rel.RelatedDefinitions) - definitions
        if related_definitions:
            rel.RelatedDefinitions = list(related_definitions)
            ifcopenshell.api.owner.update_owner_history(file, **{"element": rel})
        else:
            history = rel.OwnerHistory
            file.remove(rel)
            if history:
                ifcopenshell.util.element.remove_deep2(file, history)
