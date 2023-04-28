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
    def __init__(self, src, file, logger, attribute="Tag"):
        """Merge duplicate element types via the Tag or another attribute

        Revit is notorious for creating many duplicate element types. Element
        types may be duplicated by being mirrored, such as doors, columns, etc,
        or being certain MEP equipment. This means that even though you think
        you might have only 3 door families and 3 door types in your door
        schedule, your IFC might actually incorrectly store 6 or more door types.

        Revit stores the Revit Element ID in the "Tag" attribute of all IFC
        elements, so we can deduce that multiple IFC elements with the same Tag
        attribute have been duplicated in IFC. This patch will merge them into a
        single element type.

        You may optionally specify your own attribute if you want to merge using
        different criteria, such as "Name". For example, may Revit users
        incorrectly have multiple types with the same name as workarounds to
        overcome various Revit limitations. This is incorrect and this patch
        will merge the types into a single type.

        Occurrences of the type will be remapped to the merged type.

        :param attribute: The name of the attribute to merge element types based
            on. Typically this will be "Tag" as it stores the unique ID from the
            proprietary BIM software.
        :type attribute: str

        Example:

        .. code:: python

            # Default behaviour of merging by Tag attribute
            ifcpatch.execute({"input": model, "recipe": "MergeDuplicateTypes", "arguments": []})

            # Explicitly say we want to merge based on the Name attribute
            ifcpatch.execute({"input": model, "recipe": "MergeDuplicateTypes", "arguments": ["Name"]})
        """
        self.src = src
        self.file = file
        self.logger = logger
        self.attribute = attribute

    def patch(self):
        key = self.attribute
        keys = {}
        for element_type in self.file.by_type("IfcTypeObject"):
            original_type = keys.get(getattr(element_type, key), None)
            if original_type:
                for element in ifcopenshell.util.element.get_types(element_type):
                    self.assign_type(element, original_type)
                for inverse in self.file.get_inverse(element_type):
                    ifcopenshell.util.element.replace_attribute(inverse, element_type, original_type)
                self.file.remove(element_type)
            else:
                keys[getattr(element_type, key)] = element_type

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
