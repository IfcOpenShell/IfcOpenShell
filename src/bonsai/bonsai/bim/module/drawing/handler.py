# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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

import json

import bpy
import numpy as np
from bpy.app.handlers import persistent

import bonsai.bim.module.drawing.decoration as decoration
import bonsai.tool as tool

# ---------------------------------------------------------------------------
# Parametric dimension auto-regeneration state
# ---------------------------------------------------------------------------

# Maps element GUID → list of annotation STEP IDs that reference it.
_dim_guid_index: dict = {}
# Persistent tessellation cache for the depsgraph handler (element id → shape).
_dim_shape_cache: dict = {}
# Set True whenever BBIM_Dimension anchors change or a new file loads.
_dim_index_dirty: bool = True
# Re-entry guard so curve updates don't trigger a second handler call.
_dim_handler_running: bool = False


def invalidate_dim_index() -> None:
    """Mark the GUID index as stale so it is rebuilt on the next handler call."""
    global _dim_index_dirty, _dim_shape_cache
    _dim_index_dirty = True
    _dim_shape_cache.clear()


def _rebuild_dim_guid_index(file) -> None:
    global _dim_guid_index, _dim_index_dirty
    import ifcopenshell.util.element

    _dim_guid_index = {}
    for annotation in file.by_type("IfcAnnotation"):
        pset_data = ifcopenshell.util.element.get_pset(annotation, "BBIM_Dimension")
        if not pset_data or not pset_data.get("Anchors"):
            continue
        try:
            anchors = json.loads(pset_data["Anchors"])
        except Exception:
            continue
        ann_id = annotation.id()
        for anchor in anchors:
            guid = anchor.get("guid")
            if not guid:
                continue
            ids = _dim_guid_index.setdefault(guid, [])
            if ann_id not in ids:
                ids.append(ann_id)
    _dim_index_dirty = False


def regenerate_dims_for_layer(file, layer) -> None:
    """Regenerate all parametric dimensions anchored to elements that use *layer*."""
    global _dim_shape_cache, _dim_index_dirty, _dim_guid_index

    if _dim_index_dirty:
        _rebuild_dim_guid_index(file)

    affected_guids: set = set()
    for layer_set in file.get_inverse(layer):
        if not layer_set.is_a("IfcMaterialLayerSet"):
            continue
        for inv in file.get_inverse(layer_set):
            if inv.is_a("IfcRelAssociatesMaterial"):
                rels = [inv]
            elif inv.is_a("IfcMaterialLayerSetUsage"):
                rels = [r for r in file.get_inverse(inv) if r.is_a("IfcRelAssociatesMaterial")]
            else:
                continue
            for rel in rels:
                for element in rel.RelatedObjects:
                    if hasattr(element, "GlobalId"):
                        affected_guids.add(element.GlobalId)
                        _dim_shape_cache.pop(element.id(), None)

    if not affected_guids:
        return

    annotation_ids: set = set()
    for guid in affected_guids:
        for ann_id in _dim_guid_index.get(guid, []):
            annotation_ids.add(ann_id)

    if not annotation_ids:
        return

    import ifcopenshell.util.element
    import ifcopenshell.api.drawing as drawing_api
    import ifcopenshell.geom
    from bonsai.bim.module.drawing.operator import _update_blender_curve

    geom_settings = ifcopenshell.geom.settings()
    geom_settings.set("APPLY_DEFAULT_MATERIALS", False)

    for ann_id in annotation_ids:
        try:
            annotation = file.by_id(ann_id)
        except Exception:
            continue
        pset = ifcopenshell.util.element.get_pset(annotation, "BBIM_Dimension")
        if not pset:
            continue
        placement_override: dict = {}
        try:
            anchors_raw = json.loads(pset.get("Anchors") or "[]")
            for anchor in anchors_raw:
                guid = anchor.get("guid")
                if not guid:
                    continue
                try:
                    elem = file.by_guid(guid)
                    elem_obj = tool.Ifc.get_object(elem)
                    if elem_obj:
                        placement_override[elem.id()] = np.array(elem_obj.matrix_world)
                except Exception:
                    pass
        except Exception:
            pass
        resolved_pts = drawing_api.regenerate_dimension(
            file,
            annotation,
            settings=geom_settings,
            shape_cache=_dim_shape_cache,
            placement_override=placement_override,
        )
        if resolved_pts:
            _update_blender_curve(annotation, resolved_pts)


@persistent
def load_post(*args):
    invalidate_dim_index()
    props = tool.Drawing.get_document_props()
    if props.should_draw_decorations:
        decoration.DecorationsHandler.install(bpy.context)
    else:
        decoration.DecorationsHandler.uninstall()


@persistent
def depsgraph_update_pre_handler(scene):
    set_active_camera_resolution(scene)


def set_active_camera_resolution(scene: bpy.types.Scene) -> None:
    """Sync scene render resolution with the active drawing
    and prevent user from manually changing ``ortho_scale`` on IFC camera."""
    props = tool.Drawing.get_document_props()
    camera_obj = scene.camera
    if not camera_obj or "/" not in camera_obj.name or not props.drawings:
        return
    assert isinstance((camera := camera_obj.data), bpy.types.Camera)
    props = tool.Drawing.get_camera_props(camera)

    if camera.type != props.camera_type:
        camera.type = props.camera_type

    if props.update_props and (drawing := tool.Ifc.get_entity(camera_obj)):
        tool.Drawing.sync_perspective_camera_shifts(drawing, camera)

    ortho_scale, aspect_ratio = props.get_scale_and_aspect_ratio()
    scene_render = scene.render
    if (camera.ortho_scale != ortho_scale) or not tool.Cad.is_x(
        scene_render.resolution_x / scene_render.resolution_y, aspect_ratio
    ):
        raster_x, raster_y = props.update_camera_resolution()
        scene_render.resolution_x = raster_x
        scene_render.resolution_y = raster_y


