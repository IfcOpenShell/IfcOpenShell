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
import ifcopenshell.api.structural
import ifcopenshell.util.element
import ifcopenshell.util.structural


def remove_structural_load_case(file: ifcopenshell.file, load_case: ifcopenshell.entity_instance) -> None:
    """Removes a structural load case

    The structural activities and load groups in the load case are removed
    with it, except those that another load group or load case also groups:
    they are only taken out of this one. Its property sets are removed too.

    The load case is taken out of its load combinations as
    :func:`ifcopenshell.api.structural.unassign_structural_load_combination`
    does, so that a load group giving it its factor in one, left grouping
    nothing, goes too.

    :param load_case: The IfcStructuralLoadCase to remove.
    :return: None
    """
    for combination in ifcopenshell.util.structural.get_load_case_combinations(load_case):
        ifcopenshell.api.structural.unassign_structural_load_combination(
            file, load_case=load_case, load_combination=combination
        )
    load_groups = [
        o
        for rel in load_case.IsGroupedBy
        for o in rel.RelatedObjects
        if o.is_a("IfcStructuralLoadGroup") and _is_only_in(o, {load_case})
    ]
    # An activity in the load case and in a load group in it, too, goes with them.
    removed = {load_case, *load_groups}
    activities = {
        o
        for group in removed
        for rel in group.IsGroupedBy
        for o in rel.RelatedObjects
        if o.is_a("IfcStructuralActivity")
    }
    for activity in activities:
        if _is_only_in(activity, removed):
            ifcopenshell.api.structural.remove_structural_activity(file, activity=activity)
    for load_group in load_groups:
        ifcopenshell.api.structural.remove_structural_load_group(file, load_group=load_group)
    for rel in list(load_case.IsDefinedBy):
        if rel.is_a("IfcRelDefinesByProperties"):
            ifcopenshell.api.pset.remove_pset(file, product=load_case, pset=rel.RelatingPropertyDefinition)
    # TODO: do a deep purge
    for rel in load_case.IsGroupedBy or []:
        history = rel.OwnerHistory
        file.remove(rel)
        if history:
            ifcopenshell.util.element.remove_deep2(file, history)
    for rel in load_case.HasAssignments:
        if rel.is_a("IfcRelAssignsToGroup") and len(rel.RelatedObjects) == 1:
            history = rel.OwnerHistory
            file.remove(rel)
            if history:
                ifcopenshell.util.element.remove_deep2(file, history)
    history = load_case.OwnerHistory
    file.remove(load_case)
    if history:
        ifcopenshell.util.element.remove_deep2(file, history)


def _is_only_in(product: ifcopenshell.entity_instance, groups: set[ifcopenshell.entity_instance]) -> bool:
    """Whether every group the product is grouped into is one of these"""
    return all(rel.RelatingGroup in groups for rel in product.HasAssignments or () if rel.is_a("IfcRelAssignsToGroup"))
