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
from datetime import datetime, timedelta
from dateutil import relativedelta
import bonsai.tool as tool
from .schedule_task_operators import restore_all_ui_state
from .operator import snapshot_all_ui_state
import bonsai.core.sequence as core
import ifcopenshell.util.sequence
import ifcopenshell.util.selector
from bpy_extras.io_utils import ImportHelper, ExportHelper
from typing import TYPE_CHECKING

# --- Import and fallback block ---
try:
    from .prop import update_filter_column
    from . import prop
except Exception:
    try:
        from ..prop.filter import update_filter_column
        from .. import prop
    except Exception:
        def update_filter_column(*args, **kwargs):
            """Fallback filter column update function"""
            return
        class PropFallback:
            @staticmethod
            def safe_set_selected_colortype_in_active_group(task_obj, value, skip_validation=False):
                try: setattr(task_obj, "selected_colortype_in_active_group", value)
                except Exception as e: pass
        prop = PropFallback()

# =====================================
# COMPLETE SNAPSHOT/RESTORE SYSTEM
# =====================================
# [WARNING] WARNING: THESE FUNCTIONS ARE DUPLICATED - USE operator.py INSTEAD
# [WARNING] All imports should point to operator.py, not this file
# [WARNING] These functions are kept only for legacy compatibility

# Global variable for task state cache (used by filters)
_persistent_task_state = {}

# def snapshot_all_ui_state(context):
#     """
#     Captures the complete state of ALL tasks in the active schedule.
#     Based on v125 which worked perfectly.
#     """
#     import json
#     try:
#         # Detect active schedule to use specific keys
#         ws_props = tool.Sequence.get_work_schedule_props()
#         ws_id = int(getattr(ws_props, "active_work_schedule_id", 0))
#         
#         tprops = getattr(context.scene, 'BIMTaskTreeProperties', None)
#         task_snap = {}
#         
#         # Get ALL tasks from the active schedule (not just visible ones)
#         try:
#             ws = tool.Sequence.get_active_work_schedule()
#             if ws:
#                 import ifcopenshell.util.sequence
#                 
#                 def get_all_tasks_recursive(tasks):
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
#                 # Map visible tasks in the UI
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
#                         
#                         # Capture color groups
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
#                         
#                         task_snap[tid] = {
#                             "active": bool(getattr(t, "use_active_colortype_group", False)),
#                             "selected_active_colortype": getattr(t, "selected_colortype_in_active_group", ""),
#                             "animation_color_schemes": getattr(t, "animation_color_schemes", ""),
#                             "groups": groups_list,
#                             # Additional data to preserve UI state
#                             "is_selected": getattr(t, 'is_selected', False),
#                             "is_expanded": getattr(t, 'is_expanded', False),
#                         }
#                     else:
#                         # If not visible, preserve data from cache or create an empty entry
#                         cache_key = "_task_colortype_snapshot_cache_json"
#                         cache_raw = context.scene.get(cache_key)
#                         if cache_raw:
#                             try:
#                                 cached_data = json.loads(cache_raw)
#                                 if tid in cached_data:
#                                     task_snap[tid] = cached_data[tid]
#                                 else:
#                                     task_snap[tid] = {
#                                         "active": False,
#                                         "selected_active_colortype": "",
#                                         "animation_color_schemes": "",
#                                         "groups": [],
#                                         "is_selected": False,
#                                         "is_expanded": False,
#                                     }
#                             except Exception:
#                                 task_snap[tid] = {
#                                     "active": False,
#                                     "selected_active_colortype": "",
#                                     "animation_color_schemes": "",
#                                     "groups": [],
#                                     "is_selected": False,
#                                     "is_expanded": False,
#                                 }
#                         else:
#                             task_snap[tid] = {
#                                 "active": False,
#                                 "selected_active_colortype": "",
#                                 "animation_color_schemes": "",
#                                 "groups": [],
#                                 "is_selected": False,
#                                 "is_expanded": False,
#                             }
#         except Exception as e:
#             print(f"Bonsai WARNING: Error capturando todas las tasks: {e}")
#             # Fallback: only visible tasks
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
#                     "is_selected": getattr(t, 'is_selected', False),
#                     "is_expanded": getattr(t, 'is_expanded', False),
#                 }
#         
#         # Save schedule-specific snapshot AND update general cache
#         snap_key_specific = f"_task_colortype_snapshot_json_WS_{ws_id}"
#         cache_key = "_task_colortype_snapshot_cache_json"
#         
#         context.scene[snap_key_specific] = json.dumps(task_snap)
#         context.scene[cache_key] = json.dumps(task_snap)  # Also update cache
#         
#         print(f"📸 Snapshot guardado: {len(task_snap)} tasks en clave {snap_key_specific}")
#         
#     except Exception as e:
#         print(f"Bonsai WARNING: snapshot_all_ui_state failed: {e}")
# 
def deferred_restore_task_state():
    """
    Runs deferred to restore state, avoiding race conditions.
    """
    global _persistent_task_state
    if not _persistent_task_state or not bpy.context:
        return

    context = bpy.context
    tprops = getattr(context.scene, 'BIMTaskTreeProperties', None)
    if not tprops or not hasattr(tprops, 'tasks'):
        return

    for task in tprops.tasks:
        task_id = str(task.ifc_definition_id)
        if task_id in _persistent_task_state:
            saved_data = _persistent_task_state[task_id]
            try:
                # Restore simple properties
                task.is_selected = saved_data.get("is_selected", False)
                task.is_expanded = saved_data.get("is_expanded", False)
                task.use_active_colortype_group = saved_data.get("use_active_colortype_group", False)

                # Restore active group
                saved_active_group = saved_data.get("active_colortype_group", "")
                if saved_active_group and hasattr(task, 'active_colortype_group'):
                    try:
                        task.active_colortype_group = saved_active_group
                    except Exception:
                        pass

                # Restore custom ColorType with maximum robustness
                saved_colortype = saved_data.get("selected_colortype_in_active_group", "")
                if saved_colortype:
                    try:
                        task.selected_colortype_in_active_group = saved_colortype
                    except Exception:
                        pass
                
                # Restore DEFAULT group value if applicable
                saved_default_value = saved_data.get("default_group_value", "")
                if saved_default_value and hasattr(task, 'active_colortype_group'):
                    try:
                        if task.active_colortype_group == "DEFAULT" or saved_active_group == "DEFAULT":
                            task.selected_colortype_in_active_group = saved_default_value
                    except Exception:
                        pass
                
                # Restore PredefinedType using Blender's property system
                predefined_type_to_restore = saved_data.get("PredefinedType")
                if predefined_type_to_restore:
                    try:
                        # Method 1: Through workspace properties
                        ws_props = tool.Sequence.get_work_schedule_props()
                        if (hasattr(ws_props, 'active_task_index') and 
                            ws_props.active_task_index < len(tprops.tasks) and 
                            tprops.tasks[ws_props.active_task_index].ifc_definition_id == task.ifc_definition_id):
                            # The task is active, we can use task_attributes
                            if hasattr(ws_props, "task_attributes"):
                                for attr in ws_props.task_attributes:
                                    if attr.name == "PredefinedType":
                                        attr.string_value = predefined_type_to_restore
                                        break
                        else:
                            # Method 2: Direct modification (less reliable but a fallback)
                            ifc_task = tool.Ifc.get().by_id(task.ifc_definition_id)
                            if ifc_task and hasattr(ifc_task, 'PredefinedType'):
                                ifc_task.PredefinedType = predefined_type_to_restore
                    except Exception as e:
                        print(f"Warning: Could not restore PredefinedType for task {task_id}: {e}")

            except (TypeError, ReferenceError):
                # We ignore Enum assignment errors that may occur if the UI
                # is not yet 100% ready, the timer minimizes this.
                pass
            except Exception as e:
                pass
                
    # Force a UI redraw to ensure changes are visible
    for area in context.screen.areas:
        if area.type == 'PROPERTIES':
            area.tag_redraw()
            
    return None # End the timer


