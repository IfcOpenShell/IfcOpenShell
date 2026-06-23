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

from logging import Logger
from typing import Union

import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.util.schema
import ifcopenshell.util.shape_builder

import ifcpatch


class Patcher(ifcpatch.BasePatcher):
    def __init__(
        self,
        file: ifcopenshell.file,
        logger: Union[Logger, None] = None,
        schema: ifcopenshell.util.schema.IFC_SCHEMA = "IFC4",
    ):
        """Migrate from one IFC version to another.

        The recipe iterates every entity in the source file and rewrites it
        into a new file with the target schema, delegating per-entity class /
        attribute translation to :class:`ifcopenshell.util.schema.Migrator`.
        Upgrades (IFC2X3 → IFC4, IFC4 → IFC4X3) are best supported because the
        target schema is a superset; downgrades are lossy by definition (see
        below). Entities that fail to migrate are collected; on completion a
        summary ``RuntimeError`` is raised listing up to 20 failures.

        IFC4 → IFC2X3 downgrade additionally runs a preprocessing pipeline so
        IFC4-only geometry and element classes survive the schema gap:

        - ``IfcIndexedPolyCurve`` (including arc segments, approximated by a
          chord polyline) is flattened to ``IfcPolyline``.
        - ``IfcPolygonalFaceSet`` and ``IfcTriangulatedFaceSet`` are converted
          directly to ``IfcFacetedBrep`` at the entity level, preserving the
          original mesh topology.
        - Orphan IFC4-only geometry instances left over after the rewires are
          purged so the migration loop does not trip on them.
        - IFC4-only ``IfcElement`` subclasses (``IfcLamp``, ``IfcPipeSegment``,
          ``IfcGeographicElement``, …) fall back to ``IfcBuildingElementProxy``
          via the Migrator's ``fallback_element_to_proxy`` opt-in. The
          original class and ``PredefinedType`` are encoded into
          ``ObjectType`` (e.g. ``"IfcLamp/COMPACTFLUORESCENT"``) when
          ``ObjectType`` is empty, so the type information survives the
          downgrade.

        Non-element IFC4-only entities (relationships, geometry items outside
        any product, …) that have no direct equivalent still raise
        ``NotImplementedError`` from the Migrator with the failing class and
        inverse references named, instead of the cryptic
        ``Entity with name '' not found in schema 'IFC2X3'``.

        :param schema: The schema identifier of the IFC version to migrate to.

        Example:

        .. code:: python

            # Upgrade an IFC2X3 model to IFC4
            ifcpatch.execute({"input": "input.ifc", "file": model, "recipe": "Migrate", "arguments": ["IFC4"]})
        """
        super().__init__(file, logger)
        self.schema = schema

    def patch(self):
        # IFC4 and IFC4X3 both have geometry / element classes absent in
        # IFC2X3, so both source schemas need the downgrade preprocessing +
        # IfcBuildingElementProxy fallback when targeting IFC2X3.
        is_downgrade_to_ifc2x3 = self.schema == "IFC2X3" and self.file.schema in ("IFC4", "IFC4X3")
        if is_downgrade_to_ifc2x3:
            self._prepare_for_downgrade()

        self.file_patched = ifcopenshell.file(schema=self.schema)
        migrator = ifcopenshell.util.schema.Migrator(fallback_element_to_proxy=is_downgrade_to_ifc2x3)
        migrator.preprocess(self.file, self.file_patched)

        migrated = 0
        failures: list[tuple[ifcopenshell.entity_instance, Exception]] = []
        for element in self.file:
            try:
                migrator.migrate(element, self.file_patched)
                migrated += 1
            except Exception as exc:
                failures.append((element, exc))

        if is_downgrade_to_ifc2x3:
            self._encode_fallback_class_into_object_type(migrator)

        # BasePatcher.__init__ guarantees self.logger is non-None
        # (ensure_logger falls back to logging.getLogger("IFCPatch")).
        self.logger.info(f"Migrated {migrated} entities to {self.schema}.")
        if failures:
            summary = [f"{len(failures)} entities could not be migrated to {self.schema}:"]
            for element, exc in failures[:20]:
                summary.append(f"  #{element.id()}={element.is_a()}: {exc}")
            if len(failures) > 20:
                summary.append(f"  … (+{len(failures) - 20} more)")
            raise RuntimeError("\n".join(summary))

    def _prepare_for_downgrade(self) -> None:
        from ifcpatch.recipes.DowngradeIndexedPolyCurve import Patcher as DowngradePolyCurve

        DowngradePolyCurve(self.file, self.logger).patch()
        self._convert_face_sets_to_faceted_brep()
        self._purge_orphaned_ifc4_only_entities()

    def _convert_face_sets_to_faceted_brep(self) -> None:
        face_sets = list(self.file.by_type("IfcPolygonalFaceSet")) + list(self.file.by_type("IfcTriangulatedFaceSet"))
        if not face_sets:
            return

        # IfcShapeRepresentations carrying these face sets need their type tag
        # updated from "Tessellation" (IFC4) to "Brep" (IFC2X3-compatible).
        # Snapshot the relevant inverses before rewiring — the inverse set is
        # invalidated once replace_element runs.
        touched_reps: set[int] = set()
        for face_set in face_sets:
            faceted_brep = ifcopenshell.util.shape_builder.polygonal_face_set_to_faceted_brep(face_set)
            touched_reps.update(
                inv.id() for inv in self.file.get_inverse(face_set) if inv.is_a("IfcShapeRepresentation")
            )
            ifcopenshell.util.element.replace_element(face_set, faceted_brep)

        for rep_id in touched_reps:
            self.file.by_id(rep_id).RepresentationType = "Brep"

    def _purge_orphaned_ifc4_only_entities(self) -> None:
        # Preprocessing rewires references away from source-schema-only
        # carriers but does not delete the now-unreferenced instances
        # themselves. Sweep iteratively so cascades collapse leaf-first
        # (curves → point lists, face sets → indexed faces → point lists).
        # Scoped to the actual source schema so IFC4X3 → IFC2X3 downgrades
        # also catch IFC4X3-only geometry (IfcAlignmentCurve etc.), not just
        # the IFC4 gap.
        targets = ifcopenshell.util.schema.geometry_classes_introduced_after(
            self.schema, source_schema=self.file.schema
        )
        while True:
            removed = False
            for ifc_class in targets:
                for entity in list(self.file.by_type(ifc_class)):
                    if not self.file.get_inverse(entity):
                        self.file.remove(entity)
                        removed = True
            if not removed:
                break

    def _encode_fallback_class_into_object_type(self, migrator: ifcopenshell.util.schema.Migrator) -> None:
        # IFC4-only IfcElement subclasses (IfcLamp, IfcPipeSegment, …) migrate
        # as IfcBuildingElementProxy. The subclass identity + its PredefinedType
        # would otherwise be silently lost — IFC2X3 IfcBuildingElementProxy has
        # no slot for them. Encode "<OriginalClass>/<PredefinedType>" into
        # ObjectType when empty (don't trample author-supplied values).
        for source_id, new_id in migrator.migrated_ids.items():
            try:
                source = self.file.by_id(source_id)
                new = self.file_patched.by_id(new_id)
            except RuntimeError:
                continue
            if not new.is_a("IfcBuildingElementProxy"):
                continue
            if source.is_a("IfcBuildingElementProxy"):
                continue
            if getattr(new, "ObjectType", None):
                continue
            predef = getattr(source, "PredefinedType", None)
            new.ObjectType = f"{source.is_a()}/{predef}" if predef else source.is_a()
