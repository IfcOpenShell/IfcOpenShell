# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Bruno Postle <bruno@postle.net>
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
import ifcopenshell.api.owner
import ifcopenshell.util.element


def unassign_structural_load_combination(
    file: ifcopenshell.file,
    load_case: ifcopenshell.entity_instance,
    load_combination: ifcopenshell.entity_instance,
) -> None:
    """Removes a load case from a load combination

    If the load case isn't in the combination, nothing will happen.

    :param load_case: The IfcStructuralLoadCase to remove from the combination.
    :param load_combination: The IfcStructuralLoadGroup of type
        LOAD_COMBINATION.
    :return: None
    """
    for rel in load_combination.IsGroupedBy:
        if load_case not in rel.RelatedObjects:
            continue
        if len(rel.RelatedObjects) == 1:
            history = rel.OwnerHistory
            file.remove(rel)
            if history:
                ifcopenshell.util.element.remove_deep2(file, history)
        else:
            rel.RelatedObjects = [o for o in rel.RelatedObjects if o != load_case]
            ifcopenshell.api.owner.update_owner_history(file, element=rel)
