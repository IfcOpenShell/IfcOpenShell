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
"""Query structural analysis models

These functions follow the relationships of the structural analysis domain:
the items and load groups of an analysis model, how members and connections
are joined, the activities (loads and reactions) on an item or in a load
group, the factors of a load combination, and the building elements that a
structural member stands for.
"""

import ifcopenshell


def get_analysis_models(item: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
    """The analysis models a structural item or load group is part of

    :param item: An IfcStructuralItem, which is grouped into a model, or an
        IfcStructuralLoadGroup, which a model is loaded by.
    :return: The IfcStructuralAnalysisModels
    """
    if item.is_a("IfcStructuralLoadGroup"):
        return list(item.LoadGroupFor)
    return [
        rel.RelatingGroup
        for rel in item.HasAssignments
        if rel.is_a("IfcRelAssignsToGroup") and rel.RelatingGroup.is_a("IfcStructuralAnalysisModel")
    ]


def get_model_items(model: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
    """The structural members and connections of an analysis model

    :param model: The IfcStructuralAnalysisModel
    :return: Its IfcStructuralItems
    """
    items = {}
    for rel in model.IsGroupedBy:
        items.update(dict.fromkeys(o for o in rel.RelatedObjects if o.is_a("IfcStructuralItem")))
    return list(items)


def get_model_load_groups(model: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
    """The load groups an analysis model is loaded by

    These are the top-level ones, in LoadedBy: its load combinations if it
    has any, otherwise its load cases.

    :param model: The IfcStructuralAnalysisModel
    :return: Its IfcStructuralLoadGroups
    """
    return list(model.LoadedBy or ())


def get_model_load_cases(model: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
    """The load cases of an analysis model

    These are the load cases it is loaded by, and those of the load
    combinations it is loaded by.

    :param model: The IfcStructuralAnalysisModel
    :return: Its load cases, IfcStructuralLoadGroups of type LOAD_CASE
    """
    cases = {}
    for group in get_model_load_groups(model):
        if group.PredefinedType == "LOAD_COMBINATION":
            candidates = list(get_combination_factors(group))
        else:
            candidates = [group]
        cases.update(dict.fromkeys(c for c in candidates if c.PredefinedType == "LOAD_CASE"))
    return list(cases)


def get_combination_factors(
    combination: ifcopenshell.entity_instance,
) -> dict[ifcopenshell.entity_instance, float]:
    """The load cases of a load combination with the factor of each

    A load case's factor is the Factor of the IfcRelAssignsToGroupByFactor
    that groups it into the combination, or 1 if it is grouped by a plain
    IfcRelAssignsToGroup, times the combination's Coefficient if it has
    one. A load case grouped into the combination twice has the sum of its
    factors.

    :param combination: An IfcStructuralLoadGroup of type LOAD_COMBINATION
    :return: The factor of each load case in the combination
    """
    coefficient = 1.0 if combination.Coefficient is None else combination.Coefficient
    factors = {}
    for rel in combination.IsGroupedBy:
        factor = rel.Factor if rel.is_a("IfcRelAssignsToGroupByFactor") else 1.0
        for group in rel.RelatedObjects:
            if group.is_a("IfcStructuralLoadGroup"):
                factors[group] = factors.get(group, 0.0) + factor * coefficient
    return factors


def get_group_activities(load_group: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
    """The activities of a load group, with those of the load groups in it

    A load case may group its actions directly or through load groups of
    type LOAD_GROUP; both are included. A load combination has no
    activities of its own.

    :param load_group: An IfcStructuralLoadGroup
    :return: Its IfcStructuralActivitys
    """
    activities = {}
    for rel in load_group.IsGroupedBy:
        if rel.is_a("IfcRelAssignsToGroupByFactor"):
            continue
        for related in rel.RelatedObjects:
            if related.is_a("IfcStructuralActivity"):
                candidates = [related]
            elif related.is_a("IfcStructuralLoadGroup") and related.PredefinedType == "LOAD_GROUP":
                candidates = get_group_activities(related)
            else:
                continue
            activities.update(dict.fromkeys(candidates))
    return list(activities)


def get_item_activities(item: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
    """The activities, loads and reactions, on a structural item

    :param item: An IfcStructuralItem
    :return: Its IfcStructuralActivitys
    """
    return [rel.RelatedStructuralActivity for rel in item.AssignedStructuralActivity]


def get_member_connections(member: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
    """The structural connections a member is joined to

    :param member: An IfcStructuralMember
    :return: Its IfcStructuralConnections
    """
    return [rel.RelatedStructuralConnection for rel in member.ConnectedBy]


def get_connection_members(connection: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
    """The structural members joined to a connection

    :param connection: An IfcStructuralConnection
    :return: Its IfcStructuralMembers
    """
    return [rel.RelatingStructuralMember for rel in connection.ConnectsStructuralMembers]


def get_structural_members(element: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
    """The structural members that stand for a building element

    They are linked by an IfcRelAssignsToProduct, which IFC allows either
    way round (:func:`ifcopenshell.api.structural.assign_product` makes
    the member the RelatingProduct), or in IFC2X3 by an
    IfcRelConnectsStructuralElement.

    :param element: An IfcElement
    :return: Its IfcStructuralMembers
    """
    return _linked(element, "IfcStructuralMember")


def get_building_elements(member: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
    """The building elements a structural member stands for

    See :func:`get_structural_members` for how they are linked.

    :param member: An IfcStructuralMember
    :return: Its IfcElements
    """
    return _linked(member, "IfcElement")


def _linked(product: ifcopenshell.entity_instance, ifc_class: str) -> list[ifcopenshell.entity_instance]:
    candidates = []
    for rel in product.HasAssignments:
        if rel.is_a("IfcRelAssignsToProduct"):
            candidates.append(rel.RelatingProduct)
    for rel in getattr(product, "ReferencedBy", ()):
        if rel.is_a("IfcRelAssignsToProduct"):
            candidates.extend(rel.RelatedObjects)
    for rel in getattr(product, "HasStructuralMember", ()):
        candidates.append(rel.RelatedStructuralMember)
    for rel in getattr(product, "ReferencesElement", ()):
        candidates.append(rel.RelatingElement)
    return list(dict.fromkeys(c for c in candidates if c.is_a(ifc_class)))
