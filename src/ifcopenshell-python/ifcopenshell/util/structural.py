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
group, the factors of a load combination, the axes that loads in global
coordinates are given in, the true length or area of loads given per
projected length or area, and the building elements that a structural member
stands for.
"""

from typing import Union

import numpy as np

import ifcopenshell
import ifcopenshell.util.placement


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


#: Load group types that, inside a load combination, stand for the load
#: cases they group, their Coefficient the factor: IFC2X3's
#: LOAD_COMBINATION_GROUP, and LOAD_GROUP, which RFEM writes in IFC4 for
#: the same thing.
FACTOR_GROUP_TYPES = ("LOAD_COMBINATION_GROUP", "LOAD_GROUP")


def is_factor_group(group: ifcopenshell.entity_instance) -> bool:
    """Whether a load group in a load combination gives a factor to what it groups

    :param group: An IfcStructuralLoadGroup grouped into a load combination
    :return: True if it is a LOAD_COMBINATION_GROUP or a LOAD_GROUP
    """
    return (
        group.is_a("IfcStructuralLoadGroup")
        and not group.is_a("IfcStructuralLoadCase")
        and group.PredefinedType in FACTOR_GROUP_TYPES
    )


def get_combination_factor_groups(combination: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
    """The factor groups between a load combination and its load cases

    See :func:`get_combination_factors`.

    :param combination: An IfcStructuralLoadGroup of type LOAD_COMBINATION
    :return: Its LOAD_COMBINATION_GROUP and LOAD_GROUP load groups, each
        after every one of them that groups it
    """
    within: dict[ifcopenshell.entity_instance, list[ifcopenshell.entity_instance]] = {}
    pending = [combination]
    while pending:
        group = pending.pop(0)
        for rel in group.IsGroupedBy:
            for related in rel.RelatedObjects:
                if is_factor_group(related):
                    if related not in within:
                        within[related] = []
                        pending.append(related)
                    if group != combination:
                        within[related].append(group)
    groups = []
    while within:
        ready = [g for g, parents in within.items() if not any(p in within for p in parents)]
        # Groups that group each other, in a faulty file, in any order.
        for group in ready or list(within):
            groups.append(group)
            del within[group]
    return groups


def get_combination_factors(
    combination: ifcopenshell.entity_instance, include_coefficient: bool = True
) -> dict[ifcopenshell.entity_instance, float]:
    """The load cases of a load combination with the factor of each

    A load case's factor is the Factor of the IfcRelAssignsToGroupByFactor
    that groups it into the combination, or 1 if it is grouped by a plain
    IfcRelAssignsToGroup, times the combination's Coefficient if it has
    one. A load case grouped into the combination twice has the sum of its
    factors.

    A load case may also be given its factor by a load group between it
    and the combination, whose Coefficient is the factor: IFC2X3, which has
    no IfcRelAssignsToGroupByFactor, has load groups of type
    LOAD_COMBINATION_GROUP for this, and RFEM writes load groups of type
    LOAD_GROUP for it in IFC4. Such a group stands for what it groups, its
    Coefficient multiplying their factors.

    :param combination: An IfcStructuralLoadGroup of type LOAD_COMBINATION
    :param include_coefficient: False to leave out the combination's own
        Coefficient, as when it is shown apart from the factors. Those of
        the groups in it still count.
    :return: The factor of each load case in the combination
    """
    factors = {}
    # A group reached by two ways counts for each, but one that groups itself, in a faulty file, only once.
    pending = [(combination, 1.0, frozenset([combination]))]
    while pending:
        group, scale, path = pending.pop()
        if group.Coefficient is not None and (include_coefficient or group != combination):
            scale *= group.Coefficient
        for rel in group.IsGroupedBy:
            factor = scale * (rel.Factor if rel.is_a("IfcRelAssignsToGroupByFactor") else 1.0)
            for related in rel.RelatedObjects:
                if not related.is_a("IfcStructuralLoadGroup"):
                    continue
                if is_factor_group(related):
                    if related not in path:
                        pending.append((related, factor, path | {related}))
                else:
                    factors[related] = factors.get(related, 0.0) + factor
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


def get_activity_item(activity: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
    """The structural item an activity acts on, or is a reaction of

    :param activity: An IfcStructuralActivity
    :return: Its IfcStructuralItem, or None if it is assigned to none
    """
    for rel in activity.AssignedToStructuralItem:
        return rel.RelatingElement
    return None


def get_activity_load_cases(activity: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
    """The load cases an activity is in

    An activity is grouped into a load case directly or through load groups
    of type LOAD_GROUP, as :func:`get_group_activities` finds it.

    :param activity: An IfcStructuralActivity
    :return: Its load cases, IfcStructuralLoadGroups of type LOAD_CASE
    """
    cases = {}
    groups, seen = _load_groups_of(activity), set()
    while groups:
        group = groups.pop(0)
        if group in seen:
            continue
        seen.add(group)
        if group.PredefinedType == "LOAD_CASE":
            cases[group] = None
        elif group.PredefinedType == "LOAD_GROUP":
            groups.extend(_load_groups_of(group))
    return list(cases)


def get_global_axes(activity: ifcopenshell.entity_instance) -> np.ndarray:
    """The axes that an activity's loads in global coordinates are given in

    IFC calls the coordinate system of an analysis model "global": loads
    whose GlobalOrLocal is GLOBAL_COORDS are given in the axes of the
    model's SharedPlacement, which need not be the project's. This is the
    SharedPlacement of the analysis model of the activity's item, or of
    its load cases, else the activity's own ObjectPlacement, else the
    project's axes.

    :param activity: An IfcStructuralActivity
    :return: A 3x3 rotation matrix whose columns are the X, Y and Z axes,
        in the project's coordinates
    """
    item = get_activity_item(activity)
    models = get_analysis_models(item) if item else []
    models += [m for case in get_activity_load_cases(activity) for m in get_analysis_models(case)]
    placements = [m.SharedPlacement for m in models if m.SharedPlacement]
    placements.append(activity.ObjectPlacement)
    for placement in placements:
        if placement:
            return np.array(ifcopenshell.util.placement.get_placement(placement))[:3, :3]
    return np.eye(3)


def is_projected(activity: ifcopenshell.entity_instance) -> bool:
    """Whether an activity's load is given per projected length or area

    That is a ``ProjectedOrTrue`` of PROJECTED_LENGTH, which IFC allows only
    in global coordinates: a load in local coordinates is per true length or
    area, whatever it says.

    :param activity: An IfcStructuralActivity
    :return: True if per projected length or area
    """
    return getattr(activity, "ProjectedOrTrue", None) == "PROJECTED_LENGTH" and activity.GlobalOrLocal != "LOCAL_COORDS"


def get_true_length_factor(
    activity: ifcopenshell.entity_instance,
    force: Union[np.ndarray, list[float]],
    member_axis: Union[np.ndarray, list[float]],
) -> float:
    """What a distributed force of an activity is multiplied by to be per true length or area of its member

    A load per projected length or area (``ProjectedOrTrue`` of
    PROJECTED_LENGTH), as snow on a rafter or a pitched roof is given per
    horizontal length or plan area, is per length or area of the member as
    seen along the force. IFC allows one only in global coordinates. On a
    curve member at an angle to the force that is the sine of the angle per
    true length; on a surface member, the cosine of the angle between the
    force and the surface's normal per true area. Any other load is per
    true length or area already, and its factor is 1.

    :param activity: An IfcStructuralCurveAction or IfcStructuralSurfaceAction,
        or in IFC2X3 an IfcStructuralLinearAction or IfcStructuralPlanarAction
    :param force: The force of its applied load, in the axes it is given in
        (see get_global_axes)
    :param member_axis: For a curve member, its direction along its length;
        for a surface member, its normal. In the project's coordinates.
    :return: The factor, from 0 to 1
    """
    if not is_projected(activity):
        return 1.0
    force = get_global_axes(activity) @ np.asarray(force, dtype=float)
    axis = np.asarray(member_axis, dtype=float)
    size, axis_size = float(np.linalg.norm(force)), float(np.linalg.norm(axis))
    if size < 1e-12 or axis_size < 1e-12:
        return 1.0
    cosine = float(np.dot(force / size, axis / axis_size))
    if activity.is_a("IfcStructuralPlanarAction") or activity.is_a("IfcStructuralSurfaceAction"):
        return min(abs(cosine), 1.0)
    return float(np.sqrt(max(0.0, 1.0 - cosine * cosine)))


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


def get_boundary_condition_class(connection: ifcopenshell.entity_instance) -> str:
    """The class of boundary condition a structural connection takes

    :param connection: An IfcStructuralConnection
    :return: IfcBoundaryNodeCondition for a point connection,
        IfcBoundaryEdgeCondition for a curve connection and
        IfcBoundaryFaceCondition for a surface connection
    :raises ValueError: if the connection is none of these
    """
    if connection.is_a("IfcStructuralPointConnection"):
        return "IfcBoundaryNodeCondition"
    elif connection.is_a("IfcStructuralCurveConnection"):
        return "IfcBoundaryEdgeCondition"
    elif connection.is_a("IfcStructuralSurfaceConnection"):
        return "IfcBoundaryFaceCondition"
    raise ValueError(f"{connection} is not a point, curve or surface connection")


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


def _load_groups_of(product: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
    return [
        rel.RelatingGroup
        for rel in product.HasAssignments
        if rel.is_a("IfcRelAssignsToGroup") and rel.RelatingGroup.is_a("IfcStructuralLoadGroup")
    ]
