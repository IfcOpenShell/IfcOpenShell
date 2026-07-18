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
from typing import Any, Union

import ifcopenshell
import ifcopenshell.util.element


class Patcher:
    def __init__(self, file: ifcopenshell.file, logger: Logger):
        """Merge duplicate geometric representation contexts

        A well-formed IFC has a single geometric representation context for each
        combination of context type, identifier, and target view (e.g. one
        Model/Body/MODEL_VIEW). Some authoring tools, or files that have been
        merged or round-tripped, end up with two or more contexts that are
        identical in all three. This is non-conformant and breaks code that
        looks a context up by its attributes: only the first is ever found, so
        anything (geometry, material styles, annotations) attached to the others
        is silently orphaned. A common symptom is a layered wall rendering with
        a single material style because each layer's style hangs off the second,
        never-matched, Body context.

        This patch keeps the first context for each
        (ContextType, ContextIdentifier, TargetView) key, repoints everything
        referencing the duplicates onto that survivor, and removes the
        duplicates. Top-level contexts and subcontexts are handled separately so
        a subcontext is never merged into a parent context.

        Example:

        .. code:: python

            ifcpatch.execute({"file": model, "recipe": "MergeDuplicateContexts", "arguments": []})
        """
        self.file = file
        self.logger = logger

    def patch(self) -> None:
        # Subcontexts first, then top-level contexts, so the two kinds are never
        # merged together and a surviving subcontext keeps a valid ParentContext.
        for ifc_class in ("IfcGeometricRepresentationSubContext", "IfcGeometricRepresentationContext"):
            if ifc_class == "IfcGeometricRepresentationContext":
                contexts = self.file.by_type(ifc_class, include_subtypes=False)
            else:
                contexts = self.file.by_type(ifc_class)

            groups: dict[Any, list[ifcopenshell.entity_instance]] = {}
            for context in contexts:
                groups.setdefault(self.get_key(context), []).append(context)

            for key, group in groups.items():
                if len(group) < 2:
                    continue
                survivor, *duplicates = group
                self.logger.info(
                    "Merging %s duplicate(s) of %s into #%s", len(duplicates), key, survivor.id()
                )
                for duplicate in duplicates:
                    try:
                        # An upstream partial removal (e.g. MergeProjects'
                        # order-sensitive remove_deep2 cleanup) can leave an entity
                        # that by_type still returns but that the file can no longer
                        # resolve. Re-fetching by id raises for such a stale entity,
                        # and replace_element -> get_inverse also raises; either way
                        # there is nothing valid to collapse, so skip it.
                        duplicate = self.file.by_id(duplicate.id())
                        ifcopenshell.util.element.replace_element(duplicate, survivor)
                        self.file.remove(duplicate)
                    except RuntimeError:
                        self.logger.warning(
                            "MergeDuplicateContexts: skipping context the file cannot resolve (%s)", key
                        )
                # Repointing may leave the survivor listed twice in a SET-typed
                # attribute (e.g. IfcProject.RepresentationContexts), which is
                # non-conformant. Dedupe those aggregates.
                self.dedupe_references(survivor)

    def dedupe_references(self, element: ifcopenshell.entity_instance) -> None:
        for inverse in self.file.get_inverse(element):
            for i, value in enumerate(inverse):
                if not isinstance(value, tuple) or value.count(element) < 2:
                    continue
                # Keep the first occurrence of the survivor, drop the rest;
                # leave every other member untouched and in order.
                deduped = []
                for v in value:
                    if v == element and element in deduped:
                        continue
                    deduped.append(v)
                inverse[i] = deduped

    def get_key(self, context: ifcopenshell.entity_instance) -> tuple[Any, ...]:
        # ContextIdentifier / TargetView are None on plain contexts; that is a
        # valid, stable part of the key.
        return (
            context.ContextType,
            getattr(context, "ContextIdentifier", None),
            getattr(context, "TargetView", None),
        )
