# IfcPatch - IFC patching utiliy
# Copyright (C) 2020-2022 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcPatch.
#
# IfcPatch is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcPatch is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcPatch.  If not, see <http://www.gnu.org/licenses/>.

import ifcopenshell
import ifcopenshell.util.element


class Patcher:
    def __init__(self, src, file, logger, args=None):
        self.src = src
        self.file = file
        self.logger = logger
        self.args = args

    def patch(self):
        tags = {}
        for element_type in self.file.by_type("IfcTypeObject"):
            original_type = tags.get(element_type.Tag, None)
            if original_type:
                for element in ifcopenshell.util.element.get_types(element_type):
                    self.assign_type(element, original_type)
                for inverse in self.file.get_inverse(element_type):
                    ifcopenshell.util.element.replace_attribute(inverse, element_type, original_type)
                self.file.remove(element_type)
            else:
                tags[element_type.Tag] = element_type

    def assign_type(self, related_object, relating_type):
        # This is basically a portion of the type.assign_type API which only
        # affects the IfcRelDefinesByType relationship. To be conservative, we
        # don't use the API directly since that would do other things like
        # map type representations or recalculate material set usages which is
        # risky when we're patching an existing dataset.
        if self.file.schema == "IFC2X3":
            is_typed_by = None
            is_defined_by = related_object.IsDefinedBy
            for rel in is_defined_by:
                if rel.is_a("IfcRelDefinesByType"):
                    is_typed_by = [rel]
                    break
            types = relating_type.ObjectTypeOf
        else:
            is_typed_by = related_object.IsTypedBy
            types = relating_type.Types

        if types and is_typed_by == types:
            return

        if is_typed_by:
            related_objects = list(is_typed_by[0].RelatedObjects)
            related_objects.remove(related_object)
            if related_objects:
                is_typed_by[0].RelatedObjects = related_objects
                ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": is_typed_by[0]})
            else:
                self.file.remove(is_typed_by[0])

        if types:
            related_objects = list(types[0].RelatedObjects)
            related_objects.append(related_object)
            types[0].RelatedObjects = related_objects
            ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": types[0]})
        else:
            types = self.file.create_entity(
                "IfcRelDefinesByType",
                **{
                    "GlobalId": ifcopenshell.guid.new(),
                    "OwnerHistory": ifcopenshell.api.run("owner.create_owner_history", self.file),
                    "RelatedObjects": [related_object],
                    "RelatingType": relating_type,
                }
            )
