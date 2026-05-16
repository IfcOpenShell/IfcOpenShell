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


@persistent
def depsgraph_update_post_handler(scene, depsgraph):
    """Auto-regenerate parametric dimensions when referenced elements are moved."""
    global _dim_handler_running, _dim_index_dirty, _dim_guid_index, _dim_shape_cache

    if _dim_handler_running:
        return

    file = tool.Ifc.get()
    if not file:
        return

    # Collect GUIDs of IFC objects whose transform or geometry changed.
    # is_updated_geometry fires on Edit Mode exit after Bonsai has already
    # serialised the new mesh back to IFC via update_representation, so the
    # tessellation will reflect the edited shape.
    moved_guids: set = set()
    for update in depsgraph.updates:
        obj = update.id
        if not isinstance(obj, bpy.types.Object):
            continue
        if not (update.is_updated_transform or update.is_updated_geometry):
            continue
        element = tool.Ifc.get_entity(obj)
        if element is None or not hasattr(element, "GlobalId"):
            continue
        moved_guids.add(element.GlobalId)
        # Geometry edits invalidate the cached tessellation for this element.
        if update.is_updated_geometry:
            _dim_shape_cache.pop(element.id(), None)

    if not moved_guids:
        return

    if _dim_index_dirty:
        _rebuild_dim_guid_index(file)

    annotation_ids: set = set()
    for guid in moved_guids:
        for ann_id in _dim_guid_index.get(guid, []):
            annotation_ids.add(ann_id)

    if not annotation_ids:
        return

    import ifcopenshell.api.drawing as drawing_api
    import ifcopenshell.geom
    import ifcopenshell.util.element
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
