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
        """Unassigns a type of an occurrence

        :param related_object: The IfcElement occurrence.
        :type related_object: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

        Example:

        .. code:: python

            # A furniture type. This would correlate to a particular model in a
            # manufacturer's catalogue. Like an Ikea sofa :)
            furniture_type = ifcopenshell.api.run("root.create_entity", model,
                ifc_class="IfcFurnitureType", name="FUN01")

            # An individual occurrence of a that sofa.
            furniture = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcFurniture")

            # Assign the furniture to the furniture type.
            ifcopenshell.api.run("type.assign_type", model, related_object=furniture, relating_type=furniture_type)

            # Change our mind. Maybe it's a different type?
            ifcopenshell.api.run("type.unassign_type", model, related_object=furniture)
        """
        self.file = file
        self.settings = {"related_object": related_object}

    def execute(self):
        if self.file.schema == "IFC2X3":
            is_typed_by = None
            is_defined_by = self.settings["related_object"].IsDefinedBy
            for rel in is_defined_by:
                if rel.is_a("IfcRelDefinesByType"):
                    is_typed_by = rel
        else:
            is_typed_by = self.settings["related_object"].IsTypedBy
            if is_typed_by:
                is_typed_by = is_typed_by[0]

        if is_typed_by:
            related_objects = list(is_typed_by.RelatedObjects)
            related_objects.remove(self.settings["related_object"])
            if related_objects:
                is_typed_by.RelatedObjects = related_objects
                ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": is_typed_by})
            else:
                self.file.remove(is_typed_by)
