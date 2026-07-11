# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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
# This file was modified with the assistance of an AI coding tool.

from __future__ import annotations

import contextlib
import importlib
import math
import os
import platform
import subprocess
import sys
import tempfile
import traceback
import types
from collections.abc import (
    Callable,
    Generator,
    Iterable,
    Iterator,
    Mapping,
    Sequence,
    Sized,
)
from datetime import datetime
from functools import cache, lru_cache
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Literal,
    NamedTuple,
    Optional,
    TypeVar,
    Union,
    assert_never,
)

import bmesh
import bpy
import gpu
import ifcopenshell.util.element
import numpy as np
import numpy.typing as npt
from gpu_extras.batch import batch_for_shader
from ifcopenshell import entity_instance
from mathutils import Matrix, Vector

import bonsai.bim
import bonsai.core.tool
import bonsai.tool as tool

if TYPE_CHECKING:
    import bpy.stub_internal.rna_enums as rna_enums
    from sun_position.properties import SunPosProperties

    from bonsai.bim.ifc import IFC_CONNECTED_TYPE
    from bonsai.bim.module.attribute.prop import BIMAttributeProperties
    from bonsai.bim.module.constraint.prop import (
        BIMConstraintProperties,
        BIMObjectConstraintProperties,
    )
    from bonsai.bim.module.covetool.prop import CoveToolProperties
    from bonsai.bim.module.csv.prop import CsvProperties
    from bonsai.bim.module.diff.prop import DiffProperties
    from bonsai.bim.module.fm.prop import BIMFMProperties
    from bonsai.bim.module.light.prop import (
        BIMSolarProperties,
        RadianceExporterProperties,
    )
    from bonsai.bim.prop import (
        BIMAreaProperties,
        BIMCollectionProperties,
        BIMObjectProperties,
        BIMProperties,
        BIMTabProperties,
    )

    T = TypeVar("T")

VIEWPORT_ATTRIBUTES = [
    "view_matrix",
    "view_distance",
    "view_perspective",
    "use_box_clip",
    "use_clip_planes",
    "is_perspective",
    "show_sync_view",
    "clip_planes",
]

OBJECT_DATA_TYPE = Union[bpy.types.Mesh, bpy.types.Curve, bpy.types.Camera]

_RAILING_MODIFIER_IFC_CLASSES = ("IfcRailing", "IfcRailingType")
_STAIR_MODIFIER_IFC_CLASSES = (
    "IfcStairFlight",
    "IfcStairFlightType",
    "IfcMember",
    "IfcMemberType",
    "IfcStair",
    "IfcStairType",
)
_WINDOW_MODIFIER_IFC_CLASSES = ("IfcWindow", "IfcWindowType", "IfcWindowStyle")
_DOOR_MODIFIER_IFC_CLASSES = ("IfcDoor", "IfcDoorType", "IfcDoorStyle")
_ROOF_MODIFIER_IFC_CLASSES = ("IfcRoof", "IfcRoofType")


