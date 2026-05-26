# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2024 Bonsai Contributors
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

"""Fetch BIM-tagged entities from an active CAD Sketcher sketch and create
IFC elements in the current Bonsai project."""

import json

import bpy
from bpy.props import CollectionProperty, EnumProperty, FloatProperty, IntProperty, StringProperty
from bpy.types import Operator, PropertyGroup


import bonsai.core.geometry
import bonsai.core.root
import bonsai.tool as tool
import ifcopenshell.api.feature
import ifcopenshell.api.pset
import ifcopenshell.api.root as ifcopenshell_api_root
import ifcopenshell.util.element
import ifcopenshell.util.representation
import ifcopenshell.util.unit
import mathutils

# ── Group-aware data access ──────────────────────────────────────────────────


def _tpg_decode(raw_value):
    text = (raw_value or "").strip()
    if not text:
        return [], ""

    if text.startswith("{") and text.endswith("}"):
        try:
            obj = json.loads(text)
            if isinstance(obj, dict):
                entries = []
                if isinstance(obj.get("entries"), list):
                    for item in obj["entries"]:
                        if not isinstance(item, dict):
                            continue
                        tag = str(item.get("t") or item.get("tag") or "").strip()
                        if not tag:
                            continue
                        param = str(item.get("p") or item.get("param") or "").strip()
                        guid = str(item.get("g") or item.get("guid") or "").strip()
                        entries.append({"t": tag, "p": param, "g": guid})
                    if entries:
                        return entries, ""

                for key, value in obj.items():
                    if key in {"v", "entries"}:
                        continue
                    tag = str(key).strip()
                    if not tag:
                        continue
                    guid = "" if value is None else str(value).strip()
                    entries.append({"t": tag, "p": "", "g": guid})
                if entries:
                    return entries, ""
        except Exception:
            pass

    entries = []
    for part in text.replace("|", ";").split(";"):
        token = part.strip()
        if not token:
            continue
        if "=" in token:
            key, value = token.split("=", 1)
        elif ":" in token:
            key, value = token.split(":", 1)
        else:
            continue
        tag = key.strip()
        if not tag:
            continue
        entries.append({"t": tag, "p": "", "g": value.strip()})
    if entries:
        return entries, ""

    return [], text


def _tpg_encode(entries):
    payload = {
        "v": 1,
        "entries": [
            {
                "t": str(entry.get("t") or "").strip(),
                "p": str(entry.get("p") or "").strip(),
                "g": str(entry.get("g") or "").strip(),
            }
            for entry in entries
            if str(entry.get("t") or "").strip()
        ],
    }
    return json.dumps(payload, separators=(",", ":"))


def _tpg_get_guid(raw_value, ifc_tag=None):
    entries, legacy_single = _tpg_decode(raw_value)
    if ifc_tag:
        tag = str(ifc_tag).strip()
        for entry in entries:
            if entry["t"] == tag:
                return entry["g"]
        return legacy_single

    for entry in entries:
        if entry["g"]:
            return entry["g"]
    return legacy_single


def _tpg_set_guid(raw_value, ifc_tag, guid):
    tag = str(ifc_tag or "").strip()
    guid_value = str(guid or "").strip()
    if not tag:
        return guid_value

    entries, _legacy_single = _tpg_decode(raw_value)
    updated = []
    replaced = False
    for entry in entries:
        if entry["t"] == tag and not replaced:
            updated.append({"t": tag, "p": entry.get("p", ""), "g": guid_value})
            replaced = True
            continue
        if entry["t"] == tag:
            continue
        updated.append(entry)

    if not replaced:
        updated.append({"t": tag, "p": "", "g": guid_value})

    return _tpg_encode(updated)


def _entity_guid(sketch, slvs_index, ifc_tag=None):
    """Return the GUID stored for *slvs_index* in *sketch*.groups.

    If *ifc_tag* is given, only search groups with that tag.  Returns ``""`` if
    not found or if either argument is *None*.
    """
    if sketch is None or slvs_index == -1:
        return ""

    group_index = _decode_group_key(slvs_index)
    if group_index is not None and 0 <= group_index < len(sketch.groups):
        group = sketch.groups[group_index]
        if ifc_tag and not _group_has_active_tag(group, ifc_tag):
            return ""
        group_guid = _tpg_get_guid(group.guid, ifc_tag)
        if group_guid:
            return group_guid
        if ifc_tag == "IfcWall":
            return _group_first_member_guid(group, ifc_tag) or ""
        return ""

    for group in sketch.groups:
        if ifc_tag and not _group_has_active_tag(group, ifc_tag):
            continue
        member = group.get_member(slvs_index)
        if member:
            member_guid = _tpg_get_guid(member.guid, ifc_tag)
            if member_guid:
                return member_guid
    return ""


def _group_has_active_tag(group, ifc_tag):
    """Return True only when *group* has *ifc_tag* enabled.

    CAD Sketcher keeps tags with an ``enabled`` flag; disabled tags should not
    participate in fetch proposals.
    """
    if not ifc_tag:
        return True

    tags = getattr(group, "tags", None)
    if tags is not None:
        for tag in tags:
            if getattr(tag, "value", None) != ifc_tag:
                continue
            if getattr(tag, "enabled", True):
                return True
        return False

    # Fallback for environments where tags collection is not exposed.
    return bool(hasattr(group, "has_tag") and group.has_tag(ifc_tag))


def _group_member_guids(group):
    """Return the non-empty GUIDs stored on the members of *group*."""
    values = []
    for member in getattr(group, "members", []):
        guid = _tpg_get_guid(getattr(member, "guid", ""))
        if guid:
            values.append(guid)
    return values


def _group_first_member_guid(group, ifc_tag=None):
    member_guids = []
    for member in getattr(group, "members", []):
        guid = _tpg_get_guid(getattr(member, "guid", ""), ifc_tag)
        if guid:
            member_guids.append(guid)
    return member_guids[0] if member_guids else ""


def _set_entity_guid(sketch, slvs_index, ifc_tag, guid):
    """Write *guid* to the group member for *slvs_index* in *sketch*.

    Searches groups tagged *ifc_tag*; creates a group + member when missing.
    No-ops when *sketch* is *None* or *slvs_index* is ``-1``.
    """
    if sketch is None or slvs_index == -1:
        return

    group_index = _decode_group_key(slvs_index)
    if group_index is not None and 0 <= group_index < len(sketch.groups):
        group = sketch.groups[group_index]
        if not ifc_tag or _group_has_active_tag(group, ifc_tag):
            group.guid = _tpg_set_guid(group.guid, ifc_tag, guid)
        return

    for group in sketch.groups:
        if not _group_has_active_tag(group, ifc_tag):
            continue
        member = group.get_member(slvs_index)
        if member is None:
            member = group.add_member(slvs_index)
        member.guid = _tpg_set_guid(member.guid, ifc_tag, guid)
        return
    group = sketch.groups.add()
    group.add_tag(ifc_tag)
    member = group.add_member(slvs_index)
    member.guid = _tpg_set_guid(member.guid, ifc_tag, guid)


def _entities_with_ifc_tag(sketch, sse, ifc_tag, predicate=None):
    """Return entities in *sketch*.groups tagged *ifc_tag*.

    Optional *predicate(entity) → bool* for further filtering.  Deduplicates
    by slvs_index.  Returns an empty list when *sketch* is *None*.
    """
    if sketch is None:
        return []
    seen = set()
    result = []
    for group in sketch.groups:
        if not _group_has_active_tag(group, ifc_tag):
            continue
        for member in group.members:
            if member.entity_index in seen:
                continue
            ent = sse.get(member.entity_index)
            if ent is None:
                continue
            if predicate is None or predicate(ent):
                seen.add(member.entity_index)
                result.append(ent)
    return result


def _ensure_entity_in_group(sketch, slvs_index, ifc_tag):
    """Ensure *slvs_index* is a member of a group tagged *ifc_tag* in *sketch*.

    Creates the group and/or member if missing.  No-ops when *sketch* is *None*
    or *slvs_index* is ``-1``.
    """
    if sketch is None or slvs_index == -1:
        return

    # Group-key identifiers already point at a group; nothing to do.
    if _decode_group_key(slvs_index) is not None:
        return

    for group in sketch.groups:
        if not _group_has_active_tag(group, ifc_tag):
            continue
        if group.get_member(slvs_index) is None:
            group.add_member(slvs_index)
        return
    group = sketch.groups.add()
    group.add_tag(ifc_tag)
    group.add_member(slvs_index)


def _entity_ifc_tag(sketch, slvs_index):
    """Return the IFC class tag for *slvs_index* from its group memberships.

    Returns ``""`` when *sketch* is *None* or the entity belongs to no group.
    """
    if sketch is None:
        return ""

    group_index = _decode_group_key(slvs_index)
    if group_index is not None and 0 <= group_index < len(sketch.groups):
        vals = sketch.groups[group_index].tag_values()
        return vals[0] if vals else ""

    for group in sketch.groups:
        if group.get_member(slvs_index) is not None:
            vals = group.tag_values()
            return vals[0] if vals else ""
    return ""


def _sketch_has_role(sketch, role):
    if sketch is None:
        return False
    if hasattr(sketch, "has_tag"):
        try:
            return sketch.has_tag(role)
        except Exception:
            pass
    return getattr(sketch, "tag", "") == role


_GROUP_KEY_BASE = 2_000_000_000


def _encode_group_key(group_index):
    return -(_GROUP_KEY_BASE + int(group_index))


def _decode_group_key(value):
    if value <= -_GROUP_KEY_BASE:
        return -value - _GROUP_KEY_BASE
    return None


class _PathGroupProxy:
    """Path-group view over a SketchGroup path so downstream code can reuse
    segment-based logic while CAD Sketcher stores only groups."""

    def __init__(self, group, group_index, sse, sketch_index, ifc_tag=None):
        self._group = group
        self.slvs_index = _encode_group_key(group_index)
        self.sketch_i = sketch_index
        self.name = group.name
        self.member_guids = _group_member_guids(group)
        self.guid = group.guid or (_group_first_member_guid(group) if ifc_tag == "IfcWall" else "")
        self.segment_indices = [
            int(m.entity_index)
            for m in group.members
            if m.entity_index != -1
            and sse.get(m.entity_index) is not None
            and hasattr(sse.get(m.entity_index), "p1")
            and hasattr(sse.get(m.entity_index), "p2")
        ]
        self.segment_count = len(self.segment_indices)
        self.closed = group.path_type(sse) == "CLOSED_PATH"


def _group_path_proxies(sketch, sse, ifc_tag, path_kind="ANY"):
    if sketch is None:
        return []

    result = []
    for i, group in enumerate(sketch.groups):
        if not _group_has_active_tag(group, ifc_tag):
            continue
        ptype = group.path_type(sse)
        if path_kind == "OPEN" and ptype != "OPEN_PATH":
            continue
        if path_kind == "CLOSED" and ptype != "CLOSED_PATH":
            continue
        if path_kind == "ANY" and ptype == "NOT_PATH":
            continue
        proxy = _PathGroupProxy(group, i, sse, sketch.slvs_index, ifc_tag)
        if proxy.segment_count > 0:
            result.append(proxy)
    return result


def _resolve_path_proxy(sketch, sse, key, ifc_tag=None, path_kind="ANY"):
    group_index = _decode_group_key(key)
    if group_index is None:
        return None
    if sketch is None or not (0 <= group_index < len(sketch.groups)):
        return None

    group = sketch.groups[group_index]
    if ifc_tag and not _group_has_active_tag(group, ifc_tag):
        return None

    ptype = group.path_type(sse)
    if path_kind == "OPEN" and ptype != "OPEN_PATH":
        return None
    if path_kind == "CLOSED" and ptype != "CLOSED_PATH":
        return None
    if path_kind == "ANY" and ptype == "NOT_PATH":
        return None

    proxy = _PathGroupProxy(group, group_index, sse, sketch.slvs_index, ifc_tag)
    return proxy if proxy.segment_count > 0 else None


def _wall_type_items(self, context):
    items = []
    ifc = tool.Ifc.get()
    if ifc:
        for t in sorted(ifc.by_type("IfcWallType"), key=lambda e: e.Name or ""):
            items.append((str(t.id()), t.Name or f"#{t.id()}", ""))
    return items or [("0", "(No IfcWallType in project)", "")]


def _active_sketch_is_elevation(context):
    """Return True when the active CAD Sketcher sketch is an Elevation sketch."""
    try:
        sketch = context.scene.sketcher.entities.active
        return sketch is not None and _sketch_has_role(sketch, "Elevation")
    except Exception:
        return False


def _layer_direction_for_type(ifc_type):
    """Return LayerSetDirection if the type has an IfcMaterialLayerSetUsage, else None."""
    try:
        mat = ifcopenshell.util.element.get_material(ifc_type)
        if mat is not None and mat.is_a("IfcMaterialLayerSetUsage"):
            return mat.LayerSetDirection
    except Exception:
        pass
    return None


def _type_matches_sketch(ifc_type, is_elevation):
    """Return True when a layered type is appropriate for the given sketch orientation.

    Types with an explicit LayerSetDirection are filtered:
      - AXIS3 (layers stacked in Z) → horizontal → plan sketches only
      - AXIS1 / AXIS2              → vertical   → elevation sketches only
    Types with no direction set are shown in both contexts.
    """
    direction = _layer_direction_for_type(ifc_type)
    if direction is None:
        return True
    if is_elevation:
        return direction != "AXIS3"
    return direction == "AXIS3"


def _slab_type_items(self, context):
    items = []
    ifc = tool.Ifc.get()
    if ifc:
        is_elevation = _active_sketch_is_elevation(context)
        for t in sorted(ifc.by_type("IfcSlabType"), key=lambda e: e.Name or ""):
            if _type_matches_sketch(t, is_elevation):
                items.append((str(t.id()), t.Name or f"#{t.id()}", ""))
    return items or [("0", "(No IfcSlabType in project)", "")]


def _covering_type_items(self, context):
    items = []
    ifc = tool.Ifc.get()
    if ifc:
        is_elevation = _active_sketch_is_elevation(context)
        for t in sorted(ifc.by_type("IfcCoveringType"), key=lambda e: e.Name or ""):
            if _type_matches_sketch(t, is_elevation):
                items.append((str(t.id()), t.Name or f"#{t.id()}", ""))
    return items or [("0", "(No IfcCoveringType in project)", "")]


def _plate_type_items(self, context):
    items = []
    ifc = tool.Ifc.get()
    if ifc:
        is_elevation = _active_sketch_is_elevation(context)
        for t in sorted(ifc.by_type("IfcPlateType"), key=lambda e: e.Name or ""):
            if _type_matches_sketch(t, is_elevation):
                items.append((str(t.id()), t.Name or f"#{t.id()}", ""))
    return items or [("0", "(No IfcPlateType in project)", "")]


def _slab_instance_items(self, context):
    items = [("0", "-- select slab --", "")]
    ifc = tool.Ifc.get()
    if ifc:
        for s in sorted(ifc.by_type("IfcSlab"), key=lambda e: e.Name or ""):
            items.append((str(s.id()), s.Name or f"#{s.id()}", ""))
    return items


def _wall_instance_items(self, context):
    items = [("0", "-- select wall --", "")]
    ifc = tool.Ifc.get()
    if ifc:
        for w in sorted(ifc.by_type("IfcWall"), key=lambda e: e.Name or ""):
            items.append((str(w.id()), w.Name or f"#{w.id()}", ""))
    return items


def _window_type_items(self, context):
    items = [("0", "-- select window type --", "")]
    ifc = tool.Ifc.get()
    if ifc:
        for t in sorted(ifc.by_type("IfcWindowType"), key=lambda e: e.Name or ""):
            items.append((str(t.id()), t.Name or f"#{t.id()}", ""))
    return items


def _door_type_items(self, context):
    items = [("0", "-- select door type --", "")]
    ifc = tool.Ifc.get()
    if ifc:
        for t in sorted(ifc.by_type("IfcDoorType"), key=lambda e: e.Name or ""):
            items.append((str(t.id()), t.Name or f"#{t.id()}", ""))
    return items


def _beam_type_items(self, context):
    items = []
    ifc = tool.Ifc.get()
    if ifc:
        for t in sorted(ifc.by_type("IfcBeamType"), key=lambda e: e.Name or ""):
            items.append((str(t.id()), t.Name or f"#{t.id()}", ""))
    return items or [("0", "(No IfcBeamType in project)", "")]


def _member_type_items(self, context):
    items = []
    ifc = tool.Ifc.get()
    if ifc:
        for t in sorted(ifc.by_type("IfcMemberType"), key=lambda e: e.Name or ""):
            items.append((str(t.id()), t.Name or f"#{t.id()}", ""))
    return items or [("0", "(No IfcMemberType in project)", "")]


def _footing_type_items(self, context):
    items = []
    ifc = tool.Ifc.get()
    if ifc:
        for t in sorted(ifc.by_type("IfcFootingType"), key=lambda e: e.Name or ""):
            items.append((str(t.id()), t.Name or f"#{t.id()}", ""))
    return items or [("0", "(No IfcFootingType in project)", "")]


def _column_type_items(self, context):
    items = []
    ifc = tool.Ifc.get()
    if ifc:
        for t in sorted(ifc.by_type("IfcColumnType"), key=lambda e: e.Name or ""):
            items.append((str(t.id()), t.Name or f"#{t.id()}", ""))
    return items or [("0", "(No IfcColumnType in project)", "")]


def _pile_type_items(self, context):
    items = []
    ifc = tool.Ifc.get()
    if ifc:
        for t in sorted(ifc.by_type("IfcPileType"), key=lambda e: e.Name or ""):
            items.append((str(t.id()), t.Name or f"#{t.id()}", ""))
    return items or [("0", "(No IfcPileType in project)", "")]


def _entity_label(entity, fallback):
    """Return the entity's user-set CAD Sketcher name or *fallback* if auto-generated."""
    name = getattr(entity, "name", "") or ""
    if not name or name.startswith("Slvs"):
        return fallback
    return name


