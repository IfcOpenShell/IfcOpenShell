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


class Usecase:
    def __init__(self, file, related_object=None, relating_type=None):
        """Gets all the related occurrences of a type

        Do not use this function. It will be removed. Use
        ifcopenshell.util.element.get_type or
        ifcopenshell.util.element.get_types instead.

        :param related_object: The IfcElement occurrence.
        :type related_object: ifcopenshell.entity_instance.entity_instance
        :param relating_type: The IfcElementType type.
        :type relating_type: ifcopenshell.entity_instance.entity_instance
        :return: A list of occurrences of the type.
        :rtype: list[ifcopenshell.entity_instance.entity_instance]
        """
        self.file = file
        self.settings = {
            "related_object": related_object,
            "relating_type": relating_type,
        }

    def execute(self):
        if self.settings["related_object"]:
            if self.file.schema == "IFC2X3":
                is_defined_by = self.settings["related_object"].IsDefinedBy
                for rel in is_defined_by:
                    if rel.is_a("IfcRelDefinesByType"):
                        return set([int(o.id()) for o in rel.RelatedObjects])
            else:
                is_typed_by = self.settings["related_object"].IsTypedBy
                if is_typed_by:
                    return set([int(o.id()) for o in is_typed_by[0].RelatedObjects])
        elif self.settings["relating_type"]:
            if self.file.schema == "IFC2X3":
                types = self.settings["relating_type"].ObjectTypeOf
            else:
                types = self.settings["relating_type"].Types
            if types:
                return set([int(o.id()) for o in types[0].RelatedObjects])
        return set()
