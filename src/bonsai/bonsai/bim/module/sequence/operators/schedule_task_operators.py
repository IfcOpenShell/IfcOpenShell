# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021, 2022 Dion Moult <dion@thinkmoult.com>, Yassine Oualid <yassine@sigmadimensions.com>, Federico Eraso <feraso@svisuals.net
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

import bpy
import json
import calendar
from mathutils import Matrix
from datetime import datetime
from dateutil import relativedelta
import bonsai.tool as tool
import bonsai.core.sequence as core
from .operator import snapshot_all_ui_state

try:
    from ..prop import safe_set_selected_colortype_in_active_group
    
except (ImportError, ValueError):
    # Fallback if the structure changes
    from bonsai.bim.module.sequence.prop import safe_set_selected_colortype_in_active_group

try:
    from .prop import update_filter_column
    from . import prop
    from .ui import calculate_visible_columns_count
except Exception:
    try:
        from ..prop.filter import update_filter_column
        from .. import prop
        from ..ui.schedule_ui import calculate_visible_columns_count
    except Exception:
        def update_filter_column(*args, **kwargs):
            pass
        def calculate_visible_columns_count(context):
            return 3  # Safe fallback
        # Fallback for safe assignment function
        class PropFallback:
            @staticmethod
            def safe_set_selected_colortype_in_active_group(task_obj, value, skip_validation=False):
                try:
                    setattr(task_obj, "selected_colortype_in_active_group", value)
                except Exception as e:
                    print(f"[ERROR] Fallback safe_set failed: {e}")
        prop = PropFallback()

# LEGACY FUNCTIONS REMOVED - USE operator.py INSTEAD

