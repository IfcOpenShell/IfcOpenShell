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

# This file was generated with the assistance of an AI coding tool.

from logging import Logger
from typing import Union

import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.util.selector

import ifcpatch


class Patcher(ifcpatch.BasePatcher):
    def __init__(self, file: ifcopenshell.file, logger: Union[Logger, None] = None, query: str = ""):
        """Clear an occurrence's PredefinedType/ObjectType when its type is already concrete

        IFC forbids "double typing": if an IfcTypeObject's own PredefinedType
        is a concrete value (i.e. not NOTDEFINED), the PredefinedType and
        ObjectType of its typed occurrences must be left empty, since the
        type already carries that information (buildingSMART rule OJT001).

        Legacy files, or files typed before their type's PredefinedType was
        set, commonly carry a stray PredefinedType (often NOTDEFINED) or
        ObjectType on the occurrence anyway. This recipe finds every
        occurrence typed by a type with a concrete PredefinedType and clears
        the occurrence's own PredefinedType and ObjectType attributes,
        without touching untyped occurrences or occurrences of a type that is
        itself NOTDEFINED (as those may still carry meaningful data of their
        own).

        The "is the type concrete" check mirrors
        ifcopenshell.api.type.assign_type and
        ifcopenshell.api.attribute.edit_attributes: a type whose
        PredefinedType is USERDEFINED only counts as concrete if it also has
        a custom type name (e.g. ElementType) to fall back on. This keeps the
        recipe non-destructive: it will never remove the only description an
        occurrence has.

        :param query: A query to select the subset of IFC elements to
            restrict the patch to, optional. If not provided, patch will be
            applied to all typed occurrences in the model. See
            ifcopenshell.util.selector for query syntax.

        Example:

        .. code:: python

            # Fix all double-typed occurrences in the model.
            ifcpatch.execute({"input": "input.ifc", "file": model, "recipe": "FixDoubleTypedPredefinedType"})

            # Only fix double-typed walls.
            ifcpatch.execute({
                "input": "input.ifc",
                "file": model,
                "recipe": "FixDoubleTypedPredefinedType",
                "arguments": ["IfcWall"],
            })
        """
        super().__init__(file, logger)
        self.query = query

    def patch(self):
        occurrences = None
        if self.query:
            occurrences = ifcopenshell.util.selector.filter_elements(self.file, self.query)

        cleared = 0
        for rel in self.file.by_type("IfcRelDefinesByType"):
            predefined_type = ifcopenshell.util.element.get_predefined_type(rel.RelatingType)
            if predefined_type is None or predefined_type == "NOTDEFINED":
                continue
            for occurrence in rel.RelatedObjects:
                if occurrences is not None and occurrence not in occurrences:
                    continue
                has_predefined_type = hasattr(occurrence, "PredefinedType")
                if not occurrence.ObjectType and (not has_predefined_type or not occurrence.PredefinedType):
                    continue  # Already clean.
                occurrence.ObjectType = None
                if has_predefined_type:
                    occurrence.PredefinedType = None
                cleared += 1

        self.logger.info(f"Cleared PredefinedType/ObjectType on {cleared} double-typed occurrence(s).")
