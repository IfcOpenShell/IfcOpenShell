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


def remove_structural_load_case(file: ifcopenshell.file, load_case: ifcopenshell.entity_instance) -> None:
    """Removes a structural load case

    :param load_case: The IfcStructuralLoadCase to remove.
    :type load_case: ifcopenshell.entity_instance
    :return: None
    :rtype: None
    """
    settings = {"load_case": load_case}

    # TODO: do a deep purge
    for rel in settings["load_case"].IsGroupedBy or []:
        history = rel.OwnerHistory
        file.remove(rel)
        if history:
            ifcopenshell.util.element.remove_deep2(file, history)
    history = settings["load_case"].OwnerHistory
    file.remove(settings["load_case"])
    ifcopenshell.util.element.remove_deep2(file, history)
