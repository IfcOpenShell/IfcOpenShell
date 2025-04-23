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


def unassign_object(file: ifcopenshell.file, related_objects: list[ifcopenshell.entity_instance]) -> None:
    """Unassigns related_objects from their nests.

    An object (the whole within a decomposition) is Nested by zero or one more smaller objects.
    This function will remove this nesting relationship.

    If the object is not part of a nesting relationship, nothing will happen.

    :param related_objects: The list of children of the nesting relationship,
        typically IfcElements.
    :type related_objects: list[ifcopenshell.entity_instance]
    :return: None
    :rtype: None

    Example:

    .. code:: python

        task = ifcopenshell.api.root.create_entity(model, ifc_class="IfcTasks")
        subtask1 = ifcopenshell.api.root.create_entity(model, ifc_class="IfcTask")
        subtask2 = ifcopenshell.api.root.create_entity(model, ifc_class="IfcTask")
        ifcopenshell.api.nest.assign_object(model, related_objects=[subtask1], relating_object=task)
        ifcopenshell.api.nest.assign_object(model, related_objects=[subtask2], relating_object=task)
        # nothing is returned
        rel = ifcopenshell.api.nest.unassign_object(model, related_objects=[subtask1])
        # nothing is returned, relationship is removed
        ifcopenshell.api.nest.unassign_object(model, related_objects=[subtask2])
    """

    # NOTE: maintain .RelatedObjects order as it has meaning in IFC
    related_objects_set = set(related_objects)
    ifc2x3 = file.schema == "IFC2X3"
    if ifc2x3:
        rels = set(
            rel
            for object in related_objects_set
            if (rel := next((rel for rel in object.Decomposes if rel.is_a("IfcRelNests")), None))
        )
    else:
        rels = set(rel for object in related_objects if (rel := next((rel for rel in object.Nests), None)))

    for rel in rels:
        cur_related_objects = [o for o in rel.RelatedObjects if o not in related_objects_set]
        if cur_related_objects:
            rel.RelatedObjects = cur_related_objects
            ifcopenshell.api.owner.update_owner_history(file, **{"element": rel})
        else:
            history = rel.OwnerHistory
            file.remove(rel)
            if history:
                ifcopenshell.util.element.remove_deep2(file, history)
