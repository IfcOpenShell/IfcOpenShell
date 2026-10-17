# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Ryan Schultz
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

# This file was generated with the assistance of an AI coding tool.

import ifcopenshell
import ifcopenshell.api.root
import ifcopenshell.util.element


def remove_structural_activity(file: ifcopenshell.file, activity: ifcopenshell.entity_instance) -> None:
    """Removes a structural activity

    The activity is disconnected from its structural item and removed from
    its load groups. The applied load is kept, as other activities may share
    it.

    :param activity: The IfcStructuralActivity to remove.
    :return: None

    Example:

    .. code:: python

        ifcopenshell.api.structural.remove_structural_activity(model, activity=activity)
    """
    for rel in activity.AssignedToStructuralItem:
        history = rel.OwnerHistory
        file.remove(rel)
        if history:
            ifcopenshell.util.element.remove_deep2(file, history)
    ifcopenshell.api.root.remove_product(file, product=activity)
