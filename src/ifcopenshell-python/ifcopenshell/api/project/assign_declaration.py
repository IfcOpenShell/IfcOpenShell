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
import ifcopenshell.guid
import ifcopenshell.util.element
from typing import Union


def assign_declaration(
    file: ifcopenshell.file,
    definitions: list[ifcopenshell.entity_instance],
    relating_context: ifcopenshell.entity_instance,
) -> Union[ifcopenshell.entity_instance, None]:
    """Declares the list of elements to the project

    All data in a model must be directly or indirectly related to the
    project. Most data is indirectly related, existing instead within the
    spatial decomposition tree. Other data, such as types, may be declared
    at the top level.

    Most of the time, the API handles declaration automatically for you.
    There is one scenario where you might want to explicitly declare objects
    to the project, and that's when you want to organise objects into
    project libraries for future use (such as an assets library). Assigning
    a declaration lets you say that an object belongs to a library.

    :param definitions: The list of objects you want to declare. Typically a list of assets.
    :type definitions: list[ifcopenshell.entity_instance]
    :param relating_context: The IfcProject, or more commonly the
        IfcProjectLibrary that you want the object to be part of.
    :type relating_context: ifcopenshell.entity_instance
    :return: The new IfcRelDeclares relationship or None if all definitions
        were already declared / do not support declaration.
    :rtype: Union[ifcopenshell.entity_instance, None]

    Example:

    .. code:: python

        # Programmatically generate a library. You could do this visually too.
        library = ifcopenshell.api.project.create_file()
        root = ifcopenshell.api.root.create_entity(library, ifc_class="IfcProject", name="Demo Library")
        context = ifcopenshell.api.root.create_entity(library,
            ifc_class="IfcProjectLibrary", name="Demo Library")

        # It's necessary to say our library is part of our project.
        ifcopenshell.api.project.assign_declaration(library, definitions=[context], relating_context=root)

        # Assign units for our example library
        unit = ifcopenshell.api.unit.add_si_unit(library,
            unit_type="LENGTHUNIT", name="METRE", prefix="MILLI")
        ifcopenshell.api.unit.assign_unit(library, units=[unit])

        # Let's create a single asset of a 200mm thick concrete wall
        wall_type = ifcopenshell.api.root.create_entity(library, ifc_class="IfcWallType", name="WAL01")
        concrete = ifcopenshell.api.material.add_material(file, name="CON", category="concrete")
        rel = ifcopenshell.api.material.assign_material(library,
            products=[wall_type], type="IfcMaterialLayerSet")
        layer = ifcopenshell.api.material.add_layer(library,
            layer_set=rel.RelatingMaterial, material=concrete)
        layer.Name = "Structure"
        layer.LayerThickness = 200

        # Mark our wall type as a reusable asset in our library.
        ifcopenshell.api.project.assign_declaration(library,
            definitions=[wall_type], relating_context=context)

        # All done, just for fun let's save our asset library to disk for later use.
        library.write("/path/to/my-library.ifc")
    """
    settings = {
        "definitions": definitions,
        "relating_context": relating_context,
    }

    relating_context = settings["relating_context"]
    all_declares = relating_context.Declares
    definitions = set(settings["definitions"])

    previous_declares_rels: set[ifcopenshell.entity_instance] = set()
    objects_without_contexts: list[ifcopenshell.entity_instance] = []
    objects_with_contexts: list[ifcopenshell.entity_instance] = []

    # check if there is anything to change
    for definition in definitions:
        has_context = getattr(definition, "HasContext", None)
        if has_context is None:
            continue

        object_rel = next(iter(has_context), None)
        if object_rel is None:
            objects_without_contexts.append(definition)
            continue

        # either rel doesn't exist or product is part of different rel
        if object_rel not in all_declares:
            previous_declares_rels.add(object_rel)
            objects_with_contexts.append(definition)

    objects_to_change = objects_without_contexts + objects_with_contexts
    # nothing to change
    if not objects_to_change:
        return None

    for has_context in previous_declares_rels:
        related_definitions = set(has_context.RelatedDefinitions) - set(objects_with_contexts)
        if related_definitions:
            has_context.RelatedDefinitions = list(related_definitions)
            ifcopenshell.api.owner.update_owner_history(file, **{"element": has_context})
        else:
            history = has_context.OwnerHistory
            file.remove(has_context)
            if history:
                ifcopenshell.util.element.remove_deep2(file, history)

    declares = next(iter(all_declares), None)
    if declares:
        declares.RelatedDefinitions = list(set(declares.RelatedDefinitions) | set(objects_to_change))
        ifcopenshell.api.owner.update_owner_history(file, **{"element": declares})
    else:
        declares = file.create_entity(
            "IfcRelDeclares",
            **{
                "GlobalId": ifcopenshell.guid.new(),
                "OwnerHistory": ifcopenshell.api.owner.create_owner_history(file),
                "RelatedDefinitions": list(objects_to_change),
                "RelatingContext": relating_context,
            },
        )
    return declares
