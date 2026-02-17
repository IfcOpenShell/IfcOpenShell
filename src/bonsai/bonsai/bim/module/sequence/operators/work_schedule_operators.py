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
import time
import bonsai.tool as tool
import bonsai.core.sequence as core


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
        class PropFallback: # pyright: ignore[reportUnusedClass]
            @staticmethod
            def safe_set_selected_colortype_in_active_group(task_obj, value, skip_validation=False):
                try:
                    setattr(task_obj, "selected_colortype_in_active_group", value)
                except Exception as e:
                    print(f"[ERROR] Fallback safe_set failed: {e}")
        prop = PropFallback()

# Import helper functions from other modules
from .animation_operators import _clear_previous_animation, _get_animation_settings, _compute_product_frames, _ensure_default_group
from .operator import snapshot_all_ui_state
from .schedule_task_operators import restore_all_ui_state

try:
    from bonsai.bim.module.sequence.prop import UnifiedColorTypeManager
except Exception:
    UnifiedColorTypeManager = None  # optional

try:
    from ..prop import TaskcolortypeGroupChoice
except Exception:
    TaskcolortypeGroupChoice = None  # optional


def _ensure_local_text_settings_on_obj(_obj, _settings):
    """Attach or refresh minimal settings on text data so the handler maps frame→date correctly."""
    try:
        data = getattr(_obj, 'data', None)
        if not data:
            return
        aset = dict(data.get('animation_settings', {}))
        def _get(k, default=None):
            if isinstance(_settings, dict):
                return _settings.get(k, default)
            return getattr(_settings, k, default)

        scene = bpy.context.scene
        new_vals = {
            'start_frame': int(_get('start_frame', getattr(scene, 'frame_start', 1) or 1)),
            'total_frames': int(_get('total_frames', max(1, int(getattr(scene, 'frame_end', 250)) - int(getattr(scene, 'frame_start', 1))))),
            'start_date': _get('start', None),
            'finish_date': _get('finish', None),
            'schedule_start': _get('schedule_start', None),
            'schedule_finish': _get('schedule_finish', None),
            'schedule_name': _get('schedule_name', None),
        }
        changed = False
        for k, v in new_vals.items():
            if aset.get(k) != v and v is not None:
                aset[k] = v
                changed = True
        if changed:
            data['animation_settings'] = aset

        # Ensure text_type is defined for the handler
        if not data.get('text_type'):
            n = (getattr(_obj, 'name', '') or '').lower()
            if 'schedule_name' in n:
                data['text_type'] = 'schedule_name'
            elif 'date' in n:
                data['text_type'] = 'date'
            elif 'week' in n:
                data['text_type'] = 'week'
            elif 'day' in n:
                data['text_type'] = 'day_counter'
            elif 'progress' in n:
                data['text_type'] = 'progress'
    except Exception:
        pass


# ============================================================================
# WORK SCHEDULE OPERATORS
# ============================================================================

