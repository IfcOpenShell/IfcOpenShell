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

from __future__ import annotations

import contextlib
from collections.abc import Callable, Iterable, Iterator
from typing import TYPE_CHECKING, Any, Optional

import bpy

import bonsai.tool as tool

if TYPE_CHECKING:
    from mathutils import Matrix

    from bonsai.bim.module.clip_box.prop import (
        BIMClipBoxProperties,
        BIMSceneClipBoxProperties,
    )


PlaneTuple = tuple[float, float, float, float]
PlaneSet = tuple[PlaneTuple, PlaneTuple, PlaneTuple, PlaneTuple, PlaneTuple, PlaneTuple]

# Stable contract of Pset_*Common.Status values plus the "absent" entry.
# Duplicated locally rather than imported so this module has no load-order
# dependency on the sequence layer that hosts the matching query helper.
SOURCE_STATUS_VALUES: tuple[str, ...] = (
    "No Status",
    "NEW",
    "EXISTING",
    "DEMOLISH",
    "TEMPORARY",
    "OTHER",
    "NOTKNOWN",
    "UNSET",
)


# Outward margins so the empty's CUBE display edges sit safely INSIDE
# the clip volume. A fixed absolute margin fails under rotation: the
# float error in computing each column's length and in per-vertex dot
# products at GPU rasterisation scales with the axis's world
# half-extent, so once the box is spawned at any non-trivial scale it
# can exceed an absolute floor. The relative term tracks that drift;
# the absolute term catches sub-unit boxes where the relative term
# shrinks below float precision.
_CLIP_EXPAND_ABS = 1e-6
_CLIP_EXPAND_REL = 1e-5


