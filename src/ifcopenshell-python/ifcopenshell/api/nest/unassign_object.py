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
    def __init__(self, file, related_object=None):
        """Unassigns a related_object from its nest

        A related_object (i.e. a smaller part of a whole) may be aggregated into zero
        or one larger space or task. This function will remove that
        aggregation relationship.

        As all physical IFC model elements must be part of a hierarchical tree
        called the "spatial decomposition", using this function will remove the
        related_object from that tree. This is a dangerous operation and may result in
        the related_object no longer being visible in IFC applications.

        If the related_object is not part of an aggregation relationship, nothing will
        happen.

        :param related_object: The part of the nest, typically an IfcElement or
            IfcSpatialStructureElement subclass
        :type related_object: ifcopenshell.entity_instance.entity_instance
        :return: The IfcRelAggregate relationship instance, only returned if the
            whole still contains any other parts.
        :rtype: ifcopenshell.entity_instance.entity_instance, None

        Example:

        .. code:: python

            task = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcSite")
            subtask1 = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcBuilding")
            subtask2 = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcBuilding")
            ifcopenshell.api.run("nest.assign_object", model, related_object=subtask1, relating_object=task)
            ifcopenshell.api.run("nest.assign_object", model, related_object=subtask2, relating_object=task)
            # The relationship is returned as task still has subtask2
            rel = ifcopenshell.api.run("nest.unassign_object", model, related_object=subtask1)
            # Nothing is returned, as task is now empty
            ifcopenshell.api.run("nest.unassign_object", model, related_object=subtask2)
        """
        self.file = file
        self.settings = { "related_object": related_object }

    def execute(self):
        for rel in self.settings["related_object"].Nests or []:
            if not rel.is_a("IfcRelNests"):
                continue
            if len(rel.RelatedObjects) == 1:
                return self.file.remove(rel)
            related_objects = list(rel.RelatedObjects)
            related_objects.remove(self.settings["related_object"])
            rel.RelatedObjects = related_objects
            ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": rel})
            return rel