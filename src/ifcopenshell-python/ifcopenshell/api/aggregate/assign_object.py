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

        :param product: The part of the aggregate
        :param relating_object: The whole of the aggregate
        :return: entity: The aggregate relationship

        Example::

            element = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcSite")
            subelement = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcBuilding")
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
            return

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
