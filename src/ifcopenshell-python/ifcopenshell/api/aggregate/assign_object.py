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
import ifcopenshell.util.placement


class Usecase:
    def __init__(self, file, product=None, relating_object=None):
        """Assigns an object as an aggregate to a product

        All physical IFC model elements must be part of a hierarchical tree
        called the "spatial decomposition", where large things are made up of
        smaller things. This tree always begins at an "IfcProject" and is then
        broken down using "decomposition" relationships, of which aggregation is
        the first relationship you will use.

        Typically used when you want to describe how large spaces are made up of
        smaller spaces. For example large spatial elements (e.g. sites,
        buidings) can be made out of smaller spatial elements (e.g. storeys,
        spaces).

        The largest space (typically the IfcSite) can then be aggregated in a
        project. It is requirement for all spatial structures to be directly or
        indirectly aggregated back to the IfcProject to create a hierarchy of
        spaces.

        The other common usecase is when larger physical products are made up of
        smaller physical products. For example, a stair might be made out of a
        flight, a landing, a railing and so on. Or a wall might be made out of
        stud members, and coverings.

        As a product may only have a single locaion in the "spatial
        decomposition" tree, assigning an aggregate relationship will remove any
        previous aggregation, containment, or nesting relationships it may have.

        IFC placements follow a convention where the placement is relative to
        its parent in the spatial hierarchy. If your product has a placement,
        its placement will be recalculated to follow this convention.

        :param product: The part of the aggregate, typically an IfcElement or
            IfcSpatialStructureElement subclass
        :type product: ifcopenshell.entity_instance.entity_instance
        :param relating_object: The whole of the aggregate, typically an
            IfcElement or IfcSpatialStructureElement subclass
        :type relating_object: ifcopenshell.entity_instance.entity_instance
        :return: The IfcRelAggregate relationship instance
        :rtype: ifcopenshell.entity_instance.entity_instance

        Example:

        .. code:: python

            project = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcProject")
            element = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcSite")
            subelement = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcBuilding")

            # The project contains a site (note that project aggregation is a special case in IFC)
            ifcopenshell.api.run("aggregate.assign_object", model, product=element, relating_object=project)

            # The site has a building
            ifcopenshell.api.run("aggregate.assign_object", model, product=subelement, relating_object=element)
        """
        self.file = file
        self.settings = {
            "product": product,
            "relating_object": relating_object,
        }

    def execute(self):
        decomposes = None
        if self.settings["product"].Decomposes:
            decomposes = self.settings["product"].Decomposes[0]

        is_decomposed_by = None
        for rel in self.settings["relating_object"].IsDecomposedBy:
            if rel.is_a("IfcRelAggregates"):
                is_decomposed_by = rel
                break

        if decomposes and decomposes == is_decomposed_by:
            return decomposes

        container = ifcopenshell.util.element.get_container(self.settings["product"], should_get_direct=True)
        if container:
            ifcopenshell.api.run("spatial.remove_container", self.file, product=self.settings["product"])

        if decomposes:
            related_objects = list(decomposes.RelatedObjects)
            related_objects.remove(self.settings["product"])
            if related_objects:
                decomposes.RelatedObjects = related_objects
                ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": decomposes})
            else:
                self.file.remove(decomposes)

        if is_decomposed_by:
            related_objects = set(is_decomposed_by.RelatedObjects)
            related_objects.add(self.settings["product"])
            is_decomposed_by.RelatedObjects = list(related_objects)
            ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": is_decomposed_by})
        else:
            is_decomposed_by = self.file.create_entity(
                "IfcRelAggregates",
                **{
                    "GlobalId": ifcopenshell.guid.new(),
                    "OwnerHistory": ifcopenshell.api.run("owner.create_owner_history", self.file),
                    "RelatedObjects": [self.settings["product"]],
                    "RelatingObject": self.settings["relating_object"],
                }
            )

        placement = getattr(self.settings["product"], "ObjectPlacement", None)
        if placement and placement.is_a("IfcLocalPlacement"):
            ifcopenshell.api.run(
                "geometry.edit_object_placement",
                self.file,
                product=self.settings["product"],
                matrix=ifcopenshell.util.placement.get_local_placement(self.settings["product"].ObjectPlacement),
                is_si=False,
            )

        return is_decomposed_by
