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
import ifcopenshell.api.owner
import ifcopenshell.guid
import ifcopenshell.util.element
from typing import Union


def assign_object(
    file: ifcopenshell.file,
    related_objects: list[ifcopenshell.entity_instance],
    relating_object: ifcopenshell.entity_instance,
) -> Union[ifcopenshell.entity_instance, None]:
    """Assigns objects as nested children to a parent host

    All physical IFC model elements must be part of a hierarchical tree
    called the "spatial decomposition", where large things are made up of
    smaller things. This tree always begins at an "IfcProject" and is then
    broken down using "decomposition" relationships, of which aggregation is
    the first relationship you will use.

    Another type of "decomposition" relationship is known as "nesting".
    Nesting is used when an child object is physically attached to a parent
    host object, through a physical predetermined connection point. The
    child object must be specifically designed to attach to a other objects
    at specific positions with a particular form factor. Examples include
    faucets which must always be attached through a predrilled hole in a
    basin. Alternatively, it could be a modular attachment with a
    correlating male and female joint that must join at a particular point.
    Because there is a strict connection point, when the parent moves, all
    nested children must move with the parent. Another example might be a
    predrilled hole in a door panel where hardware must fit through.

    Nesting relationships are not very commonly used in most design and
    construction models. Its main usecase is in modular construction, kit of
    parts, or fabrication models.

    As a product may only have a single location in the "spatial
    decomposition" tree, assigning an nesting relationship will remove any
    previous aggregation, containment, or nesting relationships it may have.

    IFC placements follow a convention where the placement is relative to
    its parent in the spatial hierarchy. If your product has a placement,
    its placement will be recalculated to follow this convention.

    For physical connections which are part of a distribution system, such
    as a plug connecting into a GPO, or a duct connecting to an AHU, or two
    pipe segments connecting with a bend, tee, or wye fitting, you should
    not nest the two objects directly. Instead, you should nest a connection
    port, which determines the type of compatible distribution flow that can
    be connected to it. To do this, do not use this function, but instead
    use the more specific functions in the ifcopenshell.api.system module.

    Note that nesting relationships may also be used by non-physical
    elements, such as cost items or tasks. In this context, nesting means
    that there is an implied order to the child cost items or tasks (i.e.
    task 1 should be shown before task 2). It is not necessary to use this
    function for nesting non-physical elements. Instead, it is recommended
    to instead just use the relevant API functions, like
    ifcopenshell.api.cost.add_cost_item or
    ifcopenshell.api.sequence.add_task.

    :param related_objects: The list of children of the nesting relationship,
        typically IfcElements.
    :type related_objects: list[ifcopenshell.entity_instance]
    :param relating_object: The host parent of the nesting relationship,
        typically an IfcElement.
    :type relating_object: ifcopenshell.entity_instance
    :return: The IfcRelNests relationship instance
        or `None` if `related_objects` was empty list.
    :rtype: Union[ifcopenshell.entity_instance, None]

    Example:

    .. code:: python

        # Faucets are designed to attach onto a sink through a predrilled hole.
        sink = ifcopenshell.api.root.create_entity(model,
            ifc_class="IfcSanitaryTerminal", predefined_type="SINK")
        faucet = ifcopenshell.api.root.create_entity(model,
            ifc_class="IfcValve", predefined_type="FAUCET")
        ifcopenshell.api.nest.assign_object(model, related_objects=[faucet], relating_object=sink)
    """
    settings = {"related_objects": related_objects, "relating_object": relating_object}

    if not settings["related_objects"]:
        return

    ifc2x3 = file.schema == "IFC2X3"
    related_objects_set = set(related_objects)

    if ifc2x3:
        is_nested_by = next((i for i in relating_object.IsDecomposedBy if i.is_a("IfcRelNests")), None)
    else:
        is_nested_by = next((i for i in relating_object.IsNestedBy), None)

    # NOTE: maintain .RelatedObjects order as it has meaning in IFC
    previous_nests_rels: set[ifcopenshell.entity_instance] = set()
    objects_without_nests: list[ifcopenshell.entity_instance] = []
    objects_with_nests: list[ifcopenshell.entity_instance] = []

    # check if there is anything to change
    for object in related_objects_set:
        if ifc2x3:
            object_rel = next((i for i in object.Decomposes if i.is_a("IfcRelNests")), None)
        else:
            object_rel = next(iter(object.Nests), None)

        if object_rel is None:
            objects_without_nests.append(object)
            continue

        # either is_nested_by is None or product is part of different rel
        if object_rel != is_nested_by:
            previous_nests_rels.add(object_rel)
            objects_with_nests.append(object)

        # products with already assigned nestings will be skipped

    objects_to_change = objects_without_nests + objects_with_nests
    # nothing to change
    if not objects_to_change:
        return is_nested_by

    # NOTE: An object can both be nested and assigned to a container or an aggregate.

    # unassign elements from previous nests
    for nests in previous_nests_rels:
        cur_related_objects = [o for o in nests.RelatedObjects if o not in related_objects_set]
        if cur_related_objects:
            nests.RelatedObjects = list(cur_related_objects)
            ifcopenshell.api.owner.update_owner_history(file, **{"element": nests})
        else:
            history = nests.OwnerHistory
            file.remove(nests)
            if history:
                ifcopenshell.util.element.remove_deep2(file, history)

    # assign elements to a new nesting
    if is_nested_by:
        cur_related_objects = list(is_nested_by.RelatedObjects)
        cur_related_objects_set = set(cur_related_objects)
        is_nested_by.RelatedObjects = cur_related_objects + [
            o for o in related_objects if o not in cur_related_objects_set
        ]
        ifcopenshell.api.owner.update_owner_history(file, **{"element": is_nested_by})
    else:
        is_nested_by = file.create_entity(
            "IfcRelNests",
            **{
                "GlobalId": ifcopenshell.guid.new(),
                "OwnerHistory": ifcopenshell.api.owner.create_owner_history(file),
                "RelatedObjects": related_objects,
                "RelatingObject": relating_object,
            }
        )

    # NOTE: Creating a nesting relationship doesn't localize the object's placement,
    # unlike assigning it to an aggregate or a container.

    return is_nested_by
