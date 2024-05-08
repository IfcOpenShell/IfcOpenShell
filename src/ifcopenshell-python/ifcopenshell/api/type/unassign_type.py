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
import ifcopenshell.util.element


def unassign_type(file: ifcopenshell.file, related_objects: list[ifcopenshell.entity_instance]) -> None:
    """Unassigns a type from occurrences

    Note that unassigning a type doesn't automatically remove mapped representations
    and material usages associated with the previously assigned type.

    :param related_objects: List of IfcElement occurrences.
    :type related_objects: list[ifcopenshell.entity_instance]
    :return: None
    :rtype: None

    Example:

    .. code:: python

        # A furniture type. This would correlate to a particular model in a
        # manufacturer's catalogue. Like an Ikea sofa :)
        furniture_type = ifcopenshell.api.run("root.create_entity", model,
            ifc_class="IfcFurnitureType", name="FUN01")

        # An individual occurrence of a that sofa.
        furniture = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcFurniture")

        # Assign the furniture to the furniture type.
        ifcopenshell.api.run("type.assign_type", model, related_objects=[furniture], relating_type=furniture_type)

        # Change our mind. Maybe it's a different type?
        ifcopenshell.api.run("type.unassign_type", model, related_objects=[furniture])
    """
    settings = {"related_objects": related_objects}

    related_objects = set(settings["related_objects"])

    if file.schema == "IFC2X3":
        rels = set(
            rel
            for object in related_objects
            if (rel := next((rel for rel in object.IsDefinedBy if rel.is_a("IfcRelDefinesByType")), None))
        )
    else:
        rels = set(rel for object in related_objects if (rel := next((rel for rel in object.IsTypedBy), None)))

    for rel in rels:
        related_objects = set(rel.RelatedObjects) - related_objects
        if related_objects:
            rel.RelatedObjects = list(related_objects)
            ifcopenshell.api.run("owner.update_owner_history", file, **{"element": rel})
        else:
            history = rel.OwnerHistory
            file.remove(rel)
            if history:
                ifcopenshell.util.element.remove_deep2(file, history)