class ClipBox:
    """Driver for the viewport clip-box feature.

    Owns the bridge between ``BIMClipBoxProperties`` on a host empty and
    Blender's ``RegionView3D.clip_planes`` machinery. Plane math is in
    ``Cad``; this class is the bpy adapter.

    Region-ownership: ``_owned`` tracks which regions we have armed so
    a subsequent arm on the same region can skip the first-arm operator
    path and write planes directly. Keyed by ``region.as_pointer()``.
    """

    _owned: set[int] = set()
    _region_by_key: dict[int, tuple[Any, Any]] = {}
    # View matrix per region at last clip_border arm. PRE_VIEW only
    # updates clip_planes; without a snapshot, the C-side clip_bb stays
    # aligned to the prior view and the edit-mode picker rejects verts
    # inside the current clip_planes after orbit/pan/zoom.
    _view_matrix_at_arm: dict[int, tuple] = {}
    _pending_refresh: Optional[Callable[[], None]] = None
    # True from load_pre until the first on_pre_view tick of the new file
    # (first paint = GPU contexts wired). Suppresses schedule_refresh and
    # short-circuits on_depsgraph_update so neither path can drive
    # RegionView3D.update() against regions whose GL state is not yet
    # initialised — that crash inside GPU_matrix_ortho_set is a CTD, not
    # catchable from Python. load_post fires before the first paint, so it
    # CANNOT be the gate-clear point.
    _file_loading: bool = False
    # Edge-trigger consumed by on_pre_view: clears _file_loading on the
    # first frame after load and kicks a refresh so the new file's clip
    # box arms against now-safe regions.
    _post_load_paint_pending: bool = False
    _last_seen_ifc_id: int = 0
    # Tracks the last matrix we persisted to the pset, keyed by Blender
    # object name. Lets the depsgraph handler detect committed transform
    # changes on clip boxes rehydrated from the project pset on file load
    # (which have no modal poller watching them).
    _persisted_matrices: dict[str, tuple] = {}
    # Names of clip boxes whose matrix changed during a transform modal.
    # Flushed when the gate flips back to inactive — one save per dirty
    # box on commit, no writes during the drag.
    _dirty_for_save: set[str] = set()
    # Per-object cache of cross-section cap triangles in world space.
    # Key: obj.name. Value: (cache_key_tuple, gpu_batch). Invalidated when
    # the object's mesh data block, world matrix, or the clip box matrix
    # changes. Rebuild is skipped while any transform modal is dragging
    # matrix_world so a continuous G/R/S shows stale caps and rebuilds on
    # commit instead of re-bisecting every mesh per frame.
    _cap_cache: dict[str, tuple[tuple, Any]] = {}
    _last_cap_clip_box_hash: int = 0
    # Debounce window for cap rebuild from external (unknown-modal) drags:
    # each depsgraph tick reschedules a timer this far in the future, so
    # a burst of N ticks collapses to one rebuild after the storm.
    _CAP_REBUILD_DEBOUNCE_SECONDS: float = 1.0
    _last_modal_state: bool = False
    _pending_cap_rebuild: Optional[Callable[[], None]] = None
    # Per-object matrix hash baseline used to tell a real transform
    # change from Blender's "selection touched the flag" noise: when a
    # depsgraph tick reports is_updated_transform on an Object, the
    # relevance filter compares the live hash against this baseline.
    _last_seen_object_matrices: dict[str, int] = {}

    @classmethod
    def get_scene_props(cls, scene: Optional[bpy.types.Scene] = None) -> BIMSceneClipBoxProperties:
        if scene is None:
            scene = bpy.context.scene
        return scene.BIMSceneClipBoxProperties

    @classmethod
    def get_object_props(cls, obj: bpy.types.Object) -> BIMClipBoxProperties:
        return obj.BIMClipBoxProperties

    @classmethod
    def select_active_clip_box(cls, context: bpy.types.Context) -> None:
        """Deselect everything, then select + activate the active clip box's empty.

        Wired into the panel UIList's ``active_clip_box_index`` update
        so clicking a row in the list does the standard outliner-style
        focus: the user can immediately G/R/S the box they just picked.

        Short-circuits when the active object is already the target —
        keeps multi-selections intact when the index changed because the
        depsgraph sync detected the user clicking the empty directly.
        No-op when no active box is resolvable.
        """
        obj = cls.get_active_clip_box(context.scene)
        if obj is None:
            return
        if getattr(context, "active_object", None) is obj:
            return
        tool.Blender.set_objects_selection(
            context, active_object=obj, selected_objects=[obj], clear_previous_selection=True
        )

    @classmethod
    def get_active_clip_box(cls, scene: Optional[bpy.types.Scene] = None) -> Optional[bpy.types.Object]:
        """Return the host empty of the currently active clip box, or ``None``."""
        props = cls.get_scene_props(scene)
        index = props.active_clip_box_index
        if index < 0 or index >= len(props.clip_boxes):
            return None
        obj = props.clip_boxes[index].obj
        if obj is None:
            return None
        obj_props = cls.get_object_props(obj)
        if not obj_props.is_clip_box:
            return None
        return obj

    @classmethod
    def compute_planes(cls, obj: bpy.types.Object) -> PlaneSet:
        """Build the 6 inward world clip planes from the host empty's matrix_world.

        The empty's CUBE display spans local ``[-1, +1]^3`` (with
        ``empty_display_size = 1``); ``matrix_world`` carries translation,
        rotation, and per-axis scale, so the clip planes track the cube
        exactly as it looks in the viewport. A tiny outward margin
        prevents the cube's own wireframe from being clipped by its own
        planes.
        """
        return tool.Cad.obb_clip_planes_from_matrix(
            obj.matrix_world, expand=_CLIP_EXPAND_ABS, expand_rel=_CLIP_EXPAND_REL
        )

    @classmethod
    def compute_planes_from_matrix(cls, matrix: Any) -> PlaneSet:
        """Same as :meth:`compute_planes` but accepts a raw matrix.

        Used by the depsgraph handler to read the *evaluated* matrix during
        a live G/R/S transform — that matrix reflects the in-progress
        transform offset, while ``obj.matrix_world`` stays at the
        pre-transform value until the operator commits on release.
        """
        return tool.Cad.obb_clip_planes_from_matrix(matrix, expand=_CLIP_EXPAND_ABS, expand_rel=_CLIP_EXPAND_REL)

    @classmethod
    def apply_clip_planes(cls, planes: PlaneSet) -> None:
        """Drive every open 3D viewport's clip planes to ``planes``.

        Always calls ``view3d.clip_border`` to refresh the region's
        ``clip_bb`` at the CURRENT view. Edit-mode click-select tests
        against ``clip_local`` derived from that bbox; if we don't keep
        ``clip_bb`` fresh, the user can orbit the view (or transform
        the clip box) and find click-select rejecting verts that ARE
        visible because the test is using a stale view-frustum bbox
        captured the last time we armed. Re-arming on every commit
        keeps the bbox aligned with the view the user is actually at.
        """
        for area, region, region_3d in tool.Blender.iter_view3d_regions():
            # Skip collapsed / initializing regions wholesale: arming one
            # CTDs Blender (see _region_is_renderable), and recording an
            # arm signature for a region we didn't actually arm would make
            # the next view-change comparison spurious.
            if not cls._region_is_renderable(region, region_3d):
                continue
            key = region.as_pointer()
            cls._owned.add(key)
            cls._region_by_key[key] = (area, region)
            cls._arm_region(area, region, region_3d, planes)
            cls._view_matrix_at_arm[key] = tuple(tuple(row) for row in region_3d.view_matrix)

    @classmethod
    def _region_is_renderable(cls, region: Any, region_3d: Any) -> bool:
        """True iff ``region`` is safe to arm clip planes against.

        A collapsed / still-initializing region (``width`` or ``height``
        == 0, or no readable ``view_matrix``) has no live view-matrix
        state. Calling ``region_3d.update()`` against it drives
        ``ED_view3d_update_viewmat -> GPU_matrix_ortho_set`` into a null
        deref and HARD-CRASHES Blender (CTD, not a catchable exception) —
        observed when a 3D viewport is split/collapsed while the clip box
        re-arms from a timer. Skipping such regions is the load-bearing
        guard; they get armed on the next refresh once they have a size.
        """
        try:
            if int(getattr(region, "width", 0)) <= 0 or int(getattr(region, "height", 0)) <= 0:
                return False
            return getattr(region_3d, "view_matrix", None) is not None
        except (ReferenceError, AttributeError, TypeError):
            return False

    @classmethod
    def _arm_region(cls, area: Any, region: Any, region_3d: Any, planes: PlaneSet) -> None:
        """Initialize the region's clip machinery and write ``planes``.

        ``view3d.clip_border`` with a FULL-REGION rect arms ``RV3D_CLIPPING``
        without leaving the C-side ``clipbb`` degenerate (which would break
        edit-mode click-select). Caller must guarantee a context in which
        operators are legal (not a draw handler / depsgraph callback).

        The ``_region_is_renderable`` guard is the real crash fix — arming a
        collapsed / initializing region drives ``region_3d.update()`` into a
        native null deref inside ``GPU_matrix_ortho_set`` that NO Python
        ``try``/``except`` can catch (it's a CTD, not an exception). The
        ``suppress`` around ``update()`` is unrelated to that: it only
        swallows the *catchable* ``RuntimeError`` ("context is incorrect")
        / ``ReferenceError`` (region freed mid-call) that the override path
        can still surface — it does NOT and CANNOT make ``update()``
        crash-safe.
        """
        if not cls._region_is_renderable(region, region_3d):
            return
        with bpy.context.temp_override(area=area, region=region):
            bpy.ops.view3d.clip_border(xmin=0, ymin=0, xmax=region.width, ymax=region.height)
            region_3d.clip_planes = planes
            region_3d.use_clip_planes = True
            with contextlib.suppress(RuntimeError, ReferenceError):
                region_3d.update()

    @classmethod
    def clear_clip_planes(cls) -> None:
        """Disable clip planes on every 3D viewport region.

        Unchecking ``enabled`` or removing a clip box turns clipping
        off; any prior Alt+B clip is NOT restored. The ``_owned``
        ownership table is preserved across this clear so a later
        re-enable can skip the ``view3d.clip_border`` re-init (which
        would re-derive ``clip_bb`` at the current view and break
        edit-mode click-select alignment). The full ownership reset
        happens only on IFC reload or addon unregister.
        """
        for area, region, region_3d in tool.Blender.iter_view3d_regions():
            with contextlib.suppress(ReferenceError, AttributeError, TypeError):
                region_3d.use_clip_planes = False
                region.tag_redraw()

    @classmethod
    def _active_scene_props(cls, scene: Optional[bpy.types.Scene] = None) -> Optional[BIMSceneClipBoxProperties]:
        """Scene PG iff the clipping pipeline should drive this tick, else ``None``.

        Most sessions run with clipping disabled, so the cheap
        ``enabled`` check fires before any active-box lookup or
        per-mesh work. Callers compose with their own further checks
        (e.g. ``show_caps`` for the cap pipeline) on the returned PG.
        """
        if scene is None:
            scene = bpy.context.scene
        scene_props = cls.get_scene_props(scene)
        if not scene_props.enabled:
            return None
        return scene_props

    @classmethod
    def refresh(cls, scene: Optional[bpy.types.Scene] = None) -> None:
        """Re-arm or clear the viewport clip based on the active clip box state."""
        if cls._active_scene_props(scene) is None:
            cls.clear_clip_planes()
            return
        obj = cls.get_active_clip_box(scene)
        if obj is None:
            cls.clear_clip_planes()
            return
        cls.apply_clip_planes(cls.compute_planes(obj))

    @classmethod
    def schedule_refresh(cls) -> None:
        """Schedule a refresh on the next idle tick.

        PropertyGroup ``update=`` callbacks must not call ``bpy.ops`` (which
        ``apply_clip_planes`` may need for the first-time arm) — doing so
        from within a property write disrupts gizmo modal accounting and
        can leave the operator stack inconsistent. Deferring via a 0-delay
        timer hands the refresh to Blender's main loop, where operators are
        legal. Debounced: a pending handle suppresses repeats while one is
        in flight, and lets the file-load gate tear it down cleanly so the
        timer can't fire against not-yet-realised regions.
        """
        if cls._file_loading:
            return
        if cls._pending_refresh is not None:
            return

        def _do_refresh():
            cls._pending_refresh = None
            cls.refresh()
            return None

        cls._pending_refresh = _do_refresh
        bpy.app.timers.register(_do_refresh, first_interval=0.0)

    @classmethod
    def _cancel_pending_refresh(cls) -> None:
        """Cancel any pending debounced refresh. Idempotent; safe to call
        when none is registered (e.g. on addon unregister)."""
        pending = cls._pending_refresh
        if pending is not None and bpy.app.timers.is_registered(pending):
            bpy.app.timers.unregister(pending)
        cls._pending_refresh = None

    @classmethod
    def reset_ownership(cls) -> None:
        """Drop the ownership table without touching any region. Used on register/reload."""
        cls._owned.clear()
        cls._region_by_key.clear()
        cls._view_matrix_at_arm.clear()

    PSET_NAME = "BBIM_ClipBoxes"
    COLLECTION_NAME = "BBIM_ClipBoxes"

    @classmethod
    def _get_project_pset_entity(cls, create: bool = False):
        """Return the ``IfcPropertySet`` entity holding the clip-box state.

        Stored on ``IfcProject`` because IFC's IfcRoot pipeline locks and
        strips object scale on export, which a clip box (whose size IS
        its scale) cannot tolerate. A project-level pset side-steps any
        per-entity placement sync.
        """
        import ifcopenshell.util.element

        ifc_file = tool.Ifc.get()
        if ifc_file is None:
            return None
        projects = ifc_file.by_type("IfcProject")
        if not projects:
            return None
        project = projects[0]
        existing = ifcopenshell.util.element.get_psets(project).get(cls.PSET_NAME)
        if existing is not None:
            return ifc_file.by_id(existing["id"])
        if not create:
            return None
        return tool.Ifc.run("pset.add_pset", product=project, name=cls.PSET_NAME)

    @classmethod
    def mark_dirty_for_save(cls, obj_name: str) -> None:
        """Note that ``obj_name`` has an unpersisted matrix change.

        Accumulates dirty names during a transform drag without
        touching the IFC graph; the flush gate writes exactly one
        save per dirty box once no transform modal is active.
        """
        cls._dirty_for_save.add(obj_name)

    @classmethod
    def flush_pending_saves(cls, scene: Optional[bpy.types.Scene] = None) -> None:
        """Write the pset iff there's pending dirt AND no transform modal.

        Called from the depsgraph handler every tick. Reading
        ``tool.Blender.is_transform_modal_active(bpy.context)`` checks
        ``window.modal_operators`` against the known transform op names
        (Blender vanilla + Bonsai macro overrides — kept centrally in
        :attr:`tool.Blender.BONSAI_TRANSFORM_MACROS`), so this gate
        survives any Bonsai keymap override and any Python script that
        wraps the same operators.
        """
        if not cls._dirty_for_save:
            return
        if tool.Ifc.get() is None:
            cls._dirty_for_save.clear()
            return
        if tool.Blender.is_transform_modal_active(bpy.context):
            return
        cls._dirty_for_save.clear()
        cls.save_to_project_pset(scene)

    @classmethod
    def save_to_project_pset(cls, scene: Optional[bpy.types.Scene] = None) -> None:
        """Snapshot the active clip-box state to ``IfcProject.BBIM_ClipBoxes``.

        Each clip box contributes ``Box_<i>_Name`` and ``Box_<i>_Matrix``
        (a 16-float comma-separated string). ``Count`` is the canonical
        size. ``enabled`` is intentionally not persisted — opening a file
        should never silently hide geometry behind a remembered toggle.
        No-op when no IFC file is loaded.
        """
        if tool.Ifc.get() is None:
            return
        if scene is None:
            scene = bpy.context.scene
        scene_props = cls.get_scene_props(scene)

        pset = cls._get_project_pset_entity(create=True)
        if pset is None:
            return

        properties: dict[str, str | int] = {
            "Count": len(scene_props.clip_boxes),
            "ShowCaps": int(scene_props.show_caps),
        }
        for i, entry in enumerate(scene_props.clip_boxes):
            obj = entry.obj
            if obj is None:
                continue
            properties[f"Box_{i}_Name"] = obj.name
            properties[f"Box_{i}_Matrix"] = tool.Blender.serialize_matrix(obj.matrix_world)
        tool.Ifc.run("pset.edit_pset", pset=pset, properties=properties)

    @classmethod
    def load_from_project_pset(cls, scene: Optional[bpy.types.Scene] = None) -> None:
        """Rehydrate clip boxes from ``IfcProject.BBIM_ClipBoxes``.

        Idempotent: drops stale list entries (deleted hosts / un-flagged
        objects), then for each saved box, creates the empty if absent
        or updates its matrix if the .blend reload already restored it.

        ``scene_props.enabled`` is NOT touched: it defaults to ``False``
        (so a fresh IFC load over a fresh .blend never silently hides
        geometry), and Blender's normal .blend persistence carries the
        user's saved toggle through .blend reload.
        """
        import ifcopenshell.util.element

        if scene is None:
            scene = bpy.context.scene
        scene_props = cls.get_scene_props(scene)

        for index in range(len(scene_props.clip_boxes) - 1, -1, -1):
            entry = scene_props.clip_boxes[index]
            obj = entry.obj
            if obj is None or not cls.get_object_props(obj).is_clip_box:
                scene_props.clip_boxes.remove(index)

        ifc_file = tool.Ifc.get()
        if ifc_file is None:
            return
        projects = ifc_file.by_type("IfcProject")
        if not projects:
            return
        pset = ifcopenshell.util.element.get_psets(projects[0]).get(cls.PSET_NAME)
        if not pset:
            return

        show_caps_raw = pset.get("ShowCaps")
        if show_caps_raw is not None:
            scene_props.show_caps = bool(int(show_caps_raw))
        # enabled is intentionally NOT read from the pset — see docstring.

        existing_by_name = {entry.obj.name: entry.obj for entry in scene_props.clip_boxes if entry.obj}
        existing_objs = set(existing_by_name.values())
        count = int(pset.get("Count", 0) or 0)
        for i in range(count):
            name = pset.get(f"Box_{i}_Name") or f"ClipBox.{i:03d}"
            matrix_str = pset.get(f"Box_{i}_Matrix")
            if not matrix_str:
                continue
            matrix = tool.Blender.deserialize_matrix(matrix_str)
            existing_obj = bpy.data.objects.get(name)
            if existing_obj is None:
                # Fresh IFC load: no .blend backing, no viewport clip state.
                # Create the empty, place it, and force enabled=False so we
                # don't silently hide geometry behind a box the user forgot.
                obj = bpy.data.objects.new(name, None)
                obj.empty_display_type = "CUBE"
                obj.empty_display_size = 1.0
                obj.show_in_front = True
                collection = tool.Blender.get_or_create_collection(scene, cls.COLLECTION_NAME)
                collection.objects.link(obj)
                obj.matrix_world = matrix
                cls.get_object_props(obj).is_clip_box = True
            else:
                # .blend reload: the empty (and the scene-level enabled
                # toggle) survived Blender's own session save. Update the
                # matrix in case the pset diverged from the .blend snapshot.
                obj = existing_obj
                obj.matrix_world = matrix
                cls.get_object_props(obj).is_clip_box = True
            if obj not in existing_objs:
                entry = scene_props.clip_boxes.add()
                entry.obj = obj
                existing_objs.add(obj)

        if scene_props.clip_boxes and scene_props.active_clip_box_index >= len(scene_props.clip_boxes):
            scene_props.active_clip_box_index = 0

    @classmethod
    def apply_clip_planes_direct(cls, planes: PlaneSet) -> None:
        """Direct-write variant for contexts where ``bpy.ops`` is illegal.

        Skips the first-arm path (which needs ``view3d.clip_border``)
        and writes planes directly to every armed region.
        ``region_3d.update()`` pushes the new clip planes to the GPU
        buffer the rasteriser samples — without it the planes sit in
        the data block and the next frame still uses the previous GPU
        state. ``tag_redraw`` requests that the region actually
        redraws this frame.
        """
        for area, region, region_3d in tool.Blender.iter_view3d_regions():
            if not region_3d.use_clip_planes:
                continue
            # A collapsed / initializing region CTDs inside update() — same
            # null deref as the operator arm path (see _region_is_renderable).
            if not cls._region_is_renderable(region, region_3d):
                continue
            key = region.as_pointer()
            cls._region_by_key[key] = (area, region)
            region_3d.clip_planes = planes
            with contextlib.suppress(RuntimeError, ReferenceError):
                region_3d.update()
            region.tag_redraw()

    @classmethod
    def _sync_collection_to_list(cls, scene: bpy.types.Scene) -> None:
        """Add any clip-box-flagged empties not yet in ``scene_props.clip_boxes``.

        Bonsai's duplicate-move macros (Shift+D, Alt+D, Ctrl+Shift+D)
        deep-copy the source's ``BIMClipBoxProperties``, so the
        duplicated empty carries ``is_clip_box=True`` but no scene-list
        entry exists for it. This sync turns the duplicate into a
        first-class clip box matching the UIList duplicate button: a
        new entry, set active, persisted to the pset.

        Scoped to the ``BBIM_ClipBoxes`` collection so the cost is O(N)
        in the number of clip boxes, not O(N) in the whole scene.
        """
        scene_props = cls.get_scene_props(scene)
        known_objs = {entry.obj for entry in scene_props.clip_boxes if entry.obj}
        collection = bpy.data.collections.get(cls.COLLECTION_NAME)
        if collection is None:
            return
        appended = False
        for obj in collection.objects:
            if obj in known_objs:
                continue
            if obj.type != "EMPTY":
                continue
            obj_props = cls.get_object_props(obj)
            if not obj_props.is_clip_box:
                continue
            entry = scene_props.clip_boxes.add()
            entry.obj = obj
            scene_props.active_clip_box_index = len(scene_props.clip_boxes) - 1
            appended = True
        if appended and tool.Ifc.get() is not None:
            cls.save_to_project_pset(scene)

    @classmethod
    def on_depsgraph_update(cls, scene, depsgraph) -> None:
        """Safety-net re-arm, IFC-load rehydrate, sync + pset persistence.

        - **Shutdown guard**: skips when ``bpy.context.screen`` is ``None``
          so the persistent handler can't fault against freed UI memory.
        - **IFC reload detection**: when ``id(tool.Ifc.get())`` changes,
          drop the now-stale ``_owned`` table (the regions from the old
          screen were freed) and rehydrate clip boxes from the new
          project's ``BBIM_ClipBoxes`` pset.
        - **Collection-to-list sync**: catches clip-box empties created
          outside ``bim.add_clip_box`` / ``bim.duplicate_clip_box`` —
          notably Bonsai's Shift+D / Alt+D / Ctrl+Shift+D macros, which
          deep-copy the source's ``BIMClipBoxProperties`` (including
          ``is_clip_box=True``) but don't register the copy with us.
          Detection lives here so any future entry path is handled too.
        - **Live preview safety net**: re-applies the clip planes from
          the active box's evaluated matrix. ``on_pre_view`` is the
          primary live-preview path; this is what catches matrix changes
          outside any modal (Python set, undo, constraint update).
        - **Pset persistence**: when ``obj.matrix_world`` differs from
          the last persisted snapshot, write it to the project pset.
          Blender's G/R/S modal only commits ``matrix_world`` on release,
          so this branch fires once per commit — exactly the cadence the
          user expects for "save my latest transform".
        """
        # During the file-load danger window (load_pre → first paint of the
        # new file) the screen exists but its regions' GPU contexts are not
        # yet wired; calling apply_clip_planes_direct here drives
        # RegionView3D.update() into a CTD inside GPU_matrix_ortho_set.
        # on_pre_view will reopen this gate on first paint.
        if cls._file_loading:
            return
        if getattr(bpy.context, "screen", None) is None:
            return
        if cls._active_scene_props(scene) is None:
            return
        ifc_file = tool.Ifc.get()
        ifc_id = id(ifc_file) if ifc_file is not None else 0
        if ifc_id != cls._last_seen_ifc_id:
            cls._last_seen_ifc_id = ifc_id
            cls._owned.clear()
            cls._region_by_key.clear()
            cls._view_matrix_at_arm.clear()
            cls._persisted_matrices.clear()
            cls._last_seen_object_matrices.clear()
            if ifc_file is not None:
                cls.load_from_project_pset(scene)
                # .blend carries use_clip_planes / clip_bb forward; the
                # C-side picker is armed for the prior session's view.
                # Re-arm against the current view so click-select matches
                # what the user sees.
                cls.schedule_refresh()
        # Orphan-empty adoption is deferred while a transform modal is
        # dragging so the active-index change on adoption can't disrupt
        # the move.
        if not tool.Blender.is_transform_modal_active(bpy.context):
            cls._sync_collection_to_list(scene)
        obj = cls.get_active_clip_box(scene)
        if obj is None:
            return

        current_matrix = tuple(tuple(row) for row in obj.matrix_world)
        prev_matrix = cls._persisted_matrices.get(obj.name)
        if prev_matrix != current_matrix:
            cls._persisted_matrices[obj.name] = current_matrix
            # Only persist when an IFC file is loaded; otherwise the box
            # is purely Blender-side and there's nothing to write to.
            # Mark dirty here, FLUSH below — the gate suppresses writes
            # while a transform modal is dragging so one drag produces
            # one save on release, not N saves per frame.
            if ifc_file is not None and prev_matrix is not None:
                cls.mark_dirty_for_save(obj.name)
            # clip_bb is stale once the box settles elsewhere. The modal
            # gate suppresses per-tick re-arms during a live drag and
            # fires once on release (or on external sets — Python, undo,
            # constraint).
            if prev_matrix is not None and not tool.Blender.is_transform_modal_active(bpy.context):
                cls.schedule_refresh()
        cls.flush_pending_saves(scene)

        try:
            eval_obj = obj.evaluated_get(depsgraph)
            matrix = eval_obj.matrix_world
        except (AttributeError, RuntimeError, ReferenceError):
            return
        cls.apply_clip_planes_direct(cls.compute_planes_from_matrix(matrix))

    @classmethod
    def on_pre_view(cls) -> None:
        """Per-redraw live preview hook.

        Installed as a ``SpaceView3D.draw_handler_add`` at ``PRE_VIEW``.
        Reads the active clip box's evaluated matrix and writes the
        clip planes to ``bpy.context.region_data`` — the region being
        rendered THIS frame, so no ``temp_override`` is needed.

        IFC pset writes are NOT performed here; that's the depsgraph
        handler's job (it fires on transform commit and writes through
        the operator transaction path).
        """
        # First paint after a file load is the GPU-ready signal: open the
        # _file_loading gate and kick a refresh so the new file's clip box
        # arms against now-safe regions. Runs BEFORE the active-clip-box
        # check so the gate clears even when the new file has no clip box
        # (otherwise the gate would deadlock until the next file load).
        if cls._post_load_paint_pending:
            cls._post_load_paint_pending = False
            cls._file_loading = False
            cls.schedule_refresh()
        if cls._active_scene_props() is None:
            return
        obj = cls.get_active_clip_box()
        if obj is None:
            return
        region_3d = getattr(bpy.context, "region_data", None)
        if region_3d is None or not region_3d.use_clip_planes:
            return
        try:
            depsgraph = bpy.context.evaluated_depsgraph_get()
            matrix = obj.evaluated_get(depsgraph).matrix_world
        except (AttributeError, RuntimeError, ReferenceError):
            return
        region_3d.clip_planes = cls.compute_planes_from_matrix(matrix)
        # PRE_VIEW runs for the region being drawn this frame (always sized
        # and renderable), so the collapsed-region CTD can't occur here.
        # The suppress only mops up a catchable RuntimeError / ReferenceError
        # from a region freed mid-draw — same as the arm paths.
        with contextlib.suppress(RuntimeError, ReferenceError):
            region_3d.update()
        # clip_bb captured by view3d.clip_border is view-aligned, so an
        # orbit/pan/zoom leaves the picker testing against the old
        # frustum even after clip_planes refresh. Re-arm so the picker
        # matches the current view.
        region = getattr(bpy.context, "region", None)
        if region is not None:
            key = region.as_pointer()
            prev_view = cls._view_matrix_at_arm.get(key)
            current_view = tuple(tuple(row) for row in region_3d.view_matrix)
            if prev_view is not None and prev_view != current_view:
                cls.schedule_refresh()

    @classmethod
    def create_clip_box_empty(
        cls,
        context: bpy.types.Context,
        matrix: Any,
        name: str = "ClipBox",
    ) -> bpy.types.Object:
        """Create + register a clip-box empty whose ``matrix_world`` is ``matrix``.

        Single entry point for any operator that needs to materialise a
        clip box: handles the host collection, the per-object
        ``is_clip_box`` flag, the scene-list entry, auto-enable, viewport
        re-arm, and project-pset persistence. Returns the new empty.
        """
        scene_props = cls.get_scene_props(context.scene)

        obj = bpy.data.objects.new(name, None)
        obj.empty_display_type = "CUBE"
        obj.empty_display_size = 1.0
        obj.show_in_front = True
        obj.matrix_world = matrix

        collection = tool.Blender.get_or_create_collection(context.scene, cls.COLLECTION_NAME)
        collection.objects.link(obj)

        cls.get_object_props(obj).is_clip_box = True

        entry = scene_props.clip_boxes.add()
        entry.obj = obj
        scene_props.active_clip_box_index = len(scene_props.clip_boxes) - 1
        # Auto-enable so the user sees the cut immediately rather than
        # having to find the panel toggle after the add.
        scene_props.enabled = True

        tool.Blender.set_active_object(obj)
        cls.refresh(context.scene)
        # Project-level pset rather than a per-entity placement so IfcRoot's
        # scale-strip-on-export can't lose the box's dimensions.
        cls.save_to_project_pset(context.scene)
        return obj

    # ------------------------------------------------------------------
    # Source-based presets
    #
    # Build the host empty's ``matrix_world`` from a chosen IFC source
    # (a spatial container, a type, a material, a drawing, …) so the
    # user gets a clip box pre-sized to the AABB of the matched
    # elements instead of having to drag a default cube into position.
    # ------------------------------------------------------------------

    @classmethod
    def iter_elements_for_source(cls, kind: str, source_id: str) -> list[Any]:
        """Resolve the IFC products matching ``(kind, source_id)``.

        ``kind`` selects the IFC-graph walk; ``source_id`` is the picker
        value: an IFC entity id (stringified) for the entity-driven
        kinds, or one of :data:`SOURCE_STATUS_VALUES` for ``"STATUS"``.

        Empty list when the IFC file is absent, ``source_id`` does not
        resolve, or the walk has no matches. ``"DRAWING"`` returns the
        single drawing entity so callers can introspect it; the actual
        clip volume for that kind is built from the camera frustum, not
        an AABB of decomposed elements.
        """
        import ifcopenshell.util.element

        ifc_file = tool.Ifc.get()
        if ifc_file is None:
            return []

        if kind == "STATUS":
            if source_id not in SOURCE_STATUS_VALUES:
                return []
            return list(tool.Sequence.get_elements_by_status(source_id))

        if kind == "CLASS":
            # source_id is an IFC class name (e.g. "IfcWall"). by_type with
            # include_subtypes=True (default) so "IfcWall" matches
            # IfcWallStandardCase etc., matching "all walls" in user terms.
            try:
                return list(ifc_file.by_type(source_id))
            except RuntimeError:
                return []

        try:
            entity_id = int(source_id)
        except (TypeError, ValueError):
            return []
        try:
            entity = ifc_file.by_id(entity_id)
        except RuntimeError:
            return []
        if entity is None:
            return []

        if kind == "SPATIAL":
            return list(ifcopenshell.util.element.get_decomposition(entity, is_recursive=True))
        if kind == "TYPE":
            return list(ifcopenshell.util.element.get_types(entity))
        if kind == "MATERIAL":
            return list(ifcopenshell.util.element.get_elements_by_material(ifc_file, entity))
        if kind == "PROFILE":
            return list(ifcopenshell.util.element.get_elements_by_profile(entity))
        if kind in ("SYSTEM", "GROUP", "ZONE"):
            return list(ifcopenshell.util.element.get_grouped_by(entity, is_recursive=True))
        if kind == "DRAWING":
            return [entity]
        return []

    @classmethod
    def compute_matrix_for_source(cls, kind: str, source_id: str) -> Optional[Any]:
        """Build the empty's ``matrix_world`` for ``(kind, source_id)``.

        Returns ``None`` when nothing matches — the operator turns that
        into an ERROR report + ``CANCELLED``.

        ``"DRAWING"`` returns a rotated matrix aligned to the camera and
        sized to ``clip_start..clip_end`` × the drawing's in-plane
        extents. All other kinds return an axis-aligned matrix sized to
        the world AABB of the matched elements' Blender objects.
        """
        if kind == "DRAWING":
            ifc_file = tool.Ifc.get()
            if ifc_file is None:
                return None
            try:
                entity = ifc_file.by_id(int(source_id))
            except (TypeError, ValueError, RuntimeError):
                return None
            camera_obj = tool.Ifc.get_object(entity)
            if camera_obj is None or camera_obj.type != "CAMERA":
                return None
            return cls._camera_frustum_matrix(camera_obj)

        elements = cls.iter_elements_for_source(kind, source_id)
        return cls._world_bbox_matrix_for_elements(elements)

    @classmethod
    def _world_bbox_matrix_for_elements(cls, elements: Iterable[Any]) -> Optional[Any]:
        """World-AABB matrix of the Blender objects backing ``elements``.

        ``matrix_world = Translation(center) @ Diagonal(half_extents)``
        so the CUBE empty's local ``[-1, +1]^3`` lands on the AABB
        corners. Filters out elements without a Blender object and
        elements whose object has a zero-volume bound box (typical for
        empties used as containers). Returns ``None`` when nothing
        survives the filter so the caller can ERROR instead of creating
        a degenerate clip box.

        Half-extents are floored at :data:`_CLIP_EXPAND_ABS` so a single
        point or flat slab still produces an invertible matrix.
        """
        from mathutils import Matrix

        min_x = min_y = min_z = float("inf")
        max_x = max_y = max_z = float("-inf")
        found = False
        for element in elements:
            obj = tool.Ifc.get_object(element)
            if obj is None:
                continue
            bbox = tool.Blender.get_object_world_bounding_box(obj)
            if bbox["dimensions"] == (0.0, 0.0, 0.0):
                continue
            min_x = min(min_x, bbox["min_x"])
            min_y = min(min_y, bbox["min_y"])
            min_z = min(min_z, bbox["min_z"])
            max_x = max(max_x, bbox["max_x"])
            max_y = max(max_y, bbox["max_y"])
            max_z = max(max_z, bbox["max_z"])
            found = True
        if not found:
            return None
        cx, cy, cz = (min_x + max_x) / 2, (min_y + max_y) / 2, (min_z + max_z) / 2
        hx = max((max_x - min_x) / 2, _CLIP_EXPAND_ABS)
        hy = max((max_y - min_y) / 2, _CLIP_EXPAND_ABS)
        hz = max((max_z - min_z) / 2, _CLIP_EXPAND_ABS)
        return Matrix.Translation((cx, cy, cz)) @ Matrix.Diagonal((hx, hy, hz, 1.0))

    @classmethod
    def _camera_frustum_matrix(cls, camera_obj: bpy.types.Object) -> Optional[Any]:
        """Rotated matrix matching the camera frustum ``clip_start..clip_end``.

        Bonsai's drawing module parameterises a drawing camera's frustum
        via ``BIMCameraProperties.width`` and ``.height`` (the printed
        extents in world units). The CUBE empty inherits the camera's
        rotation; depth spans ``[clip_start, clip_end]`` along the
        camera's local −Z (Blender cameras look down −Z).

        Returns ``None`` when the camera has no usable drawing extents —
        the operator surfaces that as an ERROR + ``CANCELLED``.
        """
        from mathutils import Matrix

        cam_data = camera_obj.data
        cam_props = getattr(cam_data, "BIMCameraProperties", None)
        if cam_props is None:
            return None
        width = float(getattr(cam_props, "width", 0.0) or 0.0)
        height = float(getattr(cam_props, "height", 0.0) or 0.0)
        if width <= 0.0 or height <= 0.0:
            return None

        clip_start = float(getattr(cam_data, "clip_start", 0.0))
        clip_end = float(getattr(cam_data, "clip_end", 1.0))

        x_half = max(width / 2.0, _CLIP_EXPAND_ABS)
        y_half = max(height / 2.0, _CLIP_EXPAND_ABS)
        z_half = max((clip_end - clip_start) / 2.0, _CLIP_EXPAND_ABS)
        z_center = -(clip_start + clip_end) / 2.0
        offset = Matrix.Translation((0.0, 0.0, z_center)) @ Matrix.Diagonal((x_half, y_half, z_half, 1.0))
        return camera_obj.matrix_world @ offset

    # ------------------------------------------------------------------
    # Cross-section caps
    #
    # When the clip box is enabled, each IfcProduct mesh that crosses
    # the box gets a "cap" polygon drawn where its geometry intersects
    # a clip plane — so cut surfaces appear filled instead of hollow.
    # The pipeline (``bmesh.ops.bisect_plane(clear_outer=True)`` per
    # plane, then ``bmesh.ops.contextual_create`` to fill cut edges)
    # runs on a temp BMesh per object so the source mesh is untouched.
    # ------------------------------------------------------------------

    @classmethod
    def _compute_caps_for_object(
        cls,
        obj: bpy.types.Object,
        world_planes: PlaneSet,
        depsgraph: Optional[Any] = None,
        *,
        world_matrix: Optional[Matrix] = None,
    ) -> list[tuple[float, float, float]]:
        """Return triangle vertices for ``obj``'s cap polygons.

        Flat list of ``(x, y, z)`` tuples in world space, ready for a
        ``batch_for_shader("TRIS", ...)`` upload. Empty when the
        object's bound box doesn't cross any clip plane.

        Uses the evaluated mesh (modifier stack applied) when a
        ``depsgraph`` is passed, so caps match the rendered geometry of
        objects with subsurf / boolean / mirror modifiers. Falls back to
        ``obj.data`` only for callers without a depsgraph (e.g. unit
        tests that fabricate a mesh outside any eval context).

        ``world_matrix`` overrides ``obj.matrix_world`` for the local↔world
        transform. Used by the linked-IFC path where the effective world
        placement of a library-linked mesh is the instance empty's
        ``matrix_world`` composed with the inner mesh's own matrix, not
        the linked object's own ``matrix_world`` (which is library-local).
        When supplied, the depsgraph path is skipped — library-linked
        objects aren't part of the active scene's depsgraph and their
        Bonsai-baked meshes don't carry modifier stacks anyway.
        """
        import bmesh
        from mathutils import Vector

        mw = world_matrix if world_matrix is not None else obj.matrix_world

        bm = bmesh.new()
        eval_obj = None
        try:
            if depsgraph is not None and world_matrix is None:
                try:
                    eval_obj = obj.evaluated_get(depsgraph)
                    mesh = eval_obj.to_mesh()
                    bm.from_mesh(mesh)
                except (RuntimeError, ReferenceError):
                    return []
            else:
                try:
                    bm.from_mesh(obj.data)
                except (RuntimeError, ReferenceError):
                    return []

            ws_to_ls = mw.inverted_safe()
            rot = ws_to_ls.to_quaternion()
            planes_local = []
            for plane in world_planes:
                inward_world = Vector(plane[:3])
                d = plane[3]
                point_on_plane_world = inward_world * -d
                plane_co_local = ws_to_ls @ point_on_plane_world
                # bisect_plane removes the +plane_no side when clear_outer=True;
                # our inward normal points INTO the box, so we negate to clear
                # the box's outside.
                plane_no_local = (rot @ -inward_world).normalized()
                planes_local.append((plane_co_local, plane_no_local))

            cap_layer = tool.Geometry.bisect_and_cap(bm, planes_local)
            if cap_layer is None:
                return []

            cap_faces = [f for f in bm.faces if f.is_valid and f[cap_layer]]
            if not cap_faces:
                return []

            return cls._triangulate_cap_faces(cap_faces, mw)
        finally:
            bm.free()
            if eval_obj is not None:
                with contextlib.suppress(RuntimeError, ReferenceError, AttributeError):
                    eval_obj.to_mesh_clear()

    @classmethod
    def _iter_capable_objects(cls, scene: bpy.types.Scene) -> Iterator[bpy.types.Object]:
        """Yield mesh objects eligible for capping.

        When ``clip_only_ifc_products`` is set (default), limits to
        ``IfcElement`` (walls, slabs, doors, windows, …) so spatial
        structure (``IfcSpace``, ``IfcBuildingStorey``, ``IfcSite``) and
        annotations / grids never get capped — they're non-physical
        containers / overlays that shouldn't sprout solid fill polygons
        at clip boundaries.

        When unset, any visible mesh in the scene is eligible regardless
        of IFC association — useful for clipping Blender-side reference
        geometry alongside a loaded IFC.
        """
        scene_props = cls.get_scene_props(scene)
        only_ifc = scene_props.clip_only_ifc_products
        if only_ifc and tool.Ifc.get() is None:
            return
        for obj in scene.objects:
            if obj.type != "MESH" or obj.data is None:
                continue
            if not obj.visible_get():
                continue
            if only_ifc:
                entity = tool.Ifc.get_entity(obj)
                if entity is None or not entity.is_a("IfcElement"):
                    continue
            yield obj

    @classmethod
    def _iter_linked_ifc_capable_meshes(
        cls, scene: bpy.types.Scene
    ) -> Iterator[tuple[bpy.types.Object, bpy.types.Object, Matrix]]:
        """Yield ``(instance_empty, inner_mesh, effective_world_matrix)``
        for meshes inside loaded Project ▸ Links collection-instance empties.

        Gated by ``BIMSceneClipBoxProperties.include_linked_ifc``: returns
        nothing when the toggle is off so the main cap path stays untouched.

        The effective world matrix is ``instance.matrix_world @
        inner.matrix_world`` — the inner object's own ``matrix_world`` is
        library-local (positioned relative to the linked collection's
        origin), so the instance empty's placement has to be prepended to
        land the cap at the right place in the active scene.
        """
        scene_props = cls.get_scene_props(scene)
        if not scene_props.include_linked_ifc:
            return
        project_props = tool.Project.get_project_props()
        for link in project_props.get_loaded_links():
            instance = tool.Project.get_link_empty_handle(link)
            if instance is None or instance.instance_collection is None:
                continue
            if not instance.visible_get():
                continue
            instance_mw = instance.matrix_world
            for inner in instance.instance_collection.all_objects:
                if inner.type != "MESH" or inner.data is None:
                    continue
                yield instance, inner, instance_mw @ inner.matrix_world

    @classmethod
    def invalidate_cap_cache(cls, *, immediate: bool = False) -> None:
        """Drop the cap cache and schedule a fresh rebuild.

        Public entry point for property-update callbacks (or any external
        change to eligibility / clip-box selection) so callers don't reach
        into the private cache state directly. Pass ``immediate=True`` for
        UI-driven changes that should rebuild on the next idle tick
        without waiting for the depsgraph-debounce window.
        """
        cls._cap_cache.clear()
        cls._last_cap_clip_box_hash = 0
        cls._schedule_cap_rebuild(interval=0.0 if immediate else None)

    @classmethod
    def rebuild_caps_now(cls, scene: Optional[bpy.types.Scene] = None) -> None:
        """Drop the cap cache and rebuild SYNCHRONOUSLY, then redraw.

        Public entry point for interactive end-of-drag handlers (e.g. the
        face-resize gizmo group) where the user expects the caps to
        re-form the instant they release the handle — without the
        debounce window the depsgraph path inserts.
        """
        cls._cancel_pending_cap_rebuild()
        cls._cap_cache.clear()
        cls._last_cap_clip_box_hash = 0
        cls.rebuild_cap_cache(scene)
        for _area, region, _region_3d in tool.Blender.iter_view3d_regions():
            region.tag_redraw()

    @classmethod
    def rebuild_cap_cache(
        cls,
        scene: Optional[bpy.types.Scene] = None,
        depsgraph: Optional[Any] = None,
    ) -> None:
        """Recompute the per-object cap-vertex cache from the active clip box.

        No-op while a transform modal is dragging ``matrix_world`` — the
        existing cache stays in place and the user sees stale caps until
        the drag commits. Per-object cache entries are reused when the
        object's mesh, world matrix, and the clip-box matrix all match
        the prior key. Stale entries (deleted objects, disabled box,
        unloaded IFC) are pruned.

        When ``depsgraph`` is supplied (the typical handler path), per-mesh
        caps are computed from the evaluated mesh so modifier stacks are
        honoured; without it, raw source meshes are used.
        """
        scene_props = cls._active_scene_props(scene)
        if scene_props is None or not scene_props.show_caps:
            cls._cap_cache.clear()
            cls._last_cap_clip_box_hash = 0
            return
        if scene is None:
            scene = bpy.context.scene
        active = cls.get_active_clip_box(scene)
        if active is None:
            cls._cap_cache.clear()
            cls._last_cap_clip_box_hash = 0
            return
        if tool.Blender.is_transform_modal_active(bpy.context):
            return

        # Cap with the SAME expanded planes the viewport clips against
        # (cls.compute_planes applies the _CLIP_EXPAND_ABS margin), so the
        # cap face lines up with the visible cut. Using the un-expanded
        # planes would leave a visible margin-sized gap between the cut
        # mesh edge and the cap.
        world_planes = cls.compute_planes(active)
        clip_box_hash = hash(world_planes)
        cls._last_cap_clip_box_hash = clip_box_hash

        from mathutils import Vector

        live_names: set[str] = set()
        for obj in cls._iter_capable_objects(scene):
            live_names.add(obj.name)
            mesh = obj.data
            cache_key = (
                getattr(mesh, "session_uid", id(mesh)),
                tool.Blender.hash_matrix(obj.matrix_world),
                clip_box_hash,
            )
            cached = cls._cap_cache.get(obj.name)
            if cached is not None and cached[0] == cache_key:
                continue
            # Cheap AABB-vs-clip-box rejection before the expensive bisect.
            # bound_box has 8 corners in object-local space — transform to
            # world and check whether they're all on the outside of any
            # clip plane. If so, the mesh can't produce a cap from this
            # box and we skip the per-mesh bisect.
            mw = obj.matrix_world
            world_corners = [mw @ Vector(c) for c in obj.bound_box]
            if not tool.Cad.corners_might_cross_clip_planes(world_planes, world_corners):
                cls._cap_cache[obj.name] = (cache_key, None)
                continue
            verts = cls._compute_caps_for_object(obj, world_planes, depsgraph=depsgraph)
            batch = cls._build_cap_batch(verts) if verts else None
            cls._cap_cache[obj.name] = (cache_key, batch)

        # Linked-IFC inner meshes (gated by include_linked_ifc). The
        # ``link:`` prefix on the cache name namespaces them so they
        # cannot collide with a scene-object named identically.
        for instance, inner, world_matrix in cls._iter_linked_ifc_capable_meshes(scene):
            cache_name = f"link:{instance.name}:{inner.name}"
            live_names.add(cache_name)
            mesh = inner.data
            cache_key = (
                getattr(mesh, "session_uid", id(mesh)),
                tool.Blender.hash_matrix(world_matrix),
                clip_box_hash,
            )
            cached = cls._cap_cache.get(cache_name)
            if cached is not None and cached[0] == cache_key:
                continue
            world_corners = [world_matrix @ Vector(c) for c in inner.bound_box]
            if not tool.Cad.corners_might_cross_clip_planes(world_planes, world_corners):
                cls._cap_cache[cache_name] = (cache_key, None)
                continue
            verts = cls._compute_caps_for_object(inner, world_planes, depsgraph=depsgraph, world_matrix=world_matrix)
            batch = cls._build_cap_batch(verts) if verts else None
            cls._cap_cache[cache_name] = (cache_key, batch)

        for name in list(cls._cap_cache):
            if name not in live_names:
                cls._cap_cache.pop(name)
        for name in list(cls._last_seen_object_matrices):
            if name not in live_names:
                cls._last_seen_object_matrices.pop(name)

    @staticmethod
    def _build_cap_batch(verts: list[tuple[float, float, float]]):
        """Bake ``verts`` into a GPU ``TRIS`` batch bound to ``UNIFORM_COLOR``."""
        import gpu
        from gpu_extras.batch import batch_for_shader

        shader = gpu.shader.from_builtin("UNIFORM_COLOR")
        return batch_for_shader(shader, "TRIS", {"pos": verts})

    @classmethod
    def _triangulate_cap_faces(cls, cap_faces, mw) -> list[tuple[float, float, float]]:
        """Triangulate cap faces and return world-space triangle vertices.

        Each cap face is tessellated as a single simple ring via
        :meth:`tool.Cad.tessellate_ring_planar`. Nested cap polygons
        (hollow profiles — annular columns, pipe walls) render as solid
        discs in v1; proper polygon-with-holes triangulation is a known
        limitation and a follow-up.
        """
        verts: list[tuple[float, float, float]] = []
        for face in cap_faces:
            if not face.is_valid or len(face.verts) < 3:
                continue
            ring = [v.co.copy() for v in face.verts]
            try:
                tri_indices = tool.Cad.tessellate_ring_planar([ring])
            except Exception:
                continue
            for i, j, k in tri_indices:
                for idx in (i, j, k):
                    w = mw @ ring[idx]
                    verts.append((w.x, w.y, w.z))
        return verts

    @classmethod
    def on_depsgraph_update_caps(cls, scene, depsgraph) -> None:
        """Depsgraph entry-point — guard, then delegate to the
        modal-aware debounce in :meth:`_handle_cap_tick`."""
        if getattr(bpy.context, "screen", None) is None:
            return
        if cls._active_scene_props(scene) is None:
            return
        # Edit mode (mesh / curve / armature / …) fires depsgraph
        # constantly as the user manipulates verts/edges; the cap view
        # isn't the focus of that work, and the caps would flash off on
        # every nudge. Skip scheduling entirely while in any edit mode.
        if tool.Blender.is_in_edit_mode():
            return
        cls._handle_cap_tick(scene, depsgraph)

    @classmethod
    def _handle_cap_tick(cls, scene, depsgraph) -> None:
        """Schedule (or immediately fire) a cap-cache rebuild.

        Strategy:
        - Default: debounce. Each depsgraph tick reschedules a
          ``bpy.app.timers`` callback ``_CAP_REBUILD_DEBOUNCE_SECONDS``
          in the future, so a burst of ticks from an unknown-to-Bonsai
          drag (external-addon gizmo, scripted property updates) collapses
          to a single rebuild after the storm subsides. Drag is smooth,
          caps catch up shortly after release.
        - Fast path: when a *known* transform modal (Bonsai G/R/S) just
          finished — detected as a True→False transition on
          ``is_transform_modal_active`` — cancel any pending timer and
          rebuild immediately, preserving the snappy on-release feel for
          Bonsai-internal drags.
        - Skip path: depsgraph ticks fire for selection-only changes,
          UI events, undo writes, etc. — none of which can move a cap.
          When no update in the tick carries ``is_updated_geometry`` or
          ``is_updated_transform``, return without scheduling so the
          cache and its hide-while-pending gate don't churn for free.
        """
        is_modal = tool.Blender.is_transform_modal_active(bpy.context)
        modal_just_ended = cls._last_modal_state and not is_modal
        cls._last_modal_state = is_modal

        if modal_just_ended:
            cls._cancel_pending_cap_rebuild()
            cls.rebuild_cap_cache(scene, depsgraph=depsgraph)
            return

        if depsgraph is not None and not cls._depsgraph_has_relevant_changes(depsgraph):
            return

        cls._schedule_cap_rebuild()

    @classmethod
    def _depsgraph_has_relevant_changes(cls, depsgraph) -> bool:
        """True iff the tick carries an Object geometry change, or an
        Object transform update whose ``matrix_world`` actually moved.

        Blender raises ``is_updated_transform`` on the selected Object
        itself even for plain selection changes (no matrix delta), and
        on Scene / ViewLayer IDs for the same. We'd schedule (and hide
        caps for) every click without this check. Comparing a matrix
        hash against a per-object baseline filters selection noise
        without requiring opt-in from external addons.

        First time we see an Object the hash is recorded as baseline
        (no flag), so an addon-load-time selection burst doesn't fire
        a phantom rebuild; subsequent real moves are detected on the
        first tick the matrix actually differs.
        """
        relevant = False
        for upd in depsgraph.updates:
            obj = upd.id
            if not isinstance(obj, bpy.types.Object):
                continue
            if upd.is_updated_geometry:
                relevant = True
                continue
            if not upd.is_updated_transform:
                continue
            new_hash = tool.Blender.hash_matrix(obj.matrix_world)
            old_hash = cls._last_seen_object_matrices.get(obj.name)
            cls._last_seen_object_matrices[obj.name] = new_hash
            if old_hash is not None and old_hash != new_hash:
                relevant = True
        return relevant

    @classmethod
    def _schedule_cap_rebuild(cls, *, interval: Optional[float] = None) -> None:
        """(Re)schedule the deferred cap rebuild.

        Each call cancels any pending timer and registers a fresh one
        so a burst of updates collapses to a single rebuild once the
        debounce window of quiet elapses. Pass ``interval=0.0`` for
        next-tick rebuild without debounce (UI-driven changes that
        only fire on explicit user action, not depsgraph bursts).
        """
        cls._cancel_pending_cap_rebuild()
        delay = interval if interval is not None else cls._CAP_REBUILD_DEBOUNCE_SECONDS

        def _do_rebuild() -> None:
            cls._pending_cap_rebuild = None
            try:
                cls.rebuild_cap_cache()
            except Exception:
                # bpy.app.timers swallows exceptions silently, leaving
                # the user with stale caps + no diagnostic. Surface to
                # the console so future bisect / cap edge cases are
                # debuggable instead of mysteriously invisible.
                import traceback

                traceback.print_exc()
            # Timer fires from the main loop without an accompanying
            # depsgraph tick, so the viewport won't repaint on its own;
            # nudge every region so the freshly-baked cap batches show
            # up without the user having to wiggle the mouse.
            for _area, region, _region_3d in tool.Blender.iter_view3d_regions():
                region.tag_redraw()
            return None

        bpy.app.timers.register(_do_rebuild, first_interval=delay)
        cls._pending_cap_rebuild = _do_rebuild

    @classmethod
    def _cancel_pending_cap_rebuild(cls) -> None:
        """Cancel any pending debounced rebuild so the next event source
        gets a clean slate. Idempotent and safe to call when none is
        registered (e.g. on addon unregister)."""
        pending = cls._pending_cap_rebuild
        if pending is not None and bpy.app.timers.is_registered(pending):
            bpy.app.timers.unregister(pending)
        cls._pending_cap_rebuild = None

    @classmethod
    def on_post_view_caps(cls) -> None:
        """Draw cached cap batches over the clipped geometry.

        Installed as a ``SpaceView3D.draw_handler_add`` at ``POST_VIEW``.
        Caps render with depth-test + depth-write enabled so any
        geometry in front of the cap occludes it — without this the
        ``UNIFORM_COLOR`` shader defaults to no-depth and the caps
        would always paint on top of the scene. One ``batch.draw`` per
        object; batches are pre-baked.
        """
        if not cls._cap_cache:
            return
        scene_props = cls._active_scene_props()
        if scene_props is None or not scene_props.show_caps:
            return
        # Hide caps while in edit mode — the user's focus is on
        # vert/edge/face manipulation, not the section view; the cache
        # is also frozen by the same gate in the depsgraph path.
        if tool.Blender.is_in_edit_mode():
            return
        # Hide caps for the duration of any G/R/S to suppress mid-drag
        # visual jitter; the cache is also frozen by the same gate so
        # anything drawn here would be stale relative to the live mesh.
        if tool.Blender.is_transform_modal_active(bpy.context):
            return
        # Hide caps while a debounced rebuild is in flight (typical
        # cause: external-addon gizmo drag). The cache may reflect a
        # frame from earlier in the drag; drawing it would look stale
        # against the geometry the user is currently mutating.
        if cls._pending_cap_rebuild is not None:
            return
        import gpu

        prefs = tool.Blender.get_addon_preferences()
        cap_color = tuple(prefs.clip_box_cap_color)
        shader = gpu.shader.from_builtin("UNIFORM_COLOR")
        shader.bind()
        shader.uniform_float("color", cap_color)
        prev_depth_test = gpu.state.depth_test_get()
        prev_depth_mask = gpu.state.depth_mask_get()
        gpu.state.depth_test_set("LESS_EQUAL")
        gpu.state.depth_mask_set(True)
        try:
            for _key, batch in cls._cap_cache.values():
                if batch is None:
                    continue
                batch.draw(shader)
        finally:
            gpu.state.depth_mask_set(prev_depth_mask)
            gpu.state.depth_test_set(prev_depth_test)
