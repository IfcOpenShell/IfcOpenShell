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


def remove_system(file: ifcopenshell.file, system: ifcopenshell.entity_instance) -> None:
    """Removes a distribution system

    All the distribution elements within the system are retained.

    :param system: The IfcSystem to remove.
    :type system: ifcopenshell.entity_instance
    :return: None
    :rtype: None

    Example:

    .. code:: python

        # A completely empty distribution system
        system = ifcopenshell.api.system.add_system(model)

        # Delete it.
        ifcopenshell.api.system.remove_system(model, system=system)
    """
    settings = {"system": system}

    for inverse_id in [i.id() for i in file.get_inverse(settings["system"])]:
        try:
            inverse = file.by_id(inverse_id)
        except:
            continue
        if inverse.is_a("IfcRelDefinesByProperties"):
            ifcopenshell.api.pset.remove_pset(
                file,
                product=settings["system"],
                pset=inverse.RelatingPropertyDefinition,
            )
        elif inverse.is_a("IfcRelAssignsToGroup"):
            if inverse.RelatingGroup == settings["system"]:
                history = inverse.OwnerHistory
                file.remove(inverse)
                if history:
                    ifcopenshell.util.element.remove_deep2(file, history)
            elif len(inverse.RelatedObjects) == 1:
                history = inverse.OwnerHistory
                file.remove(inverse)
                if history:
                    ifcopenshell.util.element.remove_deep2(file, history)
    history = settings["system"].OwnerHistory
    file.remove(settings["system"])
    if history:
        ifcopenshell.util.element.remove_deep2(file, history)