def populate_persistent_task_state_from_snapshot(context):
    """
    Fills _persistent_task_state from the JSON snapshots in context.scene.
    This synchronizes the two memory systems.
    """
    global _persistent_task_state
    
    try:
        # Find active schedule
        ws_props = tool.Sequence.get_work_schedule_props()
        ws_id = getattr(ws_props, "active_work_schedule_id", 0)
        if not ws_id:
            return
        
        # Try to load from the schedule-specific snapshot
        snap_key = f"_task_colortype_snapshot_json_WS_{ws_id}"
        snapshot_data = context.scene.get(snap_key)
        
        if snapshot_data:
            import json
            try:
                data = json.loads(snapshot_data)
                for task_id, task_data in data.items():
                    _persistent_task_state[task_id] = {
                        "is_selected": task_data.get("is_selected", False),
                        "is_expanded": task_data.get("is_expanded", False),
                        "use_active_colortype_group": task_data.get("active", False),
                        "selected_colortype_in_active_group": task_data.get("selected_active_colortype", ""),
                    }
                print(f"📥 Sincronizado _persistent_task_state desde snapshot: {len(data)} tasks")
            except Exception as e:
                print(f"[WARNING] Error sincronizando desde snapshot: {e}")
                
    except Exception as e:
        print(f"[WARNING] Error poblando _persistent_task_state: {e}")

def restore_persistent_task_state(context):
    """Starts the state restoration in a deferred manner."""
    # First, synchronize from snapshots if necessary
    populate_persistent_task_state_from_snapshot(context)
    # Then restore with a delay for the UI
    bpy.app.timers.register(deferred_restore_task_state, first_interval=0.05)

