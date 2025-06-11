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
import ifcopenshell.api
import ifcopenshell.api.type
import ifcopenshell.util.element
from logging import Logger
from typing import Any


class Patcher:
    def __init__(self, file: ifcopenshell.file, logger: Logger, attribute: str = "Tag"):
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

        Example:

        .. code:: python

            # Default behaviour of merging by Tag attribute
            ifcpatch.execute({"file": model, "recipe": "MergeDuplicateTypes", "arguments": []})

            # Explicitly say we want to merge based on the Name attribute
            ifcpatch.execute({"file": model, "recipe": "MergeDuplicateTypes", "arguments": ["Name"]})
        """
        self.file = file
        self.logger = logger
        self.attribute = attribute

    def patch(self):
        key = self.attribute
        keys: dict[Any, ifcopenshell.entity_instance] = {}
        for element_type in self.file.by_type("IfcTypeObject"):
            original_type = keys.get(getattr(element_type, key), None)
            if original_type:
                elements = ifcopenshell.util.element.get_types(element_type)
                if elements:
                    self.assign_type(elements, original_type)
                for inverse in self.file.get_inverse(element_type):
                    ifcopenshell.util.element.replace_attribute(inverse, element_type, original_type)
                self.file.remove(element_type)
            else:
                keys[getattr(element_type, key)] = element_type

    def assign_type(
        self, related_objects: list[ifcopenshell.entity_instance], relating_type: ifcopenshell.entity_instance
    ) -> None:
        # To be conservative, we disable `should_map_representations`
        # since that would do other things like
        # map type representations or recalculate material set usages which is
        # risky when we're patching an existing dataset.
        ifcopenshell.api.type.assign_type(
            self.file,
            relating_type=relating_type,
            related_objects=related_objects,
            should_map_representations=False,
            should_run_listeners=False,
        )
