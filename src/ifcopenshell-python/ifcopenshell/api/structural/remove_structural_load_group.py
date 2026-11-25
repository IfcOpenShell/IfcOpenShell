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
import ifcopenshell.api.structural
import ifcopenshell.util.element
import ifcopenshell.util.structural


def remove_structural_load_group(file: ifcopenshell.file, load_group: ifcopenshell.entity_instance) -> None:
    """Removes a structural load group

    The structural activities in the load group are removed with it, except
    those that another load group or load case also groups: they are only
    taken out of this one.

    The load groups of a load combination that give its load cases their
    factors, as IFC2X3's LOAD_COMBINATION_GROUP does (see
    :func:`ifcopenshell.util.structural.get_combination_factors`), are
    removed with it, unless something else groups them.

    :param load_group: The IfcStructuralLoadGroup to remove.
    :return: None
    """
    factor_groups = []
    if load_group.PredefinedType == "LOAD_COMBINATION":
        factor_groups = ifcopenshell.util.structural.get_combination_factor_groups(load_group)
    activities = {o for rel in load_group.IsGroupedBy for o in rel.RelatedObjects if o.is_a("IfcStructuralActivity")}
    for activity in activities:
        if any(
            rel.is_a("IfcRelAssignsToGroup") and rel.RelatingGroup != load_group
            for rel in activity.HasAssignments or ()
        ):
            continue
        ifcopenshell.api.structural.remove_structural_activity(file, activity=activity)
    # TODO: do a deep purge
    for inverse in file.get_inverse(load_group):
        if inverse.is_a("IfcRelAssignsToGroup") and (
            inverse.RelatingGroup == load_group or len(inverse.RelatedObjects) == 1
        ):
            history = inverse.OwnerHistory
            file.remove(inverse)
            if history:
                ifcopenshell.util.element.remove_deep2(file, history)
    history = load_group.OwnerHistory
    file.remove(load_group)
    if history:
        ifcopenshell.util.element.remove_deep2(file, history)
    # Nearest the combination first: removing one leaves those in it in nothing.
    for group in factor_groups:
        if any(rel.is_a("IfcRelAssignsToGroup") for rel in group.HasAssignments or ()):
            continue
        if any(i.is_a("IfcStructuralAnalysisModel") for i in file.get_inverse(group)):
            continue
        remove_structural_load_group(file, load_group=group)