# # def snapshot_all_ui_state(context): # ELIMINATED - USE operator.py
#     """
#     (SNAPSHOT) Captures the complete state of the profiles UI and saves it
#     in temporary scene properties. It also maintains a persistent cache
#     to support filter toggling (filter -> unfilter)
#     without losing data from hidden tasks.
#     """
#     import json
#     try:
#         # 1. Snapshot of the profile configuration per task
#         tprops = tool.Sequence.get_task_tree_props()
#         task_snap = {}
#         
#         # Also capture data from all tasks of the active schedule
#         # to avoid data loss when filters are applied/removed
#         try:
#             ws = tool.Sequence.get_active_work_schedule()
#             if ws:
#                 import ifcopenshell.util.sequence
#                 
#                 def get_all_tasks_recursive(tasks):
#                     """Recursively gets all tasks and subtasks."""
#                     all_tasks = []
#                     for task in tasks:
#                         all_tasks.append(task)
#                         nested = ifcopenshell.util.sequence.get_nested_tasks(task)
#                         if nested:
#                             all_tasks.extend(get_all_tasks_recursive(nested))
#                     return all_tasks
#                 
#                 root_tasks = ifcopenshell.util.sequence.get_root_tasks(ws)
#                 all_tasks = get_all_tasks_recursive(root_tasks)
#                 
#                 # Create a snapshot of all tasks, not just the visible ones
#                 task_id_to_ui_data = {str(getattr(t, "ifc_definition_id", 0)): t for t in getattr(tprops, "tasks", [])}
#                 
#                 for task in all_tasks:
#                     tid = str(task.id())
#                     if tid == "0":
#                         continue
# 
#                     # If the task is visible in the UI, use its current data
#                     if tid in task_id_to_ui_data:
#                         t = task_id_to_ui_data[tid]
#                         groups_list = []
#                         for g in getattr(t, "colortype_group_choices", []):
#                             sel_attr = None
#                             for cand in ("selected_colortype", "selected", "active_colortype", "colortype"):
#                                 if hasattr(g, cand):
#                                     sel_attr = cand
#                                     break
#                             groups_list.append({
#                                 "group_name": getattr(g, "group_name", ""),
#                                 "enabled": bool(getattr(g, "enabled", False)),
#                                 "selected_value": getattr(g, sel_attr, "") if sel_attr else "",
#                                 "selected_attr": sel_attr or "",
#                             })
#                         task_snap[tid] = {
#                             "active": bool(getattr(t, "use_active_colortype_group", False)),
#                             "selected_active_colortype": getattr(t, "selected_colortype_in_active_group", ""),
#                             "animation_color_schemes": getattr(t, "animation_color_schemes", ""),
#                             "groups": groups_list,
#                         }
#                     else:
#                         # If the task is not visible (filtered), preserve data from the cache
#                         cache_key = "_task_colortype_snapshot_cache_json"
#                         cache_raw = context.scene.get(cache_key)
#                         if cache_raw:
#                             try:
#                                 cached_data = json.loads(cache_raw)
#                                 if tid in cached_data:
#                                     task_snap[tid] = cached_data[tid]
#                                 else:
#                                     # Create an empty entry for tasks without previous data
#                                     task_snap[tid] = {
#                                         "active": False,
#                                         "selected_active_colortype": "",
#                                         "animation_color_schemes": "",
#                                         "groups": [],
#                                     }
#                             except Exception:
#                                 task_snap[tid] = {
#                                     "active": False,
#                                     "selected_active_colortype": "",
#                                     "animation_color_schemes": "",
#                                     "groups": [],
#                                 }
#                         else:
#                             task_snap[tid] = {
#                                 "active": False,
#                                 "selected_active_colortype": "",
#                                 "animation_color_schemes": "",
#                                 "groups": [],
#                             }
#         except Exception as e:
#             print(f"Bonsai WARNING: Error capturando todas las tasks: {e}")
#             # Fallback to the original method with only visible tasks
#             for t in getattr(tprops, "tasks", []):
#                 tid = str(getattr(t, "ifc_definition_id", 0))
#                 if tid == "0":
#                     continue
#                 groups_list = []
#                 for g in getattr(t, "colortype_group_choices", []):
#                     sel_attr = None
#                     for cand in ("selected_colortype", "selected", "active_colortype", "colortype"):
#                         if hasattr(g, cand):
#                             sel_attr = cand
#                             break
#                     groups_list.append({
#                         "group_name": getattr(g, "group_name", ""),
#                         "enabled": bool(getattr(g, "enabled", False)),
#                         "selected_value": getattr(g, sel_attr, "") if sel_attr else "",
#                         "selected_attr": sel_attr or "",
#                     })
#                 task_snap[tid] = {
#                     "active": bool(getattr(t, "use_active_colortype_group", False)),
#                     "selected_active_colortype": getattr(t, "selected_colortype_in_active_group", ""),
#                     "animation_color_schemes": getattr(t, "animation_color_schemes", ""),
#                     "groups": groups_list,
#                 }
# 
#         # Detect the active WorkSchedule to scope the cache
#         try:
#             ws_props = tool.Sequence.get_work_schedule_props()
#             ws_id = int(getattr(ws_props, "active_work_schedule_id", 0))
#         except Exception:
#             try:
#                 ws = tool.Sequence.get_active_work_schedule()
#                 ws_id = int(getattr(ws, "id", 0) or getattr(ws, "GlobalId", 0) or 0)
#             except Exception:
#                 ws_id = 0
# 
#         # Reset cache if the active WS has changed
#         cache_ws_key = "_task_colortype_snapshot_cache_ws_id"
#         cache_key = "_task_colortype_snapshot_cache_json"
#         prior_ws = context.scene.get(cache_ws_key)
#         if prior_ws is None or int(prior_ws) != ws_id:
#             context.scene[cache_key] = "{}"
#             context.scene[cache_ws_key] = str(ws_id)
# 
#         # Save ephemeral snapshot (current cycle) - BOTH KEYS for compatibility
#         snap_key_specific = f"_task_colortype_snapshot_json_WS_{ws_id}"
#         snap_key_generic = "_task_colortype_snapshot_json"
#         
#         # Save to specific key (for Copy 3D text)
#         context.scene[snap_key_specific] = json.dumps(task_snap)
#         
#         # ALSO save to generic key (for normal system)
#         context.scene[snap_key_generic] = json.dumps(task_snap)
# 
#         # Update persistent cache (merge)
#         merged = {}
#         cache_raw = context.scene.get(cache_key)
#         if cache_raw:
#             try:
#                 merged = json.loads(cache_raw) or {}
#             except Exception:
#                 merged = {}
#         merged.update(task_snap)
#         context.scene[cache_key] = json.dumps(merged)
# 
#         # 2. Snapshot of the group selectors and the animation stack
#         anim_props = tool.Sequence.get_animation_props()
#         anim_snap = {
#             "ColorType_groups": getattr(anim_props, "ColorType_groups", "DEFAULT"),
#             "task_colortype_group_selector": getattr(anim_props, "task_colortype_group_selector", ""),
#             "animation_group_stack": [
#                 {"group": getattr(item, "group", ""), "enabled": bool(getattr(item, "enabled", False))}
#                 for item in getattr(anim_props, "animation_group_stack", [])
#             ],
#         }
#         context.scene["_anim_state_snapshot_json"] = json.dumps(anim_snap)
#         # 3. Snapshot of active selection/index of the task tree
#         try:
#             wprops = tool.Sequence.get_work_schedule_props()
#             tprops = tool.Sequence.get_task_tree_props()
#             active_idx = int(getattr(wprops, 'active_task_index', -1))
#             active_id = int(getattr(wprops, 'active_task_id', 0))
#             selected_ids = []
#             for t in getattr(tprops, 'tasks', []):
#                 tid = int(getattr(t, 'ifc_definition_id', 0))
#                 sel = False
#                 for cand in ('is_selected','selected'):
#                     if hasattr(t, cand) and bool(getattr(t, cand)):
#                         sel = True
#                         break
#                 if sel:
#                     selected_ids.append(tid)
#             sel_snap = {'active_index': active_idx, 'active_id': active_id, 'selected_ids': selected_ids}
#             context.scene['_task_selection_snapshot_json'] = json.dumps(sel_snap)
#         except Exception:
#             pass
# 
#     except Exception as e:
#         print(f"Bonsai WARNING: No se pudo crear el snapshot de la UI: {e}")
#
#

