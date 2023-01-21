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


class Usecase:
    def __init__(self, file, related_object=None, relating_object=None):
        """Assigns an object as a nested child to a parent host

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

        As a product may only have a single locaion in the "spatial
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

        :param related_object: The child of the nesting relationship, typically
            an IfcElement.
        :type related_object: ifcopenshell.entity_instance.entity_instance
        :param relating_object: The host parent of the nesting relationship,
            typically an IfcElement.
        :type relating_object: ifcopenshell.entity_instance.entity_instance
        :return: The IfcRelNests relationship instance
        :rtype: ifcopenshell.entity_instance.entity_instance

        Example:

        .. code:: python

            # Faucets are designed to attach onto a sink through a predrilled hole.
            sink = ifcopenshell.api.run("root.create_entity", model,
                ifc_class="IfcSanitaryTerminal", predefined_type="SINK")
            faucet = ifcopenshell.api.run("root.create_entity", model,
                ifc_class="IfcValve", predefined_type="FAUCET")
            ifcopenshell.api.run("nest.assign_object", model, related_object=faucet, relating_object=sink)
        """
        self.file = file
        self.settings = {"related_object": related_object, "relating_object": relating_object}

    def execute(self):
        nests = None
        if self.settings["related_object"].Nests:
            nests = self.settings["related_object"].Nests[0]

        is_nested_by = None
        for rel in self.settings["relating_object"].IsNestedBy:
            if rel.is_a("IfcRelNests"):
                is_nested_by = rel
                break

        if nests and nests == is_nested_by:
            return

        if nests:
            related_objects = list(nests.RelatedObjects)
            related_objects.remove(self.settings["related_object"])
            if related_objects:
                nests.RelatedObjects = related_objects
                ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": nests})
            else:
                self.file.remove(nests)

        if is_nested_by:
            related_objects = list(is_nested_by.RelatedObjects)
            related_objects.append(self.settings["related_object"])
            is_nested_by.RelatedObjects = related_objects
            ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": is_nested_by})
        else:
            is_nested_by = self.file.create_entity(
                "IfcRelNests",
                **{
                    "GlobalId": ifcopenshell.guid.new(),
                    "OwnerHistory": ifcopenshell.api.run("owner.create_owner_history", self.file),
                    "RelatedObjects": [self.settings["related_object"]],
                    "RelatingObject": self.settings["relating_object"],
                }
            )
        return is_nested_by
