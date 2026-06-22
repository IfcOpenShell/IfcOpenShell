# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.
#
# This file was generated with the assistance of an AI coding tool.

"""EnumProperty ``items=`` callbacks for the source-based clip-box picker.

Each callback returns ``[(id_str, label, description)]`` where ``id_str`` is
an IFC entity id stringified for entity-driven kinds, an IFC class name for
``CLASS``, or a fixed status name for ``STATUS``. The clip-box operator
turns the picked id into a ``matrix_world`` via the source-preset helper.
"""

from __future__ import annotations

import bonsai.tool as tool

EnumItems = list[tuple[str, str, str]]

# Module-level cache. Blender's EnumProperty stores raw char pointers from the
# tuples a callback returns, so the Python strings must outlive the draw call.
# Stashing the latest result per kind keeps them alive across callback firings.
_items_cache: dict[str, EnumItems] = {}

# Sentinel id used for the "no options available" placeholder. The operator
# treats this as an invalid pick and surfaces an ERROR.
NO_OPTIONS_ID = "__none__"


def _cache(kind: str, items: EnumItems) -> EnumItems:
    _items_cache[kind] = items
    return items


def _no_options(label: str) -> EnumItems:
    # Blender refuses to draw an EnumProperty with zero entries — show a
    # placeholder so the dialog renders and the user sees the empty state.
    return [(NO_OPTIONS_ID, label, "")]


def _label(entity, ifc_class: str | None = None) -> str:
    name = (getattr(entity, "Name", None) or "Unnamed").strip() or "Unnamed"
    return f"{ifc_class}: {name}" if ifc_class else name


def _build_items(kind: str, empty_label: str, build_fn) -> EnumItems:
    """Shared shape for the IFC-driven enum callbacks.

    Returns the no-IFC placeholder if no file is loaded, then runs
    ``build_fn(ifc_file)``, sorts the result alphabetically by label, and
    returns the empty-result placeholder if nothing matched. The output is
    always routed through the module cache.
    """
    ifc = tool.Ifc.get()
    if ifc is None:
        return _cache(kind, _no_options("No IFC loaded"))
    items = build_fn(ifc)
    items.sort(key=lambda t: t[1].lower())
    if not items:
        return _cache(kind, _no_options(empty_label))
    return _cache(kind, items)


# Top-down spatial hierarchy so the picker reads in the order an architect
# already thinks in, rather than a flat alphabetical mix. IfcSpace is excluded
# — spaces are typically empty volumes used for room metadata, so clipping to
# one rarely matches the user intent of "show me what's in this container".
SPATIAL_CLASSES: tuple[str, ...] = (
    "IfcProject",
    "IfcSite",
    "IfcBuilding",
    "IfcBuildingStorey",
)


def spatial_items(self, context) -> EnumItems:
    # Special-case: per-class sort within the hierarchy order rather than a
    # flat alphabetical sort, so the dropdown reads project → site → building.
    ifc = tool.Ifc.get()
    if ifc is None:
        return _cache("SPATIAL", _no_options("No IFC loaded"))
    items: EnumItems = []
    for ifc_class in SPATIAL_CLASSES:
        try:
            entities = ifc.by_type(ifc_class, include_subtypes=False)
        except RuntimeError:
            continue
        for entity in sorted(entities, key=lambda e: (e.Name or "").lower()):
            items.append((str(entity.id()), _label(entity, ifc_class), ""))
    if not items:
        return _cache("SPATIAL", _no_options("No spatial containers"))
    return _cache("SPATIAL", items)


def class_items(self, context) -> EnumItems:
    # Special-case: the picker value IS the IFC class name, not an entity id,
    # so the build shape differs from the other entity-driven callbacks.
    ifc = tool.Ifc.get()
    if ifc is None:
        return _cache("CLASS", _no_options("No IFC loaded"))
    # List only IFC classes ACTUALLY present in the file (not the whole
    # schema), so the user picks from classes that can produce a non-empty
    # clip volume. ``e.is_a()`` returns the most specific class per element.
    present = sorted({e.is_a() for e in ifc.by_type("IfcProduct")})
    if not present:
        return _cache("CLASS", _no_options("No products"))
    return _cache("CLASS", [(cls, cls, "") for cls in present])


def type_items(self, context) -> EnumItems:
    return _build_items(
        "TYPE",
        "No types defined",
        lambda ifc: [(str(e.id()), _label(e, e.is_a()), "") for e in ifc.by_type("IfcTypeProduct")],
    )


def material_items(self, context) -> EnumItems:
    return _build_items(
        "MATERIAL",
        "No materials defined",
        lambda ifc: [(str(e.id()), _label(e), "") for e in ifc.by_type("IfcMaterial")],
    )


def profile_items(self, context) -> EnumItems:
    # ProfileName is optional. Skip unnamed profiles — they can't be
    # meaningfully picked from a flat list.
    return _build_items(
        "PROFILE",
        "No named profiles",
        lambda ifc: [
            (str(e.id()), f"{e.is_a()}: {e.ProfileName}", "")
            for e in ifc.by_type("IfcProfileDef")
            if getattr(e, "ProfileName", None)
        ],
    )


def drawing_items(self, context) -> EnumItems:
    return _build_items(
        "DRAWING",
        "No drawings defined",
        lambda ifc: [(str(e.id()), _label(e), "") for e in ifc.by_type("IfcAnnotation") if e.ObjectType == "DRAWING"],
    )


# Display labels for each status value. The id strings on the left are the
# canonical Pset_*Common.Status enum values accepted by Bonsai's status query.
STATUS_LABELS: tuple[tuple[str, str], ...] = (
    ("No Status", "No Status"),
    ("NEW", "New"),
    ("EXISTING", "Existing"),
    ("DEMOLISH", "Demolish"),
    ("TEMPORARY", "Temporary"),
    ("OTHER", "Other"),
    ("NOTKNOWN", "Not Known"),
    ("UNSET", "Unset"),
)


def status_items(self, context) -> EnumItems:
    # Fixed enum; no IFC needed. Still routed through the cache to share the
    # same string-lifetime guarantee as the other callbacks.
    return _cache("STATUS", [(value, label, "") for value, label in STATUS_LABELS])


def system_items(self, context) -> EnumItems:
    # IfcStructuralAnalysisModel is a structural-grouping container, not a
    # distribution system — excluded to match Bonsai's other system pickers.
    return _build_items(
        "SYSTEM",
        "No systems defined",
        lambda ifc: [
            (str(e.id()), _label(e, e.is_a()), "")
            for e in ifc.by_type("IfcSystem")
            if not e.is_a("IfcStructuralAnalysisModel")
        ],
    )


def group_items(self, context) -> EnumItems:
    # include_subtypes=False so IfcSystem and IfcZone instances don't appear
    # under Group as well — those get their own picker entries.
    return _build_items(
        "GROUP",
        "No groups defined",
        lambda ifc: [(str(e.id()), _label(e), "") for e in ifc.by_type("IfcGroup", include_subtypes=False)],
    )


def zone_items(self, context) -> EnumItems:
    return _build_items(
        "ZONE",
        "No zones defined",
        lambda ifc: [(str(e.id()), _label(e), "") for e in ifc.by_type("IfcZone")],
    )
