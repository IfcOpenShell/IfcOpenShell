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

from logging import Logger
from typing import Any

import ifcopenshell
import ifcopenshell.api.type
import ifcopenshell.util.element


class Patcher:
    def __init__(
        self, file: ifcopenshell.file, logger: Logger, attribute: str = "Tag", should_merge_null: bool = False
    ):
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
        Only types of the same IFC class are ever merged, so e.g. an
        annotation type and a beam type that happen to share an attribute value
        are never combined.

        :param should_merge_null: If True, all types with an empty attribute
            will be merged together. This defaults to False because an empty
            attribute is an absence of evidence, not proof of duplication:
            merging every untagged type into one silently destroys distinct
            types (a common failure on Bonsai-authored or mixed models, where
            genuine, differently-named types may all lack a Tag). Genuine Revit
            duplicates always carry a populated Tag, so the default only affects
            types the recipe has no reason to believe are duplicates.

        Example:

        .. code:: python

            # Default behaviour of merging by Tag attribute
            ifcpatch.execute({"file": model, "recipe": "MergeDuplicateTypes", "arguments": []})

            # Explicitly say we want to merge based on the Name attribute
            ifcpatch.execute({"file": model, "recipe": "MergeDuplicateTypes", "arguments": ["Name"]})

            # Also merge all types that have an empty Tag into a single type
            ifcpatch.execute({"file": model, "recipe": "MergeDuplicateTypes", "arguments": ["Tag", True]})
        """
        self.file = file
        self.logger = logger
        self.attribute = attribute
        self.should_merge_null = should_merge_null

    def patch(self):
        keys: dict[Any, ifcopenshell.entity_instance] = {}
        for element_type in self.file.by_type("IfcTypeObject"):
            # Not every subtype has this attribute, e.g. IfcTypeProcess.
            attribute_value = getattr(element_type, self.attribute, None)
            if not attribute_value and not self.should_merge_null:
                continue
            # Include the IFC class in the key so that only types of the same
            # class are ever merged. Two types of different classes are not
            # duplicates, and merging them would reassign occurrences to an
            # incompatible type (e.g. an IfcTypeProduct used for annotations
            # cannot type an IfcBeam), raising a TypeError in assign_type.
            key = (element_type.is_a(), attribute_value)
            original_type = keys.get(key, None)
            if original_type:
                elements = ifcopenshell.util.element.get_types(element_type)
                if elements:
                    self.assign_type(elements, original_type)
                for inverse in self.file.get_inverse(element_type):
                    ifcopenshell.util.element.replace_attribute(inverse, element_type, original_type)
                self.file.remove(element_type)
            else:
                keys[key] = element_type

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
            should_run_listeners=False,  # ty:ignore[unknown-argument]
        )