class _FakeWallLine:
    """Duck-type mock of a CAD Sketcher line, used to pass elevation-derived endpoints
    into _create_or_update_wall without requiring a real sketch entity."""

    class _Pt:
        __slots__ = ("location", "slvs_index")

        def __init__(self, loc):
            self.location = loc
            self.slvs_index = -1

    def __init__(self, p1_loc, p2_loc, guid=""):
        self.p1 = self._Pt(p1_loc)
        self.p2 = self._Pt(p2_loc)
        self.guid = guid
        self.slvs_index = -1


class CADSketcherWallTypeItem(PropertyGroup):
    """Holds the per-wall-line type assignment for the Fetch dialog."""

    label: StringProperty(name="Label")
    slvs_index: IntProperty(name="Sketch Line Index")
    type_id: EnumProperty(name="Wall Type", items=_wall_type_items, options={"SKIP_SAVE"})
    height: FloatProperty(name="Height", default=3.0, min=0.1, unit="LENGTH")


class CADSketcherSlabTypeItem(PropertyGroup):
    """Holds the per-path-group slab type assignment for the Fetch dialog."""

    label: StringProperty(name="Label")
    slvs_index: IntProperty(name="Path Group Key")
    type_id: EnumProperty(name="Slab Type", items=_slab_type_items, options={"SKIP_SAVE"})


class CADSketcherCoveringItem(PropertyGroup):
    """Holds the per-path-group covering type assignment for the Fetch dialog."""

    label: StringProperty(name="Label")
    slvs_index: IntProperty(name="Path Group Key")
    type_id: EnumProperty(name="Covering Type", items=_covering_type_items, options={"SKIP_SAVE"})


class CADSketcherPlateItem(PropertyGroup):
    """Holds the per-path-group plate type assignment for the Fetch dialog."""

    label: StringProperty(name="Label")
    slvs_index: IntProperty(name="Path Group Key")
    type_id: EnumProperty(name="Plate Type", items=_plate_type_items, options={"SKIP_SAVE"})


class CADSketcherOpeningItem(PropertyGroup):
    """Holds the per-opening path-group host-slab assignment for the Fetch dialog."""

    label: StringProperty(name="Label")
    slvs_index: IntProperty(name="Path Group Key")
    host_id: EnumProperty(name="Host Slab", items=_slab_instance_items, options={"SKIP_SAVE"})


class CADSketcherWindowItem(PropertyGroup):
    """Holds the per-window path-group type + host-wall assignment for the Fetch dialog."""

    label: StringProperty(name="Label")
    slvs_index: IntProperty(name="Path Group Key")
    type_id: EnumProperty(name="Window Type", items=_window_type_items, options={"SKIP_SAVE"})
    host_id: EnumProperty(name="Host Wall", items=_wall_instance_items, options={"SKIP_SAVE"})


class CADSketcherDoorItem(PropertyGroup):
    """Holds the per-door path-group type + host-wall assignment for the Fetch dialog."""

    label: StringProperty(name="Label")
    slvs_index: IntProperty(name="Path Group Key")
    type_id: EnumProperty(name="Door Type", items=_door_type_items, options={"SKIP_SAVE"})
    host_id: EnumProperty(name="Host Wall", items=_wall_instance_items, options={"SKIP_SAVE"})


class CADSketcherBeamItem(PropertyGroup):
    """Holds the per-line/path-group type assignment for the Fetch dialog (IfcBeam)."""

    label: StringProperty(name="Label")
    slvs_index: IntProperty(name="Line/Path Group Key")
    type_id: EnumProperty(name="Beam Type", items=_beam_type_items, options={"SKIP_SAVE"})


class CADSketcherMemberItem(PropertyGroup):
    """Holds the per-line/path-group type assignment for the Fetch dialog (IfcMember)."""

    label: StringProperty(name="Label")
    slvs_index: IntProperty(name="Line/Path Group Key")
    type_id: EnumProperty(name="Member Type", items=_member_type_items, options={"SKIP_SAVE"})


class CADSketcherFootingItem(PropertyGroup):
    """Holds the per-line/path-group type assignment for the Fetch dialog (IfcFooting)."""

    label: StringProperty(name="Label")
    slvs_index: IntProperty(name="Line/Path Group Key")
    type_id: EnumProperty(name="Footing Type", items=_footing_type_items, options={"SKIP_SAVE"})


class CADSketcherColumnItem(PropertyGroup):
    """Holds the per-point type assignment for the Fetch dialog (IfcColumn)."""

    label: StringProperty(name="Label")
    slvs_index: IntProperty(name="Point Index")
    type_id: EnumProperty(name="Column Type", items=_column_type_items, options={"SKIP_SAVE"})
    height: FloatProperty(name="Height", default=3.0, min=0.1, unit="LENGTH")


class CADSketcherPileItem(PropertyGroup):
    """Holds the per-point type assignment for the Fetch dialog (IfcPile)."""

    label: StringProperty(name="Label")
    slvs_index: IntProperty(name="Point Index")
    type_id: EnumProperty(name="Pile Type", items=_pile_type_items, options={"SKIP_SAVE"})
    height: FloatProperty(name="Depth", default=5.0, min=0.1, unit="LENGTH")