def restore_all_ui_state(context):
    """
    (RESTORATION) Restores the complete state of the profiles UI from
    the temporary scene properties. It uses a persistent cache to
    cover tasks that were not visible in the ephemeral snapshot (e.g., when
    disabling filters).
    """
    import json
    try:
        # Detect active schedule to use specific keys
        try:
            ws_props = tool.Sequence.get_work_schedule_props()
            ws_id = int(getattr(ws_props, "active_work_schedule_id", 0))
        except Exception:
            try:
                ws = tool.Sequence.get_active_work_schedule()
                ws_id = int(getattr(ws, "id", 0) or getattr(ws, "GlobalId", 0) or 0)
            except Exception:
                ws_id = 0

        # 1. Restore profile configuration in tasks - SCHEDULE-SPECIFIC
        snap_key_specific = f"_task_colortype_snapshot_json_WS_{ws_id}"
        cache_key = "_task_colortype_snapshot_cache_json"

        # Union: cache ∪ snapshot (snapshot has priority)
        union = {}
        cache_raw = context.scene.get(cache_key)
        if cache_raw:
            try:
                union.update(json.loads(cache_raw) or {})
            except Exception:
                pass
        snap_raw = context.scene.get(snap_key_specific)
        if snap_raw:
            try:
                snap_data = json.loads(snap_raw) or {}
                union.update(snap_data)
            except Exception:
                pass
        else:
            print(f"[ERROR] DEBUG RESTORE: Key not found {snap_key_specific}")

        if union:
            print(f"[DEBUG] RESTORE: Found {len(union)} tasks in union data")
            tprops = tool.Sequence.get_task_tree_props()
            task_map = {str(getattr(t, "ifc_definition_id", 0)): t for t in getattr(tprops, "tasks", [])}
            print(f"[DEBUG] RESTORE: Current UI has {len(task_map)} tasks")

            for tid, cfg in union.items():
                t = task_map.get(str(tid))
                if not t:
                    print(f"[DEBUG] RESTORE: Task {tid} not found in UI, skipping")
                    continue
                print(f"[DEBUG] RESTORE: Restoring task {tid}")
                # Main state of the task
                try:
                    t.use_active_colortype_group = cfg.get("active", False)

                    # Validation for selected_colortype_in_active_group
                    selected_active_colortype = cfg.get("selected_active_colortype", "")
                    problematic_values = ["0", 0, None, "", "None", "null", "undefined"]

                    if selected_active_colortype in problematic_values:
                        selected_active_colortype = ""
                    else:
                        selected_active_str = str(selected_active_colortype).strip()
                        if selected_active_str in [str(v) for v in problematic_values]:
                            selected_active_colortype = ""

                    print(f"[DEBUG] RESTORE: Task {tid} - trying to restore selected_colortype_in_active_group = '{selected_active_colortype}'")
                    print(f"[DEBUG] RESTORE: Task {tid} - current value BEFORE: '{getattr(t, 'selected_colortype_in_active_group', 'ATTR_NOT_FOUND')}'")

                    from .. import prop
                    prop.safe_set_selected_colortype_in_active_group(t, selected_active_colortype, skip_validation=True)

                    print(f"[DEBUG] RESTORE: Task {tid} - current value AFTER: '{getattr(t, 'selected_colortype_in_active_group', 'ATTR_NOT_FOUND')}'")

                    # Check if the assignment actually worked
                    current_value = getattr(t, 'selected_colortype_in_active_group', '')
                    if current_value != selected_active_colortype:
                        print(f"[DEBUG] RESTORE: Task {tid} - RESTORATION FAILED! Expected: '{selected_active_colortype}', Got: '{current_value}'")

                    # RESTORE animation_color_schemes field
                    animation_color_schemes = cfg.get("animation_color_schemes", "")
                    task_is_active = cfg.get("active", False)

                    if not task_is_active and animation_color_schemes:
                        from ..prop.animation import safe_set_animation_color_schemes
                        safe_set_animation_color_schemes(t, animation_color_schemes)
                    elif not task_is_active:
                        try:
                            from ..prop.animation import get_animation_color_schemes_items, safe_set_animation_color_schemes
                            valid_items = get_animation_color_schemes_items(t, bpy.context)
                            first_valid = valid_items[0][0] if valid_items else ""
                            safe_set_animation_color_schemes(t, first_valid)
                        except Exception:
                            pass
                    else:
                        if selected_active_colortype:
                            from ..prop.animation import safe_set_animation_color_schemes
                            safe_set_animation_color_schemes(t, selected_active_colortype)

                except Exception as e:
                    print(f"[WARNING] Error restoring task properties: {e}")

                # Task groups
                try:
                    t.colortype_group_choices.clear()
                    for g_data in cfg.get("groups", []):
                        item = t.colortype_group_choices.add()
                        item.group_name = g_data.get("group_name", "")

                        # Detect selection attribute
                        sel_attr = None
                        for cand in ("selected_colortype", "selected", "active_colortype", "colortype"):
                            if hasattr(item, cand):
                                sel_attr = cand
                                break
                        if hasattr(item, "enabled"):
                            item.enabled = bool(g_data.get("enabled", False))

                        # Set selection value
                        val = g_data.get("selected_value", "")
                        truly_problematic_values = ["0", 0, None, "None", "null", "undefined"]
                        if val in truly_problematic_values:
                            val = ""
                        else:
                            val = str(val).strip() if val else ""

                        if sel_attr and val is not None:
                            try:
                                setattr(item, sel_attr, val)
                            except Exception as e:
                                print(f"[ERROR] Error setting {sel_attr}: {e}")
                except Exception as e:
                    print(f"[ERROR] Error restoring groups: {e}")
        else:
            print("[ERROR] RESTORE: No union data found - colortype data will be lost!")

        # 2. Restore animation group selectors
        anim_raw = context.scene.get("_anim_state_snapshot_json")
        if anim_raw:
            try:
                anim_data = json.loads(anim_raw) or {}
                anim_props = tool.Sequence.get_animation_props()

                colortype_groups = anim_data.get("ColorType_groups", "DEFAULT")
                if hasattr(anim_props, "ColorType_groups"):
                    anim_props.ColorType_groups = colortype_groups

                task_group_selector = anim_data.get("task_colortype_group_selector", "")
                if hasattr(anim_props, "task_colortype_group_selector"):
                    anim_props.task_colortype_group_selector = task_group_selector

                stack_data = anim_data.get("animation_group_stack", [])
                if hasattr(anim_props, "animation_group_stack"):
                    anim_props.animation_group_stack.clear()
                    for item_data in stack_data:
                        item = anim_props.animation_group_stack.add()
                        item.group = item_data.get("group", "")
                        item.enabled = bool(item_data.get("enabled", False))

            except Exception as e:
                print(f"[WARNING] Error restoring animation selectors: {e}")

        # 3. Restore task selection/index
        try:
            sel_raw = context.scene.get('_task_selection_snapshot_json')
            if sel_raw:
                sel_data = json.loads(sel_raw) or {}
                wprops = tool.Sequence.get_work_schedule_props()
                tprops = tool.Sequence.get_task_tree_props()

                active_idx = sel_data.get('active_index', -1)
                active_id = sel_data.get('active_id', 0)
                if hasattr(wprops, 'active_task_index'):
                    wprops.active_task_index = max(active_idx, -1)
                if hasattr(wprops, 'active_task_id'):
                    wprops.active_task_id = max(active_id, 0)

                selected_ids = set(sel_data.get('selected_ids', []))
                task_map = {int(getattr(t, 'ifc_definition_id', 0)): t for t in getattr(tprops, 'tasks', [])}

                for tid, t in task_map.items():
                    is_selected = tid in selected_ids
                    for cand in ('is_selected', 'selected'):
                        if hasattr(t, cand):
                            try:
                                setattr(t, cand, is_selected)
                                break
                            except Exception:
                                pass
        except Exception as e:
            print(f"[WARNING] Error restoring task selection: {e}")

    except Exception as e:
        print(f"[WARNING] No se pudo restaurar el estado de la UI: {e}")