def _sync_dimension_anchors_to_curve(file, annotation, obj) -> bool:
    """Sync BBIM_Dimension.Anchors length to match the curve's spline point count.

    Called when the user adds or removes vertices from a dimension annotation in
    Edit Mode.  New vertices get a free WORLD-type anchor at their current world
    position; removed tail vertices simply lose their anchor entries.

    Returns True if the pset was changed.
    """
    import ifcopenshell.util.element
    import ifcopenshell.api.pset

    if not obj.data or not getattr(obj.data, "splines", None) or not obj.data.splines:
        return False

    pset_data = ifcopenshell.util.element.get_pset(annotation, "BBIM_Dimension")
    if not pset_data or not pset_data.get("Anchors"):
        return False

    try:
        anchors: list = json.loads(pset_data["Anchors"])
    except Exception:
        return False

    spline = obj.data.splines[0]
    spline_world = [obj.matrix_world @ p.co.to_3d() for p in spline.points]
    n_pts = len(spline_world)
    n_anchors = len(anchors)

    if n_pts == n_anchors:
        return False

    # Match each spline point to the nearest unused anchor by proximity.
    # This handles insertions (subdivide) and deletions correctly regardless
    # of where in the polyline the edit happened.
    _MATCH_THRESH_SQ = 1e-4  # 1 cm² — distinguishes existing pts from new midpoints
    used: set = set()
    new_anchors: list = []

    for pt in spline_world:
        best_idx, best_sq = None, float("inf")
        for i, anc in enumerate(anchors):
            if i in used:
                continue
            stored = anc.get("pt")
            if not stored:
                continue
            dx, dy, dz = stored[0] - pt.x, stored[1] - pt.y, stored[2] - pt.z
            sq = dx * dx + dy * dy + dz * dz
            if sq < best_sq:
                best_sq, best_idx = sq, i
        if best_idx is not None and best_sq < _MATCH_THRESH_SQ:
            new_anchors.append(anchors[best_idx])
            used.add(best_idx)
        else:
            new_anchors.append({
                "guid": None,
                "type": "WORLD",
                "addr": {},
                "hint": None,
                "pt": [pt.x, pt.y, pt.z],
            })


    pset_entity = file.by_id(pset_data["id"])
    ifcopenshell.api.pset.edit_pset(file, pset=pset_entity, properties={"Anchors": json.dumps(new_anchors)})
    invalidate_dim_index()
    return True


@persistent
def depsgraph_update_post_handler(scene, depsgraph):
    """Auto-regenerate parametric dimensions when referenced elements are moved."""
    global _dim_handler_running, _dim_index_dirty, _dim_guid_index, _dim_shape_cache

    if _dim_handler_running:
        return

    file = tool.Ifc.get()
    if not file:
        return

    if _dim_index_dirty:
        _rebuild_dim_guid_index(file)

    import ifcopenshell.util.element

    moved_guids: set = set()
    edited_annotation_ids: set = set()

    for update in depsgraph.updates:
        obj = update.id
        if not isinstance(obj, bpy.types.Object):
            continue
        if not (update.is_updated_transform or update.is_updated_geometry):
            continue
        element = tool.Ifc.get_entity(obj)
        if element is None or not hasattr(element, "GlobalId"):
            continue


        if update.is_updated_geometry and obj.type == "CURVE" and element.is_a("IfcAnnotation"):
            import ifcopenshell.util.element as _ue
            ptype = _ue.get_predefined_type(element)
            if ptype in ("DIMENSION", "RADIUS", "DIAMETER", "ANGLE", "PLAN_LEVEL", "SECTION_LEVEL"):
                changed = _sync_dimension_anchors_to_curve(file, element, obj)
                if changed:
                    edited_annotation_ids.add(element.id())
                continue

        moved_guids.add(element.GlobalId)
        if update.is_updated_geometry:
            _dim_shape_cache.pop(element.id(), None)

    annotation_ids: set = set(edited_annotation_ids)
    for guid in moved_guids:
        for ann_id in _dim_guid_index.get(guid, []):
            annotation_ids.add(ann_id)

    if not annotation_ids:
        return

    import ifcopenshell.api.drawing as drawing_api
    import ifcopenshell.geom
    from bonsai.bim.module.drawing.operator import _update_blender_curve

    geom_settings = ifcopenshell.geom.settings()
    geom_settings.set("APPLY_DEFAULT_MATERIALS", False)

    _dim_handler_running = True
    try:
        for ann_id in annotation_ids:
            try:
                annotation = file.by_id(ann_id)
            except Exception:
                continue

            pset = ifcopenshell.util.element.get_pset(annotation, "BBIM_Dimension")
            if not pset:
                continue

            placement_override: dict = {}
            try:
                anchors_raw = json.loads(pset.get("Anchors") or "[]")
                for anchor in anchors_raw:
                    guid = anchor.get("guid")
                    if not guid:
                        continue
                    try:
                        elem = file.by_guid(guid)
                        elem_id = elem.id()
                        if elem_id in placement_override:
                            continue
                        elem_obj = tool.Ifc.get_object(elem)
                        if elem_obj:
                            placement_override[elem_id] = np.array(elem_obj.matrix_world)
                    except Exception:
                        pass
            except Exception:
                pass

            resolved_pts = drawing_api.regenerate_dimension(
                file,
                annotation,
                settings=geom_settings,
                shape_cache=_dim_shape_cache,
                placement_override=placement_override,
            )
            if resolved_pts:
                _update_blender_curve(annotation, resolved_pts)
    finally:
        _dim_handler_running = False