class Blender(bonsai.core.tool.Blender):
    OBJECT_TYPES_THAT_SUPPORT_EDIT_MODE = ("MESH", "CURVE", "SURFACE", "META", "FONT", "LATTICE", "ARMATURE")
    OBJECT_TYPES_THAT_SUPPORT_EDIT_GPENCIL_MODE = ("GPENCIL",)
    TYPE_MANAGER_ICON = "LIGHTPROBE_VOLUME"
    SEQUENCE_COLOR_SCHEME_ICON: Literal["STRIP_COLOR_03"] = (  # pyright: ignore[reportAssignmentType]
        "STRIP_COLOR_03" if bpy.app.version >= (4, 4, 0) else "SEQUENCE_COLOR_04"
    )

    BLENDER_ENUM_ITEM = Union[tuple[str, str, str], tuple[str, str, str, int], tuple[str, str, str, str, int], None]
    """
    Options:

    - (identifier, name, description)

    - (identifier, name, description, number)

    - (identifier, name, description, icon, number)
    """
    BLENDER_ENUM_ITEMS = Iterable[BLENDER_ENUM_ITEM]
    BLENDER_5 = bpy.app.version >= (5, 0, 0)

    @classmethod
    def activate_camera(cls, obj: bpy.types.Object) -> None:

        area = cls.get_view3d_area()
        assert area
        assert isinstance((space := area.spaces[0]), bpy.types.SpaceView3D)
        is_local_view = space.local_view is not None

        assert bpy.context.screen and bpy.context.scene
        if is_local_view:
            # Turn off local view before activating drawing, and then turn it on again.
            for a in bpy.context.screen.areas:
                if a.type == "VIEW_3D":
                    override = {"area": a, "region": a.regions[-1], "space": a.spaces[0], "scene": bpy.context.scene}
                    with bpy.context.temp_override(**override):
                        bpy.ops.view3d.localview()
                    bpy.context.scene.camera = obj

        else:
            bpy.context.scene.camera = obj

        assert space.region_3d
        space.region_3d.view_perspective = "CAMERA"

    @classmethod
    def get_active_area_props(cls, context: bpy.types.Context) -> BIMAreaProperties | BIMTabProperties:
        FULLSCREEN_SUFFIX = "-nonnormal"  # Ctrl-space temporary fullscreen
        assert (screen := context.screen)
        try:
            if screen.name.endswith(FULLSCREEN_SUFFIX):
                screen = bpy.data.screens[screen.name.removesuffix(FULLSCREEN_SUFFIX)]
                # The original area object has its type changed to "EMPTY" apparently
                index = [a.type for a in screen.areas].index("EMPTY")
                return cls.get_area_props(screen)[index]
            assert (area := context.area)
            return cls.get_area_props(screen)[screen.areas[:].index(area)]
        except IndexError:
            # Fallback in case areas aren't setup yet.
            return cls.get_tab_props(screen)

    @classmethod
    def set_active_object(cls, obj: bpy.types.Object) -> None:
        """Set active object and select it."""
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

    @classmethod
    def clear_active_object(cls) -> None:
        """Clear active object, object is not unselected."""
        bpy.context.view_layer.objects.active = None

    @classmethod
    def setup_tabs(cls) -> None:
        # https://blender.stackexchange.com/questions/140644/how-can-make-the-state-of-a-boolean-property-relative-to-the-3d-view-area
        for screen in bpy.data.screens:
            area_props = cls.get_area_props(screen)
            if len(area_props) == 20:
                continue
            area_props.clear()
            for i in range(20):  # 20 is an arbitrary value of split areas
                area_props.add()

    @classmethod
    def should_show_panel(cls, context: bpy.types.Context, tab: str, panel: str) -> bool:
        aprops = cls.get_active_area_props(context)
        if aprops.path_from_id() == "BIMAreaProperties" and context.area.spaces.active.search_filter:
            return True
        if (is_bookmark_tab := aprops.tab == "BOOKMARK") or aprops.tab == tab:
            bprops = tool.Blender.get_bim_props()
            if not (panel_visibility := bprops.panel_visibilities.get(panel)):
                return not is_bookmark_tab
            if is_bookmark_tab:
                if panel_visibility.is_bookmarked:
                    return True
            elif panel_visibility.is_visible:
                return True
        return False

    @classmethod
    def is_default_scene(cls) -> bool:
        if len(bpy.context.scene.objects) != 3:
            return False
        if {obj.type for obj in bpy.context.scene.objects} == {"MESH", "LIGHT", "CAMERA"}:
            return True
        return False

    @classmethod
    def get_name(cls, ifc_class: str, name: str) -> str:
        if not bpy.data.objects.get(f"{ifc_class}/{name}"):
            return name
        i = 2
        while bpy.data.objects.get(f"{ifc_class}/{name} {i}"):
            i += 1
        return f"{name} {i}"

    @classmethod
    def get_active_object(cls, is_selected: bool = False) -> Union[bpy.types.Object, None]:
        """Return the active object, or ``None`` when the current context
        exposes neither ``active_object`` nor a ``view_layer`` (stripped
        operator contexts).

        :param is_selected: If true, the active object also needs to be selected.
        """
        obj = getattr(bpy.context, "active_object", None)
        if obj is None:
            view_layer = getattr(bpy.context, "view_layer", None)
            if view_layer is not None:
                obj = view_layer.objects.active
        if obj is None:
            return None
        if is_selected and not obj.select_get():
            return None
        return obj

    @classmethod
    def get_selected_objects(cls, include_active: bool = True) -> set[bpy.types.Object]:
        """Get selected objects

        :param include_active: If true, the active object is included regardless if it is also selected.
        """
        if selected_objects := getattr(bpy.context, "selected_objects", None):
            if include_active and (active_obj := cls.get_active_object()):
                return set(selected_objects + [active_obj])
            return set(selected_objects)
        if include_active and (active_obj := cls.get_active_object()):
            return {active_obj}
        return set()

    @classmethod
    def create_ifc_object(
        cls, ifc_class: str, name: Optional[str] = None, data: Optional[OBJECT_DATA_TYPE] = None
    ) -> bpy.types.Object:
        name = name or "My " + ifc_class
        name = cls.get_name(ifc_class, name)
        obj = bpy.data.objects.new(name, data)
        bpy.ops.bim.assign_class(obj=obj.name, ifc_class=ifc_class)
        return obj

    @classmethod
    def get_obj_ifc_definition_id(
        cls,
        obj: Optional[str] = None,
        obj_type: Optional[tool.Ifc.OBJECT_TYPE] = None,
        context: Optional[bpy.types.Context] = None,
    ) -> Union[int, None]:
        # TODO: is it ever used as None?
        if obj_type is None:
            return None
        if context is None:
            context = bpy.context
        if obj_type == "Object":
            props = cls.get_object_bim_props(bpy.data.objects[obj])
            return props.ifc_definition_id
        elif obj_type == "Material":
            props = tool.Material.get_material_props()
            return props.materials[props.active_material_index].ifc_definition_id
        elif obj_type == "MaterialSetItem":
            obj_ = bpy.data.objects[obj]
            omprops = tool.Material.get_object_material_props(obj_)
            return omprops.active_material_set_item_id
        elif obj_type == "Task":
            tprops = tool.Sequence.get_task_tree_props()
            wsprops = tool.Sequence.get_work_schedule_props()
            return tprops.tasks[wsprops.active_task_index].ifc_definition_id
        elif obj_type == "Cost":
            cost_props = tool.Cost.get_cost_props()
            return cost_props.cost_items[cost_props.active_cost_item_index].ifc_definition_id
        elif obj_type == "Resource":
            active_resource = tool.Resource.get_resource_props().active_resource
            assert active_resource
            return active_resource.ifc_definition_id
        elif obj_type == "Profile":
            props = tool.Profile.get_profile_props()
            return props.profiles[props.active_profile_index].ifc_definition_id
        elif obj_type == "WorkSchedule":
            wsprops = tool.Sequence.get_work_schedule_props()
            return wsprops.active_work_schedule_id
        elif obj_type == "Group":
            props = tool.Group.get_group_props()
            assert (active_group := props.active_group)
            return active_group.ifc_definition_id
        elif obj_type == "Zone":
            props = tool.System.get_zone_props()
            assert (active_zone := props.active_zone)
            return active_zone.ifc_definition_id
        assert_never(obj_type)

    @classmethod
    def is_ifc_object(cls, obj: bpy.types.Object) -> bool:
        props = cls.get_object_bim_props(obj)
        return bool(props.ifc_definition_id)

    @classmethod
    def is_ifc_class_active(cls, ifc_class: str) -> bool:
        obj = bpy.context.active_object
        if obj:
            if cls.is_ifc_object(obj):
                return tool.Ifc.get_entity(obj).is_a(ifc_class)
            return False
        return False

    @classmethod
    def is_valid_data_block(cls, data_block: bpy.types.ID) -> bool:
        """Check if Blender data-block is still valid.

        If Blender data-block (e.g. an Object) is removed then it's
        python object gets invalidated and accessing any of it's attributes
        leads to ReferenceError: StructRNA of type Object has been removed.
        This method helps avoiding try / except ReferenceError constructions.
        """
        try:
            data_block.bl_rna
            return True
        except ReferenceError:
            return False

    @classmethod
    def show_info_message(cls, text: str, message_type: Literal["INFO", "ERROR"] = "INFO") -> None:
        """useful for showing error messages outside blender operators

        Possible `message_type`: `INFO` / `ERROR`"""

        def message_ui(self, context):
            self.layout.label(text=text)

        bpy.context.window_manager.popup_menu(message_ui, title=message_type.capitalize(), icon=message_type)

    @classmethod
    def get_view3d_area(cls) -> Union[bpy.types.Area, None]:
        assert (wm := bpy.context.window_manager)
        for window in wm.windows:
            for area in window.screen.areas:
                if area.type == "VIEW_3D":
                    return area

    @classmethod
    def operator_idname_to_py(cls, idname: str) -> str:
        """Convert a Blender internal operator idname to its Python equivalent.

        Example: ``MESH_OT_primitive_cube_add`` -> ``mesh.primitive_cube_add``
        """
        module, func = idname.split("_OT_", 1)
        return f"{module.lower()}.{func}"

    @classmethod
    def get_view3d_space(cls) -> Union[bpy.types.SpaceView3D, None]:
        if area := cls.get_view3d_area():
            space = area.spaces.active
            assert isinstance(space, bpy.types.SpaceView3D)
            return space

    @classmethod
    def get_blender_prop_default_value(cls, props: bpy.types.bpy_struct, prop_name: str) -> Any:
        prop_bl_rna = props.bl_rna.properties[prop_name]
        if getattr(prop_bl_rna, "array_length", 0) > 0:
            prop_value = prop_bl_rna.default_array
        else:
            prop_value = prop_bl_rna.default
        return prop_value

    @classmethod
    def get_viewport_context(cls) -> dict:
        """Get viewport area context for context overriding.

        Useful for calling operators outside viewport context.

        It's a bit naive since it's just taking the first available `VIEW_3D` area
        when in real life you can have a couple of those but should work for the most cases.
        """
        area = cls.get_view3d_area()
        assert area
        region = next(region for region in area.regions if region.type == "WINDOW")
        space = next(space for space in area.spaces if space.type == "VIEW_3D")
        context_override = {"area": area, "region": region, "space_data": space}

        # Need to override screen and window if area is from a different window.
        screen: bpy.types.Scene = area.id_data
        context = bpy.context
        assert context
        if context.screen != screen:
            context_override["screen"] = screen
            window = next(window for window in context.window_manager.windows if window.screen == screen)
            context_override["window"] = window
        return context_override

    @classmethod
    def get_viewport_position(cls) -> dict:
        region_3d = cls.get_viewport_context()["area"].spaces[0].region_3d
        copy_if_possible = lambda x: x.copy() if hasattr(x, "copy") else x
        viewport_data = {attr: copy_if_possible(getattr(region_3d, attr)) for attr in VIEWPORT_ATTRIBUTES}
        return viewport_data

    @classmethod
    def set_viewport_position(cls, data: dict) -> None:
        region_3d = cls.get_viewport_context()["area"].spaces[0].region_3d
        for attr in VIEWPORT_ATTRIBUTES:
            setattr(region_3d, attr, data[attr])

    @classmethod
    def set_viewport_tool(cls, tool_name: str) -> None:
        with bpy.context.temp_override(**cls.get_viewport_context()):
            bpy.ops.wm.tool_set_by_id(name=tool_name)

    @classmethod
    def are_viewport_gizmos_enabled(cls) -> bool:
        """Central gate every Bonsai gizmo poll / decorator draw checks before
        rendering. Centralises the read of
        ``gizmos.draw_gizmos_in_3d_viewport`` from addon preferences."""
        return cls.get_addon_preferences().gizmos.draw_gizmos_in_3d_viewport

    class DecoratorColors(NamedTuple):
        selected: tuple
        unselected: tuple
        special: tuple
        error: tuple
        background: tuple

    @classmethod
    def get_decorator_colors(cls) -> Blender.DecoratorColors:
        """The five ``decorator_color_*`` fields read together so each viewport
        decorator's draw callback resolves them in one call instead of five."""
        prefs = cls.get_addon_preferences()
        return cls.DecoratorColors(
            selected=prefs.decorator_color_selected,
            unselected=prefs.decorator_color_unselected,
            special=prefs.decorator_color_special,
            error=prefs.decorator_color_error,
            background=prefs.decorator_color_background,
        )

    class ViewportDecorator:
        """Shared ``SpaceView3D.draw_handler_add`` lifecycle for feature decorators.

        Single-handler subclasses set ``draw_method`` (default ``"draw"``); the
        handler binds at ``POST_VIEW``. Multi-handler subclasses set
        ``draw_methods`` to a tuple of ``(method_name, phase)`` pairs; when it
        is non-``None`` it supersedes ``draw_method``.

        Decorators whose ``install`` must accept extra arguments (e.g. a callback
        or a precomputed bmesh) override ``install`` themselves."""

        draw_method: str = "draw"
        draw_methods: tuple[tuple[str, str], ...] | None = None

        def __init_subclass__(cls, **kwargs):
            super().__init_subclass__(**kwargs)
            cls.handlers = []
            cls.is_installed = False
            # Fail loudly at class-definition time if draw_method / draw_methods
            # names an attribute the class doesn't expose. Without this, a typo
            # only surfaces on the first redraw — as a silent missing-attribute
            # handler — which may be far from the offending declaration.
            method_names = (
                tuple(name for name, _phase in cls.draw_methods) if cls.draw_methods is not None else (cls.draw_method,)
            )
            for name in method_names:
                if getattr(cls, name, None) is None:
                    raise TypeError(f"{cls.__name__}: draw method {name!r} is declared but not defined on the class")

        @classmethod
        def install(cls, context: bpy.types.Context) -> None:
            if cls.is_installed:
                cls.uninstall()
            handler = cls()
            bindings = cls.draw_methods if cls.draw_methods is not None else ((cls.draw_method, "POST_VIEW"),)
            # Rollback partial registrations on any draw_handler_add failure, so
            # cls.handlers never ends up holding a half-installed set.
            added: list = []
            try:
                for method_name, phase in bindings:
                    added.append(
                        bpy.types.SpaceView3D.draw_handler_add(
                            getattr(handler, method_name), (context,), "WINDOW", phase
                        )
                    )
            except Exception:
                for h in added:
                    try:
                        bpy.types.SpaceView3D.draw_handler_remove(h, "WINDOW")
                    except ValueError:
                        pass
                raise
            cls.handlers = added
            cls.is_installed = True

        @classmethod
        def uninstall(cls) -> None:
            for h in cls.handlers:
                try:
                    bpy.types.SpaceView3D.draw_handler_remove(h, "WINDOW")
                except ValueError:
                    pass
            cls.handlers.clear()
            cls.is_installed = False

        def draw_batch(self, shader_type, content_pos, color, indices=None):
            """Submit a GPU batch through ``self.line_shader`` (for ``"LINES"``)
            or ``self.shader`` (for any other primitive). Skips empty batches
            via ``validate_shader_batch_data`` so Blender 4.4+ doesn't crash on
            empty ``indices``. Subclasses bind both shaders in their draw method
            before calling this helper."""
            if not Blender.validate_shader_batch_data(content_pos, indices):
                return
            shader = self.line_shader if shader_type == "LINES" else self.shader
            batch = batch_for_shader(shader, shader_type, {"pos": content_pos}, indices=indices)
            shader.uniform_float("color", color)
            batch.draw(shader)

        @staticmethod
        def _lookup_active_instance(gizmo_cls: type, context: bpy.types.Context) -> Optional[Any]:
            """Return the live ``GizmoGroup`` instance registered under
            ``context.region``, or ``None`` if there isn't one. The per-region
            weakref dict on the gizmo class is populated by ``setup()``; multi-
            viewport setups put one entry per region in it so each region's
            decorator sees only its own region's hover state."""
            instances = getattr(gizmo_cls, "_active_instances", None)
            if not instances:
                return None
            region = getattr(context, "region", None)
            if region is None:
                return None
            ref = instances.get(region.as_pointer())
            if ref is None:
                return None
            return ref()

        def _cursor_icon_hovered(self, gizmo_cls: type, attr_name: str, context: bpy.types.Context) -> bool:
            """True iff the gizmo group instance in the current region exposes a gizmo
            under ``attr_name`` that reports as highlighted. Any access exception is
            swallowed so a transient bpy-state hiccup never breaks the draw loop."""
            inst = self._lookup_active_instance(gizmo_cls, context)
            if inst is None:
                return False
            try:
                return bool(getattr(inst, attr_name).is_highlight)
            except (AttributeError, ReferenceError):
                return False

        @classmethod
        def sync_all(
            cls,
            context: bpy.types.Context,
            enabled: Mapping[type[Blender.ViewportDecorator], bool],
        ) -> None:
            """Drive each listed decorator to its desired install state in one call.

            Each entry whose value is ``True`` ends up installed; each entry whose
            value is ``False`` ends up uninstalled. Pass ``True`` for always-on
            overlays so they survive subsequent file loads."""
            for decorator_cls, should_install in enabled.items():
                if should_install:
                    decorator_cls.install(context)
                else:
                    decorator_cls.uninstall()

    # Bonsai overrides Blender's default move/duplicate keymaps with macros
    # that wrap TRANSFORM_OT_translate. While a macro is the outer modal
    # entry, the inner TRANSFORM_OT_translate does not surface in
    # window.modal_operators — the macro's own idname does. The ``BIM_OT_``
    # prefix is what Blender returns from ``bl_idname`` at runtime (the
    # class declaration uses the dotted ``bim.`` form).
    BONSAI_TRANSFORM_MACROS: frozenset[str] = frozenset(
        {
            "BIM_OT_override_move_macro",  # G key
            "BIM_OT_override_object_duplicate_move_macro",  # Shift+D
            "BIM_OT_override_object_duplicate_move_linked_macro",  # Alt+D
            "BIM_OT_object_duplicate_move_linked_aggregate_macro",  # Ctrl+Shift+D
        }
    )

    @classmethod
    def is_transform_modal_active(cls, context: bpy.types.Context) -> bool:
        """True iff a Blender transform modal (G/R/S and siblings, including
        Bonsai's macro overrides) is currently driving per-frame
        ``matrix_world`` updates. Reads ``window.modal_operators`` — the
        Blender 4.2+ collection of running modal operators. Callers gate
        per-frame side effects (gizmo positioning, IFC persistence, etc.)
        on this so they don't fire during the drag.

        Falls back to scanning every window in the window manager when
        ``context.window`` is ``None`` — depsgraph callbacks run with a
        limited context where ``context.window`` is typically missing,
        but the modal is still active on one of the WM's windows.
        """
        window = getattr(context, "window", None)
        if window is not None and getattr(window, "modal_operators", None):
            windows = [window]
        else:
            wm = getattr(context, "window_manager", None) or bpy.context.window_manager
            if wm is None:
                return False
            windows = list(wm.windows)
        for w in windows:
            modal_ops = getattr(w, "modal_operators", None)
            if not modal_ops:
                continue
            for op in modal_ops:
                idname = op.bl_idname
                if idname.startswith("TRANSFORM_OT_") or idname in cls.BONSAI_TRANSFORM_MACROS:
                    return True
        return False

    @classmethod
    def is_in_edit_mode(cls, context: Optional[bpy.types.Context] = None) -> bool:
        """True iff the active object is in any edit-style mode.

        Catches every ``EDIT_*`` variant (mesh, curve, armature,
        metaball, lattice, surface, text, grease pencil). Defaults to
        ``OBJECT`` when the mode attribute is missing so background-mode
        callers (no UI context) don't false-positive.
        """
        ctx = context if context is not None else bpy.context
        mode = getattr(ctx, "mode", "OBJECT")
        return mode.startswith("EDIT_")

    @classmethod
    def iter_view3d_regions(cls) -> Iterator[tuple[bpy.types.Area, bpy.types.Region, bpy.types.RegionView3D]]:
        """Yield ``(area, region, region_3d)`` for every WINDOW region in every 3D viewport.

        Useful for features that need to act on every visible 3D viewport
        (clip planes, draw handlers, region redraw fanout). Empty
        generator when ``bpy.context.screen`` is unavailable (shutdown,
        background mode without a screen).
        """
        screen = getattr(getattr(bpy, "context", None), "screen", None)
        if screen is None:
            return
        for area in screen.areas:
            if area.type != "VIEW_3D":
                continue
            for region in area.regions:
                if region.type != "WINDOW":
                    continue
                region_3d = getattr(region, "data", None)
                if region_3d is None:
                    continue
                yield area, region, region_3d

    @classmethod
    def get_or_create_collection(cls, scene: bpy.types.Scene, name: str) -> bpy.types.Collection:
        """Return the named collection, creating + linking it to ``scene`` if absent."""
        collection = bpy.data.collections.get(name)
        if collection is None:
            collection = bpy.data.collections.new(name)
            scene.collection.children.link(collection)
        return collection

    @classmethod
    def serialize_matrix(cls, matrix: Matrix) -> str:
        """Serialize a 4x4 matrix as a 16-float comma-separated string.

        Round-trip pair with :meth:`deserialize_matrix`. Used for storing
        a matrix in an IFC pset string property without losing precision
        (``%.9g`` carries ~9 significant digits, enough for ``float32``
        round-trip).
        """
        return ",".join(f"{matrix[r][c]:.9g}" for r in range(4) for c in range(4))

    @classmethod
    def deserialize_matrix(cls, text: str) -> Matrix:
        """Inverse of :meth:`serialize_matrix`."""
        floats = [float(v) for v in text.split(",")]
        return Matrix([tuple(floats[r * 4 : r * 4 + 4]) for r in range(4)])

    @classmethod
    def hash_matrix(cls, matrix: Matrix) -> int:
        """Hash a 4x4 matrix by its 16 floats. Useful as a cache key."""
        return hash(tuple(matrix[r][c] for r in range(4) for c in range(4)))

    @classmethod
    def is_view_top_down(cls, context: bpy.types.Context, threshold: float = 0.9659) -> bool:
        """True when the viewport camera is looking ~straight down (or up) the world Z axis.

        Default threshold of 0.9659 = cos(15°) — a 15° tilt cone around ±world Z.
        Above the threshold the world-Z axis projects to a small fraction of its
        true length on screen, so callers that lay icons or markers out along
        world Z should switch to a screen-space offset and any gizmo whose intent
        is specifically "vertical" loses its visual cue. The cone is kept narrow
        so vertical-intent gizmos stay visible across the typical orbit range of
        3D viewport work and drop out only near genuine plan view."""
        rv3d = context.region_data
        if rv3d is None:
            return False
        view_forward = Vector(rv3d.view_matrix.inverted().col[2][:3]).normalized()
        return abs(view_forward.z) > threshold

    @classmethod
    def top_down_factor(cls, context: bpy.types.Context, threshold: float = 0.9659) -> float:
        """Continuous 0–1 ramp matching ``is_view_top_down``'s cone: 0 outside the
        cone, ramping linearly to 1 at strict alignment with world Z. Callers that
        want a proportional effect (an icon-stack lift growing as the view
        approaches plan) use this in place of the boolean to avoid a one-frame
        visual jump as the camera crosses the threshold."""
        rv3d = context.region_data
        if rv3d is None:
            return 0.0
        view_forward = Vector(rv3d.view_matrix.inverted().col[2][:3]).normalized()
        alignment = abs(view_forward.z)
        if alignment <= threshold:
            return 0.0
        return (alignment - threshold) / (1.0 - threshold)

    @classmethod
    def get_screen_up_world(cls, context: bpy.types.Context) -> Vector:
        """World-space direction corresponding to the camera's up axis (screen-vertical).

        Returns ``+Y`` when region data is unavailable so callers can compute an
        offset without a guard branch."""
        rv3d = context.region_data
        if rv3d is None:
            return Vector((0.0, 1.0, 0.0))
        return Vector(rv3d.view_matrix.inverted().col[1][:3]).normalized()

    @classmethod
    def get_shader_editor_context(cls) -> Union[dict[str, Any], None]:
        for screen in bpy.data.screens:
            for area in screen.areas:
                if area.type == "NODE_EDITOR":
                    space = area.spaces.active
                    assert isinstance(space, bpy.types.SpaceNodeEditor)
                    if space.tree_type == "ShaderNodeTree":
                        context_override = {"area": area, "space": space, "screen": screen}

                        # Add window if screen differs from current context
                        context = bpy.context
                        if context and context.screen != screen:
                            window = next((w for w in context.window_manager.windows if w.screen == screen), None)
                            if window:
                                context_override["window"] = window

                        return context_override

    @classmethod
    def copy_node_graph(cls, material_to: bpy.types.Material, material_from: bpy.types.Material) -> None:
        temp_override = cls.get_shader_editor_context()
        shader_editor = temp_override["space"]

        # remove all nodes from the current material
        for n in material_to.node_tree.nodes[:]:
            material_to.node_tree.nodes.remove(n)

        previous_pin_setting = shader_editor.pin
        # required to be able to change material to something else
        shader_editor.pin = True
        shader_editor.node_tree = material_from.node_tree

        # select all nodes and copy them to clipboard
        for node in material_from.node_tree.nodes:
            node.select = True
        with bpy.context.temp_override(**temp_override):
            bpy.ops.node.clipboard_copy()

        # back to original material
        shader_editor.node_tree = material_to.node_tree
        with bpy.context.temp_override(**temp_override):
            bpy.ops.node.clipboard_paste(offset=(0, 0))

        # restore shader editor settings
        shader_editor.pin = previous_pin_setting

    @classmethod
    def get_material_node(
        cls, blender_material: bpy.types.Material, node_type: str, kwargs: Optional[dict] = {}
    ) -> Union[bpy.types.ShaderNode, None]:
        """returns first node from the `blender_material` shader graph with type `node_type`"""
        if not tool.Style.get_use_nodes(blender_material):
            return
        nodes = blender_material.node_tree.nodes
        for node in nodes:
            if node.type == node_type and all(getattr(node, a) == kwargs[a] for a in kwargs):
                return node

    @classmethod
    def update_screen(cls) -> None:
        bpy.ops.wm.redraw_timer(type="DRAW_WIN_SWAP", iterations=1)

    @classmethod
    def update_viewport(cls) -> None:
        cls.get_viewport_context()["area"].tag_redraw()

    @classmethod
    def update_all_viewports(cls, context: bpy.types.Context | None = None) -> None:
        """Tag every visible 3D viewport for redraw. Silent no-op when no
        screen attached (background mode, plug-out, mid-load_post)."""
        context = context or bpy.context
        screen = getattr(context, "screen", None)
        if screen is None:
            return
        for area in screen.areas:
            if area.type == "VIEW_3D":
                area.tag_redraw()

    @classmethod
    def force_depsgraph_update(cls) -> None:
        """useful if you need to trigger callbacks like `depsgraph_update_pre`"""
        # blender is requiring some ID to be changed
        # to trigger depsgraph update
        scene = bpy.context.scene
        scene.show_subframe = scene.show_subframe
        bpy.context.view_layer.update()

    @classmethod
    def ensure_unique_name(cls, name: str, objects: Iterable[str], iteration=0) -> str:
        """returns a unique name for the given name and dictionary of objects
        blender style name with .001, .002, etc. suffix.

        objects can be `bpy.data.objects`.
        """
        current_iteration = name if not iteration else f"{name}.{iteration:03d}"
        if current_iteration not in objects:
            return current_iteration
        return cls.ensure_unique_name(name, objects, iteration + 1)

    @classmethod
    def blender_path_to_posix(cls, blender_path: str) -> str:
        """Process blender path to be saved as posix.

        If path is relative the method will keep it relative to .ifc file
        """
        if blender_path.startswith("//"):  # detect relative blender path
            ifc_path = Path(tool.Ifc.get_path())
            abs_path = Path(bpy.path.abspath(blender_path))
            path = abs_path.relative_to(ifc_path.parent)
        else:
            path = Path(blender_path)

        return path.as_posix()

    @classmethod
    def ensure_blender_path_is_abs(cls, blender_path: Path) -> Path:
        if blender_path.is_absolute():
            return blender_path
        return bpy.path.abspath("//") / blender_path

    @classmethod
    def ensure_bin_in_path(cls) -> None:
        """Check 'bin' folder is in PATH, if not add for this session"""
        bin_dir = str(Path(__file__).parent.parent.resolve() / "libs" / "bin")
        if not os.path.isdir(bin_dir):
            return  # Maybe the user is using a system-wide Python package. See #7157.
        current_path = os.environ["PATH"]
        if bin_dir not in current_path:
            os.environ["PATH"] = current_path + os.pathsep + bin_dir
            # files need to be executable
            if platform.system() != "Windows":
                for filename in os.listdir(bin_dir):
                    file_path = os.path.join(bin_dir, filename)
                    if os.path.isfile(file_path):
                        current_permissions = os.stat(file_path).st_mode
                        try:
                            os.chmod(file_path, current_permissions | 0o100)
                        except PermissionError:
                            pass

    @classmethod
    def get_default_selection_keypmap(cls) -> tuple:
        """keymap to replicate default blender selection behaviour with click and box selection"""
        # code below comes from blender_default.py which is part of default blender scripts licensed under GPL v2
        # https://github.com/blender/blender/blob/master/release/scripts/presets/keyconfig/keymap_data/blender_default.py
        # the code is the data from evaluating km_3d_view_tool_select() and km_3d_view_tool_select_box()
        #
        # You can run the snippet below in Blender console
        # to regenerate those keybindings in case of errors in the future
        # ```
        # import os
        # version = ".".join(bpy.app.version_string.split(".")[:2])
        # fl = os.path.join(os.getcwd(), version, "scripts/presets/keyconfig/keymap_data/blender_default.py")
        # def_keymap = bpy.utils.execfile(fl)
        # params = def_keymap.Params
        # box_keymap = def_keymap.km_3d_view_tool_select_box(def_keymap.Params(), fallback=None)[2]["items"]
        # click_keymap = def_keymap.km_3d_view_tool_select(def_keymap.Params(select_mouse="LEFTMOUSE"), fallback=None)[2]["items"]
        # ```
        # https://docs.blender.org/api/current/bpy.types.KeyMapItems.html
        keymap = (
            # box selection keymap
            ("view3d.select_box", {"type": "LEFTMOUSE", "value": "CLICK_DRAG"}, None),
            (
                "view3d.select_box",
                {"type": "LEFTMOUSE", "value": "CLICK_DRAG", "shift": True},
                {"properties": [("mode", "ADD")]},
            ),
            (
                "view3d.select_box",
                {"type": "LEFTMOUSE", "value": "CLICK_DRAG", "ctrl": True},
                {"properties": [("mode", "SUB")]},
            ),
            (
                "view3d.select_box",
                {"type": "LEFTMOUSE", "value": "CLICK_DRAG", "shift": True, "ctrl": True},
                {"properties": [("mode", "AND")]},
            ),
            # left-click selection keymap
            ("view3d.select", {"type": "LEFTMOUSE", "value": "PRESS"}, {"properties": [("deselect_all", True)]}),
            (
                "view3d.select",
                {"type": "LEFTMOUSE", "value": "PRESS", "shift": True},
                {"properties": [("toggle", True)]},
            ),
        )
        return keymap

    KEY_MODIFIERS = {
        "A": ("EVENT_ALT", "OPTION" if sys.platform == "Darwin" else "ALT"),
        "C": ("EVENT_CTRL", "CTRL"),
        "S": ("EVENT_SHIFT", "⇧"),
        "E": ("EVENT_PADENTER", "ENTER" if sys.platform == "Darwin" else "RETURN"),
    }

    @classmethod
    def add_layout_hotkey_operator(
        cls,
        layout: bpy.types.UILayout,
        text: str,
        hotkey: str,
        description: str,
        ui_context: str = "",
        *,
        tool_name: str,
        module_name: str,
        operator: Optional[str] = None,
    ) -> tuple[bpy.types.OperatorProperties, bpy.types.UILayout]:
        """
        :param module_name: Provide `__name__` of the current module,
            so method could pick up icon previews based on the module's `custom_icon_previews` attribute.
        :param operator: Operator to display in UI. Displaying the specific operator in UI can be useful
            to provide poll error messages.
        """
        if tool_name == "bim":
            hotkey_operator = "bim.hotkey"
        else:
            hotkey_operator = f"bim.{tool_name}_hotkey"
        operator_to_use = operator or hotkey_operator

        modifier, key = hotkey.split("_")
        op_text = "" if ui_context == "TOOL_HEADER" else text
        modifier_icon, modifier_str = cls.KEY_MODIFIERS.get(modifier, ("NONE", ""))

        module = sys.modules[module_name]
        icon_previews: Union[bpy.utils.previews.ImagePreviewCollection, None]
        icon_previews = getattr(module, "custom_icon_previews", None)

        row = layout if ui_context == "TOOL_HEADER" else layout.row(align=True)
        if icon_previews:
            custom_icon = icon_previews.get(text.upper().replace(" ", "_"), icon_previews["IFC"]).icon_id
            op = row.operator(operator_to_use, text=op_text, icon_value=custom_icon)
        else:
            op = row.operator(operator_to_use, text=op_text)
        if ui_context != "TOOL_HEADER":
            row.label(text="", icon=modifier_icon)
            row.separator(factor=1)
            row.label(text="", icon=f"EVENT_{key}")

        if operator_to_use == hotkey_operator:
            hotkey_description = f"Hotkey: {modifier_str} {key}".strip()
            description = "\n\n".join(filter(None, [description, hotkey_description]))

            op.hotkey = hotkey
            if ui_context == "TOOL_HEADER":
                op.description = text + "\n" + description
            else:
                op.description = description
        return op, row

    @classmethod
    def get_object_bounding_box(cls, obj: bpy.types.Object) -> dict[str, Union[tuple[float, float, float], Vector]]:
        """Returns dict with local min and max x, y, z values for the object.

        Careful with using this method for objects in EDIT mode because
        it requires all EDIT mode changes to be applied.
        """
        # Example bounding box points for a cube:
        # [
        #     (-1.0, -1.0, -1.0),        # 0, min.
        #     (-1.0, -1.0,  1.0),        # 1
        #     (-1.0,  1.0,  1.0),        # 2
        #     (-1.0,  1.0, -1.0),        # 3
        #     ( 1.0, -1.0, -1.0),        # 4
        #     ( 1.0, -1.0,  1.0),        # 5
        #     ( 1.0,  1.0,  1.0),        # 6, max.
        #     ( 1.0,  1.0, -1.0),        # 7
        # ]
        bound_box = obj.bound_box
        min_pt = Vector(bound_box[0])
        max_pt = Vector(bound_box[6])
        bbox_dict = {
            "min_x": min_pt.x,
            "max_x": max_pt.x,
            "min_y": min_pt.y,
            "max_y": max_pt.y,
            "min_z": min_pt.z,
            "max_z": max_pt.z,
            "min_point": min_pt,
            "max_point": max_pt,
            "center": (max_pt + min_pt) / 2,
            # Intrinsic per-axis size in object-local space. Distinct from
            # ``obj.dimensions``, which folds object-level scale into its
            # output; this is the raw mesh bbox extent.
            "dimensions": (max_pt.x - min_pt.x, max_pt.y - min_pt.y, max_pt.z - min_pt.z),
        }
        return bbox_dict

    @classmethod
    def get_object_world_bounding_box(cls, obj: bpy.types.Object) -> dict[str, Union[float, Vector]]:
        """Same shape as ``get_object_bounding_box`` but with ``matrix_world``
        applied — extents are computed across the 8 transformed corners, so
        a rotated or scaled object reports its actual world-axis AABB rather
        than the misleading transform of the local-space corners.

        ``bound_box[0]`` / ``bound_box[6]`` are the local min/max corners but
        do NOT correspond to the world AABB extremes once the object is
        rotated, so min/max must be taken per-axis across all 8 corners."""
        corners = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
        xs = [c.x for c in corners]
        ys = [c.y for c in corners]
        zs = [c.z for c in corners]
        min_point = Vector((min(xs), min(ys), min(zs)))
        max_point = Vector((max(xs), max(ys), max(zs)))
        return {
            "min_x": min_point.x,
            "max_x": max_point.x,
            "min_y": min_point.y,
            "max_y": max_point.y,
            "min_z": min_point.z,
            "max_z": max_point.z,
            "min_point": min_point,
            "max_point": max_point,
            "center": (min_point + max_point) / 2,
            # World-axis-aligned per-axis size. For rotated objects this is
            # the AABB extent, not the intrinsic mesh size (use the local
            # variant for that).
            "dimensions": (max_point.x - min_point.x, max_point.y - min_point.y, max_point.z - min_point.z),
        }

    @classmethod
    def select_and_activate_single_object(cls, context: bpy.types.Context, active_object: bpy.types.Object) -> None:
        for obj in context.selected_objects:
            obj.select_set(False)
        context.view_layer.objects.active = active_object
        active_object.select_set(True)

    @classmethod
    def set_object_selection(cls, obj: bpy.types.Object, state: bool = True):
        """Run ``Object.select_set`` but ignore errors if the object is hidden.

        Therefore, doesn't guarantee that the object is actually selected.
        """
        try:
            obj.select_set(state)
        except RuntimeError:  # Trying to select a hidden object throws an error
            pass

    @classmethod
    def select_object(cls, obj: bpy.types.Object):
        """Shortcut for ``set_object_selection(obj, True)``."""
        cls.set_object_selection(obj, True)

    @classmethod
    def deselect_object(cls, obj: bpy.types.Object, ensure_active_object: bool = True):
        """Deselect object (using ``set_object_selection``) and optionally ensure that active
        object is not the deselected object (last selected object used to replace it as active).
        """
        cls.set_object_selection(obj, False)
        if ensure_active_object and bpy.context.view_layer.objects.active == obj:
            if bpy.context.selected_objects:
                cls.set_active_object(bpy.context.selected_objects[-1])
            else:
                cls.clear_active_object()

    @classmethod
    def get_objects_selection(
        cls, context: bpy.types.Context
    ) -> tuple[bpy.types.Context, Union[bpy.types.Object, None], list[bpy.types.Object]]:
        """Get objects selection to later pass to `set_objects_selection`."""
        return context, context.view_layer.objects.active, context.selected_objects

    @classmethod
    def set_objects_selection(
        cls,
        context: bpy.types.Context,
        active_object: Optional[bpy.types.Object] = None,
        selected_objects: Sequence[bpy.types.Object] = (),
        clear_previous_selection=True,
    ) -> None:
        if clear_previous_selection:
            for obj in context.selected_objects:
                obj.select_set(False)
        for obj in selected_objects:
            obj.select_set(True)
        context.view_layer.objects.active = active_object
        if active_object:
            active_object.select_set(True)

    class ObjectsSelectionArgs(NamedTuple):
        context: bpy.types.Context
        active_object: bpy.types.Object | None
        selected_objects: list[bpy.types.Object]

    @classmethod
    def validate_object_selection(
        cls,
        context: bpy.types.Context,
        active_object: Union[bpy.types.Object, None] = None,
        selected_objects: Sequence[bpy.types.Object] = (),
    ) -> ObjectsSelectionArgs:
        """Validate object selection and return only valid objects.

        Can be used before ``set_objects_selection`` to avoid errors
        trying to select or set as active already removed objects
        or objects that are not in the current view layer (their collection is unchecked).
        """
        assert context.view_layer
        view_layer_objects = set(context.view_layer.objects)

        def is_selectable(obj: bpy.types.Object) -> bool:
            return cls.is_valid_data_block(obj) and obj in view_layer_objects

        new_selected_objects = [o for o in selected_objects if is_selectable(o)]

        if active_object and not is_selectable(active_object):
            active_object = None

        return cls.ObjectsSelectionArgs(context, active_object, new_selected_objects)

    @classmethod
    def clear_objects_selection(cls) -> None:
        """Clear objects selection and active object."""
        bpy.ops.object.select_all(action="DESELECT")
        cls.clear_active_object()

    @classmethod
    def get_enum_safe(cls, props: bpy.types.PropertyGroup, prop_name: str) -> Union[str, None]:
        """method created for readibility and to avoid console warnings like
        `pyrna_enum_to_py: current value '17' matches no enum in 'BIMModelProperties', '', 'relating_type_id'`

        :return: Enum property value as a string or None if current enum value is invalid.
        """
        # Yes, accessing items through annotations is a bit hacky
        # but it's the only way to get the dynamic enum items
        # besides providing them to get_enum_safe explicitly.
        try:
            annotations = props.__annotations__
        except AttributeError:
            annotations = type(props).__annotations__
        prop_keywords = annotations[prop_name].keywords
        items = prop_keywords.get("items")
        if items is None:
            return None
        if not isinstance(items, (list, tuple)):
            # items are retrieved through a callback, not a static list / tuple :
            items = items(props, bpy.context)

        items_amount = len(items)
        # If enum has no items it seems to always produce a warning.
        # E.g. if you try to get it's value directly: `BIMModelProperties.relating_type_id`.
        if items_amount == 0:
            return None

        index = props.get(prop_name)
        # If value was never changed (still default), we can just retrieve it from the enum.
        if index is None:
            default_value = prop_keywords.get("default", 0)
            if isinstance(default_value, int):
                index = default_value
            else:
                # If default value is a string then it's a static enum
                # and we can just return it.
                return default_value
        # Ensure index is valid.
        if items_amount > index >= 0:
            return items[index][0]
        return None

    @classmethod
    def ensure_enum_is_valid(cls, props: bpy.types.PropertyGroup, prop_name: str) -> bool:
        """Ensure that enum is valid after current enum item was deleted.

        :return: True if enum is valid and update callback was triggered,
            False if enum is still invalid (as there no enum items)
            and update callback was not triggered (may need to trigger it manually).
        """
        current_value = cls.get_enum_safe(props, prop_name)
        if current_value is not None:
            # Value is valid, just trigger the update callback.
            setattr(props, prop_name, current_value)
            return True

        # If enum was never changed prop_name won't be present in props
        # and implicit 0 index is assumed.
        current_index = props.get(prop_name, 0)
        # Index is still invalid and triggering update callback directly
        # will cause an error, so we just stop here.
        if current_index == 0:
            return False

        props[prop_name] = current_index - 1
        # Trigger update callback.
        setattr(props, prop_name, getattr(props, prop_name))
        return True

    @classmethod
    def append_data_block(cls, filepath: str, data_block_type: str, name: str, link=False, relative=False) -> dict:
        if Path(filepath) == Path(bpy.data.filepath):
            data_block = getattr(bpy.data, data_block_type).get(name, None)
            if not data_block:
                return {"data_block": None, "msg": f"Data-block {data_block_type}/{name} not found in {filepath}"}
            return {"data_block": data_block.copy(), "msg": ""}

        with bpy.data.libraries.load(filepath, link=link, relative=relative) as (data_from, data_to):
            if name not in getattr(data_from, data_block_type):
                return {"data_block": None, "msg": f"Data-block {data_block_type}/{name} not found in {filepath}"}
            getattr(data_to, data_block_type).append(name)
        return {"data_block": getattr(data_to, data_block_type)[0], "msg": ""}

    @classmethod
    def remove_object(cls, obj: bpy.types.Object) -> None:
        bpy.data.objects.remove(obj)

    @classmethod
    def remove_data_block(cls, data_block: bpy.types.ID, do_unlink=True) -> None:
        """Removes a datablock (such as a mesh)

        See https://projects.blender.org/blender/blender/issues/118787 for more
        details about do_unlink.

        :param data_block: The bpy.data datablock to delete.
        :param do_unlink: Whether or not to unlink the datablock first. This
            defaults to true, which is Blender's default behaviour. If you are
            sure that the data block has zero users, then you can set this
            to False, which will make datablock deletion significantly faster
            by avoiding unnecessary Blender data checks.
        :return: None
        """
        collection_name = repr(data_block).split(".", 2)[-1].split("[", 1)[0]
        getattr(bpy.data, collection_name).remove(
            data_block, do_unlink=do_unlink, do_id_user=do_unlink, do_ui_user=do_unlink
        )

    @classmethod
    def remove_data_blocks(cls, data_blocks: list[bpy.types.ID], remove_unused_data: bool = False) -> None:
        """Removes several data blocks at once

        :param data_blocks: iterable of data blocks to remove
        :param remove_unused_data: set to True to purge data that would be orphaned by the operation
        :return: None
        """
        data_blocks = list(data_blocks)
        if remove_unused_data:
            data_blocks.extend([o.data for o in data_blocks if hasattr(o, "data") and o.data and o.data.users <= 1])
        bpy.data.batch_remove(data_blocks)

    ## BMESH UTILS ##
    @classmethod
    def apply_bmesh(cls, mesh: bpy.types.Mesh, bm: bmesh.types.BMesh, obj: Optional[bpy.types.Object] = None) -> None:
        """`obj` argument is not optional if you plan to update mesh in EDIT mode
        and it's possible that that mesh object won't be currenly active."""
        import bmesh

        if mesh.is_editmode:
            # better to be safe because otherwise mesh won't be updated
            # and you won't get any errors
            if not bm.is_wrapped or hash(bmesh.from_edit_mesh(mesh)) != hash(bm):
                raise Exception(
                    f"{bm} is not edit mesh for {mesh}. "
                    "For applying bmesh in edit mode bmesh should be acquired with `bmesh.from_edit_mesh(me)`."
                )
            bmesh.update_edit_mesh(mesh)
            if not obj:
                if not bpy.context.active_object or bpy.context.active_object.data != mesh:
                    raise Exception(
                        "Error applying bmesh in EDIT object - object is "
                        "not provided and can't be acquired from the context. "
                    )
                obj = bpy.context.active_object
            obj.update_from_editmode()
        else:
            bm.to_mesh(mesh)
            # only freeing bmesh if object is in OBJECT mode
            # because if it's in EDIT mode
            # freeing mesh will result in dead bmeshes from `bmesh.from_edit_mesh(mesh)`
            # until you restart EDIT mode
            # which may result in errors when some other scripts will try to get bmesh
            bm.free()

        mesh.update()

    @classmethod
    def get_bmesh_for_mesh(cls, mesh: bpy.types.Mesh, clean=False) -> bmesh.types.BMesh:
        import bmesh

        if mesh.is_editmode:
            bm = bmesh.from_edit_mesh(mesh)
            if clean:
                bm.clear()
        else:
            bm = bmesh.new()
            if not clean:
                bm.from_mesh(mesh)
        return bm

    @classmethod
    def bmesh_join(
        cls,
        bm_a: bmesh.types.BMesh,
        bm_b: bmesh.types.BMesh,
        callback: Optional[
            Callable[
                [bmesh.types.BMesh, list[bmesh.types.BMVert], list[bmesh.types.BMEdge], list[bmesh.types.BMFace]], None
            ]
        ] = None,
    ):
        """Join two meshes into single one, store it in `bm_a`"""
        import bmesh

        new_verts = [bm_a.verts.new(v.co) for v in bm_b.verts]
        new_edges = [bm_a.edges.new([new_verts[v.index] for v in edge.verts]) for edge in bm_b.edges]
        new_faces = [bm_a.faces.new([new_verts[v.index] for v in face.verts]) for face in bm_b.faces]
        bmesh.ops.recalc_face_normals(bm_a, faces=bm_a.faces[:])

        if callback:
            callback(bm_a, new_verts, new_edges, new_faces)

        return bm_a

    @classmethod
    def bmesh_check_vertex_in_groups(
        cls, vertex: bmesh.types.BMVert, deform_layer: bmesh.types.BMLayerItem, groups: list[int]
    ) -> Union[tuple[Literal[True], int], tuple[Literal[False], None]]:
        """returns tuple boolean (whether vertex is in any of the groups) and related group index"""
        for group_index in vertex[deform_layer].keys():
            # ignore vertex groups assignments produced by edge subdivision near arcs
            # they usually have weight = 0.5
            if group_index in groups and vertex[deform_layer][group_index] == 1.0:
                return True, group_index
        return False, None

    @classmethod
    def bmesh_get_vertex_groups(cls, vertex: bmesh.types.BMVert, deform_layer: bmesh.types.BMLayerItem) -> list[int]:
        results = []
        for group_index in vertex[deform_layer].keys():
            # Ignore vertex groups assignments produced by edge subdivision near arcs
            # They usually have weight = 0.5
            if vertex[deform_layer][group_index] == 1.0:
                results.append(group_index)
        return results

    @classmethod
    def toggle_edit_mode(cls, context: bpy.types.Context) -> set[rna_enums.OperatorReturnItems]:
        """Run ``object.mode_set(EDIT)``."""
        ao = context.active_object
        if not ao:
            return {"CANCELLED"}
        if ao.library:
            return {"CANCELLED"}
        if ao.type in cls.OBJECT_TYPES_THAT_SUPPORT_EDIT_MODE:
            return bpy.ops.object.mode_set(mode="EDIT", toggle=True)
        elif ao.type in cls.OBJECT_TYPES_THAT_SUPPORT_EDIT_GPENCIL_MODE:
            return bpy.ops.object.mode_set(mode="EDIT_GPENCIL", toggle=True)
        return {"CANCELLED"}

    @classmethod
    def is_object_an_ifc_class(cls, obj: bpy.types.Object, classes: Iterable[str]) -> bool:
        if not tool.Ifc.get():
            return False
        element = tool.Ifc.get_entity(obj)
        return bool(element) and element.is_a() in classes

    @classmethod
    def get_object_from_guid(cls, guid: str) -> Union[bpy.types.Object, None]:
        try:
            element = tool.Ifc.get().by_guid(guid)
        except RuntimeError:
            return None
        obj = tool.Ifc.get_object(element)
        if obj:
            return obj

    @classmethod
    def lock_transform(cls, obj: bpy.types.Object, lock_state=True) -> None:
        for prop in ("lock_location", "lock_rotation", "lock_scale"):
            attr = getattr(obj, prop)
            for axis_idx in range(3):
                attr[axis_idx] = lock_state

    operator_invoke_filepath_hotkeys_description = "Hold Shift to open the file, Alt to browse containing directory"

    @classmethod
    def open_file_or_folder(cls, path: str) -> None:
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    @classmethod
    def operator_invoke_filepath_hotkeys(
        cls, operator: bpy.types.Operator, context: bpy.types.Context, event: bpy.types.Event, filepath: Path
    ) -> Union[set, None]:
        if not event.alt and not event.shift:
            return

        # resolve relative filepaths with .blend path by default
        if not filepath.is_absolute():
            if bpy.data.filepath:
                filepath = Path(bpy.data.filepath).parent / filepath
            else:
                operator.report({"ERROR"}, f'Couldn\'t resolve relative filepath "{filepath.as_posix()}"')
                return {"CANCELLED"}

        # holding ALT - open file directory
        if event.alt == True:
            # open directory
            filepath = filepath.parent
            if not filepath.exists():
                operator.report({"ERROR"}, f'Cannot open non-existing directory: "{filepath.as_posix()}"')
                return {"CANCELLED"}
            cls.open_file_or_folder(filepath.as_posix())
            return {"PASS_THROUGH"}

        # holding SHIFT - open file
        if not filepath.exists():
            operator.report({"ERROR"}, f'Cannot open non-existing file: "{filepath.as_posix()}"')
            return {"CANCELLED"}
        cls.open_file_or_folder(filepath.as_posix())
        return {"PASS_THROUGH"}

    @classmethod
    def get_layer_collection(cls, collection: bpy.types.Collection) -> Union[bpy.types.LayerCollection, None]:
        project = tool.Ifc.get_object(tool.Ifc.get().by_type("IfcProject")[0])
        project_collection = cls.get_object_bim_props(project).collection
        for layer_collection in bpy.context.view_layer.layer_collection.children:
            if layer_collection.collection == project_collection:
                for layer_collection2 in layer_collection.children:
                    if layer_collection2.collection == collection:
                        return layer_collection2

    @classmethod
    def get_layer_collections_mapping(
        cls, collections: list[bpy.types.Collection], view_layer: Optional[bpy.types.ViewLayer] = None
    ) -> dict[bpy.types.Collection, bpy.types.LayerCollection]:
        if view_layer is None:
            view_layer = bpy.context.view_layer

        collections = list(collections)  # copy to prevent mutation
        collections_mapping = dict()
        queue = [view_layer.layer_collection]

        while queue:
            layer = queue.pop()
            collection = layer.collection
            if collection in collections:
                collections_mapping[collection] = layer
                collections.remove(collection)
                if not collections:
                    break
            queue.extend(list(layer.children))

        return collections_mapping

    @classmethod
    def is_editable(cls, obj: bpy.types.Object) -> bool:
        if obj.type not in cls.OBJECT_TYPES_THAT_SUPPORT_EDIT_MODE:
            return False
        if not (element := tool.Ifc.get_entity(obj)):
            return True
        if obj in tool.Project.get_project_props().clipping_planes_objs:
            return False
        usage_type = tool.Model.get_usage_type(element)
        if usage_type in ("LAYER1", "LAYER2"):
            # At the moment, these type types of parametric elements (walls,
            # and "blocks") cannot be edited as a mesh-like object.
            return False
        return True

    class Modifier:
        @classmethod
        def try_applying_edit_mode(cls, obj: bpy.types.Object, element: entity_instance) -> bool:
            """Tries to validate the current BIM modifier parameters for the active object
            Goes into path editing mode if the modifier supports it

            :return: True if an action was taken, False otherwise
            """
            # roof and railing both finalize then drop into path-edit mode — handle
            # them before the generic finish dispatch so the path transition runs.
            if tool.Parametric.is_roof(element):
                if tool.Parametric.ROOF.is_editing(obj):
                    tool.Parametric.run_bim_op(tool.Parametric.ROOF.finish_op)
                bpy.ops.bim.enable_editing_roof_path()
            elif tool.Parametric.is_railing(element):
                if tool.Parametric.RAILING.is_editing(obj):
                    tool.Parametric.run_bim_op(tool.Parametric.RAILING.finish_op)
                bpy.ops.bim.enable_editing_railing_path()
            elif feature := tool.Parametric.is_object_editing(obj):
                tool.Parametric.run_bim_op(feature.finish_op)
            elif tool.Parametric.is_wall(element):
                # Placed after the generic finish dispatch so the TAB toggle splits:
                # wall already editing → finish above; wall not editing → enter here.
                bpy.ops.bim.enable_editing_wall()
            else:
                return False
            return True

        @classmethod
        def try_canceling_editing_modifier_parameters_or_path(cls, obj: bpy.types.Object) -> bool:
            """Tries to cancel the current BIM modifier parameters or path edition for the active object

            :return: True if an action was taken, False otherwise
            """
            # Path-edit modes are distinct from parametric draft modes; handle them first.
            if cls.is_editing_railing_path(obj):
                bpy.ops.bim.cancel_editing_railing_path()
            elif cls.is_editing_roof_path(obj):
                bpy.ops.bim.cancel_editing_roof_path()
            elif feature := tool.Parametric.is_object_editing(obj):
                tool.Parametric.run_bim_op(feature.cancel_op)
            else:
                return False
            return True

        @classmethod
        def is_eligible_for_railing_modifier(cls, obj: bpy.types.Object) -> bool:
            return tool.Blender.is_object_an_ifc_class(obj, _RAILING_MODIFIER_IFC_CLASSES)

        @classmethod
        def is_eligible_for_stair_modifier(cls, obj: bpy.types.Object) -> bool:
            return tool.Blender.is_object_an_ifc_class(obj, _STAIR_MODIFIER_IFC_CLASSES)

        @classmethod
        def is_eligible_for_window_modifier(cls, obj: bpy.types.Object) -> bool:
            return tool.Blender.is_object_an_ifc_class(obj, _WINDOW_MODIFIER_IFC_CLASSES)

        @classmethod
        def is_eligible_for_door_modifier(cls, obj: bpy.types.Object) -> bool:
            return tool.Blender.is_object_an_ifc_class(obj, _DOOR_MODIFIER_IFC_CLASSES)

        @classmethod
        def is_eligible_for_roof_modifier(cls, obj: bpy.types.Object) -> bool:
            return tool.Blender.is_object_an_ifc_class(obj, _ROOF_MODIFIER_IFC_CLASSES)

        @classmethod
        def is_array_child(cls, element: entity_instance) -> bool:
            """True if element is a CHILD of a Bonsai parametric array.

            Children are managed replicas regenerated from the parent's pset —
            their parametric attributes (door dimensions, wall lengths, …) are
            overwritten on the next ``regenerate_array``. Parametric gizmo
            groups skip children via this predicate in ``poll``.

            This sits on a different axis from ``tool.Parametric.is_array``:
            cardinality (parent vs child) is orthogonal to feature kind, and
            an arrayed wall fires both ``is_wall`` and ``is_array`` on the
            same element."""
            if element is None:
                return False
            pset = ifcopenshell.util.element.get_pset(element, "BBIM_Array")
            if not pset:
                return False
            parent_guid = pset.get("Parent")
            return parent_guid is not None and parent_guid != element.GlobalId

        @classmethod
        def any_selected_is_array_child(cls) -> bool:
            """True if any selected IFC-linked object is a Bonsai array child.

            Multi-object wall topology gizmos (merge / join / extend / unjoin
            / fillet) and their bound operators gate on this: any mutation
            applied to a child is overwritten on the next
            ``regenerate_array``, and merge specifically would leave the
            parent's ``BBIM_Array.Data`` list pointing at a deleted GUID.

            Memoised against (selection signature, IFC geometry generation)
            so gizmo polls that fire per input event don't re-walk the pset
            for every selected object every frame. Identity-keyed so plain
            Python objects (used by tests) work alongside real Blender
            ``bpy_struct`` wrappers."""
            selected = tool.Blender.get_selected_objects()
            selection_sig = frozenset(id(obj) for obj in selected)
            current_gen = tool.Parametric.get_geom_generation()
            cached = cls._any_selected_array_child_memo
            if cached is not None and cached[0] == selection_sig and cached[1] == current_gen:
                return cached[2]
            result = False
            for obj in selected:
                element = tool.Ifc.get_entity(obj)
                if element is not None and cls.is_array_child(element):
                    result = True
                    break
            cls._any_selected_array_child_memo = (selection_sig, current_gen, result)
            return result

        _any_selected_array_child_memo: tuple[frozenset[int], int, bool] | None = None

        @classmethod
        def is_slab(cls, element: entity_instance) -> bool:
            """A slab is host-eligible for the parametric add-opening gizmo if
            it is an IfcSlab with LAYER3 usage.

            Slabs carry no proprietary BBIM_Slab pset — their parametric state
            lives in standard IFC (extrusion depth, IfcMaterialLayerSetUsage
            with LayerSetDirection AXIS3). Any LAYER3 slab qualifies."""
            if element is None or not element.is_a("IfcSlab"):
                return False
            return tool.Model.get_usage_type(element) == "LAYER3"

        @classmethod
        def is_pipe_segment(cls, element: entity_instance) -> bool:
            return element is not None and element.is_a("IfcPipeSegment")

        @classmethod
        def is_duct_segment(cls, element: entity_instance) -> bool:
            return element is not None and element.is_a("IfcDuctSegment")

        @classmethod
        def is_editing_railing_path(cls, obj: bpy.types.Object) -> bool:
            props = tool.Model.get_railing_props(obj)
            return props.is_editing_path

        @classmethod
        def is_editing_roof_path(cls, obj: bpy.types.Object) -> bool:
            props = tool.Model.get_roof_props(obj)
            return props.is_editing_path

        @classmethod
        def is_modifier_with_non_editable_path(cls, element: entity_instance) -> bool:
            feature = tool.Parametric.find_for_element(element)
            return bool(feature and feature.has_non_editable_path)

    class Attribute:
        @classmethod
        def fill_attribute(cls, data: bpy.types.ID, attribute_name: str, domain: str, data_type: str, values):
            attribute = cls.ensure_attribute(data, attribute_name, domain, data_type)
            attribute.data.foreach_set(cls.get_data_name(data_type), values)

        @classmethod
        def ensure_attribute(cls, data: bpy.types.ID, attribute_name: str, domain: str, data_type: str):
            attribute = data.attributes.get(attribute_name)
            if not attribute:
                attribute = data.attributes.new(attribute_name, domain=domain, type=data_type)
            return attribute

        @classmethod
        def get_data_name(cls, data_type: str):
            if data_type in ("FLOAT", "INT", "BOOLEAN", "STRING"):
                return "value"
            if data_type.endswith("VECTOR"):
                return "vector"
            elif data_type.endswith("COLOR"):
                return "color"
            else:
                raise NotImplementedError(f"Attribute data type `{data_type}` not implemented yet")

    @classmethod
    def get_verts_coordinates(cls, verts: bpy.types.MeshVertices) -> npt.NDArray[np.float32]:
        # It's faster to get them as f and then convert to d
        # with .astype("d"), if precision is needed.
        coords = np.empty(len(verts) * 3, dtype="f")
        verts.foreach_get("co", coords)
        coords = coords.reshape(-1, 3)
        return coords

    @classmethod
    def get_last_commit_hash(cls) -> Union[str, None]:
        return bonsai.get_last_commit_hash()

    @classmethod
    @cache
    def get_bonsai_version(cls) -> str:
        """E.g. `0.8.3-alpha250617-15453a9`"""
        version = None

        # Try to retrieve actual version for live-dev environment.
        with contextlib.suppress(Exception):
            import git

            path = Path(__file__).resolve().parent
            repo = git.Repo(str(path), search_parent_directories=True)
            repo_path = repo.working_tree_dir
            assert repo_path
            version_ = (Path(repo_path) / "VERSION").read_text().strip()
            commit_date = bonsai.get_last_commit_date()
            assert commit_date
            commit_date = datetime.fromisoformat(commit_date)
            version = f"{version_}-alpha{commit_date.strftime('%y%m%d')}"

        if version is None:
            bbim = cls.get_bbim_extension_package()
            version = bbim.bbim_semver["version"]
        if commit_hash := cls.get_last_commit_hash():
            version += f"-{commit_hash}"
        return version

    @classmethod
    def register_toolbar(cls):
        import bonsai.bim.module.covering.workspace as ws_covering
        import bonsai.bim.module.drawing.workspace as ws_drawing
        import bonsai.bim.module.model.workspace as ws_model
        import bonsai.bim.module.spatial.workspace as ws_spatial
        import bonsai.bim.module.structural.workspace as ws_structural

        if bpy.app.background:
            return

        try:
            bpy.utils.register_tool(ws_model.WallTool, after={"builtin.transform"}, separator=True, group=False)
            bpy.utils.register_tool(ws_model.SlabTool, after={"bim.wall_tool"}, separator=False, group=False)
            bpy.utils.register_tool(ws_model.DoorTool, after={"bim.slab_tool"}, separator=False, group=False)
            bpy.utils.register_tool(ws_model.WindowTool, after={"bim.door_tool"}, separator=False, group=False)
            bpy.utils.register_tool(ws_model.ColumnTool, after={"bim.window_tool"}, separator=False, group=False)
            bpy.utils.register_tool(ws_model.BeamTool, after={"bim.column_tool"}, separator=False, group=False)
            bpy.utils.register_tool(ws_model.DuctTool, after={"bim.beam_tool"}, separator=False, group=False)
            bpy.utils.register_tool(ws_model.PipeTool, after={"bim.duct_tool"}, separator=False, group=False)
            bpy.utils.register_tool(ws_model.BimTool, after={"bim.pipe_tool"}, separator=False, group=False)
            bpy.utils.register_tool(ws_drawing.AnnotationTool, after={"bim.bim_tool"}, separator=True, group=False)
            bpy.utils.register_tool(ws_spatial.SpatialTool, after={"bim.annotation_tool"}, separator=False, group=False)
            bpy.utils.register_tool(
                ws_structural.StructuralTool, after={"bim.spatial_tool"}, separator=False, group=False
            )
            bpy.utils.register_tool(
                ws_covering.CoveringTool, after={"bim.structural_tool"}, separator=False, group=False
            )
        except:
            pass

    @classmethod
    def unregister_toolbar(cls):
        import bonsai.bim.module.covering.workspace as ws_covering
        import bonsai.bim.module.drawing.workspace as ws_drawing
        import bonsai.bim.module.model.workspace as ws_model
        import bonsai.bim.module.spatial.workspace as ws_spatial
        import bonsai.bim.module.structural.workspace as ws_structural

        if bpy.app.background:
            return

        try:
            bpy.utils.unregister_tool(ws_model.WallTool)
            bpy.utils.unregister_tool(ws_model.SlabTool)
            bpy.utils.unregister_tool(ws_model.DoorTool)
            bpy.utils.unregister_tool(ws_model.WindowTool)
            bpy.utils.unregister_tool(ws_model.ColumnTool)
            bpy.utils.unregister_tool(ws_model.BeamTool)
            bpy.utils.unregister_tool(ws_model.DuctTool)
            bpy.utils.unregister_tool(ws_model.PipeTool)
            bpy.utils.unregister_tool(ws_model.BimTool)
            bpy.utils.unregister_tool(ws_drawing.AnnotationTool)
            bpy.utils.unregister_tool(ws_spatial.SpatialTool)
            bpy.utils.unregister_tool(ws_structural.StructuralTool)
            bpy.utils.unregister_tool(ws_covering.CoveringTool)
        except:
            pass

    @classmethod
    def get_scene_panels_list(cls) -> tuple[bpy.types.Panel, ...]:
        # example default blender scene panels can be found in
        # https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_ui/properties_scene.py#L421
        scene_panels: list[str] = []
        panels_to_parents: dict[str, str] = dict()
        for item_name in dir(bpy.types):
            item = getattr(bpy.types, item_name)
            # filter only panels
            if not hasattr(item, "bl_rna") or not isinstance(item.bl_rna.base, bpy.types.Panel):
                continue
            # ignore bbim panels
            if item.__module__.startswith("bonsai"):
                continue
            # filter scene panels
            if getattr(item, "bl_context", None) != "scene":
                continue
            scene_panels.append(item_name)
            parent_panel = getattr(item, "bl_parent_id", None)
            if parent_panel is not None:
                panels_to_parents[item_name] = parent_panel

        scene_panels = cls.sort_panels_for_register(scene_panels, panels_to_parents)
        final_panels = [getattr(bpy.types, p) for p in scene_panels]
        return tuple(final_panels)

    @classmethod
    def sort_panels_for_register(cls, items: list[str], items_to_parents: dict[str, str]) -> list[str]:
        """sort panels ensuring parents panels will be registered first
        as otherwise we'll get errors unregistering them all and registering child panel"""
        final_items = []
        unsorted = items.copy()

        # first, add items without parents
        for item in unsorted[:]:
            if item not in items_to_parents:
                final_items.append(item)
                unsorted.remove(item)

        # store children for each parent
        children: dict[str, list[str]] = dict()
        for item in items_to_parents:
            children.setdefault(items_to_parents[item], []).append(item)

        # add children recursively, ensuring parents are added first
        keep_looking = True
        while keep_looking:
            keep_looking = False
            for item in list(children.keys()):
                # check if parent panel was already added
                if item not in final_items:
                    continue
                final_items.extend(children[item])
                del children[item]
                keep_looking = True

        assert set(items) == set(final_items), "Sorted list doesn't match original"
        return final_items

    @classmethod
    def override_scene_panel(cls, original_panel: bpy.types.Panel) -> None:
        @classmethod
        def poll_check_blender_tab(cls, context):
            aprops = tool.Blender.get_active_area_props(context)
            if aprops.path_from_id() == "BIMAreaProperties" and context.area.spaces.active.search_filter:
                return True
            return aprops.tab == "BLENDER"

        polls = bonsai.bim.original_scene_panels_polls

        # override poll method
        if not hasattr(original_panel, "poll"):
            polls[original_panel] = None
            original_panel.poll = poll_check_blender_tab
        else:
            polls[original_panel] = original_panel.poll

            @classmethod
            def wrapped_poll(cls, context):
                return polls[cls](context) and poll_check_blender_tab.__func__(cls, context)

            original_panel.poll = wrapped_poll

        # reregister to activate new poll
        bpy.utils.unregister_class(original_panel)
        bpy.utils.register_class(original_panel)

    @classmethod
    def remove_scene_panel_override(cls, panel: bpy.types.Panel) -> None:
        polls = bonsai.bim.original_scene_panels_polls

        poll = polls[panel]
        if poll is None:
            del panel.poll
        else:
            panel.poll = poll

        # panel might be already unregistered during blender exit
        # or if it's addon was disabled
        if panel.is_registered:
            # reregister to activate new poll
            bpy.utils.unregister_class(panel)
            bpy.utils.register_class(panel)
        del polls[panel]

    @classmethod
    def get_blender_addon_package_name(cls) -> str:
        return bonsai.REGISTERED_BBIM_PACKAGE

    @classmethod
    def get_bbim_extension_package(cls) -> types.ModuleType:
        name = cls.get_blender_addon_package_name()
        return importlib.import_module(name)

    @classmethod
    def is_addon_enabled(cls) -> bool:
        return cls.get_blender_addon_package_name() in bpy.context.preferences.addons

    @classmethod
    def get_addon_preferences(cls) -> bonsai.bim.ui.BIM_ADDON_preferences:
        blender_package_name = cls.get_blender_addon_package_name()
        return bpy.context.preferences.addons[blender_package_name].preferences

    @classmethod
    def get_addon(cls, name: str) -> Union[types.ModuleType, None]:
        import importlib

        try:
            return importlib.import_module(name)  # Legacy Blender addon
        except ImportError:
            pass

        for package_name in bpy.context.preferences.addons.keys():
            if package_name.endswith(f".{name}"):
                try:
                    return importlib.import_module(package_name)
                except ModuleNotFoundError:
                    pass

    @classmethod
    def get_sun_props(cls) -> Union[SunPosProperties, None]:
        assert (scene := bpy.context.scene)
        return getattr(scene, "sun_pos_properties", None)

    @classmethod
    def scale_font_size(cls, size=None):
        default_dpi = 72
        default_pixel_size = 1.0
        ui_style = bpy.context.preferences.ui_styles[0]
        base_size = ui_style.widget.points if size is None else size
        platform_scale = 0.5 if sys.platform == "darwin" else 1

        default_scale = default_dpi * default_pixel_size
        system = bpy.context.preferences.system
        system_scale = system.dpi * system.pixel_size
        return (
            (system_scale / default_scale)
            * base_size
            * platform_scale
            * tool.Blender.get_addon_preferences().decorator_font_scale
        )

    @classmethod
    def apply_transform_as_local(cls, obj: bpy.types.Object) -> bool:
        """Apply object transforms as local matrix, if possible.

        Clear parent and constraints.

        :return: `True` if transform was applied and `False`
            if transform wasn't applied it's not possible due to a shear.
        """

        if not obj.parent and not obj.constraints:
            return True

        matrix = obj.matrix_world.copy()
        # Matrix has a shear, it cannot be represented as a local matrix
        # based on rotation+translation+scale.
        if not matrix.to_3x3().is_orthogonal_axis_vectors:
            return False

        obj.parent = None
        obj.constraints.clear()
        obj.matrix_world = matrix
        return True

    @classmethod
    def get_full_data_path(cls, bpy_struct: bpy.types.bpy_struct, path: str = "") -> str:
        """Get full data path to Blender entity or it's attributes.

        :param bpy_struct: Blender entity.
        :param path: Additional path to add to entity.

        :return: Path in a format
            ``bpy.data.scenes['Scene'].BIMExplorerProperties.entity_attributes[4].enum_value``
        """
        if path:
            bpy_prop: bpy.types.bpy_prop  # pyright: ignore[reportAttributeAccessIssue]
            bpy_prop = bpy_struct.path_resolve(path, False)
            return repr(bpy_prop)
        return repr(bpy_struct)

    @classmethod
    def get_props_attribute_name(cls, props: bpy.types.PropertyGroup) -> str:
        """E.g. `bpy.data.objects['IfcAnnotation/TEXT'].BIMTextProperties` -> `BIMTextProperties`"""
        return repr(props).rpartition(".")[-1]

    @classmethod
    def resolve_data_path_to_data_attr(cls, data_path: str) -> tuple[bpy.types.bpy_struct, str]:
        """
        :param data_path: Non-full data path to attribute.
        Examples:
            - `preferences.prop_group.string_prop` (`preferences` would mean addon preferences)
            - `scene.string_prop` (`scene` can be any member of `Context`)

        :return: Resolved tuple of Blender Struct and property name.
        Examples:
            - `(preferences.prop_group, "string_prop")`
            - `(scene, "string_prop")`

        """
        # Get data to modify.
        base_path, _, data_path_ = data_path.partition(".")
        if base_path == "preferences":
            data = tool.Blender.get_addon_preferences()
            data_path = data_path_
        else:
            data = bpy.context

        # Get property group if available.
        base_path, _, attr = data_path.rpartition(".")
        if base_path:
            data = data.path_resolve(base_path)
        return data, attr

    @classmethod
    @contextlib.contextmanager
    def preserve_prop_value(cls, bpy_object: bpy.types.bpy_struct, prop_name: str):
        if bpy_object.is_property_set(prop_name):
            prop_value = getattr(bpy_object, prop_name)
        else:
            prop_value = ...
        try:
            yield
        except:
            raise
        finally:
            if prop_value is ...:
                bpy_object.property_unset(prop_name)
                return
            setattr(bpy_object, prop_name, prop_value)

    @classmethod
    def set_prop_from_path(cls, bpy_object: bpy.types.bpy_struct, prop_path: str, value: Any) -> None:
        """Set `data_block` property value using path from `path_from_id`."""

        T_ = TypeVar("T_", bound=bpy.types.bpy_struct)

        def path_resolve(obj: T_, prop_path: str) -> tuple[T_, str]:
            if "." in prop_path:
                extra_path, prop_path = prop_path.rsplit(".", 1)
                obj = obj.path_resolve(extra_path)
            return obj, prop_path

        obj, path = path_resolve(bpy_object, prop_path)
        setattr(obj, path, value)

    @classmethod
    def get_microsoft_store_app_id(cls) -> Union[str, None]:
        """Get Microsoft Store app ID for current Blender instance.

        :return: `None` if Blender is installed not from Microsoft Store (possibly using non-Windows platform).
            Otherwise return app ID string (e.g. 'ppwjx1n5r4v9t').
        """
        if os.name != "nt":
            return None
        blender_binary_path = Path(bpy.app.binary_path)
        if len(blender_binary_path.parents) > 3 and blender_binary_path.parents[2].name == "WindowsApps":
            return blender_binary_path.parents[1].name.rsplit("__", 1)[-1]
        return None

    @classmethod
    def V_(cls, *args: float) -> Vector:
        """Just a shortcut for creating mathutils Vector."""
        return Vector(args)

    @classmethod
    def detect_icon_color_mode(cls, color_path="user_interface.wcol_regular.text", threshold=1.671):
        """
        Uses the text color of a given Blender UI property to determine if custom icons should be dark mode (dm) or light mode (lm).

        Common Blender UI text color paths:
            - "user_interface.wcol_regular.text"  (Regular Text)
            - "user_interface.wcol_tool.text"  (Tool Text)
            - "user_interface.wcol_menu_back.text"  (Menu Background Text)
            - "user_interface.wcol_menu.text"  (Menu Text)
            - "user_interface.wcol_menu.text_sel"  (Menu Text Selected)

        :param color_path: The attribute path relative to bpy.context.preferences.themes[0].
        :param threshold: The RGB sum threshold for determining dark mode. Default is 1.671.

        :return: 'dm' (dark mode) if the RGB sum is > threshold, otherwise 'lm' (light mode).
        """
        full_path = f"bpy.context.preferences.themes[0].{color_path}"

        try:
            color = eval(full_path)[:3]  # Dynamically evaluate and extract RGB values
            rgb_sum = sum(color)
            return "dm" if rgb_sum > threshold else "lm"
        except Exception:
            return "dm"  # Default to dark mode if an error occurs

    @classmethod
    def get_internal_data_dir(cls) -> Path:
        return Path(__file__).parent.parent / "bim" / "data"

    @classmethod
    def get_user_data_dir(cls) -> Path:
        props = cls.get_addon_preferences()
        return Path(props.data_dir)

    @classmethod
    def get_data_dir_path(cls, relative_path: Union[str, Path]) -> Path:
        """Get specified data path in data folder.
        If this path exists in user folder, it takes the precedence."""
        custom_path = cls.get_user_data_dir() / relative_path
        if custom_path.exists():
            return custom_path
        return cls.get_internal_data_dir() / relative_path

    @classmethod
    def get_data_dir_paths(cls, relative_dir_path: Union[str, Path], glob_pattern: str) -> Generator[Path, None, None]:
        """Return paths based on glob pattern from the provided path in data folder.
        Return paths from internal data folder first and then paths from the user data folder (if it exists)."""
        custom_path = cls.get_user_data_dir() / relative_dir_path
        if custom_path.is_dir():
            for filepath in custom_path.glob(glob_pattern):
                yield filepath

        default_data_dir = cls.get_internal_data_dir()
        if default_data_dir == custom_path:
            return
        for filepath in (default_data_dir / relative_dir_path).glob(glob_pattern):
            yield filepath

    @classmethod
    def setup_user_data_dir(cls) -> None:
        """Setup empty folders in user data directory to make them more discoverable."""
        custom_data_dir = cls.get_user_data_dir()
        # Not all paths from internal data dir are listed here,
        # only the ones that intended to be used by user.
        paths_to_create = (
            custom_data_dir,
            custom_data_dir / "assets",
            custom_data_dir / "libraries",
            custom_data_dir / "pset",  # pset templates.
            custom_data_dir / "templates" / "projects",
            custom_data_dir / "templates" / "titleblocks",
        )
        for path in paths_to_create:
            path.mkdir(parents=True, exist_ok=True)

    @classmethod
    @lru_cache
    def get_list_of_tools(cls) -> tuple[str, ...]:
        from bonsai.bim.module.drawing.workspace import AnnotationTool
        from bonsai.bim.module.model.workspace import BimTool

        return tuple(cls.bl_idname for cls in (BimTool.__subclasses__() + [BimTool, AnnotationTool]))

    @classmethod
    @lru_cache
    def get_tools_to_classes_map(cls) -> types.MappingProxyType[str, str]:
        from bonsai.bim.module.model.workspace import BimTool

        dct = {cls.bl_idname: cls.ifc_element_type for cls in (BimTool.__subclasses__())}
        return types.MappingProxyType(dct)

    @classmethod
    @lru_cache
    def get_property_header_tools(cls) -> frozenset[str]:
        """``BimTool`` plus its parametric subclasses — the workspace
        tools whose 3D-view / N-panel header surfaces BIM Tool property
        floats (extrusion_depth, length, x_angle). ``AnnotationTool``
        and the non-``BimTool`` workspace tools (spatial / structural /
        cad / covering) are excluded by construction."""
        from bonsai.bim.module.model.workspace import BimTool

        return frozenset(cls.bl_idname for cls in (BimTool.__subclasses__() + [BimTool]))

    @classmethod
    def get_object_constraint_props(cls, obj: bpy.types.Object) -> BIMObjectConstraintProperties:
        return obj.BIMObjectConstraintProperties  # pyright: ignore[reportAttributeAccessIssue]

    @classmethod
    def get_constraint_props(cls) -> BIMConstraintProperties:
        assert (scene := bpy.context.scene)
        return scene.BIMConstraintProperties  # pyright: ignore[reportAttributeAccessIssue]

    @classmethod
    def get_csv_props(cls) -> CsvProperties:
        assert (scene := bpy.context.scene)
        return scene.CsvProperties  # pyright: ignore[reportAttributeAccessIssue]

    @classmethod
    def get_diff_props(cls) -> DiffProperties:
        assert (scene := bpy.context.scene)
        return scene.DiffProperties  # pyright: ignore[reportAttributeAccessIssue]

    @classmethod
    def get_bim_props(cls, scene: Optional[bpy.types.Scene] = None) -> BIMProperties:
        if scene is None:
            assert (scene := bpy.context.scene)
        return scene.BIMProperties  # pyright: ignore[reportAttributeAccessIssue]

    @classmethod
    def get_area_props(cls, screen: bpy.types.Screen) -> bpy.types.bpy_prop_collection_idprop[BIMAreaProperties]:
        return screen.BIMAreaProperties  # pyright: ignore[reportAttributeAccessIssue]

    @classmethod
    def get_tab_props(cls, screen: bpy.types.Screen) -> BIMTabProperties:
        return screen.BIMTabProperties  # pyright: ignore[reportAttributeAccessIssue]

    @classmethod
    def get_collection_props(cls, collection: bpy.types.Collection) -> BIMCollectionProperties:
        return collection.BIMCollectionProperties  # pyright: ignore[reportAttributeAccessIssue]

    @classmethod
    def get_object_bim_props(cls, obj: bpy.types.Object) -> BIMObjectProperties:
        return obj.BIMObjectProperties  # pyright: ignore[reportAttributeAccessIssue]

    @classmethod
    def get_object_attribute_props(cls, obj: bpy.types.Object) -> BIMAttributeProperties:
        return obj.BIMAttributeProperties  # pyright: ignore[reportAttributeAccessIssue]

    @classmethod
    def get_solar_props(cls) -> BIMSolarProperties:
        assert (scene := bpy.context.scene)
        return scene.BIMSolarProperties  # pyright: ignore[reportAttributeAccessIssue]

    @classmethod
    def get_radiance_exporter_props(cls) -> RadianceExporterProperties:
        assert (scene := bpy.context.scene)
        return scene.BIMRadianceExporeterProperies  # pyright: ignore[reportAttributeAccessIssue]

    @classmethod
    def get_fm_props(cls) -> BIMFMProperties:
        assert (scene := bpy.context.scene)
        return scene.BIMFMProperties  # pyright: ignore[reportAttributeAccessIssue]

    @classmethod
    def get_covetool_props(cls) -> CoveToolProperties:
        assert (scene := bpy.context.scene)
        return scene.CoveToolProperties  # pyright: ignore[reportAttributeAccessIssue]

    @classmethod
    def get_ifc_definition_id(cls, obj: IFC_CONNECTED_TYPE) -> int:
        if isinstance(obj, bpy.types.Object):
            return cls.get_object_bim_props(obj).ifc_definition_id
        return tool.Style.get_material_style_props(obj).ifc_definition_id

    @classmethod
    def get_active_uilist_element(
        cls, collection: bpy.types.bpy_prop_collection_idprop[T], index: int
    ) -> Union[T, None]:
        if 0 <= index < len(collection):
            return collection[index]
        return None

    @classmethod
    def get_valid_uilist_index(cls, current_index: int, items: Sized) -> int:
        """
        Method to help maintaining item selection after some uilist item was removed
        and items were reloaded.
        """
        return max(0, min(current_index, len(items) - 1))

    @classmethod
    def clear_undo_history(cls) -> None:
        """Clears the Blender history, Bonsai history, and IfcOpenShell history"""
        assert (preferences := bpy.context.preferences)
        old_undo_steps = preferences.edit.undo_steps
        preferences.edit.undo_steps = 2
        for i in range(3):
            bpy.ops.ed.undo_push(message="Undo history cleared")
        preferences.edit.undo_steps = old_undo_steps
        tool.Ifc.clear_history()
        old_history_size = tool.Ifc.get().history_size
        tool.Ifc.get().set_history_size(0)
        tool.Ifc.get().set_history_size(old_history_size)

    @classmethod
    def get_unit_scale(cls) -> float:
        assert (scene := bpy.context.scene)
        unit_length = scene.unit_settings.length_unit
        unit_scale = 1.0
        if unit_length == "CENTIMETERS":
            unit_scale = 0.01
        if unit_length == "MILLIMETERS":
            unit_scale = 0.001
        if unit_length == "FEET":
            unit_scale = 0.3048

        return unit_scale

    @classmethod
    def reset_object_visibility(cls):
        override = cls.get_viewport_context()
        with bpy.context.temp_override(**override):
            bpy.ops.object.hide_view_clear(select=False)

    @classmethod
    def isolate_objects(cls, objs):
        previously_selected = {o.name for o in bpy.context.selected_objects}
        previously_active = bpy.context.view_layer.objects.active

        override = cls.get_viewport_context()
        with bpy.context.temp_override(**override):
            bpy.ops.object.hide_view_clear(select=False)

        bpy.ops.object.select_all(action="DESELECT")
        for obj in objs:
            obj.select_set(True)
        with bpy.context.temp_override(**override):
            bpy.ops.object.hide_view_set(unselected=True)

        bpy.ops.object.select_all(action="DESELECT")
        for name in previously_selected:
            obj = bpy.data.objects.get(name)
            if obj:
                obj.select_set(True)
        bpy.context.view_layer.objects.active = previously_active

    @classmethod
    def sync_render_visibility(cls):
        # Doing bpy.ops.object.hide_render_clear_all() or
        # bpy.ops.object.isolate_type_render() is extremely slow.
        # Hopefully this doesn't crash on Windows, it doesn't crash on Linux.
        should_hides = [0 if obj.visible_get() else 1 for obj in bpy.data.objects]
        should_hides = np.fromiter(should_hides, dtype=np.uint8, count=len(should_hides))
        bpy.data.objects.foreach_set("hide_render", should_hides)
        return  # Otherwise...
        # for obj in bpy.data.objects:
        #     if not obj.data:
        #         continue
        #     # For speed, check equality prior to change to prevent needless updates
        #     if (is_visible := obj.visible_get()) and obj.hide_render is True:
        #         obj.hide_render = False
        #     elif not is_visible and obj.hide_render is False:
        #         obj.hide_render = True

    @classmethod
    def hide_objects(cls, objs):
        previously_selected = {o.name for o in bpy.context.selected_objects}
        previously_active = bpy.context.view_layer.objects.active

        override = cls.get_viewport_context()
        bpy.ops.object.select_all(action="DESELECT")
        for obj in objs:
            obj.select_set(True)
        with bpy.context.temp_override(**override):
            bpy.ops.object.hide_view_set(unselected=False)

        for name in previously_selected:
            obj = bpy.data.objects.get(name)
            if obj:
                obj.select_set(True)
        bpy.context.view_layer.objects.active = previously_active

    @classmethod
    def show_objects(cls, objs):
        previously_selected = {o.name for o in bpy.context.selected_objects}
        previously_active = bpy.context.view_layer.objects.active

        bpy.ops.object.select_all(action="DESELECT")
        override = cls.get_viewport_context()
        with bpy.context.temp_override(**override):
            bpy.ops.object.hide_view_clear(select=True)

        for obj in bpy.context.selected_objects:
            if obj in objs:
                obj.select_set(False)
        with bpy.context.temp_override(**override):
            bpy.ops.object.hide_view_set(unselected=False)

        bpy.ops.object.select_all(action="DESELECT")
        for name in previously_selected:
            obj = bpy.data.objects.get(name)
            if obj:
                obj.select_set(True)
        bpy.context.view_layer.objects.active = previously_active

    @classmethod
    def validate_shader_batch_data(cls, pos: Any, indices: Optional[Any]) -> bool:
        """Validate shader batch data.

        If method returns ``False``, then drawing for this batch should be skipped.
        Should be used always before running ``batch.draw(shader)``

        Important because in Blender 4.4.0 on Mac passing an empty list
        as ``indices`` is causing a crash.

        See https://projects.blender.org/blender/blender/issues/136831
        """
        # Checking `pos` is not critical but we keep it
        # to ensure batch data is always validated to avoid crashes.
        if len(pos) == 0 or (indices is not None and len(indices) == 0):
            return False
        return True

    @staticmethod
    def transparent_color(color: Iterable[float], alpha: float = 0.1) -> list[float]:
        """Copy an RGBA color with its alpha channel overridden."""
        out = [c for c in color]
        out[3] = alpha
        return out

    @classmethod
    def draw_bmesh_face_tris(
        cls,
        bm: bmesh.types.BMesh,
        world_vert_coords: list,
        color: Any,
        draw_batch: Callable[[str, list, Any, list], None],
    ) -> None:
        """Submit a non-mutating beauty-triangulated TRIS batch for ``bm``'s faces.

        ``world_vert_coords`` must be indexed by ``bm.verts`` index. Never call
        ``bmesh.ops.triangulate`` on a live bmesh to compute draw indices — it
        mutates the input and produces ear-clip fans that render as visible
        streaks at low alpha.
        """
        tris = [[loop.vert.index for loop in tri] for tri in bm.calc_loop_triangles()]
        draw_batch("TRIS", world_vert_coords, color, tris)

    @classmethod
    def draw_quads(
        cls,
        context: bpy.types.Context,
        quads: Sequence[
            tuple[
                tuple[float, float, float],
                tuple[float, float, float],
                tuple[float, float, float],
                tuple[float, float, float],
            ]
        ],
        *,
        fill_color: Optional[tuple[float, float, float, float]] = None,
        outline_color: Optional[tuple[float, float, float, float]] = None,
        outline_width: float = 1.0,
    ) -> None:
        """Render ``quads`` (each a 4-tuple of CCW world-space corners) as
        a filled TRIS batch, an outline LINES batch, or both.

        Both colors are RGBA 4-tuples. Pass ``fill_color=None`` to skip
        the fill pass and ``outline_color=None`` to skip the outline.
        Skipping both is a no-op.

        Replaces the per-decorator quad-fill helpers that used to live
        inline in each feature module.
        """
        if not quads or (fill_color is None and outline_color is None):
            return
        region = getattr(context, "region", None)
        if region is None:
            return

        verts: list[tuple[float, float, float]] = []
        tri_indices: list[tuple[int, int, int]] = []
        line_indices: list[tuple[int, int]] = []
        for quad in quads:
            if len(quad) != 4:
                continue
            base = len(verts)
            verts.extend(tuple(v) for v in quad)
            if fill_color is not None:
                tri_indices.append((base, base + 1, base + 2))
                tri_indices.append((base, base + 2, base + 3))
            if outline_color is not None:
                line_indices.append((base, base + 1))
                line_indices.append((base + 1, base + 2))
                line_indices.append((base + 2, base + 3))
                line_indices.append((base + 3, base))

        if not cls.validate_shader_batch_data(verts, None):
            return

        gpu.state.blend_set("ALPHA")
        try:
            if fill_color is not None and tri_indices:
                shader = gpu.shader.from_builtin("UNIFORM_COLOR")
                shader.bind()
                shader.uniform_float("color", fill_color)
                batch = batch_for_shader(shader, "TRIS", {"pos": verts}, indices=tri_indices)
                batch.draw(shader)
            if outline_color is not None and line_indices:
                shader = gpu.shader.from_builtin("UNIFORM_COLOR")
                shader.bind()
                shader.uniform_float("color", outline_color)
                # Outline width: the UNIFORM_COLOR shader respects the
                # GPU's current line-width state; restore on exit.
                prev_width = gpu.state.line_width_get()
                gpu.state.line_width_set(outline_width)
                try:
                    batch = batch_for_shader(shader, "LINES", {"pos": verts}, indices=line_indices)
                    batch.draw(shader)
                finally:
                    gpu.state.line_width_set(prev_width)
        finally:
            gpu.state.blend_set("NONE")

    @classmethod
    def build_dashed_line_segments(
        cls,
        world_verts: Sequence[Sequence[float]],
        edges_indices: Sequence[Sequence[int]],
        dash_period: float,
        dash_width: float,
    ) -> tuple[list[tuple[float, float, float]], list[tuple[int, int]]]:
        """Pre-segment edges into world-space dash chunks for a vanilla LINES batch.

        Each input edge is sliced into segments of length ``dash_width`` spaced
        ``dash_period`` apart (dash phase resets per-edge). The result is a fresh
        ``(verts, edges)`` pair that draws as dashes through any standard line
        shader — letting both passes of a visible/occluded outline reuse the
        same shader so depth values match exactly across passes.
        """
        new_verts: list[tuple[float, float, float]] = []
        new_edges: list[tuple[int, int]] = []
        if dash_period <= 0 or dash_width <= 0:
            return new_verts, new_edges
        n = len(world_verts)
        for i, j in edges_indices:
            if not (0 <= i < n and 0 <= j < n) or i == j:
                continue
            v0 = world_verts[i]
            v1 = world_verts[j]
            dx, dy, dz = v1[0] - v0[0], v1[1] - v0[1], v1[2] - v0[2]
            edge_length = math.sqrt(dx * dx + dy * dy + dz * dz)
            if edge_length == 0.0:
                continue
            ux, uy, uz = dx / edge_length, dy / edge_length, dz / edge_length
            t = 0.0
            while t < edge_length:
                t_end = min(t + dash_width, edge_length)
                idx = len(new_verts)
                new_verts.append((v0[0] + ux * t, v0[1] + uy * t, v0[2] + uz * t))
                new_verts.append((v0[0] + ux * t_end, v0[1] + uy * t_end, v0[2] + uz * t_end))
                new_edges.append((idx, idx + 1))
                t += dash_period
        return new_verts, new_edges

    @classmethod
    def extract_error_reports(cls, exception: RuntimeError) -> list[str]:
        """Extracts error report lines from a runtime exception during operator execution.

        If operator had any `ERROR` reports, it will always raise a `RuntimeError`,
        no matter what status is returned.
        And sometimes it's useful to pass those reports to another operator
        that called it. That way user won't get to see a scary traceback.

        If empty list is returned, then exception should be reraised,
        as it is an actual unhandled runtime error.
        """
        error_message = str(exception)
        extracted: list[str] = []

        # If operator was cancelled and had error message,
        # it will always start with this (warnings and info msgs are ignored).
        if not error_message.startswith("Error: "):
            return extracted

        # Ignore actual runtime errors, as they has to be handled separately
        # and not just rereported.
        if error_message.startswith("Error: Python: Traceback (most recent call last):"):
            return extracted

        for report in error_message.strip().split("Error: "):
            report = report.strip()
            if not report:
                continue
            extracted.append(report)
        return extracted

    @classmethod
    def report_operator_errors(cls, operator: bpy.types.Operator, error_reports: list[str]) -> None:
        for report in error_reports:
            operator.report({"ERROR"}, report)

    @classmethod
    @contextlib.contextmanager
    def bonsai_crash_txt(cls, s: str = "") -> Generator[Path, Any, None]:
        """Create a temporary bonsai.crash.txt file the with current traceback.

        Useful in case Blender crash might occur too unexpectedly (e.g. #6686),
        and at least we'll have a slightest clue on what happened.

        Intended to be used via `with` block.
        `atexit` wouldn't work for this as crash breaks everything
        and no callbacks are called.

        :param s: Optional string to add at the top of the txt file.
        """
        # TODO: Indicate that crash occurred after Blender restart?

        # Create a temp file with the traceback.
        temp_dir = tempfile.gettempdir()
        path = Path(temp_dir) / "bonsai.crash.txt"
        traceback_ = "\n".join(traceback.format_stack())
        output = ""
        if s:
            output += f"{s}\n\n"
        time = datetime.now().isoformat()
        output += f"Created at: {time} (local time).\n"
        output += f"Traceback (most recent called last):\n{traceback_}"
        path.write_text(output)
        yield path

        # Remove file if crash didn't happened.
        path.unlink()

    @classmethod
    def sync_old_preferences(cls) -> None:
        # Added on 25.07.15.
        # TODO: deprecate later.
        settings_remap = {
            "scene.BIMBSDDProperties.load_preview_dictionaries": "preferences.bsdd_load_preview_dictionaries",
            "scene.BIMBSDDProperties.load_inactive_dictionaries": "preferences.bsdd_load_inactive_dictionaries",
            "scene.BIMBSDDProperties.load_test_dictionaries": "preferences.bsdd_load_test_dictionaries",
            "scene.BIMProjectProperties.should_disable_undo_on_save": "preferences.should_disable_undo_on_save",
            "scene.BIMProjectProperties.should_stream": "preferences.should_stream",
            "scene.BIMModelProperties.occurrence_name_style": "preferences.occurrence_name_style",
            "scene.BIMModelProperties.occurrence_name_function": "preferences.occurrence_name_function",
            "scene.BIMProperties.pset_dir": "preferences.pset_dir",
            "scene.BIMProperties.data_dir": "preferences.data_dir",
            "scene.BIMProperties.cache_dir": "preferences.cache_dir",
            "scene.DocProperties.sheets_dir": "preferences.doc.sheets_dir",
            "scene.DocProperties.layouts_dir": "preferences.doc.layouts_dir",
            "scene.DocProperties.titleblocks_dir": "preferences.doc.titleblocks_dir",
            "scene.DocProperties.drawings_dir": "preferences.doc.drawings_dir",
            "scene.DocProperties.stylesheet_path": "preferences.doc.stylesheet_path",
            "scene.DocProperties.schedules_stylesheet_path": "preferences.doc.schedules_stylesheet_path",
            "scene.DocProperties.markers_path": "preferences.doc.markers_path",
            "scene.DocProperties.symbols_path": "preferences.doc.symbols_path",
            "scene.DocProperties.patterns_path": "preferences.doc.patterns_path",
            "scene.DocProperties.shadingstyles_path": "preferences.doc.shadingstyles_path",
            "scene.DocProperties.shadingstyle_default": "preferences.doc.shadingstyle_default",
            "scene.DocProperties.drawing_font": "preferences.doc.drawing_font",
            "scene.DocProperties.magic_font_scale": "preferences.doc.magic_font_scale",
            "scene.DocProperties.imperial_precision": "preferences.doc.imperial_precision",
            "scene.DocProperties.tolerance": "preferences.doc.tolerance",
            "scene.DocProperties.classes_to_wireframe": "preferences.doc.classes_to_wireframe",
            "scene.DocProperties.classes_no_cut": "preferences.doc.classes_no_cut",
        }

        props_updated = False
        for old_path, path in settings_remap.items():
            data, attr = cls.resolve_data_path_to_data_attr(path)
            # User already overridden the value.
            if data.is_property_set(attr):
                continue

            data_old, attr_old = cls.resolve_data_path_to_data_attr(old_path)
            # User was only using default value previously.
            if attr_old not in data_old:
                continue

            old_value = data_old[attr_old]
            print(f"Updating {path} based on previous value from {old_path} - '{old_value}'.")
            setattr(data, attr, old_value)
            props_updated = True

        # Doesn't seem to save on exit if edited from Python API, so we do it manually.
        assert bpy.context.preferences
        if props_updated and bpy.context.preferences.use_preferences_save:
            bpy.ops.wm.save_userpref()

    @classmethod
    def get_eevee_name(cls) -> Literal["BLENDER_EEVEE"] | Literal["BLENDER_EEVEE_NEXT"]:
        """Convenience method to get correct eevee render engine name in multiple Blender versions.

        In Blender 4.2 eevee was renamed to "eevee next".
        In Blender 5 eevee next is now just "eevee" again.
        """
        if cls.BLENDER_5:
            return "BLENDER_EEVEE"
        return "BLENDER_EEVEE_NEXT"

    @classmethod
    def np_frombuffer_legacy(cls, bytedata: bytes, n: int) -> npt.NDArray[np.float32]:
        """
        Read ``n`` float values from ``bytedata``, regardless if they are stored as ``float32`` or ``float64``.
        Needed to support .blend files saved in Blender <5.0.0.
        Also allows to work with .blend files from 5.0.0+ in older Blender versions.

        In ``bpy.app.version >= 5.0.0`` ``mathutils`` transitioned to use ``float32`` buffer type,
        while in previous version they were using ``float64``.
        In some cases we are storing raw bytes (e.g. object transforms cheksums), so old .blend files
        might still have ``float64`` data stored.

        See https://projects.blender.org/blender/blender/issues/149283
        """
        if len(bytedata) == (n * 8):  # float64 has 8 bytes per element
            return np.frombuffer(bytedata, dtype=np.float64).astype(np.float32)
        return np.frombuffer(bytedata, dtype=np.float32)

    @classmethod
    def np_array_legacy(cls, mathutils_type: Union[Vector, Matrix]) -> npt.NDArray[np.float32]:
        """
        Converts ``mathutils`` types to ``np.float32`` arrays, regardless of Blender version.

        See ``np_frombuffer_legacy`` for more details.
        """
        if cls.BLENDER_5:
            return np.array(mathutils_type)
        return np.array(mathutils_type, dtype=np.float32)

    @classmethod
    def get_selected_files(
        cls, directory: str, files: bpy.types.OperatorFileListElement, use_relative_path=False
    ) -> list[Path]:
        return [
            tool.Ifc.get_uri(Path(directory) / f.name, use_relative_path=use_relative_path)
            for f in files
            if (Path(directory) / f.name).is_file()
        ]

    @classmethod
    def ray_cast_scene(
        cls,
        context: bpy.types.Context,
        origin: Vector,
        direction: Vector,
    ) -> tuple[bool, Vector, Vector, int, bpy.types.Object, Matrix]:
        """

        The returned matrix is just ``obj.matrix_world``.
        The returned object is not evaluated by the current depsgraph,
        e.g. if object is modified by the depsgraph (e.g. by modifiers)
        object has to be evaluated first (`obj.evaluated_get(depsgraph)`).
        """
        depsgraph = context.evaluated_depsgraph_get()
        assert context.scene
        result = context.scene.ray_cast(
            depsgraph,
            origin,
            direction,
        )
        return result

    @classmethod
    def depsgraph_evaluate(cls, obj: bpy.types.Object) -> bpy.types.Object:
        depsgraph = bpy.context.evaluated_depsgraph_get()
        evaluated_obj = obj.evaluated_get(depsgraph)
        return evaluated_obj
