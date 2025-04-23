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


def unassign_actor(
    file: ifcopenshell.file, relating_actor: ifcopenshell.entity_instance, related_object: ifcopenshell.entity_instance
) -> None:
    """Unassigns an actor to an object

    This means that the actor is no longer responsible for the object.

    :param relating_actor: The IfcActor who is responsible for the object.
    :param related_object: The object the actor is responsible for.
    :return: None

    Example:

    .. code:: python

        # We need to procure and install 2 of this particular pump type in our facility.
        pump_type = ifcopenshell.api.root.create_entity(model, ifc_class="IfcPumpType")

        # Define who the manufacturer is
        manufacturer = ifcopenshell.api.owner.add_organisation(model,
            identification="PWP", name="Pumps With Power")
        ifcopenshell.api.owner.add_role(model, assigned_object=manufacturer, role="MANUFACTURER")

        # Make the manufacturer responsible for that pump type.
        ifcopenshell.api.owner.assign_actor(model,
            relating_actor=manufacturer, related_object=pump_type)

        # Undo the assignment
        ifcopenshell.api.owner.unassign_actor(model,
            relating_actor=manufacturer, related_object=pump_type)
    """
    for rel in related_object.HasAssignments or []:
        if not rel.is_a("IfcRelAssignsToActor") or rel.RelatingActor != relating_actor:
            continue
        if len(rel.RelatedObjects) == 1:
            history = rel.OwnerHistory
            file.remove(rel)
            if history:
                ifcopenshell.util.element.remove_deep2(file, history)
            return
        related_objects = list(rel.RelatedObjects)
        related_objects.remove(related_object)
        rel.RelatedObjects = related_objects
        ifcopenshell.api.owner.update_owner_history(file, **{"element": rel})