class FetchCADSketcher(Operator):
    """Create IFC elements from BIM-tagged entities in the active CAD Sketcher sketch"""

    bl_idname = "bim.fetch_cad_sketcher"
    bl_label = "Fetch from CAD Sketcher"
    bl_description = (
        "Read the active CAD Sketcher sketch and create IFC walls / slabs "
        "from lines and sketches tagged with a BIM type"
    )
    bl_options = {"REGISTER", "UNDO"}

    storey_height: FloatProperty(
        name="Default Height",
        description="Initial height for each wall (editable per wall below)",
        default=3.0,
        min=0.1,
        unit="LENGTH",
    )
    wall_type_items: CollectionProperty(type=CADSketcherWallTypeItem)
    wall_run_items: CollectionProperty(type=CADSketcherWallTypeItem)
    wall_elevation_items: CollectionProperty(type=CADSketcherWallTypeItem)
    slab_type_items: CollectionProperty(type=CADSketcherSlabTypeItem)
    opening_items: CollectionProperty(type=CADSketcherOpeningItem)
    window_items: CollectionProperty(type=CADSketcherWindowItem)
    door_items: CollectionProperty(type=CADSketcherDoorItem)
    beam_items: CollectionProperty(type=CADSketcherBeamItem)
    member_items: CollectionProperty(type=CADSketcherMemberItem)
    footing_items: CollectionProperty(type=CADSketcherFootingItem)
    beam_run_items: CollectionProperty(type=CADSketcherBeamItem)
    member_run_items: CollectionProperty(type=CADSketcherMemberItem)
    footing_run_items: CollectionProperty(type=CADSketcherFootingItem)
    column_items: CollectionProperty(type=CADSketcherColumnItem)
    pile_items: CollectionProperty(type=CADSketcherPileItem)
    covering_items: CollectionProperty(type=CADSketcherCoveringItem)
    plate_items: CollectionProperty(type=CADSketcherPlateItem)

    @classmethod
    def poll(cls, context):
        if tool.Ifc.get() is None:
            cls.poll_message_set("No active IFC project.")
            return False
        if not hasattr(context.scene, "sketcher"):
            cls.poll_message_set("CAD Sketcher addon is not installed or enabled.")
            return False
        if context.scene.sketcher.active_sketch is None:
            cls.poll_message_set("No active CAD Sketcher sketch.")
            return False
        return True

    def invoke(self, context, event):
        ifc_file = tool.Ifc.get()
        sketch = context.scene.sketcher.active_sketch
        sketch_index = sketch.slvs_index

        # Populate per-wall type entries
        self.wall_type_items.clear()
        sse = context.scene.sketcher.entities
        wall_lines = _entities_with_ifc_tag(
            sketch, sse, "IfcWall", lambda e: e.sketch_i == sketch_index and hasattr(e, "p1") and hasattr(e, "p2")
        )
        unit_scale_inv = ifcopenshell.util.unit.calculate_unit_scale(ifc_file) if ifc_file else 1.0
        for i, line in enumerate(wall_lines):
            item = self.wall_type_items.add()
            item.slvs_index = line.slvs_index
            p1 = line.p1.location
            p2 = line.p2.location
            length = (p2 - p1).length
            item.label = _entity_label(line, f"Wall {i + 1}  ({length:.2f} m)")
            item.height = self.storey_height  # default; overridden below on reimport
            # Pre-populate with existing type and height if this is a reimport
            line_guid = _entity_guid(sketch, line.slvs_index, "IfcWall")
            if ifc_file and line_guid:
                try:
                    existing = ifc_file.by_guid(line_guid)
                    if existing:
                        existing_type = ifcopenshell.util.element.get_type(existing)
                        if existing_type:
                            item.type_id = str(existing_type.id())
                        body = ifcopenshell.util.representation.get_representation(
                            existing, "Model", "Body", "MODEL_VIEW"
                        )
                        if body:
                            for rep_item in body.Items:
                                if rep_item.is_a("IfcExtrudedAreaSolid"):
                                    item.height = rep_item.Depth * unit_scale_inv
                                    break
                except Exception:
                    pass

        # Populate per-wall-run entries (Plan sketches only)
        self.wall_run_items.clear()
        _wall_run_polys = (
            _group_path_proxies(sketch, sse, "IfcWall", "OPEN") if _sketch_has_role(sketch, "Plan") else []
        )
        for i, poly in enumerate(_wall_run_polys):
            item = self.wall_run_items.add()
            item.slvs_index = poly.slvs_index
            item.label = _entity_label(poly, f"Wall Run {i + 1}  ({poly.segment_count} seg)")
            item.height = self.storey_height
            # Pre-populate from the first segment with an existing IFC element
            for j in range(poly.segment_count):
                seg_idx = int(poly.segment_indices[j])
                if seg_idx == -1:
                    continue
                seg = sse.get(seg_idx)
                if seg is None:
                    continue
                seg_guid = _entity_guid(sketch, seg.slvs_index, "IfcWall")
                if not seg_guid:
                    continue
                try:
                    existing = ifc_file.by_guid(seg_guid)
                    if existing:
                        existing_type = ifcopenshell.util.element.get_type(existing)
                        if existing_type:
                            item.type_id = str(existing_type.id())
                        body = ifcopenshell.util.representation.get_representation(
                            existing, "Model", "Body", "MODEL_VIEW"
                        )
                        if body:
                            for rep_item in body.Items:
                                if rep_item.is_a("IfcExtrudedAreaSolid"):
                                    item.height = rep_item.Depth * unit_scale_inv
                                    break
                except Exception:
                    pass
                break

        # Populate per-wall-elevation-path entries (Elevation sketches only)
        # In an Elevation sketch, IfcWall-tagged path groups are elevation profiles.
        self.wall_elevation_items.clear()
        if _sketch_has_role(sketch, "Elevation"):
            src_wall_guid = FetchCADSketcher._resolve_elevation_wall_guid(sketch, sse)
            _elev_polys = _group_path_proxies(sketch, sse, "IfcWall", "ANY")
            for i, poly in enumerate(_elev_polys):
                item = self.wall_elevation_items.add()
                item.slvs_index = poly.slvs_index
                pts = FetchCADSketcher._polygon_from_path_group(context, poly)
                if pts:
                    zs = [p.z for p in pts]
                    auto_height = max(zs) - min(zs) if len(zs) >= 2 else self.storey_height
                else:
                    auto_height = self.storey_height
                item.label = _entity_label(poly, f"Wall Elevation {i + 1}  ({auto_height:.2f} m tall)")
                item.height = auto_height
                # Prefer the path group's own GUID, then the source wall's GUID
                guid_to_use = _entity_guid(sketch, poly.slvs_index, "IfcWall") or src_wall_guid
                if ifc_file and guid_to_use:
                    try:
                        existing = ifc_file.by_guid(guid_to_use)
                        if existing:
                            existing_type = ifcopenshell.util.element.get_type(existing)
                            if existing_type:
                                item.type_id = str(existing_type.id())
                    except Exception:
                        pass

        # Populate per-slab-path entries
        self.slab_type_items.clear()
        for i, poly in enumerate(self._get_slab_path_groups(context, sketch)):
            item = self.slab_type_items.add()
            item.slvs_index = poly.slvs_index
            item.label = _entity_label(poly, f"Slab {i + 1}")
            poly_guid = _entity_guid(sketch, poly.slvs_index, "IfcSlab")
            if ifc_file and poly_guid:
                try:
                    existing_slab = ifc_file.by_guid(poly_guid)
                    if existing_slab:
                        existing_type = ifcopenshell.util.element.get_type(existing_slab)
                        if existing_type:
                            item.type_id = str(existing_type.id())
                except Exception:
                    pass

        # Populate per-covering-path entries
        self.covering_items.clear()
        for i, poly in enumerate(self._get_covering_path_groups(context, sketch)):
            item = self.covering_items.add()
            item.slvs_index = poly.slvs_index
            item.label = _entity_label(poly, f"Covering {i + 1}")
            poly_guid = _entity_guid(sketch, poly.slvs_index, "IfcCovering")
            if ifc_file and poly_guid:
                try:
                    existing_covering = ifc_file.by_guid(poly_guid)
                    if existing_covering:
                        existing_type = ifcopenshell.util.element.get_type(existing_covering)
                        if existing_type:
                            item.type_id = str(existing_type.id())
                except Exception:
                    pass

        # Populate per-plate-path entries
        self.plate_items.clear()
        for i, poly in enumerate(self._get_plate_path_groups(context, sketch)):
            item = self.plate_items.add()
            item.slvs_index = poly.slvs_index
            item.label = _entity_label(poly, f"Plate {i + 1}")
            poly_guid = _entity_guid(sketch, poly.slvs_index, "IfcPlate")
            if ifc_file and poly_guid:
                try:
                    existing_plate = ifc_file.by_guid(poly_guid)
                    if existing_plate:
                        existing_type = ifcopenshell.util.element.get_type(existing_plate)
                        if existing_type:
                            item.type_id = str(existing_type.id())
                except Exception:
                    pass

        # Populate per-opening-path entries
        self.opening_items.clear()
        for i, poly in enumerate(self._get_opening_path_groups(context, sketch)):
            item = self.opening_items.add()
            item.slvs_index = poly.slvs_index
            item.label = _entity_label(poly, f"Opening {i + 1}")
            poly_guid = _entity_guid(sketch, poly.slvs_index, "IfcOpeningElement")
            if ifc_file and poly_guid:
                try:
                    existing_opening = ifc_file.by_guid(poly_guid)
                    if existing_opening:
                        voids_rels = getattr(existing_opening, "VoidsElements", [])
                        if voids_rels:
                            item.host_id = str(voids_rels[0].RelatingBuildingElement.id())
                except Exception:
                    pass

        # Populate per-window-path entries
        self.window_items.clear()
        for i, poly in enumerate(self._get_window_path_groups(context, sketch)):
            item = self.window_items.add()
            item.slvs_index = poly.slvs_index
            item.label = _entity_label(poly, f"Window {i + 1}")
            poly_guid = _entity_guid(sketch, poly.slvs_index, "IfcWindow")
            if ifc_file and poly_guid:
                try:
                    existing_win = ifc_file.by_guid(poly_guid)
                    if existing_win:
                        existing_type = ifcopenshell.util.element.get_type(existing_win)
                        if existing_type:
                            item.type_id = str(existing_type.id())
                        fills = getattr(existing_win, "FillsVoids", [])
                        if fills:
                            host = fills[0].RelatingOpeningElement
                            voids = getattr(host, "VoidsElements", [])
                            if voids:
                                item.host_id = str(voids[0].RelatingBuildingElement.id())
                except Exception:
                    pass

        # Populate per-door-path entries
        self.door_items.clear()
        for i, poly in enumerate(self._get_door_path_groups(context, sketch)):
            item = self.door_items.add()
            item.slvs_index = poly.slvs_index
            item.label = _entity_label(poly, f"Door {i + 1}")
            poly_guid = _entity_guid(sketch, poly.slvs_index, "IfcDoor")
            if ifc_file and poly_guid:
                try:
                    existing_door = ifc_file.by_guid(poly_guid)
                    if existing_door:
                        existing_type = ifcopenshell.util.element.get_type(existing_door)
                        if existing_type:
                            item.type_id = str(existing_type.id())
                        fills = getattr(existing_door, "FillsVoids", [])
                        if fills:
                            host = fills[0].RelatingOpeningElement
                            voids = getattr(host, "VoidsElements", [])
                            if voids:
                                item.host_id = str(voids[0].RelatingBuildingElement.id())
                except Exception:
                    pass

        def _populate_profile_line_items(collection, ifc_tag, label_prefix):
            """Populate *collection* from sketch lines tagged *ifc_tag*."""
            collection.clear()
            for i, line in enumerate(
                _entities_with_ifc_tag(
                    sketch, sse, ifc_tag, lambda e: e.sketch_i == sketch_index and hasattr(e, "p1") and hasattr(e, "p2")
                )
            ):
                item = collection.add()
                item.slvs_index = line.slvs_index
                p1 = line.p1.location
                p2 = line.p2.location
                length = (p2 - p1).length
                item.label = _entity_label(line, f"{label_prefix} {i + 1}  ({length:.2f} m)")
                line_guid = _entity_guid(sketch, line.slvs_index, ifc_tag)
                if ifc_file and line_guid:
                    try:
                        existing = ifc_file.by_guid(line_guid)
                        if existing:
                            existing_type = ifcopenshell.util.element.get_type(existing)
                            if existing_type:
                                item.type_id = str(existing_type.id())
                    except Exception:
                        pass

        def _populate_profile_run_items(collection, ifc_tag, label_prefix):
            """Populate *collection* from open path groups on *sketch* tagged *ifc_tag*."""
            collection.clear()
            for i, poly in enumerate(_group_path_proxies(sketch, sse, ifc_tag, "OPEN")):
                item = collection.add()
                item.slvs_index = poly.slvs_index
                item.label = _entity_label(poly, f"{label_prefix} Run {i + 1}  ({poly.segment_count} seg)")
                # Pre-populate type from the first segment that has a GUID
                for j in range(poly.segment_count):
                    seg_idx = int(poly.segment_indices[j])
                    if seg_idx == -1:
                        continue
                    seg = sse.get(seg_idx)
                    if seg is None:
                        continue
                    seg_guid = _entity_guid(sketch, seg.slvs_index, ifc_tag)
                    if not seg_guid:
                        continue
                    try:
                        existing = ifc_file.by_guid(seg_guid)
                        if existing:
                            existing_type = ifcopenshell.util.element.get_type(existing)
                            if existing_type:
                                item.type_id = str(existing_type.id())
                    except Exception:
                        pass
                    break

        _populate_profile_line_items(self.beam_items, "IfcBeam", "Beam")
        _populate_profile_line_items(self.member_items, "IfcMember", "Member")
        _populate_profile_line_items(self.footing_items, "IfcFooting", "Footing")
        _populate_profile_run_items(self.beam_run_items, "IfcBeam", "Beam")
        _populate_profile_run_items(self.member_run_items, "IfcMember", "Member")
        _populate_profile_run_items(self.footing_run_items, "IfcFooting", "Footing")

        # Populate per-point entries for vertical elements (IfcColumn, IfcPile)
        def _populate_point_items(collection, ifc_tag, label_prefix, default_height):
            """Populate *collection* from sketch points AND lines tagged *ifc_tag*.

            A line in an elevation sketch defines the column/pile axis directly:
            p1 is the base, the line length is the height.
            """
            collection.clear()
            candidates = _entities_with_ifc_tag(
                sketch,
                sse,
                ifc_tag,
                lambda e: (
                    e.sketch_i == sketch_index
                    and (
                        (hasattr(e, "location") and not hasattr(e, "p1"))  # point entity
                        or (hasattr(e, "p1") and hasattr(e, "p2"))  # line entity
                    )
                ),
            )
            for i, pt_ent in enumerate(candidates):
                item = collection.add()
                item.slvs_index = pt_ent.slvs_index
                is_line = hasattr(pt_ent, "p1")
                if is_line:
                    loc = pt_ent.p1.location
                    item.height = (pt_ent.p2.location - pt_ent.p1.location).length
                else:
                    loc = pt_ent.location
                    item.height = default_height
                item.label = _entity_label(pt_ent, f"{label_prefix} {i + 1}  ({loc.x:.2f}, {loc.y:.2f})")
                pt_guid = _entity_guid(sketch, pt_ent.slvs_index, ifc_tag)
                if ifc_file and pt_guid:
                    try:
                        existing = ifc_file.by_guid(pt_guid)
                        if existing:
                            existing_type = ifcopenshell.util.element.get_type(existing)
                            if existing_type:
                                item.type_id = str(existing_type.id())
                            if not is_line:
                                body = ifcopenshell.util.representation.get_representation(
                                    existing, "Model", "Body", "MODEL_VIEW"
                                )
                                if body:
                                    for rep_item in body.Items:
                                        if rep_item.is_a("IfcExtrudedAreaSolid"):
                                            item.height = rep_item.Depth * unit_scale_inv
                                            break
                    except Exception:
                        pass
                if not is_line:
                    # Override height from a user-drawn line in an orthogonal sketch
                    # (takes priority so the sketch geometry is the single source of truth).
                    orth_sketch, ext_pt = FetchCADSketcher._find_orth_sketch_for_point(sse, pt_ent)
                    if orth_sketch is not None:
                        h = FetchCADSketcher._find_column_height_line(sse, orth_sketch, ext_pt)
                        if h is not None:
                            item.height = h

        _populate_point_items(self.column_items, "IfcColumn", "Column", self.storey_height)
        _populate_point_items(self.pile_items, "IfcPile", "Pile", 5.0)

        return context.window_manager.invoke_props_dialog(self, width=420)

    def draw(self, context):
        layout = self.layout

        if self.wall_type_items:
            layout.separator()
            layout.label(text="Wall Types")
            col = layout.column(align=True)
            for item in self.wall_type_items:
                row = col.row(align=True)
                row.label(text=item.label)
                row.prop(item, "height", text="H")
                row.prop(item, "type_id", text="")

        if self.wall_run_items:
            layout.separator()
            layout.label(text="Wall Runs (plan)")
            col = layout.column(align=True)
            for item in self.wall_run_items:
                row = col.row(align=True)
                row.label(text=item.label)
                row.prop(item, "height", text="H")
                row.prop(item, "type_id", text="")

        if self.wall_elevation_items:
            layout.separator()
            layout.label(text="Wall Elevations")
            col = layout.column(align=True)
            for item in self.wall_elevation_items:
                row = col.row(align=True)
                row.label(text=item.label)
                row.prop(item, "height", text="H")
                row.prop(item, "type_id", text="")

        if self.slab_type_items:
            layout.separator()
            layout.label(text="Slab Types")
            col = layout.column(align=True)
            for item in self.slab_type_items:
                row = col.row(align=True)
                row.label(text=item.label)
                row.prop(item, "type_id", text="")

        if self.covering_items:
            layout.separator()
            layout.label(text="Coverings")
            col = layout.column(align=True)
            for item in self.covering_items:
                row = col.row(align=True)
                row.label(text=item.label)
                row.prop(item, "type_id", text="")

        if self.plate_items:
            layout.separator()
            layout.label(text="Plates")
            col = layout.column(align=True)
            for item in self.plate_items:
                row = col.row(align=True)
                row.label(text=item.label)
                row.prop(item, "type_id", text="")

        if self.opening_items:
            layout.separator()
            layout.label(text="Openings")
            col = layout.column(align=True)
            for item in self.opening_items:
                row = col.row(align=True)
                row.label(text=item.label)
                row.prop(item, "host_id", text="")

        if self.window_items:
            layout.separator()
            layout.label(text="Windows")
            col = layout.column(align=True)
            for item in self.window_items:
                row = col.row(align=True)
                row.label(text=item.label)
                row.prop(item, "type_id", text="")
                row.prop(item, "host_id", text="")

        if self.door_items:
            layout.separator()
            layout.label(text="Doors")
            col = layout.column(align=True)
            for item in self.door_items:
                row = col.row(align=True)
                row.label(text=item.label)
                row.prop(item, "type_id", text="")
                row.prop(item, "host_id", text="")

        if self.beam_items:
            layout.separator()
            layout.label(text="Beams")
            col = layout.column(align=True)
            for item in self.beam_items:
                row = col.row(align=True)
                row.label(text=item.label)
                row.prop(item, "type_id", text="")

        if self.beam_run_items:
            layout.separator()
            layout.label(text="Beam Runs")
            col = layout.column(align=True)
            for item in self.beam_run_items:
                row = col.row(align=True)
                row.label(text=item.label)
                row.prop(item, "type_id", text="")

        if self.member_items:
            layout.separator()
            layout.label(text="Members")
            col = layout.column(align=True)
            for item in self.member_items:
                row = col.row(align=True)
                row.label(text=item.label)
                row.prop(item, "type_id", text="")

        if self.member_run_items:
            layout.separator()
            layout.label(text="Member Runs")
            col = layout.column(align=True)
            for item in self.member_run_items:
                row = col.row(align=True)
                row.label(text=item.label)
                row.prop(item, "type_id", text="")

        if self.footing_items:
            layout.separator()
            layout.label(text="Footings")
            col = layout.column(align=True)
            for item in self.footing_items:
                row = col.row(align=True)
                row.label(text=item.label)
                row.prop(item, "type_id", text="")

        if self.footing_run_items:
            layout.separator()
            layout.label(text="Footing Runs")
            col = layout.column(align=True)
            for item in self.footing_run_items:
                row = col.row(align=True)
                row.label(text=item.label)
                row.prop(item, "type_id", text="")

        if self.column_items:
            layout.separator()
            layout.label(text="Columns")
            col = layout.column(align=True)
            for item in self.column_items:
                row = col.row(align=True)
                row.label(text=item.label)
                row.prop(item, "height", text="H")
                row.prop(item, "type_id", text="")

        if self.pile_items:
            layout.separator()
            layout.label(text="Piles")
            col = layout.column(align=True)
            for item in self.pile_items:
                row = col.row(align=True)
                row.label(text=item.label)
                row.prop(item, "height", text="D")
                row.prop(item, "type_id", text="")

    def execute(self, context):
        ifc_file = tool.Ifc.get()
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
        sketch = context.scene.sketcher.active_sketch

        body_context = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Body", "MODEL_VIEW")
        axis_context = ifcopenshell.util.representation.get_context(ifc_file, "Plan", "Axis", "GRAPH_VIEW")

        if body_context is None:
            self.report(
                {"ERROR"},
                "No Model/Body/MODEL_VIEW context in the IFC project. " "Add geometry contexts first.",
            )
            return {"CANCELLED"}

        # Build slvs_index → IfcWallType and height mappings from dialog selections
        wall_type_map = {}
        wall_height_map = {}
        for item in self.wall_type_items:
            type_id = int(item.type_id)
            if not type_id:
                self.report({"ERROR"}, f"{item.label}: no IfcWallType selected. Add wall types to the project first.")
                return {"CANCELLED"}
            wall_type_map[item.slvs_index] = ifc_file.by_id(type_id)
            wall_height_map[item.slvs_index] = item.height

        sketch_index = sketch.slvs_index
        sse = context.scene.sketcher.entities
        created = 0

        # ── Walls ─────────────────────────────────────────────────────────────
        wall_lines = _entities_with_ifc_tag(
            sketch, sse, "IfcWall", lambda e: e.sketch_i == sketch_index and hasattr(e, "p1") and hasattr(e, "p2")
        )

        wall_pairs = []  # [(sketch_line, blender_obj), ...]
        for line in wall_lines:
            wall_type = wall_type_map.get(line.slvs_index, None)
            wall_height = wall_height_map.get(line.slvs_index, self.storey_height)
            obj = self._create_or_update_wall(
                line, ifc_file, unit_scale, body_context, axis_context, wall_type, wall_height, sketch=sketch
            )
            if obj is not None:
                wall_pairs.append((line, obj))
                created += 1

        # Join walls that share a sketch endpoint
        if len(wall_pairs) > 1:
            try:
                from bonsai.bim.module.model.wall import DumbWallJoiner

                joiner = DumbWallJoiner()
                for i, (line1, obj1) in enumerate(wall_pairs):
                    pts1 = {line1.p1.slvs_index, line1.p2.slvs_index}
                    for line2, obj2 in wall_pairs[i + 1 :]:
                        pts2 = {line2.p1.slvs_index, line2.p2.slvs_index}
                        if pts1 & pts2:
                            joiner.connect(obj2, obj1)
                            joiner.connect(obj1, obj2)
            except Exception:
                pass

        # ── Wall Runs ─────────────────────────────────────────────────────────
        for item in self.wall_run_items:
            type_id = int(item.type_id)
            if not type_id:
                self.report({"ERROR"}, f"{item.label}: no IfcWallType selected. Add wall types to the project first.")
                return {"CANCELLED"}
            run_type = ifc_file.by_id(type_id)
            run_height = item.height
            poly = _resolve_path_proxy(sketch, sse, item.slvs_index, "IfcWall", "OPEN")
            if poly is None:
                continue
            run_pairs = []
            for j in range(poly.segment_count):
                seg_idx = int(poly.segment_indices[j])
                if seg_idx == -1:
                    continue
                seg = sse.get(seg_idx)
                if seg is None or not hasattr(seg, "p1") or not hasattr(seg, "p2"):
                    continue
                # Ensure the segment is in the IfcWall group (inherits from its path group)
                _ensure_entity_in_group(sketch, seg.slvs_index, "IfcWall")
                obj = self._create_or_update_wall(
                    seg, ifc_file, unit_scale, body_context, axis_context, run_type, run_height, sketch=sketch
                )
                if obj is not None:
                    run_pairs.append((seg, obj))
                    created += 1
            if len(run_pairs) > 1:
                try:
                    from bonsai.bim.module.model.wall import DumbWallJoiner

                    joiner = DumbWallJoiner()
                    for i, (seg1, obj1) in enumerate(run_pairs):
                        pts1 = {seg1.p1.slvs_index, seg1.p2.slvs_index}
                        for seg2, obj2 in run_pairs[i + 1 :]:
                            pts2 = {seg2.p1.slvs_index, seg2.p2.slvs_index}
                            if pts1 & pts2:
                                joiner.connect(obj2, obj1)
                                joiner.connect(obj1, obj2)
                except Exception:
                    pass

        # ── Wall Elevations (one IfcWall per IfcWall-tagged path group in an Elevation sketch) ──
        wall_guid_hint = FetchCADSketcher._resolve_elevation_wall_guid(sketch, sse)
        for item in self.wall_elevation_items:
            type_id = int(item.type_id)
            if not type_id:
                self.report({"ERROR"}, f"{item.label}: no IfcWallType selected. Add wall types to the project first.")
                return {"CANCELLED"}
            elev_type = ifc_file.by_id(type_id)
            poly = _resolve_path_proxy(sketch, sse, item.slvs_index, "IfcWall", "ANY")
            if poly is None:
                continue
            obj = self._create_wall_from_elevation_path_group(
                context,
                poly,
                ifc_file,
                unit_scale,
                body_context,
                axis_context,
                elev_type,
                item.height,
                wall_guid_hint=wall_guid_hint,
                sketch=sketch,
            )
            if obj is not None:
                created += 1

        # ── Coverings (one per closed path group with tag == IfcCovering) ─────────
        for item in self.covering_items:
            type_id = int(item.type_id)
            if not type_id:
                self.report(
                    {"ERROR"}, f"{item.label}: no IfcCoveringType selected. Add covering types to the project first."
                )
                return {"CANCELLED"}
            covering_type = ifc_file.by_id(type_id)
            poly = _resolve_path_proxy(sketch, sse, item.slvs_index, "IfcCovering", "CLOSED")
            if poly is None:
                continue
            if self._create_or_update_covering(context, poly, ifc_file, unit_scale, body_context, covering_type):
                created += 1

        # ── Plates (one per closed path group with tag == IfcPlate) ────────────────
        for item in self.plate_items:
            type_id = int(item.type_id)
            if not type_id:
                self.report({"ERROR"}, f"{item.label}: no IfcPlateType selected. Add plate types to the project first.")
                return {"CANCELLED"}
            plate_type = ifc_file.by_id(type_id)
            poly = _resolve_path_proxy(sketch, sse, item.slvs_index, "IfcPlate", "CLOSED")
            if poly is None:
                continue
            if self._create_or_update_plate(context, poly, ifc_file, unit_scale, body_context, plate_type):
                created += 1

        # ── Slabs (one per closed path group with tag == IfcSlab) ──────────────────
        for item in self.slab_type_items:
            type_id = int(item.type_id)
            if not type_id:
                self.report({"ERROR"}, f"{item.label}: no IfcSlabType selected. Add slab types to the project first.")
                return {"CANCELLED"}
            slab_type = ifc_file.by_id(type_id)
            poly = _resolve_path_proxy(sketch, sse, item.slvs_index, "IfcSlab", "CLOSED")
            if poly is None:
                continue
            if self._create_or_update_slab(context, poly, ifc_file, unit_scale, body_context, slab_type):
                created += 1

        # ── Openings (IfcOpeningElement per closed path group tagged IfcOpeningElement) ──
        for item in self.opening_items:
            host_id = int(item.host_id)
            if not host_id:
                continue  # no host selected — skip silently
            host_slab = ifc_file.by_id(host_id)
            if host_slab is None:
                continue  # stale id — skip silently
            poly = _resolve_path_proxy(sketch, sse, item.slvs_index, "IfcOpeningElement", "CLOSED")
            if poly is None:
                continue
            if self._create_or_update_opening(context, poly, ifc_file, unit_scale, host_slab):
                created += 1

        # ── Windows (IfcWindow per rectangle path group tagged IfcWindow) ──
        for item in self.window_items:
            type_id = int(item.type_id)
            host_id = int(item.host_id)
            if not type_id or not host_id:
                continue  # no type or wall selected — skip silently
            window_type = ifc_file.by_id(type_id)
            host_wall = ifc_file.by_id(host_id)
            if host_wall is None:
                continue
            poly = _resolve_path_proxy(sketch, sse, item.slvs_index, "IfcWindow", "CLOSED")
            if poly is None:
                continue
            poly_sketch = next(
                (s for s in context.scene.sketcher.entities.sketches if s.slvs_index == poly.sketch_i), None
            )
            if self._create_or_update_fill_element(
                context, poly, ifc_file, unit_scale, window_type, "IfcWindow", host_wall, sketch=poly_sketch
            ):
                created += 1

        # ── Doors (IfcDoor per rectangle path group tagged IfcDoor) ──
        for item in self.door_items:
            type_id = int(item.type_id)
            host_id = int(item.host_id)
            if not type_id or not host_id:
                continue  # no type or wall selected — skip silently
            door_type = ifc_file.by_id(type_id)
            host_wall = ifc_file.by_id(host_id)
            if host_wall is None:
                continue
            poly = _resolve_path_proxy(sketch, sse, item.slvs_index, "IfcDoor", "CLOSED")
            if poly is None:
                continue
            poly_sketch = next(
                (s for s in context.scene.sketcher.entities.sketches if s.slvs_index == poly.sketch_i), None
            )
            if self._create_or_update_fill_element(
                context, poly, ifc_file, unit_scale, door_type, "IfcDoor", host_wall, sketch=poly_sketch
            ):
                created += 1

        # ── Beams (single lines tagged IfcBeam) ──────────────────────────────
        for item in self.beam_items:
            type_id = int(item.type_id)
            if not type_id:
                self.report({"ERROR"}, f"{item.label}: no IfcBeamType selected. Add beam types to the project first.")
                return {"CANCELLED"}
            beam_type = ifc_file.by_id(type_id)
            ent = sse.get(item.slvs_index)
            if ent is None:
                continue
            if self._create_or_update_profile_element(
                ent, ifc_file, unit_scale, body_context, axis_context, beam_type, sketch=sketch
            ):
                created += 1

        # ── Beam runs (open path groups tagged IfcBeam) ────────────────────────
        for item in self.beam_run_items:
            type_id = int(item.type_id)
            if not type_id:
                self.report({"ERROR"}, f"{item.label}: no IfcBeamType selected. Add beam types to the project first.")
                return {"CANCELLED"}
            beam_type = ifc_file.by_id(type_id)
            poly = _resolve_path_proxy(sketch, sse, item.slvs_index, "IfcBeam", "OPEN")
            if poly is None:
                continue
            for j in range(poly.segment_count):
                seg_idx = int(poly.segment_indices[j])
                if seg_idx == -1:
                    continue
                seg = sse.get(seg_idx)
                if seg is None or not hasattr(seg, "p1") or not hasattr(seg, "p2"):
                    continue
                _ensure_entity_in_group(sketch, seg.slvs_index, "IfcBeam")
                if self._create_or_update_profile_element(
                    seg, ifc_file, unit_scale, body_context, axis_context, beam_type, sketch=sketch
                ):
                    created += 1

        # ── Members (single lines tagged IfcMember) ──────────────────────────
        for item in self.member_items:
            type_id = int(item.type_id)
            if not type_id:
                self.report(
                    {"ERROR"}, f"{item.label}: no IfcMemberType selected. Add member types to the project first."
                )
                return {"CANCELLED"}
            member_type = ifc_file.by_id(type_id)
            ent = sse.get(item.slvs_index)
            if ent is None:
                continue
            if self._create_or_update_profile_element(
                ent, ifc_file, unit_scale, body_context, axis_context, member_type, sketch=sketch
            ):
                created += 1

        # ── Member runs (open path groups tagged IfcMember) ────────────────────
        for item in self.member_run_items:
            type_id = int(item.type_id)
            if not type_id:
                self.report(
                    {"ERROR"}, f"{item.label}: no IfcMemberType selected. Add member types to the project first."
                )
                return {"CANCELLED"}
            member_type = ifc_file.by_id(type_id)
            poly = _resolve_path_proxy(sketch, sse, item.slvs_index, "IfcMember", "OPEN")
            if poly is None:
                continue
            for j in range(poly.segment_count):
                seg_idx = int(poly.segment_indices[j])
                if seg_idx == -1:
                    continue
                seg = sse.get(seg_idx)
                if seg is None or not hasattr(seg, "p1") or not hasattr(seg, "p2"):
                    continue
                _ensure_entity_in_group(sketch, seg.slvs_index, "IfcMember")
                if self._create_or_update_profile_element(
                    seg, ifc_file, unit_scale, body_context, axis_context, member_type, sketch=sketch
                ):
                    created += 1

        # ── Footings (single lines tagged IfcFooting) ────────────────────────
        for item in self.footing_items:
            type_id = int(item.type_id)
            if not type_id:
                self.report(
                    {"ERROR"}, f"{item.label}: no IfcFootingType selected. Add footing types to the project first."
                )
                return {"CANCELLED"}
            footing_type = ifc_file.by_id(type_id)
            ent = sse.get(item.slvs_index)
            if ent is None:
                continue
            if self._create_or_update_profile_element(
                ent, ifc_file, unit_scale, body_context, axis_context, footing_type, sketch=sketch
            ):
                created += 1

        # ── Footing runs (open path groups tagged IfcFooting) ──────────────────
        for item in self.footing_run_items:
            type_id = int(item.type_id)
            if not type_id:
                self.report(
                    {"ERROR"}, f"{item.label}: no IfcFootingType selected. Add footing types to the project first."
                )
                return {"CANCELLED"}
            footing_type = ifc_file.by_id(type_id)
            poly = _resolve_path_proxy(sketch, sse, item.slvs_index, "IfcFooting", "OPEN")
            if poly is None:
                continue
            for j in range(poly.segment_count):
                seg_idx = int(poly.segment_indices[j])
                if seg_idx == -1:
                    continue
                seg = sse.get(seg_idx)
                if seg is None or not hasattr(seg, "p1") or not hasattr(seg, "p2"):
                    continue
                _ensure_entity_in_group(sketch, seg.slvs_index, "IfcFooting")
                if self._create_or_update_profile_element(
                    seg, ifc_file, unit_scale, body_context, axis_context, footing_type, sketch=sketch
                ):
                    created += 1

        # ── Columns (sketch points tagged IfcColumn) ──────────────────────────
        for item in self.column_items:
            type_id = int(item.type_id)
            if not type_id:
                self.report(
                    {"ERROR"}, f"{item.label}: no IfcColumnType selected. Add column types to the project first."
                )
                return {"CANCELLED"}
            column_type = ifc_file.by_id(type_id)
            pt_ent = sse.get(item.slvs_index)
            if pt_ent is None:
                continue
            if self._create_or_update_point_element(
                pt_ent, ifc_file, unit_scale, body_context, axis_context, column_type, item.height, sketch=sketch
            ):
                created += 1
                if not hasattr(pt_ent, "p1"):  # line entities are already the height definition
                    self._ensure_column_height_line(sse, pt_ent, item.height, "IfcColumn")

        # ── Piles (sketch points tagged IfcPile) ──────────────────────────────
        for item in self.pile_items:
            type_id = int(item.type_id)
            if not type_id:
                self.report({"ERROR"}, f"{item.label}: no IfcPileType selected. Add pile types to the project first.")
                return {"CANCELLED"}
            pile_type = ifc_file.by_id(type_id)
            pt_ent = sse.get(item.slvs_index)
            if pt_ent is None:
                continue
            if self._create_or_update_point_element(
                pt_ent, ifc_file, unit_scale, body_context, axis_context, pile_type, item.height, sketch=sketch
            ):
                created += 1
                if not hasattr(pt_ent, "p1"):  # line entities are already the height definition
                    self._ensure_column_height_line(sse, pt_ent, item.height, "IfcPile")

        if created == 0:
            self.report(
                {"WARNING"},
                "Nothing exported. Tag lines/path-groups as IfcWall, IfcSlab, IfcCovering, IfcPlate, IfcOpeningElement, "
                "IfcWindow, IfcDoor, IfcBeam, IfcMember, IfcFooting, or tag points as IfcColumn or IfcPile. "
                "For elevation sketches, set the sketch role to 'Elevation' and tag path groups as IfcWall.",
            )
        else:
            self.report({"INFO"}, f"Created / updated {created} IFC element(s).")

        # ── Propagate changes to sketches that reference this one ──────────────
        self._propagate_to_dependent_sketches(context, {sketch_index}, ifc_file, unit_scale, body_context, axis_context)

        return {"FINISHED"}

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _thickness_from_type(element_type, default):
        """Return total layer thickness (in IFC file units) from a typed element, or *default*."""
        try:
            material = ifcopenshell.util.element.get_material(element_type, should_skip_usage=True)
            if material and material.is_a("IfcMaterialLayerSet"):
                return sum(layer.LayerThickness for layer in material.MaterialLayers)
        except Exception:
            pass
        return default

    # ── Orthogonal-sketch / point helpers ─────────────────────────────────────

    @staticmethod
    def _find_orth_sketch_for_point(sse, pt_ent):
        """Find the orthogonal sketch that has *pt_ent* projected as external geometry.

        Matches by world position (1 mm tolerance).
        Returns (orth_sketch, ext_pt_2d) or (None, None).
        """
        pt_loc = pt_ent.location
        for ent in sse.all:
            if not getattr(ent, "external", False):
                continue
            if hasattr(ent, "p1"):  # skip lines; we want points only
                continue
            if not hasattr(ent, "location"):
                continue
            if (ent.location - pt_loc).length > 0.001:
                continue
            sk_idx = getattr(ent, "sketch_i", -1)
            if sk_idx == -1:
                continue
            orth_sketch = next((s for s in sse.sketches if s.slvs_index == sk_idx), None)
            if orth_sketch is None:
                continue
            return orth_sketch, ent
        return None, None

    @staticmethod
    def _find_column_height_line(sse, orth_sketch, ext_pt):
        """Return the length of a non-external line in *orth_sketch* connected to *ext_pt*.

        Skips the baseline external line (source_ext_line_i).  Returns None when
        no such line exists.
        """
        sk_idx = orth_sketch.slvs_index
        baseline_idx = getattr(orth_sketch, "source_ext_line_i", -1)
        ext_loc = ext_pt.location
        tol = 0.01  # 1 cm
        print(f"[BIM] _find_column_height_line: orth_sketch={sk_idx} baseline_idx={baseline_idx} ext_loc={ext_loc}")
        for ent in sse.all:
            if not (hasattr(ent, "p1") and hasattr(ent, "p2")):
                continue
            if getattr(ent, "sketch_i", -1) != sk_idx:
                continue
            dist_p1 = (ent.p1.location - ext_loc).length
            dist_p2 = (ent.p2.location - ext_loc).length
            print(
                f"[BIM]   line idx={ent.slvs_index} external={getattr(ent,'external',False)} d_p1={dist_p1:.4f} d_p2={dist_p2:.4f}"
            )
            if getattr(ent, "external", False):
                continue
            if ent.slvs_index == baseline_idx:
                continue
            if min(dist_p1, dist_p2) > tol:
                continue
            length = (ent.p2.location - ent.p1.location).length
            print(f"[BIM]   -> height line FOUND length={length:.4f}")
            return length
        print("[BIM]   no height line found")
        return None

    @staticmethod
    def _ensure_column_height_line(sse, pt_ent, height, ifc_tag):
        """Create a vertical height line from *pt_ent*'s external projection in any
        orthogonal sketch, but only when no such line already exists.

        The line runs from the external point at (u, 0) to (u, height) in the
        sketch's local 2-D space.
        """
        orth_sketch, ext_pt = FetchCADSketcher._find_orth_sketch_for_point(sse, pt_ent)
        if orth_sketch is None or ext_pt is None:
            return
        if FetchCADSketcher._find_column_height_line(sse, orth_sketch, ext_pt) is not None:
            return  # line already present
        u, _v = ext_pt.co  # local 2-D coordinates of the external point
        top_pt = sse.add_point_2d((u, height), orth_sketch)
        height_line = sse.add_line_2d(ext_pt, top_pt, orth_sketch)
        _ensure_entity_in_group(orth_sketch, height_line.slvs_index, ifc_tag)

    # ── Wall ──────────────────────────────────────────────────────────────────

    def _create_or_update_wall(
        self, line, ifc_file, unit_scale, body_context, axis_context, wall_type, height=None, sketch=None
    ):
        if height is None:
            height = self.storey_height
        p1 = line.p1.location
        p2 = line.p2.location
        direction = p2 - p1
        length = direction.length
        if length < 1e-6:
            return None

        # Remove existing wall before recreating; save GUID and Name so the new element reuses them
        old_guid = (
            line.guid if isinstance(line, _FakeWallLine) else _entity_guid(sketch, line.slvs_index, "IfcWall")
        ) or None
        old_name = None
        if old_guid:
            try:
                existing = ifc_file.by_guid(old_guid)
                if existing is not None:
                    old_name = getattr(existing, "Name", None)
                    obj = tool.Ifc.get_object(existing)
                    ifcopenshell_api_root.remove_product(ifc_file, product=existing)
                    if obj is not None:
                        data = obj.data
                        bpy.data.objects.remove(obj)
                        if data and data.users == 0:
                            bpy.data.meshes.remove(data)
            except Exception:
                old_guid = None  # GUID was stale; don't reuse it
        if isinstance(line, _FakeWallLine):
            line.guid = ""
        else:
            _set_entity_guid(sketch, line.slvs_index, "IfcWall", "")

        from bonsai.bim.module.model.wall import DumbWallGenerator

        generator = DumbWallGenerator(wall_type)
        generator.file = ifc_file
        generator.unit_scale = unit_scale
        generator.layers = tool.Model.get_material_layer_parameters(wall_type)
        generator.body_context = body_context
        generator.axis_context = axis_context
        generator.container = tool.Root.get_default_container()
        # Do not set container_obj: create_wall() uses it to override the z
        # coordinate with the storey level, but here the z is already encoded
        # in p1_vec / p2_vec (from the sketch geometry).  Spatial containment
        # is handled by the Collector from the object's world position.
        generator.container_obj = None
        generator.x_angle = 0.0
        generator.height = height  # per-wall height (meters)

        # create_wall_from_2_points expects world-space Vector points in meters
        p1_vec = p1.to_3d() if hasattr(p1, "to_3d") else p1.xyz.copy()
        p2_vec = p2.to_3d() if hasattr(p2, "to_3d") else p2.xyz.copy()
        data = generator.create_wall_from_2_points((p1_vec, p2_vec))
        if data is None or data.get("obj") is None:
            return None
        obj = data["obj"]

        # For tilted workplanes DumbWallGenerator places the wall with local Z =
        # global Z.  Override the placement so that local Z = workplane normal,
        # which means the wall grows perpendicular to the sketch surface (correct
        # for ramps, inclined planes, etc.).
        if sketch is not None:
            normal = sketch.wp.normal
            if abs(normal.z) < 0.9999:  # workplane is not horizontal
                local_x_raw = (p2_vec - p1_vec).normalized()
                local_z = normal.copy()
                local_y = local_z.cross(local_x_raw).normalized()
                local_x = local_y.cross(local_z).normalized()  # re-orthogonalise
                mat = mathutils.Matrix(
                    [
                        [local_x.x, local_y.x, local_z.x, p1_vec.x],
                        [local_x.y, local_y.y, local_z.y, p1_vec.y],
                        [local_x.z, local_y.z, local_z.z, p1_vec.z],
                        [0.0, 0.0, 0.0, 1.0],
                    ]
                )
                obj.matrix_world = mat
                bpy.context.view_layer.update()
                bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)

        entity = tool.Ifc.get_entity(obj)
        if old_guid:
            entity.GlobalId = old_guid
        if old_name:
            entity.Name = old_name
            obj.name = old_name
        if isinstance(line, _FakeWallLine):
            line.guid = entity.GlobalId
        else:
            _set_entity_guid(sketch, line.slvs_index, "IfcWall", entity.GlobalId)
        return obj

    # ── Profile elements (IfcBeam, IfcMember, IfcFooting) ─────────────────────

    def _create_or_update_profile_element(
        self, line, ifc_file, unit_scale, body_context, axis_context, element_type, sketch=None
    ):
        """Create or update a single profile-extruded element (IfcBeam, IfcMember, IfcFooting)
        from a sketch line with p1/p2 endpoints.

        The element is extruded along the line axis using the profile from the
        element type's IfcMaterialProfileSet.  Returns the Blender object on
        success or None on failure.
        """
        p1 = line.p1.location
        p2 = line.p2.location
        p1_vec = p1.to_3d() if hasattr(p1, "to_3d") else mathutils.Vector((p1.x, p1.y, p1.z))
        p2_vec = p2.to_3d() if hasattr(p2, "to_3d") else mathutils.Vector((p2.x, p2.y, p2.z))
        direction = p2_vec - p1_vec
        length = direction.length
        if length < 1e-6:
            return None

        # Verify the type has a profile set — if not, skip silently.
        material = ifcopenshell.util.element.get_material(element_type, should_skip_usage=True)
        if material is None or not material.is_a("IfcMaterialProfileSet"):
            return None

        # Derive IFC class tag from element type (e.g. "IfcBeamType" → "IfcBeam")
        _type_name = element_type.is_a()
        ifc_tag = _type_name[:-4] if _type_name.endswith("Type") else _type_name

        # Remove existing element before recreating so GUID / Name are preserved.
        old_guid = _entity_guid(sketch, line.slvs_index, ifc_tag) or None
        old_name = None
        if old_guid:
            try:
                existing = ifc_file.by_guid(old_guid)
                if existing is not None:
                    old_name = getattr(existing, "Name", None)
                    obj = tool.Ifc.get_object(existing)
                    ifcopenshell_api_root.remove_product(ifc_file, product=existing)
                    if obj is not None:
                        data = obj.data
                        bpy.data.objects.remove(obj)
                        if data and data.users == 0:
                            bpy.data.meshes.remove(data)
            except Exception:
                old_guid = None
        _set_entity_guid(sketch, line.slvs_index, ifc_tag, "")

        from bonsai.bim.module.model.profile import DumbProfileGenerator

        generator = DumbProfileGenerator(element_type)
        generator.file = ifc_file
        generator.unit_scale = unit_scale
        generator.body_context = body_context
        generator.axis_context = axis_context
        generator.profile_set = material  # required by create_profile(); not set when bypassing generate()
        generator.container = tool.Root.get_default_container()
        generator.container_obj = tool.Ifc.get_object(generator.container) if generator.container else None
        generator.cardinal_point = 5  # centroid — sensible default for all three types
        generator.insertion_type = "POLYLINE"

        result = generator.create_profile_from_2_points((p1_vec, p2_vec))
        if result is None or result.get("obj") is None:
            return None

        obj = result["obj"]
        entity = tool.Ifc.get_entity(obj)
        if old_guid:
            entity.GlobalId = old_guid
        if old_name:
            entity.Name = old_name
            obj.name = old_name
        _set_entity_guid(sketch, line.slvs_index, ifc_tag, entity.GlobalId)
        return obj

    # ── Point elements (IfcColumn, IfcPile) ───────────────────────────────────

    def _create_or_update_point_element(
        self, point_ent, ifc_file, unit_scale, body_context, axis_context, element_type, height, sketch=None
    ):
        """Create or update a profile element (IfcColumn, IfcPile) from a sketch point or line.

        A point entity produces a vertical element at the point world position.
        A line entity produces an element whose axis follows the line (p1 → p2),
        starting at p1's world position with height = line length.
        Returns True on success, False on failure.
        """
        # Line entities (elevation sketch) use p1 as the base; point entities use .location.
        is_line_ent = hasattr(point_ent, "p1")
        loc = point_ent.p1.location if is_line_ent else point_ent.location
        pt_vec = loc.to_3d() if hasattr(loc, "to_3d") else mathutils.Vector((loc.x, loc.y, loc.z))

        if is_line_ent:
            loc2 = point_ent.p2.location
            p2_vec = loc2.to_3d() if hasattr(loc2, "to_3d") else mathutils.Vector((loc2.x, loc2.y, loc2.z))

        material = ifcopenshell.util.element.get_material(element_type, should_skip_usage=True)
        if material is None or not material.is_a("IfcMaterialProfileSet"):
            return False

        # Derive IFC class tag from element type (e.g. "IfcColumnType" → "IfcColumn")
        _type_name = element_type.is_a()
        ifc_tag = _type_name[:-4] if _type_name.endswith("Type") else _type_name

        old_guid = _entity_guid(sketch, point_ent.slvs_index, ifc_tag) or None
        old_name = None
        if old_guid:
            try:
                existing = ifc_file.by_guid(old_guid)
                if existing is not None:
                    old_name = getattr(existing, "Name", None)
                    obj = tool.Ifc.get_object(existing)
                    ifcopenshell_api_root.remove_product(ifc_file, product=existing)
                    if obj is not None:
                        data = obj.data
                        bpy.data.objects.remove(obj)
                        if data and data.users == 0:
                            bpy.data.meshes.remove(data)
            except Exception:
                old_guid = None
        _set_entity_guid(sketch, point_ent.slvs_index, ifc_tag, "")

        from bonsai.bim.module.model.profile import DumbProfileGenerator

        generator = DumbProfileGenerator(element_type)
        generator.file = ifc_file
        generator.unit_scale = unit_scale
        generator.body_context = body_context
        generator.axis_context = axis_context
        generator.profile_set = material
        generator.container = tool.Root.get_default_container()
        generator.cardinal_point = 5  # centroid
        generator.insertion_type = "CURSOR"
        generator.depth = height
        generator.rotation = 0.0
        generator.location = pt_vec

        if is_line_ent:
            # Do not let the container override the Z position; the line's p1
            # already encodes the correct world-space start height.
            generator.container_obj = None
        else:
            generator.container_obj = tool.Ifc.get_object(generator.container) if generator.container else None

        obj = generator.create_profile()
        if obj is None:
            return False

        # For line entities re-orient the object so its local Z tracks p1 → p2.
        # create_profile() skips rotation for IfcColumnType/IfcPileType, so we
        # apply it manually and sync the IFC placement.
        if is_line_ent:
            direction = p2_vec - pt_vec
            if direction.length > 1e-6:
                direction.normalize()
                rot = direction.to_track_quat("Z", "Y")
                mat = rot.to_matrix().to_4x4()
                mat.translation = pt_vec
                obj.matrix_world = mat
                bpy.context.view_layer.update()
                import bonsai.core.geometry as bonsai_geometry

                bonsai_geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)

        entity = tool.Ifc.get_entity(obj)
        if old_guid:
            entity.GlobalId = old_guid
        if old_name:
            entity.Name = old_name
            obj.name = old_name
        _set_entity_guid(sketch, point_ent.slvs_index, ifc_tag, entity.GlobalId)
        return True

    def _create_wall_from_elevation_path_group(
        self,
        context,
        path_group,
        ifc_file,
        unit_scale,
        body_context,
        axis_context,
        wall_type,
        height_override=None,
        wall_guid_hint="",
        sketch=None,
    ):
        """Create or update a single IfcWall from a path group in an Elevation sketch.

        The path group's bounding box in sketch-space defines the wall geometry:
          • Horizontal (XY) extent → wall length and axis direction
          • Vertical   (Z) extent  → wall height (overridden by *height_override* when set)

        Works for any sketch orientation (east, west, north, south, or diagonal).
        The wall base is placed at the minimum-Z edge of the bounding box.
        The wall axis direction is detected from the XY-plane projection, so the
        approach works for any sketch orientation (X-aligned, Y-aligned, diagonal).

        *wall_guid_hint* is the GUID of the source plan wall (from source_line_i),
        used to link the elevation profile back to the existing IfcWall.
        """
        polygon_pts = self._polygon_from_path_group(context, path_group)
        if len(polygon_pts) < 2:
            return None

        # Use the workplane local frame when available; fall back to global axes
        # (standard X-axis horizontal, global Z vertical) so existing callers
        # without a sketch still work correctly.
        if sketch is not None:
            wp_mat = sketch.wp.matrix_basis
            local_x = wp_mat.col[0].to_3d().normalized()  # wall axis in elevation
            local_y = wp_mat.col[1].to_3d().normalized()  # height direction in elevation
            wp_origin = wp_mat.col[3].to_3d()
        else:
            local_x = mathutils.Vector((1.0, 0.0, 0.0))
            local_y = mathutils.Vector((0.0, 0.0, 1.0))
            wp_origin = polygon_pts[0]

        # Project every vertex into the workplane (u = local_x, v = local_y).
        us = [(p - wp_origin).dot(local_x) for p in polygon_pts]
        vs = [(p - wp_origin).dot(local_y) for p in polygon_pts]
        u_min, u_max = min(us), max(us)
        v_min, v_max = min(vs), max(vs)
        u_range = u_max - u_min  # wall length
        v_range = v_max - v_min  # wall height

        if u_range < 1e-6:
            return None

        # Wall base corners in world space (bottom-left, bottom-right).
        p1_loc = wp_origin + u_min * local_x + v_min * local_y
        p2_loc = wp_origin + u_max * local_x + v_min * local_y
        u_vec_3d = local_x.copy()

        print("[ELEV WALL] polygon_pts:", [f"({p.x:.3f},{p.y:.3f},{p.z:.3f})" for p in polygon_pts])
        print(
            "[ELEV WALL] local_x:", tuple(round(v, 4) for v in local_x), "local_y:", tuple(round(v, 4) for v in local_y)
        )
        print("[ELEV WALL] wp_origin:", tuple(round(v, 4) for v in wp_origin))
        print("[ELEV WALL] us:", [round(u, 4) for u in us], "vs:", [round(v, 4) for v in vs])
        print("[ELEV WALL] u_range:", round(u_range, 4), "v_range:", round(v_range, 4))
        print("[ELEV WALL] p1_loc:", tuple(round(v, 4) for v in p1_loc), "p2_loc:", tuple(round(v, 4) for v in p2_loc))

        # Analyse the elevation profile to detect non-rectangular shapes (e.g. gables).
        # For non-rectangular profiles the wall is created with a 5 % overhead so
        # that an IfcOpeningElement can cleanly subtract the complement region.
        # The same 5 % factor is used on all sides of the complement opening.
        _VOID_MARGIN = 0.001  # 1 mm fixed overshoot — enough for clean booleans
        top_contour, is_non_rect, bottom_left_uv, bottom_right_uv = self._extract_elevation_top_contour(
            polygon_pts, p1_loc, u_vec_3d, v_range, v_vec_3d=local_y
        )
        print("[ELEV WALL] top_contour:", top_contour, "is_non_rect:", is_non_rect)
        print("[ELEV WALL] bottom_left_uv:", bottom_left_uv, "bottom_right_uv:", bottom_right_uv)
        if is_non_rect:
            wall_height = v_range + _VOID_MARGIN
        else:
            wall_height = height_override if height_override is not None else v_range
        print("[ELEV WALL] wall_height:", round(wall_height, 4))

        # Resolve the GUID to use for this wall.
        # Priority 1: the path group already has a GUID (reimport of a previously
        #              elevation-derived wall).
        # Priority 2: GUID from the source plan wall (via sketch.source_line_i).
        # Priority 3: a plan IfcWall line with matching XY endpoints already has
        #              a GUID — reuse it so we update the existing wall instead of
        #              creating a duplicate.
        _sse_elev = context.scene.sketcher.entities
        _path_sketch_elev = next((s for s in _sse_elev.sketches if s.slvs_index == path_group.sketch_i), None)
        guid = _entity_guid(_path_sketch_elev, path_group.slvs_index, "IfcWall") or ""
        if not guid and wall_guid_hint:
            guid = wall_guid_hint
        if not guid:
            tol = 0.001  # 1 mm
            for _sk in _sse_elev.sketches:
                for ent in _entities_with_ifc_tag(
                    _sk, _sse_elev, "IfcWall", lambda e: hasattr(e, "p1") and hasattr(e, "p2")
                ):
                    ent_guid = _entity_guid(_sk, ent.slvs_index, "IfcWall")
                    if not ent_guid:
                        continue
                    ep1 = ent.p1.location
                    ep2 = ent.p2.location
                    ep1_xy = mathutils.Vector((ep1.x, ep1.y))
                    ep2_xy = mathutils.Vector((ep2.x, ep2.y))
                    p1_xy = mathutils.Vector((p1_loc.x, p1_loc.y))
                    p2_xy = mathutils.Vector((p2_loc.x, p2_loc.y))
                    forward = (p1_xy - ep1_xy).length < tol and (p2_xy - ep2_xy).length < tol
                    reverse = (p1_xy - ep2_xy).length < tol and (p2_xy - ep1_xy).length < tol
                    if forward or reverse:
                        guid = ent_guid
                        break
                if guid:
                    break

        mock_line = _FakeWallLine(p1_loc, p2_loc, guid=guid)
        obj = self._create_or_update_wall(
            mock_line, ifc_file, unit_scale, body_context, axis_context, wall_type, wall_height
        )
        if obj is not None and sketch is not None:
            # DumbWallGenerator always extrudes along global Z.  Override the
            # placement so that col[2] (local Z = extrusion direction) maps to
            # local_y (the workplane height direction) and col[1] (thickness
            # direction) maps to the workplane outward normal (n_vec).
            n_vec = local_y.cross(u_vec_3d).normalized()
            elev_mat = mathutils.Matrix(
                [
                    [u_vec_3d.x, n_vec.x, local_y.x, p1_loc.x],
                    [u_vec_3d.y, n_vec.y, local_y.y, p1_loc.y],
                    [u_vec_3d.z, n_vec.z, local_y.z, p1_loc.z],
                    [0.0, 0.0, 0.0, 1.0],
                ]
            )
            obj.matrix_world = elev_mat
            bpy.context.view_layer.update()
            bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)
        if obj is not None:
            _set_entity_guid(_path_sketch_elev, path_group.slvs_index, "IfcWall", mock_line.guid)

            # Back-propagate GUID to the source plan line when it has no GUID yet
            # (i.e. the user drew the elevation path group first without having
            # tagged the original line in the plan sketch).
            sse_bp = context.scene.sketcher.entities
            elev_sketch = next((s for s in sse_bp.sketches if s.slvs_index == path_group.sketch_i), None)
            if elev_sketch is not None:
                src_line_i = getattr(elev_sketch, "source_line_i", -1)
                if src_line_i != -1:
                    src_line = sse_bp.get(src_line_i)
                    if src_line is not None:
                        src_line_sketch_i = getattr(src_line, "sketch_i", -1)
                        src_line_sketch = next((s for s in sse_bp.sketches if s.slvs_index == src_line_sketch_i), None)
                        if src_line_sketch is not None and not _entity_guid(
                            src_line_sketch, src_line.slvs_index, "IfcWall"
                        ):
                            _ensure_entity_in_group(src_line_sketch, src_line.slvs_index, "IfcWall")
                            _set_entity_guid(src_line_sketch, src_line.slvs_index, "IfcWall", mock_line.guid)
            # For non-rectangular elevation profiles (e.g. gable walls), create an
            # IfcOpeningElement that subtracts the complement region — the space
            # between the actual profile and the 10 % taller outer bounding box.
            if is_non_rect and top_contour:
                wall_entity = tool.Ifc.get_entity(obj)
                if wall_entity is not None:
                    self._create_complement_opening_for_wall(
                        context,
                        wall_entity,
                        obj,
                        p1_loc,
                        u_vec_3d,
                        top_contour,
                        wall_height,
                        u_range,
                        wall_type,
                        ifc_file,
                        unit_scale,
                        bottom_left_uv,
                        bottom_right_uv,
                        _VOID_MARGIN,
                        v_up_3d=local_y,
                    )
        return obj

    @staticmethod
    def _extract_elevation_top_contour(polygon_pts, origin, u_vec_3d, z_range, bottom_tol=0.005, v_vec_3d=None):
        """Project the elevation polygon into wall-local (u, v) space and return
        the top contour (the non-bottom path) plus a non-rectangular flag.

        Args:
            polygon_pts: world-space Vector list from _polygon_from_path_group.
            origin:      p1_loc — world start of the wall axis, at min_z.
            u_vec_3d:    unit vector along the wall axis (no Z component).
            z_range:     max_z - min_z of the profile (the natural wall height).
            bottom_tol:  tolerance (metres) for classifying a vertex as on the floor.
            v_vec_3d:    unit vector for the height direction.  When None, global Z
                         is used (backward-compatible default).

        Returns:
            (top_contour, is_non_rect, bottom_left_uv, bottom_right_uv)
        """
        uvs = []
        for pt in polygon_pts:
            rel = pt - origin
            u_c = rel.dot(u_vec_3d)
            v_c = rel.dot(v_vec_3d) if v_vec_3d is not None else rel.z
            uvs.append((u_c, v_c))

        bottom_idxs = [i for i, (u, v) in enumerate(uvs) if abs(v) < bottom_tol]
        if len(bottom_idxs) < 2:
            return [], False, (0.0, 0.0), (0.0, 0.0)

        left_idx = min(bottom_idxs, key=lambda i: uvs[i][0])
        right_idx = max(bottom_idxs, key=lambda i: uvs[i][0])
        n = len(uvs)

        def _traverse(start, end, step):
            path = []
            idx = start
            for _ in range(n):
                idx = (idx + step) % n
                if idx == end:
                    break
                path.append(uvs[idx])
            return path

        fwd = _traverse(left_idx, right_idx, +1)
        bwd = _traverse(left_idx, right_idx, -1)

        def _path_score(path):
            above_floor = [(u, v) for u, v in path if v > bottom_tol]
            return (
                len(above_floor),
                sum(v for _, v in above_floor),
                max((v for _, v in above_floor), default=0.0),
            )

        fwd_score = _path_score(fwd)
        bwd_score = _path_score(bwd)
        chosen_path = fwd if fwd_score >= bwd_score else bwd

        # Strip any residual floor vertices from the chosen path. These can occur
        # when the polygon contains more than two bottom-edge points.
        top_contour = [(u, v) for u, v in chosen_path if v > bottom_tol]

        # Non-rectangular: any top-contour vertex sits below the profile peak, OR
        # the leftmost/rightmost top-contour vertices don't align with the bottom
        # corners (diagonal side edges create left/right voids).
        u_lb_actual = uvs[left_idx][0]
        u_rb_actual = uvs[right_idx][0]
        _side_tol = 0.01  # 1 cm
        is_non_rect = bool(top_contour) and (
            any(abs(v - z_range) > _side_tol for _, v in top_contour)
            or (top_contour and top_contour[0][0] > u_lb_actual + _side_tol)
            or (top_contour and top_contour[-1][0] < u_rb_actual - _side_tol)
        )
        return top_contour, is_non_rect, uvs[left_idx], uvs[right_idx]

    def _create_complement_opening_for_wall(
        self,
        context,
        host_wall_entity,
        host_wall_obj,
        p1_loc,
        u_vec_3d,
        top_contour,
        outer_height,
        wall_length,
        wall_type,
        ifc_file,
        unit_scale,
        bottom_left_uv=(0.0, 0.0),
        bottom_right_uv=None,
        void_margin_factor=0.001,
        v_up_3d=None,
    ):
        """Create an IfcOpeningElement that subtracts the complement region above the
        gable profile from the wall.  Mirrors the slab-opening approach: world-space
        mesh, identity matrix_world, edit_object_placement, update_representation.
        """
        # Height direction: workplane local Y when provided, else global Z.
        v_up = v_up_3d if v_up_3d is not None else mathutils.Vector((0.0, 0.0, 1.0))
        # Wall normal: perpendicular to both the wall axis and the height direction.
        n_vec = v_up.cross(u_vec_3d).normalized()

        # 1 mm overshoot so the opening slightly exceeds both wall faces.
        thickness_ifc = self._thickness_from_type(wall_type, 0.1 / unit_scale)
        full_t = thickness_ifc * unit_scale  # metres

        # Back/front of opening: 1 mm behind and 1 mm past the front wall face.
        back_offset = -void_margin_factor
        depth_m = full_t + 2 * void_margin_factor

        # 1 mm horizontal overshoot so the boolean cuts cleanly past both wall ends.
        # The vertical margin is already baked into outer_height.
        u_over = void_margin_factor

        u_lb, v_lb = bottom_left_uv
        u_rb, v_rb = bottom_right_uv if bottom_right_uv is not None else (wall_length, 0.0)

        # Full complement polygon: bounding-box rectangle minus the actual polygon.
        # Traces the outer bbox boundary then follows the actual top contour back,
        # reaching all the way down to the polygon's bottom corners.  This captures
        # top voids (gable / sloped tops) AND side voids (diagonal left/right edges)
        # in a single connected opening polygon.
        comp_uvs = [
            (-u_over, outer_height),  # bbox top-left
            (wall_length + u_over, outer_height),  # bbox top-right
            (wall_length + u_over, v_rb),  # bbox right, down to polygon's bottom-right
            (u_rb, v_rb),  # actual polygon bottom-right corner
        ]
        for uv in reversed(top_contour):  # top contour from right → left
            comp_uvs.append(uv)
        comp_uvs.append((u_lb, v_lb))  # actual polygon bottom-left corner
        comp_uvs.append((-u_over, v_lb))  # bbox left, down to polygon's bottom-left

        if len(comp_uvs) < 3:
            return False

        # The opening's local frame has:
        #   origin  = p1_loc  (wall start at min_z)
        #   local X = u_vec_3d  (along wall length)
        #   local Y = n_vec     (into wall thickness)
        #   local Z = v_up      (vertical)
        # A world point  p1_loc + u*u_vec + v*v_up + n*n_vec
        # has local coords (u, n, v).
        # Matrix that maps opening-local → world:
        #   col0 = local X = u_vec_3d
        #   col1 = local Y = n_vec
        #   col2 = local Z = v_up
        #   col3 = origin  = p1_loc
        opening_world_mat = mathutils.Matrix(
            (
                (u_vec_3d.x, n_vec.x, v_up.x, p1_loc.x),
                (u_vec_3d.y, n_vec.y, v_up.y, p1_loc.y),
                (u_vec_3d.z, n_vec.z, v_up.z, p1_loc.z),
                (0.0, 0.0, 0.0, 1.0),
            )
        )

        # ── Step 1: create the opening element via Bonsai ──
        bpy.ops.object.select_all(action="DESELECT")
        host_wall_obj.select_set(True)
        context.view_layer.objects.active = host_wall_obj

        root_props = tool.Root.get_root_props()
        root_props.ifc_product = "IfcFeatureElement"
        root_props.ifc_class = "IfcOpeningElement"
        root_props.representation_template = "EXTRUSION"
        root_props.featured_obj = host_wall_obj

        existing_ids = {r.RelatedOpeningElement.id() for r in host_wall_entity.HasOpenings}
        bpy.ops.bim.add_element(
            ifc_product="IfcFeatureElement",
            ifc_class="IfcOpeningElement",
            skip_dialog=True,
        )

        new_rels = [r for r in host_wall_entity.HasOpenings if r.RelatedOpeningElement.id() not in existing_ids]
        if not new_rels:
            return False

        element = new_rels[0].RelatedOpeningElement
        opening_obj = tool.Ifc.get_object(element)

        # ── Step 2: attach a display mesh (viewport only); IFC geometry built below ──
        n_poly = len(comp_uvs)
        verts_back = [(u, back_offset, v) for u, v in comp_uvs]
        verts_front = [(u, back_offset + depth_m, v) for u, v in comp_uvs]
        disp_faces = (
            [list(range(n_poly - 1, -1, -1))]  # back cap
            + [list(range(n_poly, 2 * n_poly))]  # front cap
            + [[i, (i + 1) % n_poly, (i + 1) % n_poly + n_poly, i + n_poly] for i in range(n_poly)]  # side quads
        )
        if opening_obj is None:
            mesh = bpy.data.meshes.new("IfcOpeningElement")
            mesh.from_pydata(verts_back + verts_front, [], disp_faces)
            mesh.update()
            opening_obj = bpy.data.objects.new("IfcOpeningElement", mesh)
            bpy.context.scene.collection.objects.link(opening_obj)
            tool.Ifc.link(element, opening_obj)
            tool.Collector.assign(opening_obj)
        else:
            mesh = opening_obj.data or bpy.data.meshes.new("IfcOpeningElement")
            opening_obj.data = mesh
            mesh.clear_geometry()
            mesh.from_pydata(verts_back + verts_front, [], disp_faces)
            mesh.update()

        opening_obj.matrix_world = opening_world_mat

        # ── Step 3: sync placement and convert mesh to IFC representation ──
        context.view_layer.objects.active = opening_obj
        bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=opening_obj)
        bpy.ops.bim.update_representation(obj=opening_obj.name)

        # ── Step 4: apply the void to the host wall ──
        context.view_layer.objects.active = host_wall_obj
        host_wall_obj.select_set(True)
        bpy.ops.bim.hotkey(hotkey="A_O", description="Toggle openings\n\nHotkey: ALT O")

        return True

    # ── Slab ──────────────────────────────────────────────────────────────────

    @staticmethod
    def _get_slab_path_groups(context, sketch):
        """Return all closed path groups on *sketch* tagged as 'IfcSlab'."""
        if sketch is None:
            return []
        sse = context.scene.sketcher.entities
        return _group_path_proxies(sketch, sse, "IfcSlab", "CLOSED")

    @staticmethod
    def _get_covering_path_groups(context, sketch):
        """Return all closed path groups on *sketch* tagged as 'IfcCovering'."""
        if sketch is None:
            return []
        sse = context.scene.sketcher.entities
        return _group_path_proxies(sketch, sse, "IfcCovering", "CLOSED")

    @staticmethod
    def _get_plate_path_groups(context, sketch):
        """Return all closed path groups on *sketch* tagged as 'IfcPlate'."""
        if sketch is None:
            return []
        sse = context.scene.sketcher.entities
        return _group_path_proxies(sketch, sse, "IfcPlate", "CLOSED")

    @staticmethod
    def _get_opening_path_groups(context, sketch):
        """Return all closed path groups on *sketch* tagged as 'IfcOpeningElement'."""
        if sketch is None:
            return []
        sse = context.scene.sketcher.entities
        return _group_path_proxies(sketch, sse, "IfcOpeningElement", "CLOSED")

    @staticmethod
    def _get_window_path_groups(context, sketch):
        """Return all closed path groups on *sketch* tagged as 'IfcWindow'."""
        if sketch is None:
            return []
        sse = context.scene.sketcher.entities
        return _group_path_proxies(sketch, sse, "IfcWindow", "CLOSED")

    @staticmethod
    def _get_door_path_groups(context, sketch):
        """Return all closed path groups on *sketch* tagged as 'IfcDoor'."""
        if sketch is None:
            return []
        sse = context.scene.sketcher.entities
        return _group_path_proxies(sketch, sse, "IfcDoor", "CLOSED")

    @staticmethod
    def _resolve_elevation_wall_guid(sketch, sse):
        """Return the GUID of the plan IfcWall line that drives this elevation sketch.

        Uses sketch.source_line_i to find the source line, then returns its GUID
        from the sketch group.  Returns '' if the sketch has no source line or
        the line has no GUID.
        """
        src_i = getattr(sketch, "source_line_i", -1)
        if src_i == -1:
            return ""
        line = sse.get(src_i)
        if line is None:
            return ""
        src_sketch_i = getattr(line, "sketch_i", -1)
        src_sketch = next((s for s in sse.sketches if s.slvs_index == src_sketch_i), None)
        return _entity_guid(src_sketch, src_i, "IfcWall")

    @staticmethod
    def _rectangle_dimensions(context, path_group, up_vec=None):
        """If *path_group* is a rectangle path group return (centroid, width, height, pts) in world units, else None.

        width  = length of the edge that runs more perpendicular to *up_vec*
        height = length of the edge that runs more parallel to *up_vec*
        pts    = ordered list of 4 corner Vector positions
        """
        pts = FetchCADSketcher._polygon_from_path_group(context, path_group)
        if len(pts) != 4:
            return None
        # All four corners must be ~90°
        for i in range(4):
            a = pts[i]
            b = pts[(i + 1) % 4]
            c = pts[(i + 2) % 4]
            v1 = (b - a).normalized()
            v2 = (c - b).normalized()
            if abs(v1.dot(v2)) > 0.05:  # cos(~87°); rejects non-right-angle corners
                return None
        centroid = sum(pts, mathutils.Vector()) / 4
        # Determine which edge runs along the height direction.
        edge0 = pts[1] - pts[0]
        edge1 = pts[2] - pts[1]
        up = up_vec if up_vec is not None else mathutils.Vector((0.0, 0.0, 1.0))
        if abs(edge0.dot(up)) > abs(edge1.dot(up)):
            # edge0 runs more along the height direction
            width = edge1.length
            height = edge0.length
        else:
            # edge1 runs more along the height direction
            width = edge0.length
            height = edge1.length
        return centroid, width, height, pts

    def _create_or_update_fill_element(
        self, context, path_group, ifc_file, unit_scale, fill_type, ifc_class, host_wall, sketch=None
    ):
        """Create or update an IfcWindow or IfcDoor from a rectangle path group.

        Width and height are derived relative to *sketch*'s workplane local Y axis
        (height direction); falls back to global Z when *sketch* is None.
        The element is snapped onto *host_wall* at the rectangle centroid via FilledOpeningGenerator.
        """
        if sketch is not None:
            wp_mat = sketch.wp.matrix_basis
            local_x = wp_mat.col[0].to_3d().normalized()
            local_y = wp_mat.col[1].to_3d().normalized()
            wp_origin = wp_mat.col[3].to_3d()
        else:
            local_x = local_y = wp_origin = None
        dims = self._rectangle_dimensions(context, path_group, up_vec=local_y)
        if dims is None:
            self.report({"WARNING"}, f"{ifc_class} path group {path_group} is not a rectangle — skipped.")
            return False
        centroid, width, height, rect_pts = dims

        # DEBUG — path-group info
        print(f"\n[CADSketcher] ── {ifc_class} path-group debug ──")
        print(f"[CADSketcher]   rect_pts : {[tuple(round(v, 4) for v in pt) for pt in rect_pts]}")
        print(f"[CADSketcher]   centroid : {tuple(round(v, 4) for v in centroid)}")
        print(f"[CADSketcher]   width    : {width:.4f} m")
        print(f"[CADSketcher]   height   : {height:.4f} m")
        print(f"[CADSketcher]   unit_scale: {unit_scale}")

        # Choose the fill anchor corner in workplane local XY (u=local_x, v=local_y).
        # Both doors and windows use lower-left.
        # Using extrema keeps the result independent of polygon point order.
        if local_y is not None:
            us = [(p - wp_origin).dot(local_x) for p in rect_pts]
            vs = [(p - wp_origin).dot(local_y) for p in rect_pts]
            u_min = min(us)
            v_min = min(vs)
            fill_origin = wp_origin + u_min * local_x + v_min * local_y
            centroid_u = (centroid - wp_origin).dot(local_x)
            centroid_3d = wp_origin + centroid_u * local_x + v_min * local_y
        else:
            # Fallback when no sketch/workplane is available: prefer lower-left.
            fill_origin = min(rect_pts, key=lambda p: (round(p.z, 6), round(p.x, 6), round(p.y, 6)))
            centroid_3d = (
                centroid.to_3d() if hasattr(centroid, "to_3d") else mathutils.Vector((centroid.x, centroid.y, 0.0))
            )
            centroid_3d.z = fill_origin.z  # keep sill level for the raycast target too

        print(f"[CADSketcher]   fill_origin: {tuple(round(v, 4) for v in fill_origin)}")
        print(f"[CADSketcher]   centroid_3d: {tuple(round(v, 4) for v in centroid_3d)} (sill z)")
        print(f"[CADSketcher]   cursor → fill_origin before add_occurrence")

        # Remove existing element before recreating; save GUID so it is reused
        old_guid = _entity_guid(sketch, path_group.slvs_index, ifc_class) or None
        if old_guid:
            try:
                existing = ifc_file.by_guid(old_guid)
                if existing is not None:
                    obj = tool.Ifc.get_object(existing)
                    ifcopenshell_api_root.remove_product(ifc_file, product=existing)
                    if obj is not None:
                        data = obj.data
                        bpy.data.objects.remove(obj)
                        if data and data.users == 0:
                            bpy.data.meshes.remove(data)
            except Exception:
                old_guid = None
        _set_entity_guid(sketch, path_group.slvs_index, ifc_class, "")

        # Place cursor at the chosen corner so add_occurrence starts there.
        saved_cursor = context.scene.cursor.location.copy()
        context.scene.cursor.location = fill_origin.copy()

        # Snapshot existing elements so we can find the newly created one after the call.
        # add_occurrence skips select_and_activate_single_object for IfcDoorType when any
        # objects are selected, so context.view_layer.objects.active is unreliable.
        existing_ids = {e.id() for e in ifc_file.by_type(ifc_class)}

        # Pass relating_type_id directly as an IntProperty argument — avoids the
        # filtered EnumProperty on model props which only accepts types for the
        # currently active BIM tool.
        bpy.ops.bim.add_occurrence(relating_type_id=fill_type.id())

        context.scene.cursor.location = saved_cursor

        new_elements = [e for e in ifc_file.by_type(ifc_class) if e.id() not in existing_ids]
        if not new_elements:
            self.report({"WARNING"}, f"add_occurrence did not create a {ifc_class} element for {path_group}.")
            return False
        element = new_elements[0]
        obj = tool.Ifc.get_object(element)
        if obj is None:
            self.report({"WARNING"}, f"add_occurrence: {ifc_class} element #{element.id()} has no Blender object.")
            return False

        print(f"[CADSketcher]   add_occurrence → obj='{obj.name}' loc={tuple(round(v,4) for v in obj.location)}")
        print(f"[CADSketcher]   element: {element}")
        ow = getattr(element, "OverallWidth", "n/a")
        oh = getattr(element, "OverallHeight", "n/a")
        print(f"[CADSketcher]   element.OverallWidth={ow}  .OverallHeight={oh} (before our update)")

        # If the type uses the BBIM parametric modifier, regenerate geometry with the
        # correct dimensions.  We bypass bpy.ops entirely so that both window and door
        # follow the exact same pattern regardless of how their operators iterate objects
        # internally (enable_editing_window uses context.active_object; enable_editing_door
        # iterates get_selected_objects() — calling the underlying functions directly avoids
        # that difference and is more reliable for a freshly-created occurrence).
        #
        # Pattern (identical for window and door):
        #   1. Read the type's BBIM pset Data directly so we get defaults for all params.
        #   2. Populate the occurrence's BIM props from those defaults.
        #   3. Override overall_width / overall_height with the sketch-derived values (metres).
        #   4. Call update_*_modifier_representation to regenerate IFC geometry.
        #   5. Write the new data back to the pset.
        context.view_layer.objects.active = obj
        obj.select_set(True)
        bbim_pset_name = f"BBIM_{ifc_class[3:]}"  # "BBIM_Window" or "BBIM_Door"
        element_type = ifcopenshell.util.element.get_type(element)
        bbim_data_json = (
            ifcopenshell.util.element.get_pset(element_type, bbim_pset_name, "Data") if element_type else None
        )
        print(f"[CADSketcher]   bbim_pset_name={bbim_pset_name}  element_type={element_type}")
        print(f"[CADSketcher]   bbim_data_json found: {bbim_data_json is not None}")
        if bbim_data_json:
            from bonsai.bim.module.model.window import update_window_modifier_representation
            from bonsai.bim.module.model.door import update_door_modifier_representation

            bbim_data = json.loads(bbim_data_json)
            bbim_data.update(bbim_data.pop("lining_properties", {}))
            bbim_data.update(bbim_data.pop("panel_properties", {}))
            bbim_data.update(tool.Model.get_constituents_props_data(element))

            if ifc_class == "IfcWindow":
                props = tool.Model.get_window_props(obj)
                props.set_props_kwargs_from_ifc_data(bbim_data)
                props.overall_width = width  # Blender metres
                props.overall_height = height  # Blender metres
                props.is_editing = True
                print(
                    f"[CADSketcher]   → window props set: overall_width={props.overall_width:.4f} overall_height={props.overall_height:.4f}"
                )
                update_window_modifier_representation(context)
                props.is_editing = False
                new_data = props.get_general_kwargs(convert_to_project_units=True)
                new_data["lining_properties"] = props.get_lining_kwargs(convert_to_project_units=True)
                new_data["panel_properties"] = props.get_panel_kwargs(convert_to_project_units=True)
            else:  # IfcDoor
                props = tool.Model.get_door_props(obj)
                props.set_props_kwargs_from_ifc_data(bbim_data)
                props.overall_width = width  # Blender metres
                props.overall_height = height  # Blender metres
                props.is_editing = True
                print(
                    f"[CADSketcher]   → door props set: overall_width={props.overall_width:.4f} overall_height={props.overall_height:.4f}"
                )
                update_door_modifier_representation(obj)
                props.is_editing = False
                new_data = props.get_general_kwargs(convert_to_project_units=True)
                new_data["lining_properties"] = props.get_lining_kwargs(convert_to_project_units=True)
                new_data["panel_properties"] = props.get_panel_kwargs(convert_to_project_units=True)

            print(
                f"[CADSketcher]   new_data overall_width={new_data.get('overall_width')}  overall_height={new_data.get('overall_height')}"
            )
            pset = tool.Pset.get_element_pset(element, bbim_pset_name)
            if pset:
                ifcopenshell.api.pset.edit_pset(
                    ifc_file, pset=pset, properties={"Data": ifc_file.createIfcText(json.dumps(new_data, default=list))}
                )
        else:
            # Non-BBIM type: set IFC attributes directly and let the existing shape stand.
            print(f"[CADSketcher]   No BBIM pset → setting OverallWidth/Height directly on element")
            element.OverallWidth = width / unit_scale
            element.OverallHeight = height / unit_scale

        # Snap the filling onto the host wall using the centroid as target so the opening
        # is centred on the rectangle horizontally, at sill level.
        host_wall_obj = tool.Ifc.get_object(host_wall)
        if host_wall_obj:
            from bonsai.bim.module.model.opening import FilledOpeningGenerator

            print(
                f"[CADSketcher]   FilledOpeningGenerator.generate(obj='{obj.name}', wall='{host_wall_obj.name}', target={tuple(round(v,4) for v in centroid_3d)})"
            )
            err = FilledOpeningGenerator().generate(obj, host_wall_obj, target=centroid_3d)
            print(f"[CADSketcher]   FilledOpeningGenerator result: {err!r}")
            print(f"[CADSketcher]   obj.location after generate: {tuple(round(v,4) for v in obj.location)}")
            if err:
                self.report({"WARNING"}, f"FilledOpeningGenerator: {err}")
        else:
            self.report({"WARNING"}, f"Host wall Blender object not found for {host_wall} — fill not linked to wall.")

        # Compute inward wall normal and wall thickness when workplane frame is known.
        # n_vec_fill = -workplane_normal = direction from exterior face into the wall.
        n_vec_fill = None
        wall_thickness_m = 0.0
        if local_y is not None and local_x is not None:
            n_vec_fill = local_y.cross(local_x)
            host_wall_type = ifcopenshell.util.element.get_type(host_wall)
            if host_wall_type is not None:
                wall_thickness_m = self._thickness_from_type(host_wall_type, 0.0) * unit_scale

        # Final placement for both windows and doors:
        #   Keep origin exactly at fill_origin (no wall-thickness offset).
        obj.location = fill_origin.copy()

        # FilledOpeningGenerator may auto-rotate based on wall side-axis proximity.
        # For CAD Sketcher windows and doors we want a deterministic transform
        # from sketch axes:
        #   local X = sketch local_x (opening width)
        #   local Z = sketch local_y (opening height)
        #   local Y = local Z x local X (depth)
        if ifc_class in {"IfcWindow", "IfcDoor"} and local_x is not None and local_y is not None:
            x_axis = local_x.normalized()
            z_axis = local_y.normalized()
            y_axis = z_axis.cross(x_axis).normalized()
            obj.matrix_world = mathutils.Matrix(
                (
                    (x_axis.x, y_axis.x, z_axis.x, fill_origin.x),
                    (x_axis.y, y_axis.y, z_axis.y, fill_origin.y),
                    (x_axis.z, y_axis.z, z_axis.z, fill_origin.z),
                    (0.0, 0.0, 0.0, 1.0),
                )
            )

        print(f"[CADSketcher]   obj.location forced → {tuple(round(v,4) for v in obj.location)}")

        # Sync the IFC opening placement with the new object location.
        # Equivalent to the "S G" / Recalculate Element Geometry hotkey.
        obj.select_set(True)
        context.view_layer.objects.active = obj
        bpy.ops.bim.recalculate_fill()

        ow2 = getattr(element, "OverallWidth", "n/a")
        oh2 = getattr(element, "OverallHeight", "n/a")
        print(f"[CADSketcher]   element.OverallWidth={ow2}  .OverallHeight={oh2} (after all updates)")
        print(
            f"[CADSketcher]   obj.matrix_world.translation = {tuple(round(v,4) for v in obj.matrix_world.translation)}"
        )
        print(f"[CADSketcher] ── end debug ──\n")

        # Preserve GUID across reimports
        if old_guid:
            element.GlobalId = old_guid
        _set_entity_guid(sketch, path_group.slvs_index, ifc_class, element.GlobalId)

        return True

    @staticmethod
    def _polygon_from_path_group(context, path_group):
        """Return an ordered list of world-space Vector locations forming the path-group polygon."""
        sse = context.scene.sketcher.entities
        segments = []
        for i in range(path_group.segment_count):
            idx = int(path_group.segment_indices[i])
            if idx == -1:
                continue
            seg = sse.get(idx)
            if seg is not None and hasattr(seg, "p1") and hasattr(seg, "p2"):
                segments.append(seg)
        if len(segments) < 2:
            return []

        point_locs = {}
        point_to_segments = {}
        for seg in segments:
            p1_idx = seg.p1.slvs_index
            p2_idx = seg.p2.slvs_index
            point_locs[p1_idx] = seg.p1.location.copy()
            point_locs[p2_idx] = seg.p2.location.copy()
            point_to_segments.setdefault(p1_idx, []).append(seg)
            point_to_segments.setdefault(p2_idx, []).append(seg)

        def _point_sort_key(point_idx):
            loc = point_locs[point_idx]
            return (round(loc.x, 6), round(loc.y, 6), round(loc.z, 6), point_idx)

        endpoints = [point_idx for point_idx, attached in point_to_segments.items() if len(attached) == 1]
        start_point_idx = min(endpoints, key=_point_sort_key) if endpoints else min(point_locs, key=_point_sort_key)

        pts = [point_locs[start_point_idx].copy()]
        ordered_point_indices = [start_point_idx]
        visited_segment_ids = set()
        current_point_idx = start_point_idx

        for _ in range(len(segments)):
            candidates = [
                seg for seg in point_to_segments[current_point_idx] if seg.slvs_index not in visited_segment_ids
            ]
            if not candidates:
                break

            if len(candidates) == 1:
                next_seg = candidates[0]
            else:
                next_seg = min(
                    candidates,
                    key=lambda seg: _point_sort_key(
                        seg.p2.slvs_index if seg.p1.slvs_index == current_point_idx else seg.p1.slvs_index
                    ),
                )

            visited_segment_ids.add(next_seg.slvs_index)
            next_point_idx = (
                next_seg.p2.slvs_index if next_seg.p1.slvs_index == current_point_idx else next_seg.p1.slvs_index
            )

            if next_point_idx == start_point_idx and len(visited_segment_ids) == len(segments):
                break

            ordered_point_indices.append(next_point_idx)
            pts.append(point_locs[next_point_idx].copy())
            current_point_idx = next_point_idx

        return pts

    @staticmethod
    def _path_group_uses_external_geometry(context, path_group):
        """Return True if any segment of *path_group* is external geometry.

        CAD Sketcher marks externally-imported geometry with external=True.
        When a slab loop includes such a segment, the working plane is the slab
        bottom face and the slab grows upward from it.
        """
        sse = context.scene.sketcher.entities
        for i in range(path_group.segment_count):
            idx = int(path_group.segment_indices[i])
            if idx == -1:
                continue
            seg = sse.get(idx)
            if seg is None:
                continue
            if getattr(seg, "external", False):
                return True
        return False

    def _create_layered_element_from_elevation_path_group(
        self, polygon_pts, poly_sketch, element_type, ifc_file, unit_scale, body_context, offset_by_thickness=False
    ):
        """Create a layered IFC element (Covering / Slab / Plate) in any workplane.

        The profile is always built in the workplane's local XY and the
        extrusion direction is determined from the workplane normal:

        * Plan  (normal mostly vertical, |normal.z| >= 0.3): extrude in +normal
          (grows away from the surface — upward for horizontal slabs, outward
          for ramps).
        * Elevation  (normal mostly horizontal, |normal.z| < 0.3): extrude in
          -normal (grows into the surface — inward for wall coverings).

        Returns the Blender object, or None if the type has no usable thickness.
        """
        import bonsai.core.root

        wp_mat = poly_sketch.wp.matrix_basis
        local_x = wp_mat.col[0].to_3d().normalized()
        local_y = wp_mat.col[1].to_3d().normalized()
        normal = poly_sketch.wp.normal

        # Choose extrusion direction based on how close the workplane is to vertical.
        # Threshold 0.17 ≈ within ~10° of truly vertical (e.g. walls, elevation views).
        # Steep roofs/ramps still fall through to the plan path (+normal).
        is_vertical_plane = abs(normal.z) < 0.17
        local_z = -normal if is_vertical_plane else normal

        origin = polygon_pts[0]

        print(
            "[HELPER] sketch roles =",
            poly_sketch.tag_values() if hasattr(poly_sketch, "tag_values") else [getattr(poly_sketch, "tag", "<none>")],
            "  is_vertical_plane =",
            is_vertical_plane,
        )
        print(
            "[HELPER] normal =",
            [round(v, 4) for v in normal],
            "  local_z (extrusion dir) =",
            [round(v, 4) for v in local_z],
        )
        print("[HELPER] origin =", [round(v, 4) for v in origin])
        print("[HELPER] polygon_pts (world) =", [[round(v, 4) for v in p] for p in polygon_pts])

        # 2D profile in element-local XY (u, v relative to origin)
        profile_2d = []
        for pt in polygon_pts:
            rel = pt - origin
            profile_2d.append((rel.dot(local_x), rel.dot(local_y), 0.0))
        if profile_2d[0] != profile_2d[-1]:
            profile_2d.append(profile_2d[0])
        print("[HELPER] profile_2d (local) =", [(round(u, 4), round(v, 4), 0) for u, v, _ in profile_2d])

        # Placement matrix: columns = [local_x, local_y, local_z, origin]
        mat = mathutils.Matrix(
            [
                [local_x.x, local_y.x, local_z.x, origin.x],
                [local_x.y, local_y.y, local_z.y, origin.y],
                [local_x.z, local_y.z, local_z.z, origin.z],
                [0.0, 0.0, 0.0, 1.0],
            ]
        )
        print("[HELPER] placement mat =", [[round(v, 4) for v in row] for row in mat])

        thickness_ifc = self._thickness_from_type(element_type, 0.0)
        depth_m = thickness_ifc * unit_scale  # IFC units → metres
        print("[HELPER] depth_m =", depth_m, "  unit_scale =", unit_scale)
        if depth_m == 0.0:
            return None

        # For slabs the workplane represents the top face; shift the placement
        # origin down by the thickness so the element grows below the workplane.
        if offset_by_thickness:
            shifted_origin = origin - depth_m * local_z
            mat[0][3] = shifted_origin.x
            mat[1][3] = shifted_origin.y
            mat[2][3] = shifted_origin.z
            print("[HELPER] shifted_origin (offset by depth) =", [round(v, 4) for v in shifted_origin])

        ifc_classes = ifcopenshell.util.type.get_applicable_entities(element_type.is_a(), ifc_file.schema)
        ifc_class = next(c for c in ifc_classes if "StandardCase" not in c)

        mesh = bpy.data.meshes.new("Dummy")
        obj = bpy.data.objects.new(tool.Model.generate_occurrence_name(element_type, ifc_class), mesh)

        # Set placement BEFORE any IFC geometry operations.
        obj.matrix_world = mat
        bpy.context.view_layer.update()
        print(
            "[HELPER] obj.matrix_world after set (pre-assign_class) =",
            [[round(v, 4) for v in row] for row in obj.matrix_world],
        )

        element = bonsai.core.root.assign_class(
            tool.Ifc,
            tool.Collector,
            tool.Root,
            obj=obj,
            ifc_class=ifc_class,
            should_add_representation=False,
        )
        ifcopenshell.api.type.assign_type(ifc_file, related_objects=[element], relating_type=element_type)

        print(
            "[HELPER] obj.matrix_world before edit_object_placement =",
            [[round(v, 4) for v in row] for row in obj.matrix_world],
        )
        bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)
        print("[HELPER] IFC placement =", element.ObjectPlacement)

        representation = ifcopenshell.api.geometry.add_slab_representation(
            ifc_file,
            context=body_context,
            depth=depth_m,
            x_angle=0.0,
            polyline=profile_2d,
        )
        ifcopenshell.api.geometry.assign_representation(ifc_file, product=element, representation=representation)

        bonsai.core.geometry.switch_representation(
            tool.Ifc,
            tool.Geometry,
            obj=obj,
            representation=representation,
        )
        print(
            "[HELPER] obj.matrix_world AFTER switch_representation =",
            [[round(v, 4) for v in row] for row in obj.matrix_world],
        )

        footprint_context = ifcopenshell.util.representation.get_context(ifc_file, "Plan", "FootPrint", "SKETCH_VIEW")
        if footprint_context:
            extrusion = tool.Model.get_extrusion(representation)
            if extrusion and extrusion.SweptArea.is_a("IfcArbitraryClosedProfileDef"):
                curves = [extrusion.SweptArea.OuterCurve]
                if extrusion.SweptArea.is_a("IfcArbitraryProfileDefWithVoids"):
                    curves.extend(extrusion.SweptArea.InnerCurves)
                fp_rep = ifcopenshell.api.geometry.add_footprint_representation(
                    ifc_file, context=footprint_context, curves=curves
                )
                ifcopenshell.api.geometry.assign_representation(ifc_file, product=element, representation=fp_rep)

        pset = ifcopenshell.api.pset.add_pset(ifc_file, product=element, name="EPset_Parametric")
        ifcopenshell.api.pset.edit_pset(ifc_file, pset=pset, properties={"Engine": "Bonsai.DumbLayer3"})
        mat_usage = ifcopenshell.util.element.get_material(element)
        if mat_usage is not None and mat_usage.is_a("IfcMaterialLayerSetUsage"):
            mat_usage.LayerSetDirection = "AXIS3"

        tool.Blender.select_object(obj)
        return obj

    def _create_or_update_slab(self, context, path_group, ifc_file, unit_scale, body_context, slab_type):
        polygon_pts = self._polygon_from_path_group(context, path_group)
        if len(polygon_pts) < 3:
            self.report({"WARNING"}, f"Path group {path_group} has fewer than 3 vertices for a slab.")
            return False

        sse = context.scene.sketcher.entities
        poly_sketch = next((s for s in sse.sketches if s.slvs_index == path_group.sketch_i), None)

        # Remove existing slab before recreating; save GUID so the new element reuses it
        old_guid = _entity_guid(poly_sketch, path_group.slvs_index, "IfcSlab") or None
        if old_guid:
            try:
                existing = ifc_file.by_guid(old_guid)
                if existing is not None:
                    obj = tool.Ifc.get_object(existing)
                    ifcopenshell_api_root.remove_product(ifc_file, product=existing)
                    if obj is not None:
                        data = obj.data
                        bpy.data.objects.remove(obj)
                        if data and data.users == 0:
                            bpy.data.meshes.remove(data)
            except Exception:
                old_guid = None  # GUID was stale; don't reuse it
        _set_entity_guid(poly_sketch, path_group.slvs_index, "IfcSlab", "")

        origin = polygon_pts[0]
        grows_up_from_workplane = self._path_group_uses_external_geometry(context, path_group)

        # ── Typed path ────────────────────────────────────────────────────────
        if slab_type is not None:
            print(
                "[SLAB] poly_sketch =",
                poly_sketch,
                "  roles =",
                (
                    (
                        poly_sketch.tag_values()
                        if (poly_sketch and hasattr(poly_sketch, "tag_values"))
                        else [getattr(poly_sketch, "tag", "<none>")]
                    )
                    if poly_sketch
                    else "N/A"
                ),
            )

            if poly_sketch is not None:
                obj = self._create_layered_element_from_elevation_path_group(
                    polygon_pts,
                    poly_sketch,
                    slab_type,
                    ifc_file,
                    unit_scale,
                    body_context,
                    offset_by_thickness=True,
                )
                if obj is None:
                    self.report({"ERROR"}, "Slab type has no material layer set with a non-zero thickness.")
                    return False
            else:
                from bonsai.bim.module.model.slab import DumbSlabGenerator

                generator = DumbSlabGenerator(slab_type)
                generator.file = ifc_file
                generator.unit_scale = unit_scale
                generator.body_context = body_context
                generator.footprint_context = ifcopenshell.util.representation.get_context(
                    ifc_file, "Plan", "FootPrint", "SKETCH_VIEW"
                )
                generator.x_angle = 0.0
                generator.container = tool.Root.get_default_container()
                generator.container_obj = tool.Ifc.get_object(generator.container) if generator.container else None
                generator.depth = self._thickness_from_type(slab_type, 0.0) * unit_scale
                generator.location = origin.copy()
                generator.polyline = [(pt.x - origin.x, pt.y - origin.y, 0.0) for pt in polygon_pts]
                if generator.polyline[0] != generator.polyline[-1]:
                    generator.polyline.append(generator.polyline[0])
                obj = generator.create_slab()
                if obj is None:
                    self.report({"ERROR"}, "Slab type has no material layer set with a non-zero thickness.")
                    return False
                obj.matrix_world.translation = origin.copy()
                if not grows_up_from_workplane:
                    obj.matrix_world.translation.z -= generator.depth
                bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)

            entity = tool.Ifc.get_entity(obj)
            if old_guid:
                entity.GlobalId = old_guid
            _set_entity_guid(poly_sketch, path_group.slvs_index, "IfcSlab", entity.GlobalId)
            return True

    # ── Covering ──────────────────────────────────────────────────────────────

    def _create_or_update_covering(self, context, path_group, ifc_file, unit_scale, body_context, covering_type):
        """Create or update an IfcCovering from a closed path group.

        Plan sketches:      footprint in world XY, extrudes upward (+Z).
        Elevation sketches: profile in the sketch plane, extrudes along -normal.
        """
        sse = context.scene.sketcher.entities
        polygon_pts = self._polygon_from_path_group(context, path_group)
        if len(polygon_pts) < 3:
            self.report({"WARNING"}, f"Path group {path_group} has fewer than 3 vertices for a covering.")
            return False

        poly_sketch = next((s for s in sse.sketches if s.slvs_index == path_group.sketch_i), None)

        old_guid = _entity_guid(poly_sketch, path_group.slvs_index, "IfcCovering") or None
        if old_guid:
            try:
                existing = ifc_file.by_guid(old_guid)
                if existing is not None:
                    obj = tool.Ifc.get_object(existing)
                    ifcopenshell_api_root.remove_product(ifc_file, product=existing)
                    if obj is not None:
                        data = obj.data
                        bpy.data.objects.remove(obj)
                        if data and data.users == 0:
                            bpy.data.meshes.remove(data)
            except Exception:
                old_guid = None
        _set_entity_guid(poly_sketch, path_group.slvs_index, "IfcCovering", "")

        if poly_sketch is not None:
            obj = self._create_layered_element_from_elevation_path_group(
                polygon_pts, poly_sketch, covering_type, ifc_file, unit_scale, body_context
            )
            if obj is None:
                self.report({"ERROR"}, "Covering type has no material layer set with a non-zero thickness.")
                return False
        else:
            origin = polygon_pts[0]
            from bonsai.bim.module.model.slab import DumbSlabGenerator

            generator = DumbSlabGenerator(covering_type)
            generator.file = ifc_file
            generator.unit_scale = unit_scale
            generator.body_context = body_context
            generator.footprint_context = ifcopenshell.util.representation.get_context(
                ifc_file, "Plan", "FootPrint", "SKETCH_VIEW"
            )
            generator.x_angle = 0.0
            generator.container = tool.Root.get_default_container()
            generator.container_obj = None  # prevent z-snap to storey level
            generator.depth = self._thickness_from_type(covering_type, 0.0) * unit_scale
            generator.location = origin.copy()
            generator.polyline = [(pt.x - origin.x, pt.y - origin.y, 0.0) for pt in polygon_pts]
            if generator.polyline[0] != generator.polyline[-1]:
                generator.polyline.append(generator.polyline[0])
            obj = generator.create_slab()
            if obj is None:
                self.report({"ERROR"}, "Covering type has no material layer set with a non-zero thickness.")
                return False
            obj.matrix_world.translation = origin.copy()
            bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)

        entity = tool.Ifc.get_entity(obj)
        if old_guid:
            entity.GlobalId = old_guid
        _set_entity_guid(poly_sketch, path_group.slvs_index, "IfcCovering", entity.GlobalId)
        return True

    # ── Plate ──────────────────────────────────────────────────────────────────

    def _create_or_update_plate(self, context, path_group, ifc_file, unit_scale, body_context, plate_type):
        """Create or update an IfcPlate from a closed path group.

        Plan sketches:      footprint in world XY, extrudes upward (+Z).
        Elevation sketches: profile in the sketch plane, extrudes along -normal.
        """
        sse = context.scene.sketcher.entities
        polygon_pts = self._polygon_from_path_group(context, path_group)
        if len(polygon_pts) < 3:
            self.report({"WARNING"}, f"Path group {path_group} has fewer than 3 vertices for a plate.")
            return False

        poly_sketch = next((s for s in sse.sketches if s.slvs_index == path_group.sketch_i), None)

        old_guid = _entity_guid(poly_sketch, path_group.slvs_index, "IfcPlate") or None
        if old_guid:
            try:
                existing = ifc_file.by_guid(old_guid)
                if existing is not None:
                    obj = tool.Ifc.get_object(existing)
                    ifcopenshell_api_root.remove_product(ifc_file, product=existing)
                    if obj is not None:
                        data = obj.data
                        bpy.data.objects.remove(obj)
                        if data and data.users == 0:
                            bpy.data.meshes.remove(data)
            except Exception:
                old_guid = None
        _set_entity_guid(poly_sketch, path_group.slvs_index, "IfcPlate", "")

        is_elevation = poly_sketch is not None and _sketch_has_role(poly_sketch, "Elevation")
        # Also treat any non-horizontal workplane as needing the elevation path.
        if poly_sketch is not None and not is_elevation:
            n = poly_sketch.wp.normal
            is_elevation = abs(n.dot(mathutils.Vector((0.0, 0.0, 1.0)))) < 0.9999

        if is_elevation:
            obj = self._create_layered_element_from_elevation_path_group(
                polygon_pts, poly_sketch, plate_type, ifc_file, unit_scale, body_context
            )
            if obj is None:
                self.report({"ERROR"}, "Plate type has no material layer set with a non-zero thickness.")
                return False
        else:
            origin = polygon_pts[0]
            from bonsai.bim.module.model.slab import DumbSlabGenerator

            generator = DumbSlabGenerator(plate_type)
            generator.file = ifc_file
            generator.unit_scale = unit_scale
            generator.body_context = body_context
            generator.footprint_context = ifcopenshell.util.representation.get_context(
                ifc_file, "Plan", "FootPrint", "SKETCH_VIEW"
            )
            generator.x_angle = 0.0
            generator.container = tool.Root.get_default_container()
            generator.container_obj = None  # prevent z-snap to storey level
            generator.depth = self._thickness_from_type(plate_type, 0.0) * unit_scale
            origin = polygon_pts[0]
            generator.location = origin.copy()
            generator.polyline = [(pt.x - origin.x, pt.y - origin.y, 0.0) for pt in polygon_pts]
            if generator.polyline[0] != generator.polyline[-1]:
                generator.polyline.append(generator.polyline[0])
            obj = generator.create_slab()
            if obj is None:
                self.report({"ERROR"}, "Plate type has no material layer set with a non-zero thickness.")
                return False
            obj.matrix_world.translation = origin.copy()
            bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)

        entity = tool.Ifc.get_entity(obj)
        if old_guid:
            entity.GlobalId = old_guid
        _set_entity_guid(poly_sketch, path_group.slvs_index, "IfcPlate", entity.GlobalId)
        return True

    # ── Opening ───────────────────────────────────────────────────────────────────────

    def _create_or_update_opening(self, context, path_group, ifc_file, unit_scale, host_slab):
        """Create or update an IfcOpeningElement from a closed path group and void the host slab."""
        polygon_pts = self._polygon_from_path_group(context, path_group)
        if len(polygon_pts) < 3:
            self.report({"WARNING"}, f"Opening path group {path_group} has fewer than 3 vertices.")
            return False

        _sse_op = context.scene.sketcher.entities
        _poly_sketch_op = next((s for s in _sse_op.sketches if s.slvs_index == path_group.sketch_i), None)

        # Remove existing opening before recreating; save GUID so the new element reuses it
        old_guid = _entity_guid(_poly_sketch_op, path_group.slvs_index, "IfcOpeningElement") or None
        if old_guid:
            try:
                existing = ifc_file.by_guid(old_guid)
                if existing is not None:
                    obj = tool.Ifc.get_object(existing)
                    ifcopenshell_api_root.remove_product(ifc_file, product=existing)
                    if obj is not None:
                        data = obj.data
                        bpy.data.objects.remove(obj)
                        if data and data.users == 0:
                            bpy.data.meshes.remove(data)
            except Exception:
                old_guid = None
        _set_entity_guid(_poly_sketch_op, path_group.slvs_index, "IfcOpeningElement", "")

        # ── Step 1: activate the host slab so add_element picks it up as featured_obj ──
        host_obj = tool.Ifc.get_object(host_slab)
        if not host_obj:
            return False

        bpy.ops.object.select_all(action="DESELECT")
        host_obj.select_set(True)
        context.view_layer.objects.active = host_obj

        # ── Step 2: pre-set root props so add_element._invoke finds featured_obj ──
        # _invoke checks props.ifc_product BEFORE applying self.ifc_product, so if
        # props.ifc_product was set to something else in a prior operation, featured_obj
        # never gets populated and _execute bails with "A featured element must be nominated."
        root_props = tool.Root.get_root_props()
        root_props.ifc_product = "IfcFeatureElement"
        root_props.ifc_class = "IfcOpeningElement"
        root_props.representation_template = "EXTRUSION"
        root_props.featured_obj = host_obj

        # ── Step 3: snapshot existing openings so we can identify the new one ──
        existing_opening_ids = {r.RelatedOpeningElement.id() for r in host_slab.HasOpenings}

        # ── Step 4: let Bonsai create the opening with correct collection placement ──
        # add_element with IfcFeatureElement:
        #   • calls tool.Feature.add_feature  → IfcRelVoidsElement created
        #   • calls bpy.ops.bim.show_openings → opening object made visible
        #   • calls tool.Collector.assign    → object placed under slab collection
        bpy.ops.bim.add_element(
            ifc_product="IfcFeatureElement",
            ifc_class="IfcOpeningElement",
            skip_dialog=True,
        )

        # ── Step 5: find the new opening element via IFC (active object is unreliable) ──
        new_opening_rels = [
            r for r in host_slab.HasOpenings if r.RelatedOpeningElement.id() not in existing_opening_ids
        ]
        if not new_opening_rels:
            self.report({"WARNING"}, f"add_element did not create an opening for {path_group}.")
            return False
        element = new_opening_rels[0].RelatedOpeningElement
        opening_obj = tool.Ifc.get_object(element)

        # ── Step 6: build the path-group prism geometry ──
        host_depth_ifc = self._thickness_from_type(ifcopenshell.util.element.get_type(host_slab), 0.2 / unit_scale)
        host_depth = host_depth_ifc * unit_scale  # metres
        overcut = host_depth * 0.5

        # Slab grows downward (z=0 at top, z=-depth at bottom).
        # Opening spans +½T above the top to -1½T below the bottom face.
        z_top = overcut
        z_bottom = -(host_depth + overcut)

        verts_bottom = [mathutils.Vector((pt.x, pt.y, z_bottom)) for pt in polygon_pts]
        verts_top = [mathutils.Vector((pt.x, pt.y, z_top)) for pt in polygon_pts]
        n = len(verts_bottom)
        all_verts = verts_bottom + verts_top
        faces = [list(range(n)), list(range(n, 2 * n))]
        for i in range(n):
            j = (i + 1) % n
            faces.append([i, j, j + n, i + n])

        if opening_obj is not None:
            # Object exists — replace its mesh in-place
            if opening_obj.data is None:
                opening_obj.data = bpy.data.meshes.new("IfcOpeningElement")
            opening_obj.matrix_world = mathutils.Matrix.Identity(4)
            mesh = opening_obj.data
            mesh.clear_geometry()
            mesh.from_pydata([v.to_tuple() for v in all_verts], [], faces)
            mesh.update()
        else:
            # Opening was hidden/purged by show_openings — recreate the Blender object
            mesh = bpy.data.meshes.new("IfcOpeningElement")
            mesh.from_pydata([v.to_tuple() for v in all_verts], [], faces)
            mesh.update()
            opening_obj = bpy.data.objects.new("IfcOpeningElement", mesh)
            opening_obj.matrix_world = mathutils.Matrix.Identity(4)
            bpy.context.scene.collection.objects.link(opening_obj)
            tool.Ifc.link(element, opening_obj)
            tool.Collector.assign(opening_obj)

        # ── Step 7: sync the new geometry back to IFC ──
        context.view_layer.objects.active = opening_obj
        bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=opening_obj)
        bpy.ops.bim.update_representation(obj=opening_obj.name)

        # ── Step 8: show the void (hole) rather than the opening solid ──
        # Select the host slab and toggle openings so the boolean cut is visible.
        context.view_layer.objects.active = host_obj
        host_obj.select_set(True)
        bpy.ops.bim.hotkey(hotkey="A_O", description="Toggle openings\n\nHotkey: ALT O")

        # ── Step 9: preserve GUID across reimports ──
        if old_guid:
            element.GlobalId = old_guid
        _set_entity_guid(_poly_sketch_op, path_group.slvs_index, "IfcOpeningElement", element.GlobalId)

        return True

    # ── Sketch dependency propagation ─────────────────────────────────────────

    @staticmethod
    def _find_dependent_sketch_indices(context, sketch_index):
        """Return the set of sketch slvs_index values that reference at least one
        entity/point belonging to *sketch_index*.

        CAD Sketcher stores cross-sketch links when a point from one sketch is used
        as a constraint or reference in another.  We detect this by comparing the
        slvs_index of every endpoint (p1/p2) in the candidate sketch against the
        set of slvs_indices owned by the source sketch.
        """
        sse = context.scene.sketcher.entities

        # Collect all entity indices that belong to the source sketch
        source_indices = {ent.slvs_index for ent in sse.all if getattr(ent, "sketch_i", -1) == sketch_index}
        if not source_indices:
            return set()

        dependent = set()
        for ent in sse.all:
            sk = getattr(ent, "sketch_i", -1)
            if sk == sketch_index or sk == -1:
                continue
            for attr in ("p1", "p2"):
                pt = getattr(ent, attr, None)
                if pt is not None and getattr(pt, "slvs_index", -1) in source_indices:
                    dependent.add(sk)
                    break
        return dependent

    def _auto_fetch_sketch(self, context, sketch_index, ifc_file, unit_scale, body_context, axis_context):
        """Process all IFC-tagged entities in *sketch_index* without a user dialog.

        Only entities that already have a GUID (or whose corresponding plan wall
        can be matched by XY position) are updated.  No new element is created if
        no type can be resolved — this prevents spurious elements during propagation.

        Returns the count of elements created / updated.
        """
        sse = context.scene.sketcher.entities
        us_inv = unit_scale  # metres per IFC unit (same variable name used elsewhere)
        count = 0

        # ── Resolve sketch entity for role checks ────────────────────────────
        sketch_entity = next((s for s in sse.sketches if s.slvs_index == sketch_index), None)
        is_plan = _sketch_has_role(sketch_entity, "Plan")
        is_elevation = _sketch_has_role(sketch_entity, "Elevation")

        if is_plan:
            # ── Plan walls (tagged lines) ──────────────────────────────────────
            for ent in _entities_with_ifc_tag(
                sketch_entity,
                sse,
                "IfcWall",
                lambda e: hasattr(e, "p1")
                and hasattr(e, "p2")
                and bool(_entity_guid(sketch_entity, e.slvs_index, "IfcWall")),
            ):
                _ent_guid = _entity_guid(sketch_entity, ent.slvs_index, "IfcWall")
                try:
                    existing = ifc_file.by_guid(_ent_guid)
                except Exception:
                    continue
                if existing is None:
                    continue
                wall_type = ifcopenshell.util.element.get_type(existing)
                if wall_type is None:
                    continue
                height = self.storey_height
                body = ifcopenshell.util.representation.get_representation(existing, "Model", "Body", "MODEL_VIEW")
                if body:
                    for rep_item in body.Items:
                        if rep_item.is_a("IfcExtrudedAreaSolid"):
                            height = rep_item.Depth * us_inv
                            break
                obj = self._create_or_update_wall(
                    ent, ifc_file, unit_scale, body_context, axis_context, wall_type, height
                )
                if obj is not None:
                    count += 1

            # ── Wall runs (open path groups) ───────────────────────────────────
            for poly in _group_path_proxies(sketch_entity, sse, "IfcWall", "OPEN"):
                # Determine type from the first segment that has a GUID
                run_type = None
                run_height = self.storey_height
                for j in range(poly.segment_count):
                    seg_idx = int(poly.segment_indices[j])
                    if seg_idx == -1:
                        continue
                    seg = sse.get(seg_idx)
                    if seg is None:
                        continue
                    seg_guid = _entity_guid(sketch_entity, seg.slvs_index, "IfcWall")
                    if not seg_guid:
                        continue
                    try:
                        existing = ifc_file.by_guid(seg_guid)
                    except Exception:
                        continue
                    if existing is None:
                        continue
                    run_type = ifcopenshell.util.element.get_type(existing)
                    body = ifcopenshell.util.representation.get_representation(existing, "Model", "Body", "MODEL_VIEW")
                    if body:
                        for rep_item in body.Items:
                            if rep_item.is_a("IfcExtrudedAreaSolid"):
                                run_height = rep_item.Depth * us_inv
                                break
                    break
                if run_type is None:
                    continue
                run_pairs = []
                for j in range(poly.segment_count):
                    seg_idx = int(poly.segment_indices[j])
                    if seg_idx == -1:
                        continue
                    seg = sse.get(seg_idx)
                    if seg is None or not hasattr(seg, "p1") or not hasattr(seg, "p2"):
                        continue
                    _ensure_entity_in_group(sketch_entity, seg.slvs_index, "IfcWall")
                    obj = self._create_or_update_wall(
                        seg,
                        ifc_file,
                        unit_scale,
                        body_context,
                        axis_context,
                        run_type,
                        run_height,
                        sketch=sketch_entity,
                    )
                    if obj is not None:
                        run_pairs.append((seg, obj))
                        count += 1
                if len(run_pairs) > 1:
                    try:
                        from bonsai.bim.module.model.wall import DumbWallJoiner

                        joiner = DumbWallJoiner()
                        for i, (seg1, obj1) in enumerate(run_pairs):
                            pts1 = {seg1.p1.slvs_index, seg1.p2.slvs_index}
                            for seg2, obj2 in run_pairs[i + 1 :]:
                                pts2 = {seg2.p1.slvs_index, seg2.p2.slvs_index}
                                if pts1 & pts2:
                                    joiner.connect(obj2, obj1)
                                    joiner.connect(obj1, obj2)
                    except Exception:
                        pass

        # ── Wall elevation path groups (Elevation sketches only) ────────────────
        if sketch_entity is not None and is_elevation:
            wall_guid = self._resolve_elevation_wall_guid(sketch_entity, sse)
            for poly in _group_path_proxies(sketch_entity, sse, "IfcWall", "ANY"):
                # Resolve wall type via path-group GUID or source wall GUID
                wall_type = None
                guid = _entity_guid(sketch_entity, poly.slvs_index, "IfcWall") or wall_guid
                if guid:
                    try:
                        existing = ifc_file.by_guid(guid)
                        if existing:
                            wall_type = ifcopenshell.util.element.get_type(existing)
                    except Exception:
                        pass

                if wall_type is None:
                    continue

                pts = self._polygon_from_path_group(context, poly)
                if not pts:
                    continue
                zs = [p.z for p in pts]
                height = max(zs) - min(zs)

                obj = self._create_wall_from_elevation_path_group(
                    context,
                    poly,
                    ifc_file,
                    unit_scale,
                    body_context,
                    axis_context,
                    wall_type,
                    height,
                    wall_guid_hint=wall_guid,
                )
                if obj is not None:
                    count += 1

        # ── Profile elements: IfcBeam, IfcMember, IfcFooting ─────────────────
        for ifc_tag in ("IfcBeam", "IfcMember", "IfcFooting"):
            # Single tagged lines that have a GUID
            for ent in _entities_with_ifc_tag(
                sketch_entity,
                sse,
                ifc_tag,
                lambda e: hasattr(e, "p1")
                and hasattr(e, "p2")
                and bool(_entity_guid(sketch_entity, e.slvs_index, ifc_tag)),
            ):
                _ent_guid = _entity_guid(sketch_entity, ent.slvs_index, ifc_tag)
                try:
                    existing = ifc_file.by_guid(_ent_guid)
                except Exception:
                    continue
                if existing is None:
                    continue
                element_type = ifcopenshell.util.element.get_type(existing)
                if element_type is None:
                    continue
                obj = self._create_or_update_profile_element(
                    ent,
                    ifc_file,
                    unit_scale,
                    body_context,
                    axis_context,
                    element_type,
                    sketch=sketch_entity,
                )
                if obj is not None:
                    count += 1

            # Open path groups (runs) whose segments have a GUID
            for poly in _group_path_proxies(sketch_entity, sse, ifc_tag, "OPEN"):
                run_type = None
                for j in range(poly.segment_count):
                    seg_idx = int(poly.segment_indices[j])
                    if seg_idx == -1:
                        continue
                    seg = sse.get(seg_idx)
                    if seg is None:
                        continue
                    seg_guid = _entity_guid(sketch_entity, seg.slvs_index, ifc_tag)
                    if not seg_guid:
                        continue
                    try:
                        existing = ifc_file.by_guid(seg_guid)
                    except Exception:
                        continue
                    if existing is None:
                        continue
                    run_type = ifcopenshell.util.element.get_type(existing)
                    break
                if run_type is None:
                    continue
                for j in range(poly.segment_count):
                    seg_idx = int(poly.segment_indices[j])
                    if seg_idx == -1:
                        continue
                    seg = sse.get(seg_idx)
                    if seg is None or not hasattr(seg, "p1") or not hasattr(seg, "p2"):
                        continue
                    _ensure_entity_in_group(sketch_entity, seg.slvs_index, ifc_tag)
                    obj = self._create_or_update_profile_element(
                        seg,
                        ifc_file,
                        unit_scale,
                        body_context,
                        axis_context,
                        run_type,
                        sketch=sketch_entity,
                    )
                    if obj is not None:
                        count += 1

        return count

    def _propagate_to_dependent_sketches(
        self, context, seed_sketch_indices, ifc_file, unit_scale, body_context, axis_context
    ):
        """BFS propagation: starting from *seed_sketch_indices*, find every sketch
        that references at least one entity from an already-processed sketch and
        auto-fetch it.  Each sketch is processed at most once (visited set guard).

        Args:
            seed_sketch_indices: set of sketch slvs_index values already processed
                                  in the current fetch operation.
        """
        visited = set(seed_sketch_indices)
        queue = list(seed_sketch_indices)
        total_propagated = 0

        while queue:
            current_idx = queue.pop(0)
            for dep_idx in self._find_dependent_sketch_indices(context, current_idx):
                if dep_idx in visited:
                    continue
                visited.add(dep_idx)
                n = self._auto_fetch_sketch(context, dep_idx, ifc_file, unit_scale, body_context, axis_context)
                total_propagated += n
                if n > 0:
                    # This sketch produced updates — its own dependents may need refreshing too
                    queue.append(dep_idx)

        if total_propagated:
            pass
