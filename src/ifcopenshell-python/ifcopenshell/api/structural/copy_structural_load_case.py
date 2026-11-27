# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Ryan Schultz <ryan@openingdesign.com>
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
import ifcopenshell.api.root
import ifcopenshell.api.structural
import ifcopenshell.util.element


def copy_structural_load_case(
    file: ifcopenshell.file, load_case: ifcopenshell.entity_instance, name: Optional[str] = None
) -> ifcopenshell.entity_instance:
    """Copies a structural load case, with its load groups and activities

    The copy has the load case's attributes and its own copies of its
    property sets, and loads the same structural analysis models. Each load
    group in it is copied the same way, into the copy. Each structural
    activity in it is copied onto the same structural item, sharing its
    applied load, so that a load definition edited once changes in both.

    The copy joins no load combination the load case is part of, as that
    would count its loads twice.

    Activities with their own placement keep it relative to the same
    placement as the original's, and their own representation in the same
    representation context. Load groups and activities grouped by factor
    keep their factor.

    :param load_case: The IfcStructuralLoadCase to copy.
    :param name: The copy's name. Defaults to the load case's name followed
        by " (copy)", or " (copy 2)" and so on if a load group already has
        that name, as results are listed by load case name.
    :return: The new IfcStructuralLoadCase

    Example:

    .. code:: python

        about_a = ifcopenshell.api.structural.add_structural_load_case(model, name="About A")
        about_b = ifcopenshell.api.structural.copy_structural_load_case(model, load_case=about_a, name="About B")
    """
    copy = copy_load_group(file, load_case)
    copy.Name = name if name is not None else get_copy_name(file, load_case.Name or "Unnamed")
    return copy


def get_copy_name(file: ifcopenshell.file, name: str) -> str:
    names = {group.Name for group in file.by_type("IfcStructuralLoadGroup")}
    copy_name, i = f"{name} (copy)", 2
    while copy_name in names:
        copy_name, i = f"{name} (copy {i})", i + 1
    return copy_name


def copy_load_group(file: ifcopenshell.file, group: ifcopenshell.entity_instance) -> ifcopenshell.entity_instance:
    copy = ifcopenshell.util.element.copy(file, group)
    copy_psets(file, group, copy)
    for model in group.LoadGroupFor:
        ifcopenshell.api.structural.assign_structural_load_group(
            file, load_groups=[copy], structural_analysis_model=model
        )
    for rel in group.IsGroupedBy:
        members = []
        for member in rel.RelatedObjects:
            if member.is_a("IfcStructuralActivity"):
                members.append(copy_activity(file, member))
            elif member.is_a("IfcStructuralLoadGroup"):
                members.append(copy_load_group(file, member))
        if members:
            # A copy of the relationship keeps its class, such as IfcRelAssignsToGroupByFactor, and its factor.
            new_rel = ifcopenshell.util.element.copy(file, rel)
            new_rel.RelatedObjects = members
            new_rel.RelatingGroup = copy
    return copy


def copy_activity(file: ifcopenshell.file, activity: ifcopenshell.entity_instance) -> ifcopenshell.entity_instance:
    copy = ifcopenshell.util.element.copy(file, activity)
    # Relative to the same placements, and in the project's representation contexts.
    if copy.ObjectPlacement:
        copy.ObjectPlacement = ifcopenshell.util.element.copy_deep(
            file, copy.ObjectPlacement, exclude=["IfcObjectPlacement"]
        )
    if copy.Representation:
        copy.Representation = ifcopenshell.util.element.copy_deep(
            file, copy.Representation, exclude=["IfcRepresentationContext"]
        )
    for rel in activity.AssignedToStructuralItem:
        new_rel = ifcopenshell.api.root.create_entity(file, ifc_class="IfcRelConnectsStructuralActivity")
        new_rel.RelatingElement = rel.RelatingElement
        new_rel.RelatedStructuralActivity = copy
    copy_psets(file, activity, copy)
    return copy


def copy_psets(
    file: ifcopenshell.file, element: ifcopenshell.entity_instance, copy: ifcopenshell.entity_instance
) -> None:
    for rel in element.IsDefinedBy:
        if rel.is_a("IfcRelDefinesByProperties"):
            new_rel = ifcopenshell.util.element.copy(file, rel)
            new_rel.RelatedObjects = [copy]
            new_rel.RelatingPropertyDefinition = ifcopenshell.util.element.copy_deep(
                file, rel.RelatingPropertyDefinition
            )
