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

from __future__ import annotations
import sys
import bpy
import bmesh
import json
import os
import platform
import subprocess
import numpy as np
import numpy.typing as npt
from ifcopenshell import entity_instance
import ifcopenshell.api
import ifcopenshell.util.element
import bonsai.core.tool
import bonsai.tool as tool
import bonsai.bim
import types
import importlib
from mathutils import Vector
from pathlib import Path
from functools import lru_cache
from bonsai.bim.ifc import IFC_CONNECTED_TYPE
from typing import Any, Optional, Union, Literal, Iterable, Callable, TypeVar, Generator, TYPE_CHECKING
from typing_extensions import assert_never

if TYPE_CHECKING:
    from bonsai.bim.prop import BIMProperties, BIMObjectProperties
    from bonsai.bim.module.csv.prop import CsvProperties
    from bonsai.bim.module.diff.prop import DiffProperties

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


class Blender(bonsai.core.tool.Blender):
    OBJECT_TYPES_THAT_SUPPORT_EDIT_MODE = ("MESH", "CURVE", "SURFACE", "META", "FONT", "LATTICE", "ARMATURE")
    OBJECT_TYPES_THAT_SUPPORT_EDIT_GPENCIL_MODE = ("GPENCIL",)
    TYPE_MANAGER_ICON = "LIGHTPROBE_VOLUME"

    BLENDER_ENUM_ITEM = Union[tuple[str, str, str], tuple[str, str, str, str], tuple[str, str, str, str, str]]
    """
    Options:

    - (identifier, name, description)

    - (identifier, name, description, number)

    - (identifier, name, description, icon, number)
    """

    @classmethod
    def activate_camera(cls, obj: bpy.types.Object) -> None:

        area = tool.Blender.get_view3d_area()
        is_local_view = area.spaces[0].local_view is not None

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

        area.spaces[0].region_3d.view_perspective = "CAMERA"

    @classmethod
    def get_area_props(cls, context: bpy.types.Context) -> bpy.types.PropertyGroup:
        try:
            if context.screen.name.endswith("-nonnormal"):  # Ctrl-space temporary fullscreen
                screen = bpy.data.screens[context.screen.name.removesuffix("-nonnormal")]
                # The original area object has its type changed to "EMPTY" apparently
                index = [a.type for a in screen.areas].index("EMPTY")
                return screen.BIMAreaProperties[index]
            return context.screen.BIMAreaProperties[context.screen.areas[:].index(context.area)]
        except IndexError:
            # Fallback in case areas aren't setup yet.
            return context.screen.BIMTabProperties

    @classmethod
    def set_active_object(cls, obj: bpy.types.Object) -> None:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

    @classmethod
    def clear_active_object(cls) -> None:
        bpy.context.view_layer.objects.active = None

    @classmethod
    def setup_tabs(cls) -> None:
        # https://blender.stackexchange.com/questions/140644/how-can-make-the-state-of-a-boolean-property-relative-to-the-3d-view-area
        for screen in bpy.data.screens:
            if len(screen.BIMAreaProperties) == 20:
                continue
            screen.BIMAreaProperties.clear()
            for i in range(20):  # 20 is an arbitrary value of split areas
                screen.BIMAreaProperties.add()

    @classmethod
    def is_tab(cls, context: bpy.types.Context, tab: str) -> bool:
        aprops = cls.get_area_props(context)
        if aprops.path_from_id() == "BIMAreaProperties" and context.area.spaces.active.search_filter:
            return True
        return aprops.tab == tab

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
        """Gets the active object

        :param is_selected: If true, the active object also needs to be selected.
        """
        if obj := (getattr(bpy.context, "active_object", None) or bpy.context.view_layer.objects.active):
            if not is_selected:
                return obj
            if obj.select_get():
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
            props = tool.Blender.get_object_bim_props(bpy.data.objects[obj])
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
            return context.scene.BIMResourceTreeProperties.resources[
                context.scene.BIMResourceProperties.active_resource_index
            ].ifc_definition_id
        elif obj_type == "Profile":
            props = tool.Profile.get_profile_props()
            return props.profiles[props.active_profile_index].ifc_definition_id
        elif obj_type == "WorkSchedule":
            wsprops = tool.Sequence.get_work_schedule_props()
            return wsprops.active_work_schedule_id
        elif obj_type == "Group":
            prop = context.scene.BIMGroupProperties
            return prop.groups[prop.active_group_index].ifc_definition_id
        assert_never(obj_type)

    @classmethod
    def is_ifc_object(cls, obj: bpy.types.Object) -> bool:
        props = tool.Blender.get_object_bim_props(obj)
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
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == "VIEW_3D":
                    return area

    @classmethod
    def get_view3d_space(cls) -> Union[bpy.types.SpaceView3D, None]:
        if area := cls.get_view3d_area():
            return area.spaces.active

    @classmethod
    def get_blender_prop_default_value(cls, props, prop_name: str) -> Any:
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
        with bpy.context.temp_override(**tool.Blender.get_viewport_context()):
            bpy.ops.wm.tool_set_by_id(name=tool_name)

    @classmethod
    def get_shader_editor_context(cls) -> Union[dict[str, Any], None]:
        for screen in bpy.data.screens:
            for area in screen.areas:
                if area.type == "NODE_EDITOR":
                    space = area.spaces.active
                    assert isinstance(space, bpy.types.SpaceNodeEditor)
                    if space.tree_type == "ShaderNodeTree":
                        context_override = {"area": area, "space": space, "screen": screen}
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
        if not blender_material.use_nodes:
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
        tool.Blender.get_viewport_context()["area"].tag_redraw()

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

        row = layout if ui_context == "TOOL_HEADER" else layout.row(align=True)
        module = sys.modules[module_name]
        icon_previews: Union[bpy.utils.previews.ImagePreviewCollection, None]
        icon_previews = getattr(module, "custom_icon_previews", None)
        if icon_previews:
            custom_icon = icon_previews.get(text.upper().replace(" ", "_"), icon_previews["IFC"]).icon_id
            op = row.operator(operator_to_use, text=op_text, icon_value=custom_icon)
        else:
            op = row.operator(operator_to_use, text=op_text)
        if ui_context != "TOOL_HEADER":
            row.label(text="", icon=modifier_icon)
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
    def get_object_bounding_box(cls, obj: bpy.types.Object) -> dict:
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
        bbox_dict = {
            "min_x": bound_box[0][0],
            "max_x": bound_box[6][0],
            "min_y": bound_box[0][1],
            "max_y": bound_box[6][1],
            "min_z": bound_box[0][2],
            "max_z": bound_box[6][2],
            "min_point": Vector(bound_box[0]),
            "max_point": Vector(bound_box[6]),
            "center": (Vector(bound_box[6]) + Vector(bound_box[0])) / 2,
        }
        return bbox_dict

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
        selected_objects: list[bpy.types.Object] = list(),
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

    @classmethod
    def get_enum_safe(cls, props: bpy.types.PropertyGroup, prop_name: str) -> Union[str, None]:
        """method created for readibility and to avoid console warnings like
        `pyrna_enum_to_py: current value '17' matches no enum in 'BIMModelProperties', '', 'relating_type_id'`

        :return: Enum property value as a string or None if current enum value is invalid.
        """
        # Yes, accessing items through annotations is a bit hacky
        # but it's the only way to get the dynamic enum items
        # besides providing them to get_enum_safe explicitly.
        prop_keywords = props.__annotations__[prop_name].keywords
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
        current_value = tool.Blender.get_enum_safe(props, prop_name)
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
        :rtype: None
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
        :rtype: None
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
    def toggle_edit_mode(cls, context: bpy.types.Context) -> set[str]:
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
        element = tool.Ifc.get().by_guid(guid)
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
        project_collection = tool.Blender.get_object_bim_props(project).collection
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

            Returns True if an action was taken, False otherwise
            """
            if cls.is_roof(element):
                if cls.is_editing_roof_parameters(obj):
                    bpy.ops.bim.finish_editing_roof()
                bpy.ops.bim.enable_editing_roof_path()
            elif cls.is_railing(element):
                if cls.is_editing_railing_parameters(obj):
                    bpy.ops.bim.finish_editing_railing()
                bpy.ops.bim.enable_editing_railing_path()
            elif cls.is_editing_stair_parameters(obj):
                bpy.ops.bim.finish_editing_stair()
            elif cls.is_editing_door_parameters(obj):
                bpy.ops.bim.finish_editing_door()
            elif cls.is_editing_window_parameters(obj):
                bpy.ops.bim.finish_editing_window()
            else:
                return False
            return True

        @classmethod
        def try_canceling_editing_modifier_parameters_or_path(cls, obj: bpy.types.Object) -> bool:
            """Tries to cancel the current BIM modifier parameters or path edition for the active object

            Returns True if an action was taken, False otherwise
            """
            if cls.is_editing_railing_path(obj):
                bpy.ops.bim.cancel_editing_railing_path()
            elif cls.is_editing_roof_path(obj):
                bpy.ops.bim.cancel_editing_roof_path()
            elif cls.is_editing_railing_parameters(obj):
                bpy.ops.bim.cancel_editing_railing()
            elif cls.is_editing_door_parameters(obj):
                bpy.ops.bim.cancel_editing_door()
            elif cls.is_editing_window_parameters(obj):
                bpy.ops.bim.cancel_editing_window()
            elif cls.is_editing_roof_parameters(obj):
                bpy.ops.bim.cancel_editing_roof()
            elif cls.is_editing_stair_parameters(obj):
                bpy.ops.bim.cancel_editing_stair()
            else:
                return False
            return True

        @classmethod
        def is_eligible_for_railing_modifier(cls, obj: bpy.types.Object) -> bool:
            return tool.Blender.is_object_an_ifc_class(obj, ("IfcRailing", "IfcRailingType"))

        @classmethod
        def is_eligible_for_stair_modifier(cls, obj: bpy.types.Object) -> bool:
            return tool.Blender.is_object_an_ifc_class(
                obj, ("IfcStairFlight", "IfcStairFlightType", "IfcMember", "IfcMemberType", "IfcStair", "IfcStairType")
            )

        @classmethod
        def is_eligible_for_window_modifier(cls, obj: bpy.types.Object) -> bool:
            return tool.Blender.is_object_an_ifc_class(obj, ("IfcWindow", "IfcWindowType", "IfcWindowStyle"))

        @classmethod
        def is_eligible_for_door_modifier(cls, obj: bpy.types.Object) -> bool:
            return tool.Blender.is_object_an_ifc_class(obj, ("IfcDoor", "IfcDoorType", "IfcDoorStyle"))

        @classmethod
        def is_eligible_for_roof_modifier(cls, obj: bpy.types.Object) -> bool:
            return tool.Blender.is_object_an_ifc_class(obj, ("IfcRoof", "IfcRoofType"))

        @classmethod
        def is_railing(cls, element: entity_instance) -> bool:
            return tool.Pset.get_element_pset(element, "BBIM_Railing")

        @classmethod
        def is_roof(cls, element: entity_instance) -> bool:
            return tool.Pset.get_element_pset(element, "BBIM_Roof")

        @classmethod
        def is_window(cls, element: entity_instance) -> bool:
            return tool.Pset.get_element_pset(element, "BBIM_Window")

        @classmethod
        def is_door(cls, element: entity_instance) -> bool:
            return tool.Pset.get_element_pset(element, "BBIM_Door")

        @classmethod
        def is_stair(cls, element: entity_instance) -> bool:
            return tool.Pset.get_element_pset(element, "BBIM_Stair")

        @classmethod
        def is_editing_railing_path(cls, obj: bpy.types.Object):
            props = tool.Model.get_railing_props(obj)
            return props.is_editing_path

        @classmethod
        def is_editing_roof_path(cls, obj: bpy.types.Object) -> bool:
            props = tool.Model.get_roof_props(obj)
            return props.is_editing_path

        @classmethod
        def is_editing_railing_parameters(cls, obj: bpy.types.Object) -> bool:
            props = tool.Model.get_railing_props(obj)
            return props.is_editing

        @classmethod
        def is_editing_roof_parameters(cls, obj: bpy.types.Object) -> bool:
            props = tool.Model.get_roof_props(obj)
            return props.is_editing

        @classmethod
        def is_editing_window_parameters(cls, obj: bpy.types.Object) -> bool:
            props = tool.Model.get_window_props(obj)
            return props.is_editing

        @classmethod
        def is_editing_door_parameters(cls, obj: bpy.types.Object) -> bool:
            props = tool.Model.get_door_props(obj)
            return props.is_editing

        @classmethod
        def is_editing_stair_parameters(cls, obj: bpy.types.Object) -> bool:
            props = tool.Model.get_stair_props(obj)
            return props.is_editing

        @classmethod
        def is_modifier_with_non_editable_path(cls, element: entity_instance) -> bool:
            return cls.is_stair(element) or cls.is_door(element) or cls.is_window(element)

        class Array:
            @classmethod
            def bake_children_transform(cls, parent_element: entity_instance, item: int) -> None:
                modifier_data = list(cls.get_modifiers_data(parent_element))[item]
                children = cls.get_children_objects(modifier_data)
                for child in children:
                    constraint = next((c for c in child.constraints if c.type == "CHILD_OF"), None)
                    if constraint:
                        with bpy.context.temp_override(object=child):
                            bpy.ops.constraint.apply(constraint=constraint.name, owner="OBJECT")

            @classmethod
            def constrain_children_to_parent(cls, parent_element: ifcopenshell.entity_instance) -> None:
                parent_obj = tool.Ifc.get_object(parent_element)
                assert isinstance(parent_obj, bpy.types.Object)
                children = cls.get_all_children_objects(parent_element)
                for child in children:
                    constraint = next((c for c in child.constraints if c.type == "CHILD_OF"), None)
                    if constraint:
                        child.constraints.remove(constraint)
                    constraint = child.constraints.new("CHILD_OF")
                    constraint.name = "BBIM_Array_CHILD_OF"
                    assert isinstance(constraint, bpy.types.ChildOfConstraint)
                    constraint.target = parent_obj

            @classmethod
            def set_children_lock_state(
                cls, parent_element: ifcopenshell.entity_instance, item: int, lock_state: bool = True
            ) -> None:
                modifier_data = list(cls.get_modifiers_data(parent_element))[item]
                children = cls.get_children_objects(modifier_data)
                for child_obj in children:
                    Blender.lock_transform(child_obj, lock_state)

            @classmethod
            def remove_constraints(cls, parent_element: ifcopenshell.entity_instance) -> None:
                children = cls.get_all_children_objects(parent_element)
                for child in children:
                    constraint = next((c for c in child.constraints if c.type == "CHILD_OF"), None)
                    if constraint:
                        child.constraints.remove(constraint)

            @classmethod
            def get_all_objects(cls, parent_element: ifcopenshell.entity_instance) -> list[bpy.types.Object]:
                parent_obj = tool.Ifc.get_object(parent_element)
                assert isinstance(parent_obj, bpy.types.Object)
                children_objects = list(cls.get_all_children_objects(parent_element))
                array_objects = [parent_obj] + children_objects  # We ensure the parent is at index 0
                return array_objects

            @classmethod
            def get_all_children_objects(
                cls, parent_element: ifcopenshell.entity_instance
            ) -> Generator[bpy.types.Object, None, None]:
                for array_modifier in cls.get_modifiers_data(parent_element):
                    yield from cls.get_children_objects(array_modifier)

            @classmethod
            def get_modifiers_data(
                cls, parent_element: ifcopenshell.entity_instance
            ) -> Generator[dict[str, Any], None, None]:
                array_pset = ifcopenshell.util.element.get_pset(parent_element, "BBIM_Array")
                yield from json.loads(array_pset["Data"])

            @classmethod
            def get_children_objects(cls, modifier_data: dict[str, Any]) -> Generator[bpy.types.Object, None, None]:
                child_guid: str
                for child_guid in modifier_data["children"]:
                    child_obj = tool.Blender.get_object_from_guid(child_guid)
                    if child_obj:
                        yield child_obj

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
        """Get 8 symbols of last commit hash if it's present or return None otherwise."""
        bbim = cls.get_bbim_extension_package()
        commit_hash = bbim.last_commit_hash

        # Commit hash is unset - user is using __init__ from repo
        # without setting up git repository.
        if commit_hash == "8888888":
            return None

        return commit_hash[:7]

    @classmethod
    def get_bonsai_version(cls) -> str:
        bbim = cls.get_bbim_extension_package()
        version = bbim.bbim_semver["version"]
        if commit_hash := cls.get_last_commit_hash():
            version += f"-{commit_hash}"
        return version

    @classmethod
    def register_toolbar(cls):
        import bonsai.bim.module.model.workspace as ws_model
        import bonsai.bim.module.drawing.workspace as ws_drawing
        import bonsai.bim.module.spatial.workspace as ws_spatial
        import bonsai.bim.module.structural.workspace as ws_structural
        import bonsai.bim.module.covering.workspace as ws_covering

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
        import bonsai.bim.module.model.workspace as ws_model
        import bonsai.bim.module.drawing.workspace as ws_drawing
        import bonsai.bim.module.spatial.workspace as ws_spatial
        import bonsai.bim.module.structural.workspace as ws_structural
        import bonsai.bim.module.covering.workspace as ws_covering

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
            return tool.Blender.is_tab(context, "BLENDER")

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
    def get_sun_position_addon(cls) -> Union[types.ModuleType, None]:
        # Check if it's installed as legacy Blender addon.
        import importlib

        try:
            sun_position = importlib.import_module("sun_position")
        except ImportError:
            sun_position = None

        if sun_position:
            return sun_position

        for package_name in bpy.context.preferences.addons.keys():
            if package_name.endswith(".sun_position"):
                try:
                    sun_position = importlib.import_module(package_name)
                    return sun_position
                except ModuleNotFoundError:
                    pass

        return sun_position

    @classmethod
    def scale_font_size(cls, size):
        default_dpi = 72
        default_pixel_size = 1.0
        default_scale = default_dpi * default_pixel_size
        system = bpy.context.preferences.system
        system_scale = system.dpi * system.pixel_size
        return (system_scale / default_scale) * size

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

        Args:
            color_path (str, optional): The attribute path relative to bpy.context.preferences.themes[0].
            threshold (float, optional): The RGB sum threshold for determining dark mode. Default is 1.671.

        Returns:
            str: 'dm' (dark mode) if the RGB sum is > threshold, otherwise 'lm' (light mode).
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
        props = tool.Blender.get_bim_props()
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
        from bonsai.bim.module.model.workspace import BimTool
        from bonsai.bim.module.drawing.workspace import AnnotationTool

        return tuple(cls.bl_idname for cls in (BimTool.__subclasses__() + [BimTool, AnnotationTool]))

    @classmethod
    @lru_cache
    def get_tools_to_classes_map(cls) -> types.MappingProxyType[str, str]:
        from bonsai.bim.module.model.workspace import BimTool

        dct = {cls.bl_idname: cls.ifc_element_type for cls in (BimTool.__subclasses__())}
        return types.MappingProxyType(dct)

    @classmethod
    def get_csv_props(cls) -> CsvProperties:
        return bpy.context.scene.CsvProperties

    @classmethod
    def get_diff_props(cls) -> DiffProperties:
        return bpy.context.scene.DiffProperties

    @classmethod
    def get_bim_props(cls, scene: Optional[bpy.types.Scene] = None) -> BIMProperties:
        if scene is None:
            scene = bpy.context.scene
        return scene.BIMProperties

    @classmethod
    def get_object_bim_props(cls, obj: bpy.types.Object) -> BIMObjectProperties:
        return obj.BIMObjectProperties

    @classmethod
    def get_ifc_definition_id(cls, obj: IFC_CONNECTED_TYPE) -> int:
        if isinstance(obj, bpy.types.Object):
            return tool.Blender.get_object_bim_props(obj).ifc_definition_id
        return tool.Style.get_material_style_props(obj).ifc_definition_id

    @classmethod
    def get_active_uilist_element(
        cls, collection: bpy.types.bpy_prop_collection_idprop[T], index: int
    ) -> Union[T, None]:
        if 0 <= index < len(collection):
            return collection[index]
        return None

    @classmethod
    def clear_undo_history(cls) -> None:
        """Clears the Blender history, Bonsai history, and IfcOpenShell history"""
        old_undo_steps = bpy.context.preferences.edit.undo_steps
        bpy.context.preferences.edit.undo_steps = 2
        for i in range(3):
            bpy.ops.ed.undo_push(message="Undo history cleared")
        bpy.context.preferences.edit.undo_steps = old_undo_steps
        tool.Ifc.clear_history()
        old_history_size = tool.Ifc.get().history_size
        tool.Ifc.get().set_history_size(0)
        tool.Ifc.get().set_history_size(old_history_size)

    @classmethod
    def get_unit_scale(cls):
        unit_length = bpy.context.scene.unit_settings.length_unit
        unit_scale = 1.0
        if unit_length == "CENTIMETERS":
            unit_scale = 0.01
        if unit_length == "MILLIMETERS":
            unit_scale = 0.001
        if unit_length == "FEET":
            unit_scale = 0.3048

        return unit_scale
