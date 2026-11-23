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

from typing import Optional

import ifcopenshell
import ifcopenshell.api.group
import ifcopenshell.api.owner
import ifcopenshell.api.root
import ifcopenshell.api.structural
import ifcopenshell.guid
import ifcopenshell.util.structural


def assign_structural_load_combination(
    file: ifcopenshell.file,
    load_case: ifcopenshell.entity_instance,
    load_combination: ifcopenshell.entity_instance,
    factor: float = 1.0,
) -> ifcopenshell.entity_instance:
    """Assigns a load case to a load combination with a factor

    The load case is grouped into the combination by an
    IfcRelAssignsToGroupByFactor, which is shared by every load case of the
    combination that has the same factor. A load case already in the
    combination has its factor changed. A load case may be in any number of
    combinations, with a factor in each.

    A load case already in the combination through a load group that gives
    it its factor, as RFEM writes them (see
    :func:`ifcopenshell.util.structural.get_combination_factors`), is taken
    out of that group and grouped into the combination by factor instead.

    IFC2X3 has no IfcRelAssignsToGroupByFactor. There the load case is
    grouped into a load group of type LOAD_COMBINATION_GROUP whose
    Coefficient is the factor, in the combination, shared by every load
    case of the combination that has the same factor.

    A load case is an IfcStructuralLoadCase, or an IfcStructuralLoadGroup
    of type LOAD_CASE, as some programs, such as RFEM, write them.

    :param load_case: The load case to assign.
    :param load_combination: The IfcStructuralLoadGroup of type
        LOAD_COMBINATION.
    :param factor: The factor the load case is multiplied by in this
        combination.
    :return: The relationship that groups the load case: an
        IfcRelAssignsToGroupByFactor, or in IFC2X3 the IfcRelAssignsToGroup
        of its LOAD_COMBINATION_GROUP
    """
    if not load_case.is_a("IfcStructuralLoadCase") and not (
        load_case.is_a("IfcStructuralLoadGroup") and load_case.PredefinedType == "LOAD_CASE"
    ):
        raise ValueError(f"Only load cases can be combined, not {load_case}")
    if load_combination.PredefinedType != "LOAD_COMBINATION":
        raise ValueError(f"{load_combination} is not a load combination")

    if file.schema == "IFC2X3":
        return _assign_by_group(file, load_case, load_combination, factor)

    if (rel := _the_only_place(load_case, load_combination)) and (
        rel.RelatingGroup == load_combination and rel.is_a("IfcRelAssignsToGroupByFactor") and rel.Factor == factor
    ):
        return rel

    ifcopenshell.api.structural.unassign_structural_load_combination(
        file, load_case=load_case, load_combination=load_combination
    )

    for rel in load_combination.IsGroupedBy:
        if rel.is_a("IfcRelAssignsToGroupByFactor") and rel.Factor == factor:
            rel.RelatedObjects = rel.RelatedObjects + (load_case,)
            ifcopenshell.api.owner.update_owner_history(file, element=rel)
            return rel

    return file.create_entity(
        "IfcRelAssignsToGroupByFactor",
        GlobalId=ifcopenshell.guid.new(),
        OwnerHistory=ifcopenshell.api.owner.create_owner_history(file),
        RelatedObjects=[load_case],
        RelatingGroup=load_combination,
        Factor=factor,
    )


def _the_only_place(
    load_case: ifcopenshell.entity_instance, load_combination: ifcopenshell.entity_instance
) -> Optional[ifcopenshell.entity_instance]:
    """The relationship that groups a load case into a combination, if just one does"""
    groups = [load_combination] + ifcopenshell.util.structural.get_combination_factor_groups(load_combination)
    places = [rel for group in groups for rel in group.IsGroupedBy if load_case in rel.RelatedObjects]
    return places[0] if len(places) == 1 else None


def _is_own_factor_group(
    group: ifcopenshell.entity_instance, load_combination: ifcopenshell.entity_instance, factor: float
) -> bool:
    """Whether a group gives the factor to load cases of this combination only, and directly"""
    return (
        group.is_a("IfcStructuralLoadGroup")
        and group.PredefinedType == "LOAD_COMBINATION_GROUP"
        and group.Coefficient == factor
        and all(
            rel.RelatingGroup == load_combination
            for rel in group.HasAssignments or ()
            if rel.is_a("IfcRelAssignsToGroup")
        )
        and all(
            o.is_a("IfcStructuralLoadGroup") and o.PredefinedType == "LOAD_CASE"
            for rel in group.IsGroupedBy
            for o in rel.RelatedObjects
        )
    )


def _assign_by_group(
    file: ifcopenshell.file,
    load_case: ifcopenshell.entity_instance,
    load_combination: ifcopenshell.entity_instance,
    factor: float,
) -> ifcopenshell.entity_instance:
    if (rel := _the_only_place(load_case, load_combination)) and _is_own_factor_group(
        rel.RelatingGroup, load_combination, factor
    ):
        if rel.RelatingGroup in [o for r in load_combination.IsGroupedBy for o in r.RelatedObjects]:
            return rel

    ifcopenshell.api.structural.unassign_structural_load_combination(
        file, load_case=load_case, load_combination=load_combination
    )

    for group in [o for rel in load_combination.IsGroupedBy for o in rel.RelatedObjects]:
        if _is_own_factor_group(group, load_combination, factor):
            return ifcopenshell.api.group.assign_group(file, products=[load_case], group=group)

    group = ifcopenshell.api.root.create_entity(
        file,
        ifc_class="IfcStructuralLoadGroup",
        predefined_type="LOAD_COMBINATION_GROUP",
        name=f"{load_combination.Name or 'Combination'} x {factor:g}",
    )
    group.ActionType = "NOTDEFINED"
    group.ActionSource = "NOTDEFINED"
    group.Coefficient = factor
    # In IFC2X3 a group has a single IfcRelAssignsToGroup, which assign_group adds to.
    ifcopenshell.api.group.assign_group(file, products=[group], group=load_combination)
    return ifcopenshell.api.group.assign_group(file, products=[load_case], group=group)