class AssignWorkSchedule(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_work_schedule"
    bl_label = "Assign Work Schedule"
    bl_options = {"REGISTER", "UNDO"}
    work_plan: bpy.props.IntProperty()
    work_schedule: bpy.props.IntProperty()

    def _execute(self, context):
        core.assign_work_schedule(
            tool.Ifc,
            work_plan=tool.Ifc.get().by_id(self.work_plan),
            work_schedule=tool.Ifc.get().by_id(self.work_schedule),
        )


class UnassignWorkSchedule(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unassign_work_schedule"
    bl_label = "Unassign Work Schedule"
    bl_options = {"REGISTER", "UNDO"}
    work_plan: bpy.props.IntProperty()
    work_schedule: bpy.props.IntProperty()

    def _execute(self, context):
        core.unassign_work_schedule(
            tool.Ifc,
            work_schedule=tool.Ifc.get().by_id(self.work_schedule),
        )


class AddWorkSchedule(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_work_schedule"
    bl_label = "Add Work Schedule"
    bl_options = {"REGISTER", "UNDO"}
    name: bpy.props.StringProperty()

    def _execute(self, context):
        core.add_work_schedule(tool.Ifc, tool.Sequence, name=self.name)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "name", text="Name")
        self.props = tool.Sequence.get_work_schedule_props()
        layout.prop(self.props, "work_schedule_predefined_types", text="Type")
        if self.props.work_schedule_predefined_types == "USERDEFINED":
            layout.prop(self.props, "object_type", text="Object type")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class EditWorkSchedule(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_work_schedule"
    bl_label = "Edit Work Schedule"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = tool.Sequence.get_work_schedule_props()
        work_schedule_id = props.active_work_schedule_id
        work_schedule = tool.Ifc.get().by_id(work_schedule_id)
        
        # 1. Save the profile configuration to the IFC before saving the schedule attributes.
        #    This ensures that changes to task profiles are not lost.
        try:
            import bonsai.core.sequence as core
            anim_props = tool.Sequence.get_animation_props()
            
            # Use the helper to capture the current state of the task UI
            snapshot_all_ui_state(context)
            # Use a schedule-specific key
            snap_key_specific = f"_task_colortype_snapshot_json_WS_{work_schedule_id}"
            task_snap = json.loads(context.scene.get(snap_key_specific, "{}"))

            colortype_data_to_save = {
                "colortype_sets": {},  # Moved to config_operators.py
                "task_configurations": task_snap,
                "animation_settings": {
                    "active_editor_group": getattr(anim_props, "ColorType_groups", "DEFAULT"),
                    "active_task_group": getattr(anim_props, "task_colortype_group_selector", ""),
                    "group_stack": [{"group": item.group, "enabled": item.enabled} for item in anim_props.animation_group_stack],
                }
            }
            core.save_colortypes_to_ifc_core(tool.Ifc.get(), work_schedule, colortype_data_to_save)
            print(f"Bonsai INFO: colortype data for schedule '{work_schedule.Name}' saved to IFC.")
        except Exception as e:
            print(f"Bonsai WARNING: Failed to auto-save colortype data during schedule edit: {e}")
     

        # Execute the standard edit operation
        core.edit_work_schedule(
            tool.Ifc,
            tool.Sequence,
            work_schedule=work_schedule,
        )

        # Exit edit mode normally so the UI updates correctly.
        tool.Sequence.disable_editing_work_schedule()


class RemoveWorkSchedule(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_work_schedule"
    bl_label = "Remove Work Schedule"
    back_reference = "Remove provided work schedule."
    bl_options = {"REGISTER", "UNDO"}
    work_schedule: bpy.props.IntProperty()

    def _execute(self, context):
        import ifcopenshell.util.sequence
        
        schedule_to_remove_id = self.work_schedule
        schedule_to_remove = tool.Ifc.get().by_id(schedule_to_remove_id)
        
        print(f"[INFO] Deleting schedule ID {schedule_to_remove_id} - '{schedule_to_remove.Name}'")
        
        # BEFORE deleting: Inspect the state
        ifc_file = tool.Ifc.get()
        all_schedules_before = ifc_file.by_type("IfcWorkSchedule")
        
        print(f"[INFO] BEFORE - Total schedules: {len(all_schedules_before)}")
        for ws in all_schedules_before:
            tasks = ifcopenshell.util.sequence.get_root_tasks(ws)
            print(f"  [INFO] '{ws.Name}' (ID:{ws.id()}) - {len(tasks)} root tasks")
            for i, task in enumerate(tasks[:3]):  # Only first 3 tasks
                print(f"    [INFO] Task {i+1}: '{task.Name}' (ID:{task.id()})")
        
        # Current active schedule
        ws_props = tool.Sequence.get_work_schedule_props()
        current_active = ws_props.active_work_schedule_id
        print(f"[INFO] Current active schedule: {current_active}")
        
        # Delete the schedule (original operation)
        core.remove_work_schedule(tool.Ifc, work_schedule=schedule_to_remove)
        
        # AFTER deleting: Inspect the state
        all_schedules_after = ifc_file.by_type("IfcWorkSchedule")
        
        print(f"[INFO] AFTER - Total schedules: {len(all_schedules_after)}")
        for ws in all_schedules_after:
            try:
                tasks = ifcopenshell.util.sequence.get_root_tasks(ws)
                print(f"  [INFO] '{ws.Name}' (ID:{ws.id()}) - {len(tasks)} root tasks")
                for i, task in enumerate(tasks[:3]):  # Only first 3 tasks
                    print(f"    [INFO] Task {i+1}: '{task.Name}' (ID:{task.id()})")
            except Exception as e:
                print(f"  [ERROR] Error inspecting '{ws.Name}': {e}")
        
        # Check active schedule after deletion
        current_active_after = ws_props.active_work_schedule_id
        print(f"🎯 Active schedule after: {current_active_after}")
        
        print(f"[INFO] Schedule deleted: ID {schedule_to_remove_id}")


class CopyWorkSchedule(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.copy_work_schedule"
    bl_label = "Copy Work Schedule"
    bl_description = "Create a duplicate of the provided work schedule."
    bl_options = {"REGISTER", "UNDO"}
    work_schedule: bpy.props.IntProperty()  # pyright: ignore[reportRedeclaration]

    def _execute(self, context):
        import ifcopenshell.util.sequence
        
        # Take a snapshot BEFORE capturing to ensure everything is saved
        print(f"[INFO] Forcing full snapshot before duplicating...")
        from .operator import snapshot_all_ui_state
        snapshot_all_ui_state(context)
        
        # 1. Capture ColorType configuration from the source schedule AFTER the snapshot
        source_schedule = tool.Ifc.get().by_id(self.work_schedule)
        source_colortype_config = self._capture_schedule_colortype_config(context, source_schedule)
        
        print(f"[INFO] Duplicating schedule '{source_schedule.Name}' (ID:{source_schedule.id()})")
        
        # BEFORE duplicating: Inspect the state
        ifc_file = tool.Ifc.get()
        all_schedules_before = ifc_file.by_type("IfcWorkSchedule")
        source_tasks = ifcopenshell.util.sequence.get_root_tasks(source_schedule)
        
        print(f"[INFO] BEFORE - Total schedules: {len(all_schedules_before)}")
        print(f"[INFO] Source schedule has {len(source_tasks)} root tasks:")
        for i, task in enumerate(source_tasks[:3]):  # Only first 3 tasks
            print(f"  [INFO] Task {i+1}: '{task.Name}' (ID:{task.id()})")
        
        # 2. Execute the copy logic that now creates a duplicate in the IFC.
        core.copy_work_schedule(tool.Sequence, work_schedule=source_schedule)
        
        # AFTER duplicating: Inspect the state
        all_schedules_after = ifc_file.by_type("IfcWorkSchedule")
        
        print(f"[INFO] AFTER - Total schedules: {len(all_schedules_after)}")
        
        # Find the newly duplicated schedule
        new_schedules = [ws for ws in all_schedules_after if ws.id() not in [s.id() for s in all_schedules_before]]
        
        if new_schedules:
            duplicate_schedule = new_schedules[0]
            duplicate_tasks = ifcopenshell.util.sequence.get_root_tasks(duplicate_schedule)
            print(f"🆕 Duplicated schedule: '{duplicate_schedule.Name}' (ID:{duplicate_schedule.id()})")
            print(f"📝 Duplicated schedule has {len(duplicate_tasks)} root tasks:")
            for i, task in enumerate(duplicate_tasks[:3]):  # Only first 3 tasks
                print(f"  [INFO] Task {i+1}: '{task.Name}' (ID:{task.id()})")
        else:
            print("[ERROR] No duplicated schedule found!")
        
        # Verify if the tasks have different IDs
        if new_schedules and source_tasks:
            duplicate_tasks = ifcopenshell.util.sequence.get_root_tasks(new_schedules[0])
            if duplicate_tasks:
                print(f"🔍 ID VERIFICATION:")
                print(f"  Original task 1 ID: {source_tasks[0].id()}")
                print(f"  Duplicated task 1 ID: {duplicate_tasks[0].id()}")
                if source_tasks[0].id() == duplicate_tasks[0].id():
                    print("🚨 PROBLEM!!! Tasks share the same ID!")
                else:
                    print("✅ Tasks have different IDs as expected")

        # 3. Apply ColorType configuration to the duplicated schedule
        if source_colortype_config:
            # Get the mapping from original to duplicated tasks
            task_mapping = getattr(tool.Sequence, 'last_duplication_mapping', {})
            self._apply_colortype_config_to_duplicate(context, source_colortype_config, task_mapping)

        # 4. Force data reload and UI redraw.
        try:
            from bonsai.bim.module.sequence.data import SequenceData, WorkScheduleData
            SequenceData.load()
            WorkScheduleData.load()
            for area in context.screen.areas:
                if area.type in ['PROPERTIES', 'OUTLINER']:
                    area.tag_redraw()
        except Exception as e:
            print(f"Bonsai WARNING: UI refresh failed after copying schedule: {e}")
    
    def _capture_schedule_colortype_config(self, context, source_schedule):
        """
        Captures DIRECTLY from the UI the entire ColorType configuration of the source schedule.
        """
        try:
            import json
            import ifcopenshell.util.sequence
            
            config = {}
            
            # EXHAUSTIVE DIAGNOSTIC: Capture DIRECTLY from UI properties
            print(f"🔍🔍🔍 === STARTING EXHAUSTIVE DIRECT CAPTURE ===")
            print(f"📋 Source schedule: {source_schedule.Name} (ID: {source_schedule.id()})")
            
            # Get all tasks from the source schedule
            def get_all_tasks_recursive(tasks):
                all_tasks_list = []
                for task in tasks:
                    all_tasks_list.append(task)
                    nested_tasks = ifcopenshell.util.sequence.get_nested_tasks(task)
                    if nested_tasks:
                        all_tasks_list.extend(get_all_tasks_recursive(nested_tasks))
                return all_tasks_list
            
            root_tasks = ifcopenshell.util.sequence.get_root_tasks(source_schedule)
            all_tasks = get_all_tasks_recursive(root_tasks)
            print(f"📊 Total tasks in schedule: {len(all_tasks)}")
            
            # Get UI properties
            try:
                tprops = tool.Sequence.get_task_tree_props()
                if not tprops:
                    print(f"[ERROR] Could not get task_tree_props")
                    return {}
                
                
                # Examine the complete structure of tprops
                print(f"🔎 Structure of tprops:")
                for attr_name in dir(tprops):
                    if not attr_name.startswith('_'):
                        attr_value = getattr(tprops, attr_name, None)
                        if hasattr(attr_value, '__len__') and not isinstance(attr_value, str):
                            try: # pyright: ignore[reportUnusedTry]
                                print(f"  {attr_name}: type {type(attr_value).__name__}, length {len(attr_value)}")
                            except:
                                print(f"  {attr_name}: type {type(attr_value).__name__}")
                        else:
                            print(f"  {attr_name}: {type(attr_value).__name__} = {attr_value}")
                
                # Create a mapping from IDs to UI elements
                tasks_prop = getattr(tprops, "tasks", [])
                print(f"📋 tprops.tasks length: {len(tasks_prop)}")
                
                task_id_to_ui = {} # pyright: ignore[reportUnusedVariable]
                for i, t in enumerate(tasks_prop):
                    task_id = str(getattr(t, "ifc_definition_id", 0))
                    task_id_to_ui[task_id] = t
                    print(f"  UI Task {i}: ID={task_id}, Name='{getattr(t, 'name', 'NO_NAME')}'")
                    
                    # Examine ColorType properties of this UI task
                    colortype_attrs = []
                    for attr_name in dir(t):
                        if 'color' in attr_name.lower() and not attr_name.startswith('_'):
                            attr_value = getattr(t, attr_name, None)
                            colortype_attrs.append(f"{attr_name}={attr_value}")
                    if colortype_attrs:
                        print(f"    ColorType attrs: {', '.join(colortype_attrs)}")
                    
                    # Examine colortype_group_choices specifically
                    colortype_group_choices = getattr(t, "colortype_group_choices", [])
                    print(f"    colortype_group_choices: {len(colortype_group_choices)} groups")
                    for j, group in enumerate(colortype_group_choices):
                        print(f"      Group {j}:")
                        for attr_name in dir(group): # pyright: ignore[reportUnboundVariable]
                            if not attr_name.startswith('_'):
                                attr_value = getattr(group, attr_name, None)
                                print(f"        {attr_name}: {attr_value}")
                
                print(f"📋 UI has {len(task_id_to_ui)} tasks loaded, IDs: {list(task_id_to_ui.keys())}")
                
                # Capture configuration for each task
                for task in all_tasks:
                    task_id = str(task.id()) # pyright: ignore[reportUnusedVariable]
                    task_name = getattr(task, 'Name', 'NO_NAME')
                    print(f"\n🎯 Processing IFC task: {task_id} '{task_name}'")
                    
                    if task_id == "0":
                        print(f"    ⏭️ Skipping task ID=0")
                        continue
                        
                    # Find the task in the UI
                    if task_id in task_id_to_ui:
                        ui_task = task_id_to_ui[task_id]
                        
                        # Capture color groups DIRECTLY
                        groups_list = []
                        colortype_group_choices = getattr(ui_task, "colortype_group_choices", [])
                        print(f"    📊 colortype_group_choices: {len(colortype_group_choices)} groups")
                        
                        for idx, group in enumerate(colortype_group_choices):
                            group_name = getattr(group, "group_name", "")
                            print(f"      Group {idx}: name='{group_name}'")
                            
                            if group_name:
                                # Detect the correct attribute for the selected value
                                selected_value = ""
                                selected_attr = ""
                                
                                for attr in ["selected_colortype", "selected", "active_colortype", "colortype"]:
                                    if hasattr(group, attr):
                                        val = getattr(group, attr, "")
                                        print(f"        {attr}: '{val}'")
                                        if val and not selected_value:
                                            selected_value = val
                                            selected_attr = attr
                                
                                enabled = bool(getattr(group, "enabled", False))
                                print(f"        enabled: {enabled}")
                                print(f"        selected_value: '{selected_value}' (from {selected_attr})")
                                
                                groups_list.append({
                                    "group_name": group_name,
                                    "enabled": enabled,
                                    "selected_value": selected_value,
                                    "selected_attr": selected_attr,
                                })
                        
                        # Capture checkbox state and active selector
                        use_active = bool(getattr(ui_task, "use_active_colortype_group", False))
                        selected_active = getattr(ui_task, "selected_colortype_in_active_group", "")
                        animation_schemes = getattr(ui_task, "animation_color_schemes", "")
                        
                        print(f"    📋 use_active_colortype_group: {use_active}")
                        print(f"    📋 selected_colortype_in_active_group: '{selected_active}'")
                        print(f"    📋 animation_color_schemes: '{animation_schemes}'")
                        
                        config[task_id] = {
                            "active": use_active,
                            "selected_active_colortype": selected_active,
                            "animation_color_schemes": animation_schemes,
                            "groups": groups_list,
                            "is_selected": getattr(ui_task, 'is_selected', False),
                            "is_expanded": getattr(ui_task, 'is_expanded', False),
                        }
                        
                        
                    else:
                        print(f"    [ERROR] Task {task_id} '{task_name}' NOT found in UI")
                        print(f"       Available IDs in UI: {list(task_id_to_ui.keys())}")
                
                print(f"\n🎨 === DIRECT CAPTURE SUMMARY ===")
                print(f"🎨 Total configurations captured: {len(config)} tasks")
                
                for task_id, task_config in config.items():
                    print(f"🔍 TASK {task_id} final configuration:")
                    groups = task_config.get("groups", [])
                    print(f"    groups: {len(groups)} items") # pyright: ignore[reportUnusedVariable]
                    for g in groups:
                        print(f"      - '{g.get('group_name', 'no name')}': enabled={g.get('enabled')}, value='{g.get('selected_value', '')}'")
                    print(f"    active: {task_config.get('active')}") # pyright: ignore[reportUnusedVariable]
                    print(f"    selected_active_colortype: '{task_config.get('selected_active_colortype', '')}'")
                
                return config
                
            except Exception as ui_error:
                print(f"[ERROR] Error capturing from UI: {ui_error}")
                import traceback
                traceback.print_exc()
                return {}
            
        except Exception as e:
            print(f"[ERROR] General error during capture: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def _apply_colortype_config_to_duplicate(self, context, source_config, task_mapping=None):
        """
        Applies the captured ColorType configuration to the duplicated schedule.
        """
        try:
            import json
            import ifcopenshell.util.sequence
            
            print(f"🔄🔄🔄 === STARTING EXHAUSTIVE APPLICATION ===")
            
            if not source_config:
                print(f"[ERROR] source_config is empty, nothing to apply")
                return
            
            print(f"📊 source_config tiene {len(source_config)} entradas")
            
            # Find the newly created schedule (last "Copy of...")
            ifc_file = tool.Ifc.get()
            all_schedules = ifc_file.by_type("IfcWorkSchedule")
            duplicate_schedule = None
            
            print(f"📋 Searching for duplicated schedule among {len(all_schedules)} schedules:")
            for schedule in all_schedules:
                schedule_name = getattr(schedule, 'Name', 'NO_NAME')
                print(f"  - {schedule.id()}: '{schedule_name}'")
                if schedule_name and schedule_name.startswith("Copy of "):
                    duplicate_schedule = schedule
            
            if not duplicate_schedule:
                print("[ERROR] No duplicated schedule found")
                return
            
            # Get all tasks from the duplicated schedule
            def get_all_tasks_recursive(tasks):
                all_tasks_list = []
                for task in tasks:
                    all_tasks_list.append(task)
                    nested_tasks = ifcopenshell.util.sequence.get_nested_tasks(task)
                    if nested_tasks:
                        all_tasks_list.extend(get_all_tasks_recursive(nested_tasks))
                return all_tasks_list
            
            root_tasks = ifcopenshell.util.sequence.get_root_tasks(duplicate_schedule)
            all_duplicate_tasks = get_all_tasks_recursive(root_tasks)
            
            print(f"📊 Duplicated schedule '{duplicate_schedule.Name}' has {len(all_duplicate_tasks)} tasks")
            
            # Create mapping by Identification to find corresponding tasks
            duplicate_task_map = {}
            for task in all_duplicate_tasks:
                identification = getattr(task, "Identification", None)
                if identification:
                    duplicate_task_map[identification] = task
                    print(f"  Duplicate task {task.id()}: '{getattr(task, 'Name', 'NO_NAME')}' -> identification: '{identification}'")
            
            # Apply configuration to duplicated tasks
            duplicate_ws_id = duplicate_schedule.id()
            snap_key_duplicate = f"_task_colortype_snapshot_json_WS_{duplicate_ws_id}"
            cache_key = "_task_colortype_snapshot_cache_json"
            
            print(f"📁 Keys for saving configuration:")
            print(f"  snap_key_duplicate: {snap_key_duplicate}")
            print(f"  cache_key: {cache_key}")
            
            # Use the exact ID mapping if available
            duplicate_config = {}
            
            if task_mapping:
                print(f"🎯 Using exact mapping of {len(task_mapping)} tasks for ColorType")
                print(f"🔗 Available mapping: {task_mapping}")
                
                # Direct mapping using the duplication mapping
                for source_task_id_int, target_task_id_int in task_mapping.items():
                    source_task_id_str = str(source_task_id_int)
                    target_task_id_str = str(target_task_id_int)
                    
                    print(f"\n🎯 Processing mapping: {source_task_id_str} → {target_task_id_str}")
                    
                    if source_task_id_str in source_config:
                        config_data = source_config[source_task_id_str].copy()
                        duplicate_config[target_task_id_str] = config_data
                        
                        print(f"    📁 Keys in original config: {list(config_data.keys())}")

                        # Verify structure in detail
                        if "groups" in config_data:
                            groups = config_data["groups"]
                            print(f"    📁 Groups found: {len(groups)} items")
                            
                            for idx, g in enumerate(groups): # pyright: ignore[reportUnusedVariable]
                                group_name = g.get("group_name", "NO_NAME")
                                enabled = g.get("enabled", False)
                                value = g.get("selected_value", "")
                                print(f"      {idx}: '{group_name}' (enabled={enabled}, value='{value}')") # pyright: ignore[reportUnusedVariable]
                                
                                # Special focus on DEFAULT
                                if group_name == "DEFAULT":
                                    print(f"      🔍 DEFAULT DETECTED: enabled={enabled}, value='{value}'")
                        else:
                            print(f"    [ERROR] 'groups' field NOT found in configuration")
                        
                        # Verify active checkbox
                        active = config_data.get("active", False)
                        selected = config_data.get("selected_active_colortype", "")
                        print(f"    📋 Active checkbox: {active}")
                        print(f"    📋 Selected value: '{selected}'")
                        
                    else:
                        print(f"  [ERROR] Source ID {source_task_id_str} NOT found in source_config")
                        print(f"      Available IDs: {list(source_config.keys())}")
                        
                print(f"🎨 Exact mapping result: {len(duplicate_config)} configurations transferred")

            else:
                print(f"[WARNING] No exact mapping, using fallback method by Identification")
                # Fallback: mapping by Identification (previous method)
                for source_task_id, config_data in source_config.items():
                    print(f"🔍 Searching for correspondence for source task {source_task_id}")
                    
                    # Try to find the corresponding task by Identification
                    for identification, duplicate_task in duplicate_task_map.items():
                        duplicate_task_id = str(duplicate_task.id())
                        if duplicate_task_id not in duplicate_config:
                            duplicate_config[duplicate_task_id] = config_data.copy() # pyright: ignore[reportUnusedVariable]
                            break
                
                # If there are not enough mappings by Identification, apply sequentially
                if len(duplicate_config) < len(source_config):
                    print(f"[WARNING] Insufficient mapping by Identification, applying sequentially")
                    duplicate_task_ids = [str(task.id()) for task in all_duplicate_tasks]
                    source_configs = list(source_config.values())
                    
                    for i, duplicate_task_id in enumerate(duplicate_task_ids):
                        if duplicate_task_id not in duplicate_config and i < len(source_configs): # pyright: ignore[reportUnusedVariable]
                            duplicate_config[duplicate_task_id] = source_configs[i].copy()
                            print(f"  [INFO] Assigned sequentially: index {i} → {duplicate_task_id}")
            
            print(f"\n📊 === FINAL CONFIGURATION RESULT ===")
            print(f"Total configurations to apply: {len(duplicate_config)}")
            
            # Show final configuration to be saved
            for task_id, config in duplicate_config.items():
                print(f"🔍 TASK {task_id} final configuration:")
                groups = config.get("groups", [])
                print(f"    groups: {len(groups)} items")
                for g in groups: # pyright: ignore[reportUnboundVariable]
                    name = g.get('group_name', 'no name')
                    enabled = g.get('enabled', False)
                    value = g.get('selected_value', '')
                    print(f"      - '{name}': enabled={enabled}, value='{value}'")
                    if name == "DEFAULT": # pyright: ignore[reportUnboundVariable]
                        print(f"        🔍 DEFAULT: enabled={enabled}, value='{value}'")
                print(f"    active: {config.get('active')}")
                print(f"    selected_active_colortype: '{config.get('selected_active_colortype', '')}'")
            
            # Save configuration to snapshot and cache
            print(f"\n💾 === SAVING CONFIGURATION ===")
            
            config_json = json.dumps(duplicate_config)
            context.scene[snap_key_duplicate] = config_json # pyright: ignore[reportUnusedVariable]
            
            # Also update the general cache
            try:
                cache_raw = context.scene.get(cache_key, "{}")
                cache_data = json.loads(cache_raw) if cache_raw else {}
                cache_data.update(duplicate_config)
                context.scene[cache_key] = json.dumps(cache_data) # pyright: ignore[reportUnusedVariable]
            except Exception as cache_error:
                print(f"[WARNING] Error updating general cache: {cache_error}")
                context.scene[cache_key] = json.dumps(duplicate_config)
            
            # Verify that it was actually saved
            verification = context.scene.get(snap_key_duplicate, "")
            if verification:
                verification_data = json.loads(verification)
            else:
                print(f"[ERROR] ERROR: Could not verify save")
            
            print(f"🎨 Applied ColorType config to {len(duplicate_config)} tasks in duplicated schedule '{duplicate_schedule.Name}'") # pyright: ignore[reportUnusedVariable]
            
            # Load the configuration into the UI to make it visible
            if duplicate_config:
                try:
                    from .filter_operators import restore_persistent_task_state
                    print(f"🔄 === LOADING CONFIGURATION INTO UI ===")
                    
                    # Temporarily switch to the duplicated schedule to load its configuration
                    ws_props = tool.Sequence.get_work_schedule_props()
                    original_active_id = ws_props.active_work_schedule_id
                    print(f"📋 Original active schedule: {original_active_id}")
                    
                    # Temporarily switch to the duplicated schedule
                    ws_props.active_work_schedule_id = duplicate_ws_id
                    print(f"📋 Temporarily switching to duplicated schedule: {duplicate_ws_id}")
                    tool.Sequence.load_task_tree(duplicate_schedule)
                    
                    # Restore the configuration in the UI
                    print(f"🔄 Executing restore_persistent_task_state...")
                    restore_persistent_task_state(context)
                    
                    # Switch back to the original schedule
                    if original_active_id != 0:
                        print(f"📋 Returning to original schedule: {original_active_id}")
                        ws_props.active_work_schedule_id = original_active_id
                        original_schedule = tool.Ifc.get().by_id(original_active_id) # pyright: ignore[reportUnusedVariable]
                        tool.Sequence.load_task_tree(original_schedule)
                    
                    
                except Exception as ui_error:
                    print(f"[ERROR] Error loading configuration into UI: {ui_error}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"[ERROR] No configuration to load into UI") # pyright: ignore[reportUnusedVariable]
            
            print(f"🎨 === ColorType duplication process COMPLETED ===")

        except Exception as e:
            print(f"[ERROR] General error applying ColorType config: {e}")
            import traceback
            traceback.print_exc()


class EnableEditingWorkSchedule(bpy.types.Operator):
    bl_idname = "bim.enable_editing_work_schedule"
    bl_label = "Enable Editing Work Schedule"
    bl_description = "Enable editing work schedule attributes."
    bl_options = {"REGISTER", "UNDO"}
    work_schedule: bpy.props.IntProperty()

    def execute(self, context):
        core.enable_editing_work_schedule(tool.Sequence, work_schedule=tool.Ifc.get().by_id(self.work_schedule))
        return {"FINISHED"}


class EnableEditingWorkScheduleTasks(bpy.types.Operator):
    """
    Enables editing of the task structure for a specific work schedule,
    ensuring that the state cache is managed correctly.
    """
    bl_idname = "bim.enable_editing_work_schedule_tasks"
    bl_label = "Enable Editing Work Schedule Tasks"
    bl_description = "Enable editing work schedule tasks."
    bl_options = {"REGISTER", "UNDO"}

    work_schedule: bpy.props.IntProperty()

    def execute(self, context):
        
        # --- STEP 1: SELECTIVELY CLEAR THE PERSISTENT CACHE ---
        # We only clear the cache of the PREVIOUS schedule, not globally.
        # This preserves the tasks of the original schedule when duplicating/deleting.
        try:
            # Get the schedule being left (if any)
            ws_props = tool.Sequence.get_work_schedule_props()
            previous_schedule_id = getattr(ws_props, "active_work_schedule_id", 0)
            
            if previous_schedule_id != 0 and previous_schedule_id != self.work_schedule:
                # Only clear the cache of the previous schedule, not the one being activated
                bpy.ops.bim.clear_task_state_cache(work_schedule_id=previous_schedule_id)
                print(f"🎯 Selective cache: cleared previous schedule {previous_schedule_id}")
            else:
                print("🔄 Schedule change: no cache clearing needed")
                
        except Exception as e:
            print(f"Warning: Selective clearing failed: {e}. No cache clearing.")

        # --- STEP 2: SAVE THE GENERAL UI STATE ---
        # This saves things like the scroll position or the active task,
        # using the mechanism you already had.
        snapshot_all_ui_state(context)

        # --- STEP 3: SET THE NEW ACTIVE SCHEDULE AND LOAD DATA ---
        # We get the schedule instance from its ID
        work_schedule_instance = tool.Ifc.get().by_id(self.work_schedule)
        
        # We call the tool function that handles the main activation logic
        tool.Sequence.enable_editing_work_schedule_tasks(work_schedule_instance)
        
        # We reload the task tree and properties, as in your original version.
        # This is necessary for the UI to show the tasks of the new schedule.
        tool.Sequence.load_task_tree(work_schedule_instance)
        tool.Sequence.load_task_properties()

        # --- STEP 4: RESTORE THE GENERAL UI STATE ---
        # We restore the scroll and selection that we saved in step 2.
        # Since the ColorTypes cache is empty, it will not try to restore
        # incorrect data from the previous schedule.
        restore_all_ui_state(context)

        return {"FINISHED"}


class DisableEditingWorkSchedule(bpy.types.Operator):
    bl_idname = "bim.disable_editing_work_schedule"
    bl_label = "Disable Editing Work Schedule"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        # USE THE SAME PATTERN AS THE FILTERS (which works correctly):
        snapshot_all_ui_state(context)  # >>> 1. Save state BEFORE canceling
        
        # >>> 2. Execute the cancel operation (which can reset/clear data)
        core.disable_editing_work_schedule(tool.Sequence)
        
        return {"FINISHED"}


class SortWorkScheduleByIdAsc(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.sort_schedule_by_id_asc"
    bl_label = "Sort by ID (Ascending)"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = tool.Sequence.get_work_schedule_props()
        # Set sort column to Identification and ascending
        props.sort_column = "IfcTask.Identification"
        props.is_sort_reversed = False
        try:
            import bonsai.core.sequence as core
            core.load_task_tree(tool.Ifc, tool.Sequence)
        except Exception:
            pass
        return {"FINISHED"}


class VisualiseWorkScheduleDateRange(bpy.types.Operator):
    bl_idname = "bim.visualise_work_schedule_date_range"
    bl_label = "Create Animation" # Updated text for the UI
    bl_description = "Create or update 4D animation based on the current work schedule and date range settings. Animates objects with colors and visibility changes over time."
    bl_options = {"REGISTER", "UNDO"}
    work_schedule: bpy.props.IntProperty()

    # NEW: Property for the user to choose the action in the popup dialog
    camera_action: bpy.props.EnumProperty(
        name="Camera Action",
        description="Choose whether to create a new camera or update the existing one",
        items=[
            ('UPDATE', "Update Existing Camera", "Update the existing 4D camera with current settings"),
            ('CREATE_NEW', "Create New Camera", "Create a new 4D camera"),
            ('NONE', "No Camera Action", "Do not add or modify the camera"),
        ],
        default='UPDATE'
    )

    @classmethod
    def poll(cls, context):
        import bonsai.tool as tool
        props = tool.Sequence.get_work_schedule_props()
        has_start = bool(props.visualisation_start and props.visualisation_start != "-")
        has_finish = bool(props.visualisation_finish and props.visualisation_finish != "-")
        return has_start and has_finish

    def execute(self, context):
        # Clear all caches before animation to ensure fresh data
        try:
            from bonsai.bim.module.sequence.utils import performance_cache, ifc_lookup, colortype_cache
            performance_cache.invalidate_cache()
            ifc_lookup.invalidate_all_lookups()
            colortype_cache.clear_global_cache()
        except Exception:
            pass
        import time  # Fix for UnboundLocalError
        import bonsai.tool as tool
        try:
            
            # It is crucial to capture the current state of the task UI (custom
            # assignments) BEFORE generating the animation. Without this, recent
            # changes in the task list will not be reflected.
            snapshot_all_ui_state(context) # pyright: ignore[reportUnusedFunction]
            

           
            # Auto-saving of profile configuration in IFC
            try:
                work_schedule_entity = tool.Ifc.get().by_id(self.work_schedule)
                if work_schedule_entity:
                    import bonsai.core.sequence as core
                    anim_props = tool.Sequence.get_animation_props()
                    colortype_data_to_save = {
                        "colortype_sets": {},  # Moved to config_operators.py
                        "task_configurations": _task_colortype_snapshot(context) if '_task_colortype_snapshot' in globals() else {},
                        "animation_settings": {
                            "active_editor_group": getattr(anim_props, "ColorType_groups", "DEFAULT"),
                            "active_task_group": getattr(anim_props, "task_colortype_group_selector", ""),
                            "group_stack": [
                                {"group": getattr(item, "group", ""), "enabled": bool(getattr(item, "enabled", False))}
                                for item in getattr(anim_props, "animation_group_stack", [])
                            ]
                        }
                    }
                    # core.save_colortypes_to_ifc_core(tool.Ifc.get(), work_schedule_entity, colortype_data_to_save)
            except Exception as e:
                print(f"Bonsai WARNING: Auto-saving of profiles to IFC failed: {e}")

            # --- 1. Product animation logic (no changes) ---
            tool.Sequence.sync_active_group_to_json()
            work_schedule = tool.Ifc.get().by_id(self.work_schedule)

            # Better error logging to understand what's failing
            if not work_schedule:
                self.report({'ERROR'}, f"Work schedule with ID {self.work_schedule} not found in IFC file.")
                return {'CANCELLED'}

            # Try to get animation settings, provide fallback if needed
            try:
                settings = tool.Sequence.get_animation_settings()
            except Exception as e:
                print(f"Warning: Could not get animation settings: {e}")
                settings = None

            if not settings:
                print("Warning: Animation settings not available, using basic fallback")
                # Provide complete settings to allow operation to continue
                from datetime import datetime, timedelta

                # Use current date as fallback start/finish dates
                current_date = datetime.now()
                end_date = current_date + timedelta(days=365)  # 1 year duration

                settings = {
                    'start_frame': 1,
                    'end_frame': 250,
                    'total_frames': 249,  # end_frame - start_frame
                    'fps': 24,
                    'start': current_date,
                    'finish': end_date,
                    'duration': timedelta(days=365),
                    'schedule_name': 'Fallback Schedule'
                }
            
            # Add schedule name to settings for the handler
            if work_schedule and hasattr(work_schedule, 'Name'):
                settings['schedule_name'] = work_schedule.Name

            # Comment out clear to avoid crash
            # _clear_previous_animation(context)

            
            # FORCE OPTIMIZED FRAME COMPUTATION 
            frames_start = time.time()
            try:
                # Always try optimized method first
                from bonsai.bim.module.sequence import ifc_lookup
                lookup = ifc_lookup.get_ifc_lookup()
                date_cache = ifc_lookup.get_date_cache()
                if not lookup.lookup_built:
                    print("[OPTIMIZED] Building lookup tables...")
                    lookup.build_lookup_tables(work_schedule)
                print("[OPTIMIZED] Using enhanced optimized frame computation...")
                product_frames = tool.Sequence.get_animation_product_frames_enhanced_optimized(
                    work_schedule, settings, lookup, date_cache
                )
                frames_time = time.time() - frames_start
                print(f"📊 FRAMES COMPUTED: {len(product_frames)} products in {frames_time:.2f}s")
            except Exception as e:
                print(f"[WARNING] Optimized frames method not available, using fallback: {e}")
                product_frames = tool.Sequence.get_animation_product_frames_enhanced(work_schedule, settings)
            if not product_frames:
                self.report({'WARNING'}, "No products found to animate.")

            # FORCE OPTIMIZED ANIMATION APPLICATION 
            anim_start = time.time()

            # BUILD COLORTYPE CACHE 
            try:
                try:
                    from . import colortype_cache
                except ImportError:
                    import sys, os
                    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
                    import colortype_cache
                cache_instance = colortype_cache.get_colortype_cache()
                colortype_build_time = cache_instance.build_cache(bpy.context)
                print(f"🎨 COLORTYPE CACHE: Built in {colortype_build_time:.3f}s")
            except Exception as e:
                print(f"[WARNING] ColorType cache failed to build: {e}")

            # DIRECT SCRIPT EXECUTION - Copy exact working code from COMPLETE_SYSTEM_ULTRA_FAST
            print(f"[DIRECT] Executing exact script code for {len(product_frames)} products")

            # EXACT COPY FROM apply_complete_system_animation function
            print("🔧 Starting complete system...")
            opt_start = time.time()

            # MAPEO: IFC a Blender
            map_start = time.time()
            ifc_to_blender = {}
            all_ifc_objects = [] # pyright: ignore[reportUnusedVariable]

            for obj in bpy.data.objects:
                if obj.type == 'MESH':
                    element = tool.Ifc.get_entity(obj)
                    if element and not element.is_a("IfcSpace"):
                        ifc_to_blender[element.id()] = obj
                        all_ifc_objects.append(obj)

            map_time = time.time() - map_start
            print(f"📦 Mapped {len(ifc_to_blender)} IFC objects in {map_time:.3f}s")

            # Get REAL ColorType group
            animation_props = tool.Sequence.get_animation_props()
            active_group_name = None
            for item in getattr(animation_props, "animation_group_stack", []):
                if getattr(item, "enabled", False) and getattr(item, "group", None):
                    active_group_name = item.group
                    break
            if not active_group_name:
                active_group_name = "DEFAULT"

            print(f"🎨 REAL ColorType Group: '{active_group_name}'")

            # Exact visibility like the real system (lines 4779-4789)
            hide_start = time.time()

            # FIRST: Clear animation from ALL (SAME AS THE SCRIPT)
            for obj in all_ifc_objects:
                if obj.animation_data:
                    obj.animation_data_clear()

            # SECOND: Ensure frame 0 for keyframes
            context.scene.frame_set(0)

            # THIRD: Apply the EXACT logic of the real system
            assigned_objects = set()
            unassigned_objects = set()
            for obj in all_ifc_objects:
                element = tool.Ifc.get_entity(obj)
                if not element:
                    continue

                if element.id() not in product_frames:
                    # Unassigned objects hidden WITHOUT keyframes
                    obj.hide_viewport = True
                    obj.hide_render = True
                    unassigned_objects.add(obj)
                else:
                    #Assigned objects hidden WITH keyframe at frame 0
                    obj.hide_viewport = True
                    obj.hide_render = True
                    obj.keyframe_insert(data_path="hide_viewport", frame=0)
                    obj.keyframe_insert(data_path="hide_render", frame=0)
                    assigned_objects.add(obj)

            hide_time = time.time() - hide_start
            print(f"👁️ Visibility configured according to real system in {hide_time:.3f}s")
            print(f"🚫 Unassigned objects: {len(unassigned_objects)} (hidden WITHOUT keyframes)")
            print(f"📋 Assigned objects: {len(assigned_objects)} (hidden WITH keyframe at frame 0)")

            # Get original colors of assigned objects
            colors_start = time.time()
            original_colors = {}
            for obj in assigned_objects:
                try:
                    original_colors[obj.name] = [obj.color[0], obj.color[1], obj.color[2], obj.color[3]]
                except:
                    original_colors[obj.name] = [1.0, 1.0, 1.0, 1.0]

            colors_time = time.time() - colors_start # pyright: ignore[reportUnusedVariable]
            print(f"🎨 Original colors of {len(original_colors)} assigned objects in {colors_time:.3f}s")

            # Cache of REAL ColorTypes (support for custom ranges)
            process_start = time.time()
            colortype_cache = {}
            visibility_ops = []
            color_ops = []
            processed_count = 0

            for product_id, frame_data_list in product_frames.items():
                if product_id not in ifc_to_blender:
                    continue

                obj = ifc_to_blender[product_id]
                if obj not in assigned_objects:
                    continue

                original_color = original_colors.get(obj.name, [1.0, 1.0, 1.0, 1.0]) # pyright: ignore[reportUnusedVariable]

                for frame_data in frame_data_list:
                    task = frame_data.get("task")

                    # Cache ColorType REAL (maneja rangos personalizados)
                    task_key = task.id() if task else "None"
                    if task_key not in colortype_cache:
                        try:
                            # USE the real system that handles custom START/FINISH
                            colortype_cache[task_key] = tool.Sequence.get_assigned_ColorType_for_task(
                                task, animation_props, active_group_name)
                        except Exception as e:
                            print(f"[WARNING] Error getting ColorType for task {task_key}: {e}")
                            colortype_cache[task_key] = None

                    ColorType = colortype_cache[task_key]
                    if not ColorType:
                        continue

                    states = frame_data.get("states", {})
                    if states:
                        # Plan operations using the exact function from the script
                        is_construction = frame_data.get("relationship") == "output"

                        consider_start = getattr(ColorType, 'consider_start', False)
                        consider_active = getattr(ColorType, 'consider_active', True)
                        consider_end = getattr(ColorType, 'consider_end', True)

                        print(f"   Task: {task.Name if task else 'None'}")
                        print(f"   ColorType: {getattr(ColorType, 'name', 'Unknown')}")
                        print(f"   consider_start: {consider_start}")
                        print(f"   consider_active: {consider_active}")
                        print(f"   consider_end: {consider_end}")
                        print(f"   is_construction: {is_construction}")
                        print(f"   states: {states}")

                        # PRIORITY MODE CHECK: Only START is enabled
                        is_priority_mode = (consider_start and not consider_active and not consider_end) # pyright: ignore[reportUnusedVariable]
                        print(f"   is_priority_mode: {is_priority_mode}")

                        if is_priority_mode:
                            # Para priority mode, usar el rango 'active' completo con estado 'start'
                            active_range = states.get("active", (0, -1))
                            print(f"   PRIORITY MODE: Using active range {active_range} for START state")
                            if active_range[1] >= active_range[0]:
                                visibility_ops.append({'obj': obj, 'frame': active_range[0], 'hide': False})

                                # START COLOR using REAL ColorType
                                use_original = getattr(ColorType, 'use_start_original_color', False)
                                if use_original:
                                    color = original_color
                                else:
                                    start_color = getattr(ColorType, 'start_color', [0.8, 0.8, 0.8, 1.0])
                                    transparency = getattr(ColorType, 'start_transparency', 0.0)
                                    color = [start_color[0], start_color[1], start_color[2], 1.0 - transparency]
                                color_ops.append({'obj': obj, 'frame': active_range[0], 'color': color})
                            continue  # Skip normal logic for priority mode

                        # START state with REAL ColorType
                        before_start = states.get("before_start", (0, -1))
                        print(f"   before_start range: {before_start}")
                        if before_start[1] >= before_start[0]:
                            consider_start = getattr(ColorType, 'consider_start', False)
                            should_be_visible = not is_construction or consider_start
                            print(f"      START logic: consider_start={consider_start}, should_be_visible={should_be_visible}")
                            if should_be_visible:
                               # If consider_start is enabled, start from frame 0
                                start_frame = 0 if consider_start else before_start[0]
                                visibility_ops.append({'obj': obj, 'frame': start_frame, 'hide': False})
                           
                                # START COLOR using REAL ColorType
                                use_original = getattr(ColorType, 'use_start_original_color', False)
                                if use_original:
                                    color = original_color
                                else:
                                    start_color = getattr(ColorType, 'start_color', [0.8, 0.8, 0.8, 1.0])
                                    transparency = getattr(ColorType, 'start_transparency', 0.0)
                                    color = [start_color[0], start_color[1], start_color[2], 1.0 - transparency]

                                color_ops.append({'obj': obj, 'frame': start_frame, 'color': color})
 
                                       
                            else:
                                print(f"      [ERROR] NOT ADDING VISIBILITY OP: object should stay hidden")    

                        # ACTIVE state with REAL ColorType
                        active = states.get("active", (0, -1))
                        if active[1] >= active[0] and getattr(ColorType, 'consider_active', True):
                            visibility_ops.append({'obj': obj, 'frame': active[0], 'hide': False})

                            # ACTIVE COLOR using REAL ColorType
                            active_color = getattr(ColorType, 'in_progress_color', [0.5, 0.9, 0.5, 1.0])
                            transparency = getattr(ColorType, 'in_progress_transparency', 0.0) # pyright: ignore[reportUnusedVariable]
                            color = [active_color[0], active_color[1], active_color[2], 1.0 - transparency]
                            color_ops.append({'obj': obj, 'frame': active[0], 'color': color})

                        # END state with REAL ColorType
                        after_end = states.get("after_end", (0, -1))
                        if after_end[1] >= after_end[0]:
                            consider_end = getattr(ColorType, 'consider_end', True)
                            print(f"      END logic: consider_end={consider_end}, after_end range: {after_end}")

                            if not consider_end:
                                # If consider_end=False, hide objects at END phase (like snapshot logic)
                                visibility_ops.append({'obj': obj, 'frame': after_end[0], 'hide': True})
                            else:
                                should_hide_at_end = getattr(ColorType, 'hide_at_end', False)
                                if should_hide_at_end:
                                    # Hide object at the end (e.g., demolitions)
                                    visibility_ops.append({'obj': obj, 'frame': after_end[0], 'hide': True})
                                else:
                                    # Show object at the end with END color
                                    visibility_ops.append({'obj': obj, 'frame': after_end[0], 'hide': False})

                                # END COLOR using REAL ColorType - only if not hidden
                                use_original = getattr(ColorType, 'use_end_original_color', False)
                                if use_original:
                                    color = original_color # pyright: ignore[reportUnusedVariable]
                                else:
                                    end_color = getattr(ColorType, 'end_color', [0.7, 0.7, 0.7, 1.0])
                                    transparency = getattr(ColorType, 'end_transparency', 0.0)
                                    color = [end_color[0], end_color[1], end_color[2], 1.0 - transparency]
                                color_ops.append({'obj': obj, 'frame': after_end[0], 'color': color})

                        processed_count += 1

            process_time = time.time() - process_start
            print(f"📋 Processed {processed_count} frames with REAL ColorTypes in {process_time:.3f}s")

            # Execute operations only on ASSIGNED objects
            exec_start = time.time()

            frame_analysis = {}
            visibility_false_count = 0  # ops that make objects visible
            visibility_true_count = 0   # ops that make objects hidden

            for op in visibility_ops:
                if op['obj'] in assigned_objects:
                    frame = op['frame']
                    hide_value = op['hide']

                    if frame not in frame_analysis:
                        frame_analysis[frame] = {'hide_false': 0, 'hide_true': 0}

                    if hide_value:
                        frame_analysis[frame]['hide_true'] += 1
                        visibility_true_count += 1
                    else:
                        frame_analysis[frame]['hide_false'] += 1
                        visibility_false_count += 1

            print(f"🔍 VISIBILITY_OPS ANALYSIS:")
            print(f"   Total ops haciendo VISIBLE (hide=False): {visibility_false_count}")
            print(f"   Total ops haciendo HIDDEN (hide=True): {visibility_true_count}")

            # Show most problematic frames
            sorted_frames = sorted(frame_analysis.keys())[:5]  # First 5 frames
            for frame in sorted_frames:
                data = frame_analysis[frame]
                print(f"   Frame {frame}: {data['hide_false']} visible, {data['hide_true']} hidden")

            # EXECUTE visibility_ops CORRECTLY - only the necessary ones
            executed_ops = 0
            for op in visibility_ops:
                if op['obj'] in assigned_objects:
                    # Only execute if visibility really needs to change
                    op['obj'].hide_viewport = op['hide']
                    op['obj'].hide_render = op['hide']
                    op['obj'].keyframe_insert(data_path="hide_viewport", frame=op['frame'])
                    op['obj'].keyframe_insert(data_path="hide_render", frame=op['frame'])
                    executed_ops += 1


            for op in color_ops:
                if op['obj'] in assigned_objects: # pyright: ignore[reportUnboundVariable]
                    op['obj'].color = op['color']
                    op['obj'].keyframe_insert(data_path="color", frame=op['frame'])

            exec_time = time.time() - exec_start
            opt_total = time.time() - opt_start

            print(f"⚡ Executed {len(visibility_ops)} visibilities + {len(color_ops)} colors in {exec_time:.3f}s")

            anim_time = time.time() - anim_start
            print(f"🎬 DIRECT SCRIPT ANIMATION COMPLETED: {anim_time:.2f}s")

            # Ensure we are at frame 0 and FORCE objects to be hidden
            context.scene.frame_set(0)
            current_frame = context.scene.frame_current # pyright: ignore[reportUnusedVariable]

            # Ensure all objects are hidden in frame 0 viewport
            force_hidden_count = 0
            for obj in assigned_objects:
                if not obj.hide_viewport:
                    obj.hide_viewport = True
                    obj.hide_render = True
                    force_hidden_count += 1

            print(f"🔧 FORCE: Hid {force_hidden_count} objects in viewport")

            # Are the objects really hidden?
            visible_check = sum(1 for obj in assigned_objects if not obj.hide_viewport)
            hidden_check = sum(1 for obj in assigned_objects if obj.hide_viewport)
            print(f"🔍 FINAL VERIFICATION (FRAME {current_frame}):")
            print(f"   [ERROR] Visible objects: {visible_check}")

            if visible_check == 0:
                print("🎉 SUCCESS: All objects hidden in viewport at frame 0")

            # Only basic functionalities to avoid crash
            # Add functionalities one by one to identify the cause of the crash

            print("[WARNING] CRASH PREVENTION: Only adding basic functionalities")

            # BÁSICO 1: Text animation handler (SAFE - no auto-arrange)
            try:
                tool.Sequence.add_text_animation_handler(settings)
                print("[WARNING] Auto-arrange disabled to prevent crashes")
            except Exception as e:
                print(f"[ERROR] Text animation handler failed: {e}")
                import traceback
                traceback.print_exc()

            # REMOVED: Schedule name text - CAUSES CRASH
            # The creation of text objects is causing crashes

            # SAFE FUNCTIONALITIES (do not create objects):

            try:
                tool.Sequence.set_object_shading()
            except Exception as e:
                print(f"[ERROR] Viewport shading failed: {e}")

            try:
                anim_props = tool.Sequence.get_animation_props()
                camera_props = anim_props.camera_orbit
                should_hide = not getattr(camera_props, "show_3d_schedule_texts", False)

                # Apply automatic deactivation logic if 3D HUD Render is disabled
                if should_hide:
                    current_legend_enabled = getattr(camera_props, "enable_3d_legend_hud", False)
                    if current_legend_enabled:
                        print("🔴 ANIMATION: 3D HUD Render disabled, auto-disabling 3D Legend HUD")
                        camera_props.enable_3d_legend_hud = False

                collection = bpy.data.collections.get("Schedule_Display_Texts")
                if collection:
                    # Synchronize the collection's visibility with the checkbox state.
                    # If show_3d_schedule_texts is False, hide_viewport must be True.
                    collection.hide_viewport = should_hide
                    collection.hide_render = should_hide

                # Also apply to 3D Legend HUD collection
                legend_collection = bpy.data.collections.get("Schedule_Display_3D_Legend")
                if legend_collection:
                    legend_collection.hide_viewport = should_hide
                    legend_collection.hide_render = should_hide

                    # Force redraw of the 3D view so the change is immediate.
                    for window in context.window_manager.windows:
                        for area in window.screen.areas:
                            if area.type == 'VIEW_3D':
                                area.tag_redraw()

            except Exception as e: # pyright: ignore[reportUnusedVariable]
                print(f"[ERROR] Collection visibility failed: {e}")

            # SAFE 5: HUD Legend profile restoration
            try:
                anim_props = tool.Sequence.get_animation_props()
                if anim_props and hasattr(anim_props, 'camera_orbit'):
                    camera_props = anim_props.camera_orbit
                    # Clear hidden profiles list to show all
                    camera_props.legend_hud_visible_colortypes = ""
                    # Invalidate legend HUD cache
                    from ..hud import invalidate_legend_hud_cache
                    invalidate_legend_hud_cache()
                else:
                    print("[WARNING] Animation props not available")
            except Exception as e:
                print(f"[ERROR] HUD Legend restoration failed: {e}")

            # SAFE 6: 3D Legend HUD support - MOVED AFTER HUD INITIALIZATION

            # SAFE 7: Camera 360/pingpong support
            try:
                if hasattr(tool.Sequence, 'setup_camera_360_support'):
                    tool.Sequence.setup_camera_360_support()
                else:
                    print("[WARNING] Camera 360 support method not available")
            except Exception as e:
                print(f"[ERROR] Camera 360 support failed: {e}")

            # Revert to the stable version without batch creation
            print("[WARNING] Task bars functionality DISABLED (reverting to stable version)")

            # The camera will only be created when the user specifies it via camera_action

            # RESTORE ALL FUNCTIONALITIES - SAME AS CURRENT SYSTEM
            print("🎯 RESTORING ALL FUNCTIONALITIES - LIKE CURRENT SYSTEM")

            try:
                if settings and settings.get("start") and settings.get("finish"):
                    print("🎬 Auto-configuring HUD Compositor for high-quality renders...")
                    bpy.ops.bim.setup_hud_compositor()
                    print("📹 Regular renders (Ctrl+F12) will now include HUD overlay")
                else:  # Fallback to Viewport HUD if there is no timeline
                    bpy.ops.bim.enable_schedule_hud()
            except Exception as e:
                print(f"[WARNING] Auto-setup of HUD failed: {e}. Falling back to Viewport HUD.")
                try:
                    bpy.ops.bim.enable_schedule_hud()
                except Exception:
                    pass

            print("🎯 ALL EXACT FUNCTIONALITIES FROM CURRENT SYSTEM IMPLEMENTED")

            # --- 3D LEGEND HUD INITIALIZATION (AFTER HUD IS READY) ---
            try:
                print("🎨 Setting up 3D Legend HUD support...")
                # Now that ScheduleHUD is initialized, we can set up 3D Legend HUD callbacks
                anim_props = tool.Sequence.get_animation_props()
                if anim_props and hasattr(anim_props, 'camera_orbit'):
                    camera_props = anim_props.camera_orbit

                    # If 3D Legend HUD is enabled, try to create it now that HUD is ready
                    legend_enabled = getattr(camera_props, 'enable_3d_legend_hud', False)
                    if legend_enabled:
                        print("🎨 3D Legend HUD enabled - attempting to create...")
                        bpy.ops.bim.setup_3d_legend_hud()
                    else:
                        print("📋 3D Legend HUD ready (enable via checkbox when needed)")
                else:
                    print("[WARNING] Animation props not available for 3D Legend HUD")
            except Exception as e:
                print(f"[WARNING] 3D Legend HUD setup failed: {e}")

            # --- 3D TEXTS CREATION ---
            try:
                # Get schedule name
                schedule_name = work_schedule.Name if work_schedule and hasattr(work_schedule, 'Name') else 'No Schedule'

                # Create or get collection
                coll_name = "Schedule_Display_Texts"
                if coll_name not in bpy.data.collections:
                    coll = bpy.data.collections.new(name=coll_name)
                    bpy.context.scene.collection.children.link(coll)
                else:
                    coll = bpy.data.collections[coll_name]

                # Create text object
                text_name = "Schedule_Name"
                if text_name in bpy.data.objects:
                    text_obj = bpy.data.objects[text_name]
                else:
                    text_data = bpy.data.curves.new(name=text_name, type='FONT')
                    text_obj = bpy.data.objects.new(name=text_name, object_data=text_data)
                    coll.objects.link(text_obj)

                # Set content and properties
                text_obj.data.body = f"Schedule: {schedule_name}"
                text_obj.data['text_type'] = 'schedule_name' # Custom type for the handler
 
                # --- PROPER 3D TEXT ALIGNMENT SETUP ---
                # Set alignment properties for consistent 3D text positioning
                if hasattr(text_obj.data, 'align_x'):
                    text_obj.data.align_x = 'CENTER'  # Horizontal center alignment
                if hasattr(text_obj.data, 'align_y'):
                    text_obj.data.align_y = 'BOTTOM_BASELINE'  # Vertical bottom baseline alignment

                # Reset offsets to ensure clean positioning at Z=0
                if hasattr(text_obj.data, 'offset_x'):
                    text_obj.data.offset_x = 0.0
                if hasattr(text_obj.data, 'offset_y'):
                    text_obj.data.offset_y = 0.0

                # Also pass the main settings for frame sync
                _ensure_local_text_settings_on_obj(text_obj, settings)

            except Exception as e:
                print(f"[WARNING] Could not create schedule name text: {e}")

            # Auto-arrange texts to default layout after creation
            try:
                bpy.ops.bim.arrange_schedule_texts()
            except Exception as e:
                print(f"[WARNING] Could not auto-arrange schedule texts: {e}")

            # --- PARENT TEXTS TO A CONSTRAINED EMPTY ---
            try:
                text_coll = bpy.data.collections.get("Schedule_Display_Texts")
                if text_coll and text_coll.objects:
                    parent_name = "Schedule_Display_Parent"
                    parent_empty = bpy.data.objects.get(parent_name)
                    if not parent_empty:
                        parent_empty = bpy.data.objects.new(parent_name, None)
                        context.scene.collection.objects.link(parent_empty)
                        parent_empty.empty_display_type = 'PLAIN_AXES' # pyright: ignore[reportAttributeAccessIssue]
                        parent_empty.empty_display_size = 2
                
                    for obj in text_coll.objects:
                        if obj.parent != parent_empty: # pyright: ignore[reportUnboundVariable]
                            obj.parent = parent_empty
                            obj.matrix_parent_inverse = parent_empty.matrix_world.inverted()

                    # Call the function directly instead of using prop fallback
                    from ..prop import callbacks_prop
                    callbacks_prop.update_schedule_display_parent_constraint(context)
            except Exception as e:
                print(f"[WARNING] Could not parent schedule texts: {e}")
            tool.Sequence.set_object_shading()
            bpy.context.scene.frame_start = settings["start_frame"]
            bpy.context.scene.frame_end = int(settings["start_frame"] + settings["total_frames"])


            if self.camera_action != 'NONE':
                # USE THE ACTIVE CAMERA FROM THE SELECTOR instead of the first one
                existing_cam = None
                try:
                    anim_props = tool.Sequence.get_animation_props()
                    camera_props = anim_props.camera_orbit
                    active_camera_name = getattr(camera_props, 'active_animation_camera', None)


                    # Handle different types that active_animation_camera might be
                    if hasattr(active_camera_name, 'name'):
                        # It's a Blender object, get the name
                        camera_name_str = active_camera_name.name
                    elif isinstance(active_camera_name, str):
                        # It's already a string
                        camera_name_str = active_camera_name
                    else:
                        # Unknown type or None
                        camera_name_str = None

                    if camera_name_str and camera_name_str != 'NONE':
                        existing_cam = bpy.data.objects.get(camera_name_str)
                        if existing_cam and existing_cam.type == 'CAMERA':
                            print(f"🎯 SUCCESS: Using camera from selector: {camera_name_str}")
                        else:
                            existing_cam = None
                            print(f"[WARNING] FAILED: Camera '{camera_name_str}' not found or invalid")

                    # Fallback: if there is no active camera, use the first one available
                    if not existing_cam:
                        existing_cam = next((obj for obj in bpy.data.objects if "4D_Animation_Camera" in obj.name), None)
                        if existing_cam:
                            print(f"🔄 FALLBACK: No active camera selected, using first available: {existing_cam.name}")

                except Exception as e:
                    print(f"[WARNING] ERROR getting active camera, using fallback: {e}")
                    existing_cam = next((obj for obj in bpy.data.objects if "4D_Animation_Camera" in obj.name), None)

                if self.camera_action == 'UPDATE':
                    print(f"🔄 UPDATE ACTION: existing_cam = {existing_cam}")
                    if existing_cam:

                        # NEW: Save panel values to the camera BEFORE updating # pyright: ignore[reportUnusedVariable]
                        try:
                            print(f"💾 SAVING panel values to camera '{existing_cam.name}' BEFORE update...")
                            anim_props = tool.Sequence.get_animation_props()
                            camera_props = anim_props.camera_orbit

                            # Save all panel values to camera
                            existing_cam['orbit_mode'] = camera_props.orbit_mode
                            existing_cam['orbit_radius'] = camera_props.orbit_radius
                            existing_cam['orbit_height'] = camera_props.orbit_height
                            existing_cam['orbit_start_angle_deg'] = camera_props.orbit_start_angle_deg
                            existing_cam['orbit_direction'] = camera_props.orbit_direction
                            existing_cam['orbit_radius_mode'] = camera_props.orbit_radius_mode
                            existing_cam['orbit_path_shape'] = camera_props.orbit_path_shape
                            existing_cam['orbit_path_method'] = camera_props.orbit_path_method
                            existing_cam['interpolation_mode'] = camera_props.interpolation_mode

                        except Exception as save_error:
                            print(f"[WARNING] Error saving panel values: {save_error}")

                        # Call the function only with the camera object.
                        tool.Sequence.update_animation_camera(existing_cam)
                    else:
                        self.report({'INFO'}, "[ERROR] FALLBACK: No existing camera to update. Creating a new one instead.")
                        print(f"[ERROR] FALLBACK: existing_cam is None, creating new camera with add_animation_camera()")
                        # Call the function without arguments.
                        tool.Sequence.add_animation_camera()
                elif self.camera_action == 'CREATE_NEW':
                    self.report({'INFO'}, "Creating a new 4D camera.")
                    # Call the function without arguments.
                    tool.Sequence.add_animation_camera()

                        # --- AUTOMATIC HUD CONFIGURATION (Dual System) ---
            try: # pyright: ignore[reportUnusedTry]
                if settings and settings.get("start") and settings.get("finish"):
                    print("🎬 Auto-configuring HUD Compositor for high-quality renders...")
                    bpy.ops.bim.setup_hud_compositor()
                    print("📹 Regular renders (Ctrl+F12) will now include HUD overlay") # pyright: ignore[reportUnusedVariable]
                else: # Fallback al HUD de Viewport si no hay timeline
                    bpy.ops.bim.enable_schedule_hud()
            except Exception as e:
                print(f"[WARNING] Auto-setup of HUD failed: {e}. Falling back to Viewport HUD.")
                try:
                    bpy.ops.bim.enable_schedule_hud()
                except Exception:
                    pass
            try:
                anim_props = tool.Sequence.get_animation_props()
                camera_props = anim_props.camera_orbit
                should_hide = not getattr(camera_props, "show_3d_schedule_texts", False)
                
                # Apply automatic deactivation logic if 3D HUD Render is disabled
                if should_hide:
                    current_legend_enabled = getattr(camera_props, "enable_3d_legend_hud", False)
                    if current_legend_enabled:
                        print("🔴 ANIMATION: 3D HUD Render disabled, auto-disabling 3D Legend HUD")
                        camera_props.enable_3d_legend_hud = False

                collection = bpy.data.collections.get("Schedule_Display_Texts")
                if collection:
                    # Synchronize the collection's visibility with the checkbox state.
                    # If show_3d_schedule_texts is False, hide_viewport must be True.
                    collection.hide_viewport = should_hide
                    collection.hide_render = should_hide

                # Also apply to 3D Legend HUD collection
                legend_collection = bpy.data.collections.get("Schedule_Display_3D_Legend")
                if legend_collection:
                    legend_collection.hide_viewport = should_hide
                    legend_collection.hide_render = should_hide

                    # Force redraw of the 3D view so the change is immediate.
                    for window in context.window_manager.windows:
                        for area in window.screen.areas:
                            if area.type == 'VIEW_3D':
                                area.tag_redraw()
            except Exception as e:
                print(f"[WARNING] Could not sync 3D text visibility: {e}")
        

            # Restore profile visibility in HUD Legend
            try:
                anim_props = tool.Sequence.get_animation_props()
                if anim_props and hasattr(anim_props, 'camera_orbit'):
                    camera_props = anim_props.camera_orbit
                    # Clear the list of hidden profiles to show all
                    camera_props.legend_hud_visible_colortypes = ""
                    # Invalidate legend HUD cache
                    from ..hud import invalidate_legend_hud_cache
                    invalidate_legend_hud_cache()
                    print("🎨 colortype group visibility restored in HUD Legend")
            except Exception as legend_e:
                print(f"[WARNING] Could not restore colortype group visibility: {legend_e}")

             
 
            self.report({'INFO'}, f"Animation created successfully for {len(product_frames)} products.")
            
            anim_props = tool.Sequence.get_animation_props()
            anim_props.is_animation_created = True

            # Force UI redraw to update button states
            for area in context.screen.areas:
                if area.type in ['PROPERTIES', 'VIEW_3D']:
                    area.tag_redraw()

            return {'FINISHED'}

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.report({'ERROR'}, f"Animation failed: {str(e)}")
            return {'CANCELLED'}

    def invoke(self, context, event):
        # Remove window completely and use smart fallback logic
        try:
            animation_props = tool.Sequence.get_animation_props()
            camera_props = animation_props.camera_orbit
            active_camera_name = camera_props.active_animation_camera

            # If there is an active camera selected in the selector, use it directly
            if active_camera_name and active_camera_name != "None":
                active_cam = bpy.data.objects.get(active_camera_name)
                if active_cam:
                    print(f"🎥 Using active camera from selector: {active_camera_name}")
                    self.camera_action = 'UPDATE'
                    return self.execute(context)
        except Exception as e:
            print(f"[WARNING] Error checking active camera: {e}")

        # FALLBACK: Search for any existing 4D camera and use the first one available
        existing_cam = next((obj for obj in bpy.data.objects if "4D_Animation_Camera" in obj.name), None)

        if existing_cam:
            # If it finds a camera but there is no active one in the selector, use the first one without a window
            print(f"🎥 No active camera in selector, using first available: {existing_cam.name}")
            self.camera_action = 'UPDATE'
            return self.execute(context)
        else:
            # If there are no cameras, create a new one (first time)
            print("🎥 No cameras found, creating new camera")
            self.camera_action = 'CREATE_NEW'
            return self.execute(context)

    def draw(self, context):
        # Draws the options in the popup dialog. # pyright: ignore[reportUnusedFunction]
        layout = self.layout
        layout.label(text="An existing 4D camera was found.")
        layout.label(text="What would you like to do with the camera?")
        layout.prop(self, "camera_action", expand=True)


class SelectWorkScheduleProducts(bpy.types.Operator):
    bl_idname = "bim.select_work_schedule_products"
    bl_label = "Select Work Schedule Products"
    bl_options = {"REGISTER", "UNDO"}
    work_schedule: bpy.props.IntProperty()

    def execute(self, context):
        try:
            work_schedule = tool.Ifc.get().by_id(self.work_schedule)
            if not work_schedule:
                self.report({'ERROR'}, "Work schedule not found")
                return {'CANCELLED'}

            # Use the corrected function from sequence
            result = tool.Sequence.select_work_schedule_products(work_schedule)

            if isinstance(result, str):
                if "Error" in result:
                    self.report({'ERROR'}, result)
                    return {'CANCELLED'}
                else:
                    self.report({'INFO'}, result)

            return {"FINISHED"}

        except Exception as e:
            self.report({'ERROR'}, f"Failed to select work schedule products: {str(e)}")
            return {'CANCELLED'}


class SelectUnassignedWorkScheduleProducts(bpy.types.Operator):
    bl_idname = "bim.select_unassigned_work_schedule_products"
    bl_label = "Select Unassigned Work Schedule Products"
    bl_options = {"REGISTER", "UNDO"}
    work_schedule: bpy.props.IntProperty()

    def execute(self, context):
        try:
            # Use the corrected function from sequence
            result = tool.Sequence.select_unassigned_work_schedule_products()

            if isinstance(result, str):
                if "Error" in result:
                    self.report({'ERROR'}, result)
                    return {'CANCELLED'}
                else:
                    self.report({'INFO'}, result)

            return {"FINISHED"}

        except Exception as e:
            self.report({'ERROR'}, f"Failed to select unassigned products: {str(e)}")
            return {'CANCELLED'}
