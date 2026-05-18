# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Bonsai contributors
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

from typing import TYPE_CHECKING

import re
import bpy
from bpy.props import BoolProperty, StringProperty

import bonsai.tool as tool


def _derive_per_obj_key(base_key: str, obj_name: str) -> str:
    """Return the per-object binding key for obj_name, replacing any embedded object name or appending a ::suffix."""
    m = re.search(r"bpy\.data\.objects\['([^']+)'\]", base_key)
    if m:
        source_name = m.group(1)
        return base_key.replace(f"['{source_name}']", f"['{obj_name}']", 1)
    return f"{base_key}::{obj_name}"


def _get_param_items(self, context: bpy.types.Context):
    """Return enum items for all parameters defined in the BExpEng panel."""
    items = [("__NONE__", "\u2014 select a parameter \u2014", "No parameter selected")]
    for item in context.scene.bexpeng.expressions:
        tooltip = f"= {item.expression}  [{item.value_str}]"
        if item.description:
            tooltip += f"\n{item.description}"
        items.append((item.param_name, item.param_name, tooltip))
    return items


def _param_name_update(self: bpy.types.Operator, context: bpy.types.Context) -> None:
    """Auto-attach when a real parameter is selected while the toggle is unlinked."""
    if self.param_name != "__NONE__" and not self.is_attached:
        self.is_attached = True


class BIM_OT_bexpeng_attach_param(bpy.types.Operator):
    """Bind this field to an existing BExpEng parameter"""

    bl_idname = "bim.bexpeng_attach_param"
    bl_label = "Attach BExpEng Parameter"
    bl_options = {"UNDO"}

    binding_key: StringProperty(name="Binding Key", options={"HIDDEN"})
    data_type: StringProperty(name="Data Type", options={"HIDDEN"})
    show_bulk: BoolProperty(name="Show Bulk", default=True, options={"HIDDEN"})
    was_bound: BoolProperty(name="Was Bound", default=False, options={"HIDDEN", "SKIP_SAVE"})
    param_name: bpy.props.EnumProperty(
        name="Parameter",
        description="Select a BExpEng parameter to bind this field to",
        items=_get_param_items,
        update=_param_name_update,
        options={"SKIP_SAVE"},
    )
    is_attached: BoolProperty(
        name="Attached",
        description="Toggle binding on/off. Attach requires a parameter to be selected",
        default=False,
        options={"SKIP_SAVE"},
    )

    if TYPE_CHECKING:
        binding_key: str
        data_type: str
        show_bulk: bool
        was_bound: bool
        param_name: str
        is_attached: bool

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> set[str]:
        from bonsai.bim.module import bexpeng as bexpengmod

        current = bexpengmod.get_binding(self.binding_key)
        valid_names = {item.param_name for item in context.scene.bexpeng.expressions}
        if current and current not in valid_names:
            current = None
        self.was_bound = bool(current)
        self.param_name = current if current else "__NONE__"
        self.is_attached = bool(current)
        return context.window_manager.invoke_props_dialog(self, width=300)

    def draw(self, context: bpy.types.Context) -> None:
        from bonsai.bim.module import bexpeng as bexpengmod

        current = bexpengmod.get_binding(self.binding_key)
        now_bound = bool(current)
        if now_bound != self.was_bound:
            self.is_attached = now_bound
            self.was_bound = now_bound
        row = self.layout.row(align=True)
        row.prop(self, "param_name", text="")
        toggle_row = row.row(align=True)
        has_param = self.param_name != "__NONE__"
        toggle_row.enabled = self.is_attached or has_param
        icon = "LINKED" if self.is_attached else "UNLINKED"
        toggle_row.prop(self, "is_attached", text="", icon=icon, toggle=True)
        if self.show_bulk:
            param = self.param_name if self.param_name != "__NONE__" else ""
            op = row.operator("bim.bexpeng_bulk_apply_param", text="", icon="FOLDER_REDIRECT")
            op.binding_key = self.binding_key
            op.param_name = param
            op.data_type = self.data_type
            op.is_removing = False

    def execute(self, context: bpy.types.Context) -> set[str]:
        from bonsai.bim.module import bexpeng as bexpengmod

        if not self.is_attached:
            obj = context.active_object
            key = _derive_per_obj_key(self.binding_key, obj.name) if obj is not None else self.binding_key
            bexpengmod.clear_binding(key)
            from bexpeng.operators import sync_ui_list

            sync_ui_list(context)
            for area in context.screen.areas:
                area.tag_redraw()
            return {"FINISHED"}

        param = self.param_name if self.param_name not in ("__NONE__", "") else ""
        if not param:
            bexpengmod.clear_binding(self.binding_key)
            for area in context.screen.areas:
                area.tag_redraw()
            return {"FINISHED"}

        commit = bexpengmod._detect_commit(self.binding_key, context)
        objects: list[str] | None = None
        if commit and commit.get("op") in ("bim.change_extrusion_depth", "bim.change_layer_length"):
            objects = [obj.name for obj in tool.Model.get_selected_mesh_ifc_objects()]
        try:
            from bexpeng.engine import ParametricEngine

            param_id = ParametricEngine.get_instance().get_id(param) or ""
        except Exception:
            param_id = ""
        if not param_id:
            self.report({"WARNING"}, f"BExpEng: parameter '{param}' not found in engine. Is bexpeng loaded?")
            return {"CANCELLED"}
        bexpengmod.set_binding(self.binding_key, param_id, self.data_type, commit, objects=objects)
        bexpengmod._attach_and_apply(self.binding_key, self.data_type, param_id, commit, objects=objects)
        from bexpeng.operators import sync_ui_list

        sync_ui_list(context)
        for area in context.screen.areas:
            area.tag_redraw()
        return {"FINISHED"}


