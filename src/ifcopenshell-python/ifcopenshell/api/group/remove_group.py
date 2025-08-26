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
import ifcopenshell.api.pset
import ifcopenshell.util.element


def remove_group(file: ifcopenshell.file, group: ifcopenshell.entity_instance) -> None:
    """Removes a group

    All products assigned to the group will remain, but the relationship to
    the group will be removed.

    :param group: The IfcGroup entity you want to remove
    :return: None

    Example:

    .. code:: python

        group = ifcopenshell.api.group.add_group(model, name="Unit 1A")
        ifcopenshell.api.group.remove_group(model, group=group)
    """
    for inverse_id in [i.id() for i in file.get_inverse(group)]:
        try:
            inverse = file.by_id(inverse_id)
        except:
            continue
        if inverse.is_a("IfcRelDefinesByProperties"):
            ifcopenshell.api.pset.remove_pset(
                file,
                product=group,
                pset=inverse.RelatingPropertyDefinition,
            )
        elif inverse.is_a("IfcRelAssignsToGroup"):
            if inverse.RelatingGroup == group:
                history = inverse.OwnerHistory
                file.remove(inverse)
                if history:
                    ifcopenshell.util.element.remove_deep2(file, history)
            elif len(inverse.RelatedObjects) == 1:
                history = inverse.OwnerHistory
                file.remove(inverse)
                if history:
                    ifcopenshell.util.element.remove_deep2(file, history)
    history = group.OwnerHistory
    file.remove(group)
    if history:
        ifcopenshell.util.element.remove_deep2(file, history)
