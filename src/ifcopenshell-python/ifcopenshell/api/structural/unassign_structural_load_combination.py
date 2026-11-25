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
import ifcopenshell.api.structural
import ifcopenshell.util.element
import ifcopenshell.util.structural


def unassign_structural_load_combination(
    file: ifcopenshell.file,
    load_case: ifcopenshell.entity_instance,
    load_combination: ifcopenshell.entity_instance,
) -> None:
    """Removes a load case from a load combination

    The load case is taken out wherever it is in the combination: grouped
    into it directly, or through a load group that gives it its factor, as
    IFC2X3's LOAD_COMBINATION_GROUP does (see
    :func:`ifcopenshell.util.structural.get_combination_factors`). Such a
    group left grouping nothing is taken out of the combination too, and is
    removed if nothing else groups it.

    If the load case isn't in the combination, nothing will happen.

    :param load_case: The load case to remove from the combination: an
        IfcStructuralLoadCase, or an IfcStructuralLoadGroup of type LOAD_CASE.
    :param load_combination: The IfcStructuralLoadGroup of type
        LOAD_COMBINATION.
    :return: None
    """
    factor_groups = ifcopenshell.util.structural.get_combination_factor_groups(load_combination)
    for group in [load_combination] + factor_groups:
        for rel in list(group.IsGroupedBy):
            if load_case in rel.RelatedObjects:
                _remove_from_group(file, rel, load_case)
    within = {g.id() for g in [load_combination] + factor_groups}
    # Those furthest from the combination first, so that a group emptied by removing one in it goes too.
    for group in reversed(factor_groups):
        if any(rel.RelatedObjects for rel in group.IsGroupedBy):
            continue
        for rel in list(group.HasAssignments or ()):
            if rel.is_a("IfcRelAssignsToGroup") and rel.RelatingGroup.id() in within:
                _remove_from_group(file, rel, group)
        if not _is_used(file, group):
            ifcopenshell.api.structural.remove_structural_load_group(file, load_group=group)


def _remove_from_group(
    file: ifcopenshell.file, rel: ifcopenshell.entity_instance, related: ifcopenshell.entity_instance
) -> None:
    if len(rel.RelatedObjects) == 1:
        history = rel.OwnerHistory
        file.remove(rel)
        if history:
            ifcopenshell.util.element.remove_deep2(file, history)
    else:
        rel.RelatedObjects = [o for o in rel.RelatedObjects if o != related]
        ifcopenshell.api.owner.update_owner_history(file, element=rel)


def _is_used(file: ifcopenshell.file, group: ifcopenshell.entity_instance) -> bool:
    """Whether a load group is in another group, or loads an analysis model"""
    return any(rel.is_a("IfcRelAssignsToGroup") for rel in group.HasAssignments or ()) or any(
        i.is_a("IfcStructuralAnalysisModel") for i in file.get_inverse(group)
    )