# ============================================================================
# CORE TASK MANAGEMENT OPERATORS
# ============================================================================

class LoadTaskProperties(bpy.types.Operator):
    bl_idname = "bim.load_task_properties"
    bl_label = "Load Task Properties"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.load_task_properties(tool.Sequence)
        return {"FINISHED"}


class AddTask(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_task"
    bl_label = "Add Task"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()

    def _execute(self, context):
        snapshot_all_ui_state(context)

        core.add_task(tool.Ifc, tool.Sequence, parent_task=tool.Ifc.get().by_id(self.task))

        try:
            ws = tool.Sequence.get_active_work_schedule()
            if ws:
                tool.Sequence.load_task_tree(ws)
                tool.Sequence.load_task_properties()
        except Exception:
            pass

        restore_all_ui_state(context)


class AddSummaryTask(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_summary_task"
    bl_label = "Add Task"
    bl_options = {"REGISTER", "UNDO"}
    work_schedule: bpy.props.IntProperty()

    def _execute(self, context):
        snapshot_all_ui_state(context)

        core.add_summary_task(tool.Ifc, tool.Sequence, work_schedule=tool.Ifc.get().by_id(self.work_schedule))

        try:
            ws = tool.Sequence.get_active_work_schedule()
            if ws:
                tool.Sequence.load_task_tree(ws)
                tool.Sequence.load_task_properties()
        except Exception:
            pass

        restore_all_ui_state(context)


class ExpandTask(bpy.types.Operator):
    bl_idname = "bim.expand_task"
    bl_label = "Expand Task"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()

    def execute(self, context):
        snapshot_all_ui_state(context)

        core.expand_task(tool.Sequence, task=tool.Ifc.get().by_id(self.task))

        return {'FINISHED'}


class ContractTask(bpy.types.Operator):
    bl_idname = "bim.contract_task"
    bl_label = "Contract Task"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()

    def execute(self, context):
        snapshot_all_ui_state(context)

        core.contract_task(tool.Sequence, task=tool.Ifc.get().by_id(self.task))

        return {'FINISHED'}


class RemoveTask(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_task"
    bl_label = "Remove Task"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()

    def _execute(self, context):
        snapshot_all_ui_state(context)

        core.remove_task(tool.Ifc, tool.Sequence, task=tool.Ifc.get().by_id(self.task))

        try:
            ws = tool.Sequence.get_active_work_schedule()
            if ws:
                tool.Sequence.load_task_tree(ws)
                tool.Sequence.load_task_properties()
        except Exception:
            pass

        restore_all_ui_state(context)


class EnableEditingTask(bpy.types.Operator):
    bl_idname = "bim.enable_editing_task_attributes"
    bl_label = "Enable Editing Task Attributes"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()

    def execute(self, context):
        core.enable_editing_task_attributes(tool.Sequence, task=tool.Ifc.get().by_id(self.task))
        return {"FINISHED"}


class DisableEditingTask(bpy.types.Operator):
    bl_idname = "bim.disable_editing_task"
    bl_label = "Disable Editing Task"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        # USE THE SAME PATTERN AS THE FILTERS (which works correctly):
        snapshot_all_ui_state(context)  # >>> 1. Save state BEFORE canceling
        
        # >>> 2. Execute the cancel operation
        core.disable_editing_task(tool.Sequence)
        
        return {"FINISHED"}


class EditTask(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_task"
    bl_label = "Edit Task"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = tool.Sequence.get_work_schedule_props()
        core.edit_task(tool.Ifc, tool.Sequence, task=tool.Ifc.get().by_id(props.active_task_id))


class CopyTaskAttribute(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.copy_task_attribute"
    bl_label = "Copy Task Attribute"
    bl_options = {"REGISTER", "UNDO"}
    name: bpy.props.StringProperty()

    def _execute(self, context):
        core.copy_task_attribute(tool.Ifc, tool.Sequence, attribute_name=self.name)


class CalculateTaskDuration(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.calculate_task_duration"
    bl_label = "Calculate Task Duration"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()

    def _execute(self, context):
        snapshot_all_ui_state(context)

        core.calculate_task_duration(tool.Ifc, tool.Sequence, task=tool.Ifc.get().by_id(self.task))

        restore_all_ui_state(context)


class ExpandAllTasks(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.expand_all_tasks"
    bl_label = "Expands All Tasks"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Finds the related Task"
    product_type: bpy.props.StringProperty()

    def _execute(self, context):
        snapshot_all_ui_state(context)

        core.expand_all_tasks(tool.Sequence)

        restore_all_ui_state(context)


class ContractAllTasks(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.contract_all_tasks"
    bl_label = "Expands All Tasks"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Finds the related Task"
    product_type: bpy.props.StringProperty()

    def _execute(self, context):
        snapshot_all_ui_state(context)

        core.contract_all_tasks(tool.Sequence)

        restore_all_ui_state(context)


class CopyTask(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.duplicate_task"
    bl_label = "Copy Task"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()

    def _execute(self, context):
        snapshot_all_ui_state(context)

        core.duplicate_task(tool.Ifc, tool.Sequence, task=tool.Ifc.get().by_id(self.task))

        try:
            ws = tool.Sequence.get_active_work_schedule()
            if ws:
                tool.Sequence.load_task_tree(ws)
                tool.Sequence.load_task_properties()
        except Exception:
            pass

        restore_all_ui_state(context)


class GoToTask(bpy.types.Operator):
    bl_idname = "bim.go_to_task"
    bl_label = "Highlight Task"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()

    def execute(self, context):
        r = core.go_to_task(tool.Sequence, task=tool.Ifc.get().by_id(self.task))
        if isinstance(r, str):
            self.report({"WARNING"}, r)
        return {"FINISHED"}


class ReorderTask(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.reorder_task_nesting"
    bl_label = "Reorder Nesting"
    bl_options = {"REGISTER", "UNDO"}
    new_index: bpy.props.IntProperty()
    task: bpy.props.IntProperty()

    def _execute(self, context):
        snapshot_all_ui_state(context)

        r = core.reorder_task_nesting(
            tool.Ifc, tool.Sequence, task=tool.Ifc.get().by_id(self.task), new_index=self.new_index
        )

        if isinstance(r, str):
            self.report({"WARNING"}, r)

        try:
            ws = tool.Sequence.get_active_work_schedule()
            if ws:
                tool.Sequence.load_task_tree(ws)
                tool.Sequence.load_task_properties()
        except Exception:
            pass

        restore_all_ui_state(context)

def _save_3d_texts_state():
    # Save current state of all three-dimensional text objects before snapshot
    try:
        coll = bpy.data.collections.get("Schedule_Display_Texts")
        if not coll:
            return
        
        state_data = {}
        for obj in coll.objects:
            if hasattr(obj, "data") and obj.data:
                state_data[obj.name] = obj.data.body
        
        # Store in scene for restoration
        bpy.context.scene["3d_texts_previous_state"] = json.dumps(state_data)
        print(f"💾 Saved state for {len(state_data)} three-dimensional text objects")
        
    except Exception as e:
        print(f"[ERROR] Error saving three-dimensional texts state: {e}")

def _restore_3d_texts_state():
    """Restore previous state of all three-dimensional text objects after snapshot reset."""
    import json
    try:
        if "3d_texts_previous_state" not in bpy.context.scene:
            print("[WARNING] No previous three-dimensional texts state found to restore")
            return

        coll = bpy.data.collections.get("Schedule_Display_Texts")
        if not coll:
            print("[WARNING] No 'Schedule_Display_Texts' collection found for restoration")
            return

        state_data = json.loads(bpy.context.scene["3d_texts_previous_state"])
        restored_count = 0

        for obj in coll.objects:
            if hasattr(obj, "data") and obj.data and obj.name in state_data:
                obj.data.body = state_data[obj.name]
                restored_count += 1

        # Clean up saved state
        del bpy.context.scene["3d_texts_previous_state"]
        print(f"🔄 Restored state for {restored_count} three-dimensional text objects")

    except Exception as e:
        print(f"[ERROR] Error restoring three-dimensional texts state: {e}")


class RefreshTaskOutputCounts(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.refresh_task_output_counts"
    bl_label = "Refresh Task Output Counts"
    bl_description = "Refresh the count of 3D elements assigned to tasks"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        try:
            core.refresh_task_output_counts(tool.Sequence)
            self.report({'INFO'}, "Task output counts refreshed successfully")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to refresh task output counts: {str(e)}")
        return {"FINISHED"}
