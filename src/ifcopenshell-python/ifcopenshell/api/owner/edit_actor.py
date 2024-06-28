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
from typing import Any


def edit_actor(file: ifcopenshell.file, actor: ifcopenshell.entity_instance, attributes: dict[str, Any]) -> None:
    """Edits the attributes of an IfcActor

    For more information about the attributes and data types of an
    IfcActor, consult the IFC documentation.

    :param actor: The IfcActor entity you want to edit
    :type actor: ifcopenshell.entity_instance
    :param attributes: a dictionary of attribute names and values.
    :type attributes: dict
    :return: None
    :rtype: None

    Example:

    .. code:: python

        # Setup an organisation with a single role
        organisation = ifcopenshell.api.owner.add_organisation(model,
            identification="AWB", name="Architects Without Ballpens")
        role = ifcopenshell.api.owner.add_role(model, assigned_object=organisation)
        ifcopenshell.api.owner.edit_role(model, role=role, attributes={"Role": "ARCHITECT"})

        # Assign that organisation to a newly created actor
        actor = ifcopenshell.api.owner.add_actor(model, actor=organisation)

        # Edit the description of the attribute.
        ifcopenshell.api.actor.edit_actor(model,
            actor=actor, attributes={"Description": "Responsible for buildings A, B, and C."})
    """
    settings = {"actor": actor, "attributes": attributes}

    for name, value in settings["attributes"].items():
        setattr(settings["actor"], name, value)
