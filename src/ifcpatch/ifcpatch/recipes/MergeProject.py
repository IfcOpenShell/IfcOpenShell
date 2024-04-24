# IfcPatch - IFC patching utiliy
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell.util.unit
from typing import Union
from logging import Logger


class Patcher:
    def __init__(self, src: str, file: ifcopenshell.file, logger: Logger, filepath: str):
        """Merge two IFC models into one

        Note that other than combining the two IfcProject elements into one, no
        further processing will be done. This means that you may end up with
        duplicate spatial hierarchies (i.e. 2 sites, 2 buildings, etc).

        Will automatically convert length units in the second model to the main
        model's unit before merging.

        :param filepath: The filepath of the second IFC model to merge into the
            first. The first model is already specified as the input to
            IfcPatch.
        :type filepath: str

        Example:

        .. code:: python

            ifcpatch.execute({"input": "input.ifc", "file": model, "recipe": "MergeProject", "arguments": ["/path/to/model2.ifc"]})
        """
        self.src = src
        self.file = file
        self.logger = logger
        self.filepath = filepath

    def patch(self):
        source = ifcopenshell.open(self.filepath)
        # make sure models units will match
        if (main_unit := self.get_unit_name(self.file)) != self.get_unit_name(source):
            source = ifcopenshell.util.unit.convert_file_length_units(source, main_unit)

        self.existing_contexts: list[ifcopenshell.entity_instance] = self.file.by_type(
            "IfcGeometricRepresentationContext"
        )
        self.added_contexts: set[ifcopenshell.entity_instance] = set()

        original_project = self.file.by_type("IfcProject")[0]
        merged_project = self.file.add(source.by_type("IfcProject")[0])

        for element in source.by_type("IfcGeometricRepresentationContext"):
            new = self.file.add(element)
            self.added_contexts.add(new)

        for element in source:
            self.file.add(element)

        for inverse in self.file.get_inverse(merged_project):
            ifcopenshell.util.element.replace_attribute(inverse, merged_project, original_project)
        self.file.remove(merged_project)

        self.reuse_existing_contexts()

    def get_unit_name(self, ifc_file: ifcopenshell.file) -> str:
        length_unit = ifcopenshell.util.unit.get_project_unit(ifc_file, "LENGTHUNIT")
        return ifcopenshell.util.unit.get_full_unit_name(length_unit)

    def reuse_existing_contexts(self):
        to_delete = set()

        for added_context in self.added_contexts:
            equivalent_existing_context = self.get_equivalent_existing_context(added_context)
            if equivalent_existing_context:
                for inverse in self.file.get_inverse(added_context):
                    ifcopenshell.util.element.replace_attribute(inverse, added_context, equivalent_existing_context)
                to_delete.add(added_context)

        for added_context in to_delete:
            ifcopenshell.util.element.remove_deep2(self.file, added_context)

    def get_equivalent_existing_context(
        self, added_context: ifcopenshell.entity_instance
    ) -> Union[ifcopenshell.entity_instance, None]:
        for context in self.existing_contexts:
            if context.is_a() != added_context.is_a():
                continue
            if context.is_a("IfcGeometricRepresentationSubContext"):
                if (
                    context.ContextType == added_context.ContextType
                    and context.ContextIdentifier == added_context.ContextIdentifier
                    and context.TargetView == added_context.TargetView
                ):
                    return context
            elif (
                context.ContextType == added_context.ContextType
                and context.ContextIdentifier == added_context.ContextIdentifier
            ):
                return context