class ClearTaskStateCache(bpy.types.Operator):
    bl_idname = "bim.clear_task_state_cache"; bl_label = "Clear Task State Cache"; bl_options = {"REGISTER", "INTERNAL"}
    work_schedule_id: bpy.props.IntProperty(default=0)  # For selective clearing
    
    def execute(self, context):
        global _persistent_task_state
        
        # If no schedule is specified, clear everything (original behavior)
        if self.work_schedule_id == 0:
            _persistent_task_state.clear()
            print("🧹 Cache completo limpiado (modo global)")
            return {'FINISHED'}
        
        # Selective clearing: only remove tasks from the specified schedule
        try:
            import ifcopenshell.util.sequence
            work_schedule = tool.Ifc.get().by_id(self.work_schedule_id)
            if not work_schedule:
                print(f"[WARNING] Cronograma {self.work_schedule_id} no encontrado para cleanup selectiva")
                return {'FINISHED'}
            
            # Get all tasks from the specified schedule
            def get_all_task_ids_recursive(tasks):
                all_ids = set()
                for task in tasks:
                    all_ids.add(str(task.id()))
                    nested = ifcopenshell.util.sequence.get_nested_tasks(task)
                    if nested:
                        all_ids.update(get_all_task_ids_recursive(nested))
                return all_ids
            
            root_tasks = ifcopenshell.util.sequence.get_root_tasks(work_schedule)
            task_ids_to_clear = get_all_task_ids_recursive(root_tasks)
            
            # Remove only the tasks of this schedule from the cache
            removed_count = 0
            for task_id in list(_persistent_task_state.keys()):
                if task_id in task_ids_to_clear:
                    del _persistent_task_state[task_id]
                    removed_count += 1
            
            print(f"🧹 Cache selectivo: {removed_count} tasks removidas del schedule '{work_schedule.Name or 'Sin nombre'}'")
            
        except Exception as e:
            print(f"[ERROR] Error en cleanup selectiva: {e}. Fallback a cleanup global.")
            _persistent_task_state.clear()
        
        return {'FINISHED'}

# =============================================================================
# ▲▲▲ END OF MEMORY SYSTEM ▲▲▲
# =============================================================================


# =============================================================================
# ▼▼▼ STATUS FILTER OPERATORS ▼▼▼
# =============================================================================
class EnableStatusFilters(bpy.types.Operator):
    bl_idname = "bim.enable_status_filters"
    bl_label = "Enable Status Filters"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        from collections import Counter
        props = tool.Sequence.get_status_props()
        props.is_enabled = True
        hidden_statuses = {s.name for s in props.statuses if not s.is_visible}

        props.statuses.clear()

        statuses_used = Counter()
        user_defined_statuses = set()
        for element in tool.Ifc.get().by_type("IfcPropertyEnumeratedValue"):
            if element.Name == "Status":
                enum_values = element.EnumerationValues
                if element.PartOfPset and isinstance(enum_values, tuple):
                    pset = element.PartOfPset[0]
                    pset_name = pset.Name
                    if pset_name.startswith("Pset_") and pset_name.endswith("Common"):
                        statuses_used.update([s.wrappedValue for s in enum_values])
                    elif pset_name == "EPset_Status":  # Our secret sauce
                        statuses_used.update([s.wrappedValue for s in enum_values])
            elif element.Name == "UserDefinedStatus":
                status = element.NominalValue.wrappedValue
                statuses_used[element.NominalValue.wrappedValue] += 1
                user_defined_statuses.add(status)

        statuses = ["No Status"]
        statuses.extend(tool.Sequence.ELEMENT_STATUSES)
        statuses.extend(user_defined_statuses)

        for status in statuses:
            new = props.statuses.add()
            new.name = status
            if new.name in hidden_statuses:
                new.is_visible = False
            new.has_elements = bool(statuses_used[status])

        visible_statuses = {s.name for s in props.statuses if s.is_visible}
        tool.Sequence.set_visibility_by_status(visible_statuses)
        return {"FINISHED"}

class DisableStatusFilters(bpy.types.Operator):
    bl_idname = "bim.disable_status_filters"; bl_label = "Disable Status Filters"; bl_description = "Deactivate status filters panel"; bl_options = {"REGISTER", "UNDO"}
    def execute(self, context):
        props = tool.Sequence.get_status_props(); all_statuses = {s.name for s in props.statuses}; tool.Sequence.set_visibility_by_status(all_statuses); props.is_enabled = False; return {"FINISHED"}

class ActivateStatusFilters(bpy.types.Operator):
    bl_idname = "bim.activate_status_filters"; bl_label = "Activate Status Filters"; bl_description = "Filter objects based on selected IFC statuses"; bl_options = {"REGISTER", "UNDO"}; only_if_enabled: bpy.props.BoolProperty(default=False)
    def execute(self, context):
        props = tool.Sequence.get_status_props()
        if not props.is_enabled and self.only_if_enabled: return {"FINISHED"}
        visible_statuses = {s.name for s in props.statuses if s.is_visible}; tool.Sequence.set_visibility_by_status(visible_statuses); return {"FINISHED"}