class BIM_OT_bexpeng_detach_param(bpy.types.Operator):
    """Remove the BExpEng parameter binding from this field"""

    bl_idname = "bim.bexpeng_detach_param"
    bl_label = "Detach BExpEng Parameter"
    bl_options = {"UNDO"}

    binding_key: StringProperty(name="Binding Key", options={"HIDDEN"})
    if TYPE_CHECKING:
        binding_key: str

    def execute(self, context: bpy.types.Context) -> set[str]:
        from bonsai.bim.module import bexpeng as bexpengmod

        bexpengmod.clear_binding(self.binding_key)

        for area in context.screen.areas:
            area.tag_redraw()
        return {"FINISHED"}


class BIM_OT_bexpeng_bulk_apply_param(bpy.types.Operator):
    """Apply or remove this parameter binding for all selected objects.\nALT + CLICK to remove from all selected"""

    bl_idname = "bim.bexpeng_bulk_apply_param"
    bl_label = "Bulk Apply BExpEng Parameter"
    bl_options = {"UNDO"}
    bl_description = "Apply binding to all currently selected objects\nALT + CLICK to remove from all selected"

    binding_key: StringProperty(name="Binding Key", options={"HIDDEN"})
    param_name: StringProperty(name="Parameter Name", options={"HIDDEN"})
    data_type: StringProperty(name="Data Type", options={"HIDDEN"})
    is_removing: BoolProperty(name="Remove", default=False, options={"HIDDEN", "SKIP_SAVE"})

    if TYPE_CHECKING:
        binding_key: str
        param_name: str
        data_type: str
        is_removing: bool

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> set[str]:
        self.is_removing = self.is_removing or event.alt
        return self.execute(context)

    def execute(self, context: bpy.types.Context) -> set[str]:
        from bonsai.bim.module import bexpeng as bexpengmod

        base_key = self.binding_key.split("::")[0]
        bexpengmod.clear_binding(base_key)

        selected = set(context.selected_objects)
        if context.active_object:
            selected.add(context.active_object)

        count = 0
        for obj in selected:
            obj_key = _derive_per_obj_key(base_key, obj.name)
            if self.is_removing:
                bexpengmod.clear_binding(obj_key)
                count += 1
            else:
                if not self.param_name:
                    continue
                commit = bexpengmod._detect_commit(obj_key, context)
                if commit and isinstance(commit.get("kwargs"), dict):
                    patched_kwargs = dict(commit["kwargs"])
                    if "obj" in patched_kwargs:
                        patched_kwargs["obj"] = obj.name
                    if "_obj" in patched_kwargs:
                        patched_kwargs["_obj"] = obj.name
                    commit = {**commit, "kwargs": patched_kwargs}
                try:
                    from bexpeng.engine import ParametricEngine

                    param_id = ParametricEngine.get_instance().get_id(self.param_name) or ""
                except Exception:
                    param_id = ""
                if not param_id:
                    continue
                bexpengmod.set_binding(obj_key, param_id, self.data_type, commit, objects=[obj.name])
                bexpengmod._attach_and_apply(obj_key, self.data_type, param_id, commit, objects=[obj.name])
                count += 1

        from bexpeng.operators import sync_ui_list

        sync_ui_list(context)
        for area in context.screen.areas:
            area.tag_redraw()
        action = "removed from" if self.is_removing else "applied to"
        self.report({"INFO"}, f"BExpEng binding {action} {count} objects.")
        return {"FINISHED"}
