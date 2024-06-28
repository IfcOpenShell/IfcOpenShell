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
from typing import Optional


def add_group(
    file: ifcopenshell.file, name: str = "Unnamed", description: Optional[str] = None
) -> ifcopenshell.entity_instance:
    """Adds a new group

    An IFC group is an arbitrary collection of products, which are typically
    physical. It may be used when there is no other more specific group
    which may be used. Other types of groups include distribution systems,
    which group together products that are connected and circulate a medium
    (such as fluid or electricity), or zones, which group together spaces,
    or structural load groups, which group together loads for structural
    analysis, or inventories, which are groups of assets.

    :param Name: The name of the group. Defaults to "Unnamed"
    :type Name: str, optional
    :param description: The description of the purpose of the group.
    :type description: str, optional
    :return: The newly created IfcGroup
    :rtype: ifcopenshell.entity_instance

    Example:

    .. code:: python

        ifcopenshell.api.group.add_group(model, name="Unit 1A")
    """
    settings = {
        "name": name or "Unnamed",
        "description": description,
    }

    return file.create_entity(
        "IfcGroup",
        **{
            "GlobalId": ifcopenshell.guid.new(),
            "OwnerHistory": ifcopenshell.api.owner.create_owner_history(file),
            "Name": settings["name"],
            "Description": settings["description"],
        }
    )