class SelectStatusFilter(bpy.types.Operator):
    bl_idname = "bim.select_status_filter"; bl_label = "Select Status Filter"; bl_description = "Select elements with the specified status"; bl_options = {"REGISTER", "UNDO"}
    status: bpy.props.StringProperty()

    def execute(self, context):
        import ifcopenshell.util.selector
        query = f"IfcProduct, /Pset_.*Common/.Status={self.status} + IfcProduct, EPset_Status.Status={self.status}"
        if self.status == "No Status": query = f"IfcProduct, /Pset_.*Common/.Status=NULL, EPset_Status.Status=NULL"
        for element in ifcopenshell.util.selector.filter_elements(tool.Ifc.get(), query):
            obj = tool.Ifc.get_object(element)
            if obj: obj.select_set(True)
        return {"FINISHED"}

class AssignStatus(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_status"
    bl_label = "Assign Status"
    bl_description = "Assign status to the selected elements.\n\nAlt+CLICK to unassign the status."
    bl_options = {"REGISTER", "UNDO"}

    should_override_previous_status: bpy.props.BoolProperty(
        name="Override Previous Status",
        description=(
            "Whether assigning new status should override previous one.\n\n"
            "IFC allows storing multiple statuses for the same element. "
            "This option can be disabled to take advantage of that."
        ),
        default=True,
    )
    status: bpy.props.StringProperty()
    should_unassign_status: bpy.props.BoolProperty(
        options={"SKIP_SAVE"},
    )

    def invoke(self, context, event):
        self.should_unassign_status = event.alt
        return self.execute(context)

    def _execute(self, context):
        import ifcopenshell.api.pset
        import ifcopenshell.util.element
        import bonsai.bim.schema
        from functools import cache

        # TODO: UserDefinedStatus
        if self.status not in tool.Sequence.ELEMENT_STATUSES:
            self.report({"ERROR"}, "Assigning user defined statuses or 'No Status' is not yet supported.")
            return {"CANCELLED"}

        EPSET_NAME = "EPset_Status"
        elements_changed = 0
        ifc_file = tool.Ifc.get()

        @cache
        def get_common_pset_name(element):
            templates = bonsai.bim.schema.ifc.psetqto.get_applicable(
                element.is_a(),
                pset_only=True,
                schema=tool.Ifc.get_schema(),
            )
            for template in templates:
                template_name = template.Name
                if template_name.startswith("Pset_") and template_name.endswith("Common"):
                    return template_name

        for obj in tool.Blender.get_selected_objects():
            if not (element := tool.Ifc.get_entity(obj)) or not element.is_a("IfcProduct"):
                continue

            psets = ifcopenshell.util.element.get_psets(element, psets_only=True)
            common_pset_name = get_common_pset_name(element)

            existing_psets = [
                pset_name for pset_name in psets if pset_name == EPSET_NAME or pset_name == common_pset_name
            ]
            # Common pset comes first.
            existing_psets.sort(key=lambda x: x == EPSET_NAME)

            if not existing_psets:
                if self.should_unassign_status:
                    continue
                pset_name = common_pset_name or EPSET_NAME
                pset = ifcopenshell.api.pset.add_pset(ifc_file, element, pset_name)
                ifcopenshell.api.pset.edit_pset(ifc_file, pset, properties={"Status": [self.status]})
                elements_changed += 1
                continue

            pset_changed = False
            for pset_i, pset_name in enumerate(existing_psets):
                pset_data = psets[pset_name]
                status_data = pset_data.get("Status", ...)

                if self.should_unassign_status:
                    if status_data is ... or not status_data:
                        continue
                    # Already unassigned.
                    if self.status not in status_data:
                        continue
                    status_data.remove(self.status)

                else:
                    if status_data is None or status_data is ...:
                        status_data = [self.status]
                    elif self.status in status_data:
                        # Already assigned.
                        continue
                    else:
                        if self.should_override_previous_status:
                            status_data = [self.status]
                        else:
                            status_data.append(self.status)

                if pset_i > 0:
                    # Try to maintain status in just 1 pset.
                    if not self.should_unassign_status:
                        status_data.remove(self.status)

                ifcopenshell.api.pset.edit_pset(
                    ifc_file, pset=ifc_file.by_id(pset_data["id"]), properties={"Status": status_data}
                )
                pset_changed = True
            elements_changed += pset_changed

        self.report(
            {"INFO"},
            f"Status '{self.status}' "
            f"{'un' * self.should_unassign_status}assigned {'from' if self.should_unassign_status else 'to'} "
            f"{elements_changed} elements.",
        )
        return {"FINISHED"}
# =============================================================================
# ▲▲▲ END OF STATUS FILTER OPERATORS ▲▲▲
# =============================================================================


# =============================================================================
# ▼▼▼ TASK FILTER OPERATORS ▼▼▼
# =============================================================================
class ApplyTaskFilters(bpy.types.Operator):
    bl_idname = "bim.apply_task_filters"; bl_label = "Apply Task Filters"; bl_options = {"REGISTER", "UNDO"}
    def execute(self, context):
        # FUNCTIONAL V125 SYSTEM: Snapshot → Reload → Restore
        try:
            snapshot_all_ui_state(context)
        except Exception as e:
            print(f"Bonsai WARNING: snapshot_all_ui_state failed: {e}")
        
        # Destructive task reload
        try:
            ws = tool.Sequence.get_active_work_schedule()
            if ws: 
                tool.Sequence.load_task_tree(ws)
                tool.Sequence.load_task_properties()
        except Exception as e: 
            print(f"Bonsai WARNING: Task tree reload failed: {e}")
        
        # Restore full state
        try:
            restore_all_ui_state(context)
        except Exception as e:
            print(f"Bonsai WARNING: restore_all_ui_state failed: {e}")
        
        # Variance color logic
        try:
            if not tool.Sequence.has_variance_calculation_in_tasks(): 
                tool.Sequence.clear_variance_colors_only()
        except Exception as e: 
            print(f"[WARNING] Error in variance color check: {e}")
        
        return {'FINISHED'}

class AddTaskFilter(bpy.types.Operator):
    bl_idname = "bim.add_task_filter"; bl_label = "Add Task Filter"; bl_options = {"REGISTER", "UNDO"}
    def execute(self, context):
        props = tool.Sequence.get_work_schedule_props(); new_rule = props.filters.rules.add(); new_rule.column = "IfcTask.Name||string"; update_filter_column(new_rule, context); props.filters.active_rule_index = len(props.filters.rules) - 1; return {'FINISHED'}

class RemoveTaskFilter(bpy.types.Operator):
    bl_idname = "bim.remove_task_filter"; bl_label = "Remove Task Filter"; bl_options = {"REGISTER", "UNDO"}
    def execute(self, context):
        props = tool.Sequence.get_work_schedule_props(); index = props.filters.active_rule_index
        if 0 <= index < len(props.filters.rules):
            props.filters.rules.remove(index); props.filters.active_rule_index = min(max(0, index - 1), len(props.filters.rules) - 1)
            if len(props.filters.rules) == 0: props.last_lookahead_window = ""
            bpy.ops.bim.apply_task_filters()
        return {'FINISHED'}

class ClearAllTaskFilters(bpy.types.Operator):
    bl_idname = "bim.clear_all_task_filters"; bl_label = "Clear All Filters"; bl_options = {"REGISTER", "UNDO"}
    def execute(self, context):
        props = tool.Sequence.get_work_schedule_props(); props.filters.rules.clear(); props.filters.active_rule_index = 0; props.last_lookahead_window = ""; bpy.ops.bim.apply_task_filters(); self.report({'INFO'}, "All filters cleared"); return {'FINISHED'}

class ApplyLookaheadFilter(bpy.types.Operator):
    bl_idname = "bim.apply_lookahead_filter"; bl_label = "Apply Lookahead Filter"; bl_description = "Week Look Ahead - Filter tasks by time window"; bl_options = {"REGISTER", "UNDO"}
    time_window: bpy.props.EnumProperty(name="Time Window", items=[('THIS_WEEK', "This Week", ""), ('LAST_WEEK', "Last Week", ""), ("1_WEEK", "Next 1 Week", ""), ("2_WEEKS", "Next 2 Weeks", ""), ("4_WEEKS", "Next 4 Weeks", ""), ("6_WEEKS", "Next 6 Weeks", ""), ("12_WEEKS", "Next 12 Weeks", "")])
    def execute(self, context):
        active_schedule = tool.Sequence.get_active_work_schedule()
        if not active_schedule: self.report({'ERROR'}, "No active work schedule."); return {'CANCELLED'}
        if not ifcopenshell.util.sequence.get_root_tasks(active_schedule): self.report({'WARNING'}, "The active schedule has no tasks."); return {'CANCELLED'}
        props = tool.Sequence.get_work_schedule_props(); props.last_lookahead_window = self.time_window; props.filters.rules.clear(); date_source = getattr(props, "date_source_type", "SCHEDULE"); date_prefix = date_source.capitalize(); start_column = f"IfcTaskTime.{date_prefix}Start||date"; finish_column = f"IfcTaskTime.{date_prefix}Finish||date"; today = datetime.now()
        if self.time_window == 'THIS_WEEK': filter_start = today - timedelta(days=today.weekday()); filter_end = filter_start + timedelta(days=6)
        elif self.time_window == 'LAST_WEEK': filter_start = today - timedelta(days=today.weekday(), weeks=1); filter_end = filter_start + timedelta(days=6)
        else: weeks = int(self.time_window.split('_')[0]); filter_start = today; filter_end = today + timedelta(weeks=weeks)
        rule1 = props.filters.rules.add(); rule1.is_active = True; rule1.column = start_column; rule1.operator = "LTE"; rule1.value_string = filter_end.strftime("%Y-%m-%d")
        rule2 = props.filters.rules.add(); rule2.is_active = True; rule2.column = finish_column; rule2.operator = "GTE"; rule2.value_string = filter_start.strftime("%Y-%m-%d")
        props.filters.logic = "AND"; tool.Sequence.update_visualisation_date(filter_start, filter_end); bpy.ops.bim.apply_task_filters(); self.report({"INFO"}, f"Filter applied: {self.time_window.replace('_', ' ')}"); return {"FINISHED"}

# =============================================================================
# ▼▼▼ FILTER SET OPERATORS ▼▼▼
# =============================================================================
class UpdateSavedFilterSet(bpy.types.Operator):
    bl_idname = "bim.update_saved_filter_set"; bl_label = "Update Saved Filter Set"; bl_options = {"REGISTER", "UNDO"}; set_index: bpy.props.IntProperty()
    def execute(self, context):
        props = tool.Sequence.get_work_schedule_props(); saved_set = props.saved_filter_sets[self.set_index]; saved_set.rules.clear()
        for active_rule in props.filters.rules:
            saved_rule = saved_set.rules.add(); saved_rule.is_active = active_rule.is_active; saved_rule.column = active_rule.column; saved_rule.operator = active_rule.operator; saved_rule.value_string = active_rule.value_string; saved_rule.data_type = active_rule.data_type
        self.report({'INFO'}, f"Filter '{saved_set.name}' updated."); return {'FINISHED'}

class SaveFilterSet(bpy.types.Operator):
    bl_idname = "bim.save_filter_set"; bl_label = "Save Filter Set"; bl_options = {"REGISTER", "UNDO"}; set_name: bpy.props.StringProperty(name="Name", description="Name for this filter set")
    def execute(self, context):
        if not self.set_name.strip(): self.report({'ERROR'}, "Name cannot be empty."); return {'CANCELLED'}
        props = tool.Sequence.get_work_schedule_props(); new_set = props.saved_filter_sets.add(); new_set.name = self.set_name
        for active_rule in props.filters.rules:
            saved_rule = new_set.rules.add(); saved_rule.is_active = active_rule.is_active; saved_rule.column = active_rule.column; saved_rule.operator = active_rule.operator; saved_rule.value_string = active_rule.value_string; saved_rule.data_type = active_rule.data_type
        self.report({'INFO'}, f"Filter '{self.set_name}' saved."); return {'FINISHED'}
    def invoke(self, context, event): return context.window_manager.invoke_props_dialog(self)

class LoadFilterSet(bpy.types.Operator):
    bl_idname = "bim.load_filter_set"; bl_label = "Load Filter Set"; bl_options = {"REGISTER", "UNDO"}; set_index: bpy.props.IntProperty()
    def execute(self, context):
        props = tool.Sequence.get_work_schedule_props()
        if not (0 <= self.set_index < len(props.saved_filter_sets)): self.report({'ERROR'}, "Invalid filter index."); return {'CANCELLED'}
        saved_set = props.saved_filter_sets[self.set_index]; props.filters.rules.clear()
        for saved_rule in saved_set.rules:
            active_rule = props.filters.rules.add(); active_rule.is_active = saved_rule.is_active; active_rule.column = saved_rule.column; active_rule.operator = saved_rule.operator; active_rule.value_string = saved_rule.value_string; active_rule.data_type = saved_rule.data_type
        bpy.ops.bim.apply_task_filters(); return {'FINISHED'}

class RemoveFilterSet(bpy.types.Operator):
    bl_idname = "bim.remove_filter_set"; bl_label = "Remove Filter Set"; bl_options = {"REGISTER", "UNDO"}; set_index: bpy.props.IntProperty()
    def execute(self, context):
        props = tool.Sequence.get_work_schedule_props()
        if not (0 <= self.set_index < len(props.saved_filter_sets)): self.report({'ERROR'}, "Invalid filter index."); return {'CANCELLED'}
        set_name = props.saved_filter_sets[self.set_index].name; props.saved_filter_sets.remove(self.set_index); props.active_saved_filter_set_index = min(max(0, self.set_index - 1), len(props.saved_filter_sets) - 1); self.report({'INFO'}, f"Filter '{set_name}' removed."); return {'FINISHED'}

class ExportFilterSet(bpy.types.Operator, ExportHelper):
    bl_idname = "bim.export_filter_set"; bl_label = "Export Filter Library"; bl_description = "Export all saved filters to a JSON file"; filename_ext = ".json"; filter_glob: bpy.props.StringProperty(default="*.json", options={"HIDDEN"})
    def execute(self, context):
        props = tool.Sequence.get_work_schedule_props(); library_data = {}
        for saved_set in props.saved_filter_sets:
            rules_data = []
            for rule in saved_set.rules: rules_data.append({"is_active": rule.is_active, "column": rule.column, "operator": rule.operator, "value": rule.value})
            library_data[saved_set.name] = {"rules": rules_data}
        with open(self.filepath, 'w', encoding='utf-8') as f: json.dump(library_data, f, ensure_ascii=False, indent=4)
        self.report({'INFO'}, f"Filter library exported to {self.filepath}"); return {'FINISHED'}

class ImportFilterSet(bpy.types.Operator, ImportHelper):
    bl_idname = "bim.import_filter_set"; bl_label = "Import Filter Library"; bl_description = "Import filters from a JSON file"; filename_ext = ".json"; filter_glob: bpy.props.StringProperty(default="*.json", options={"HIDDEN"})
    def execute(self, context):
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f: library_data = json.load(f)
        except Exception as e: self.report({'ERROR'}, f"Could not read JSON file: {e}"); return {'CANCELLED'}
        props = tool.Sequence.get_work_schedule_props(); existing_names = {fs.name for fs in props.saved_filter_sets}; imported_count = 0
        for set_name, set_data in library_data.items():
            if set_name in existing_names: continue
            new_set = props.saved_filter_sets.add(); new_set.name = set_name
            for rule_data in set_data.get("rules", []):
                new_rule = new_set.rules.add(); new_rule.is_active = rule_data.get("is_active", True); new_rule.column = rule_data.get("column", ""); new_rule.operator = rule_data.get("operator", "CONTAINS"); new_rule.value = rule_data.get("value", "")
            imported_count += 1
        self.report({'INFO'}, f"{imported_count} new filter sets imported."); return {'FINISHED'}

# =============================================================================
# ▼▼▼ DATE PICKER OPERATORS ▼▼▼
# =============================================================================
class Bonsai_DatePicker(bpy.types.Operator):
    bl_label = "Date Picker"; bl_idname = "bim.datepicker"; bl_options = {"REGISTER", "UNDO"}; target_prop: bpy.props.StringProperty(name="Target date prop to set"); include_time: bpy.props.BoolProperty(name="Include Time", default=True)
    def execute(self, context):
        selected_date = context.scene.DatePickerProperties.selected_date
        try: tool.Sequence.parse_isodate_datetime(selected_date, self.include_time); self.set_scene_prop(self.target_prop, selected_date); return {"FINISHED"}
        except Exception as e: self.report({"ERROR"}, f"Invalid date: '{selected_date}'. Error: {str(e)}."); return {"CANCELLED"}
    def draw(self, context):
        props = context.scene.DatePickerProperties; display_date = tool.Sequence.parse_isodate_datetime(props.display_date, False); current_month = (display_date.year, display_date.month); lines = calendar.monthcalendar(*current_month); month_title, week_titles = calendar.month(*current_month).splitlines()[:2]; layout = self.layout; row = layout.row(); row.prop(props, "selected_date", text="Date")
        if self.include_time: row = layout.row(); row.label(text="Time:"); row.prop(props, "selected_hour", text="H"); row.prop(props, "selected_min", text="M"); row.prop(props, "selected_sec", text="S")
        month_delta = relativedelta.relativedelta(months=1); split = layout.split(); col = split.row(); op = col.operator("wm.context_set_string", icon="TRIA_LEFT", text=""); op.data_path = "scene.DatePickerProperties.display_date"; op.value = tool.Sequence.isodate_datetime(display_date - month_delta, False)
        col = split.row(); col.label(text=month_title.strip()); col = split.row(); col.alignment = "RIGHT"; op = col.operator("wm.context_set_string", icon="TRIA_RIGHT", text=""); op.data_path = "scene.DatePickerProperties.display_date"; op.value = tool.Sequence.isodate_datetime(display_date + month_delta, False)
        row = layout.row(align=True)
        for title in week_titles.split(): col = row.column(align=True); col.alignment = "CENTER"; col.label(text=title.strip())
        current_selected_date = tool.Sequence.parse_isodate_datetime(props.selected_date, self.include_time); current_selected_date = current_selected_date.replace(hour=0, minute=0, second=0)
        for line in lines:
            row = layout.row(align=True)
            for i in line:
                col = row.column(align=True)
                if i == 0: col.label(text="  ")
                else:
                    selected_date = datetime(year=display_date.year, month=display_date.month, day=i); is_current_date = current_selected_date == selected_date; op = col.operator("wm.context_set_string", text="{:2d}".format(i), depress=is_current_date)
                    if self.include_time: selected_date = selected_date.replace(hour=props.selected_hour, minute=props.selected_min, second=props.selected_sec)
                    op.data_path = "scene.DatePickerProperties.selected_date"; op.value = tool.Sequence.isodate_datetime(selected_date, self.include_time)
    def invoke(self, context, event):
        props = context.scene.DatePickerProperties; current_date_str = self.get_scene_prop(self.target_prop); current_date = None
        if current_date_str: 
            try: current_date = tool.Sequence.parse_isodate_datetime(current_date_str, self.include_time)
            except: pass
        if current_date is None: current_date = datetime.now(); current_date = current_date.replace(second=0)
        if self.include_time: props["selected_hour"] = current_date.hour; props["selected_min"] = current_date.minute; props["selected_sec"] = current_date.second
        props.display_date = tool.Sequence.isodate_datetime(current_date.replace(day=1), False); props.selected_date = tool.Sequence.isodate_datetime(current_date, self.include_time); return context.window_manager.invoke_props_dialog(self)
    def get_scene_prop(self, prop_path: str) -> str: return bpy.context.scene.path_resolve(prop_path)
    def set_scene_prop(self, prop_path: str, value: str) -> None: tool.Blender.set_prop_from_path(bpy.context.scene, prop_path, value)

class FilterDatePicker(bpy.types.Operator):
    bl_idname = "bim.filter_datepicker"; bl_label = "Select Filter Date"; bl_options = {"REGISTER", "UNDO"}; rule_index: bpy.props.IntProperty(default=-1)
    def execute(self, context):
        props = tool.Sequence.get_work_schedule_props()
        if self.rule_index < 0 or self.rule_index >= len(props.filters.rules): self.report({'ERROR'}, "Invalid filter rule index."); return {'CANCELLED'}
        selected_date_str = context.scene.DatePickerProperties.selected_date
        if not selected_date_str: self.report({'ERROR'}, "No date selected."); return {'CANCELLED'}
        target_rule = props.filters.rules[self.rule_index]; target_rule.value_string = selected_date_str
        try: bpy.ops.bim.apply_task_filters()
        except Exception as e: print(f"Error applying filters: {e}")
        self.report({'INFO'}, f"Date set to: {selected_date_str}"); return {"FINISHED"}
    def invoke(self, context, event):
        if self.rule_index < 0: self.report({'ERROR'}, "No rule index specified."); return {'CANCELLED'}
        props = tool.Sequence.get_work_schedule_props()
        if self.rule_index >= len(props.filters.rules): self.report({'ERROR'}, "Invalid filter rule index."); return {'CANCELLED'}
        current_date_str = props.filters.rules[self.rule_index].value_string; date_picker_props = context.scene.DatePickerProperties
        if current_date_str and current_date_str.strip():
            try: current_date = datetime.fromisoformat(current_date_str.split('T')[0])
            except Exception:
                try: from dateutil import parser as date_parser; current_date = date_parser.parse(current_date_str)
                except Exception: current_date = datetime.now()
        else: current_date = datetime.now()
        date_picker_props.selected_date = current_date.strftime("%Y-%m-%d"); date_picker_props.display_date = current_date.replace(day=1).strftime("%Y-%m-%d"); return context.window_manager.invoke_props_dialog(self, width=350)
    def draw(self, context):
        layout = self.layout; props = context.scene.DatePickerProperties
        try: display_date = datetime.fromisoformat(props.display_date)
        except Exception: display_date = datetime.now(); props.display_date = display_date.strftime("%Y-%m-%d")
        row = layout.row(); row.prop(props, "selected_date", text="Date"); current_month = (display_date.year, display_date.month); lines = calendar.monthcalendar(*current_month); month_title = calendar.month_name[display_date.month] + f" {display_date.year}"; row = layout.row(align=True)
        prev_month = display_date - relativedelta.relativedelta(months=1); op = row.operator("wm.context_set_string", icon="TRIA_LEFT", text=""); op.data_path = "scene.DatePickerProperties.display_date"; op.value = prev_month.strftime("%Y-%m-%d")
        row.label(text=month_title)
        next_month = display_date + relativedelta.relativedelta(months=1); op = row.operator("wm.context_set_string", icon="TRIA_RIGHT", text=""); op.data_path = "scene.DatePickerProperties.display_date"; op.value = next_month.strftime("%Y-%m-%d")
        row = layout.row(align=True)
        for day_name in ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']: col = row.column(align=True); col.alignment = "CENTER"; col.label(text=day_name)
        try: selected_date = datetime.fromisoformat(props.selected_date)
        except Exception: selected_date = None
        for week in lines:
            row = layout.row(align=True)
            for day in week:
                col = row.column(align=True)
                if day == 0: col.label(text="")
                else:
                    day_date = datetime(display_date.year, display_date.month, day); day_str = day_date.strftime("%Y-%m-%d"); is_selected = (selected_date and day_date.date() == selected_date.date()); op = col.operator("wm.context_set_string", text=str(day), depress=is_selected); op.data_path = "scene.DatePickerProperties.selected_date"; op.value = day_str