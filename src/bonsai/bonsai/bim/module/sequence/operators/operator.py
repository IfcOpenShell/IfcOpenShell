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

import os
import time
import isodate
import bonsai.core.sequence as core
import bonsai.bim.module.sequence.utils.helper_utils as helper
try:
    from .animation_operators import _clear_previous_animation, _get_animation_settings, _compute_product_frames, _ensure_default_group
except ImportError:
    # Fallback functions
    def _clear_previous_animation(context):
        pass
    def _get_animation_settings(context):
        return {}
    def _compute_product_frames(context, work_schedule, settings):
        return []
    def _ensure_default_group(context):
        pass
try:
    from bonsai.bim.module.sequence.prop import UnifiedColorTypeManager
except Exception:
    UnifiedColorTypeManager = None  # optional
try:
    from ..prop import TaskcolortypeGroupChoice
except Exception:
    try:
        from bonsai.bim.module.sequence.prop import TaskcolortypeGroupChoice
    except Exception:
        TaskcolortypeGroupChoice = None  # optional

import ifcopenshell.util.sequence
import ifcopenshell.util.selector
from datetime import datetime
from dateutil import parser, relativedelta
from bpy_extras.io_utils import ImportHelper, ExportHelper

# === Local handler to keep schedule texts in sync with the chosen date range ===
_LOCAL_TEXT_HANDLER = None

def _parse_dt_any(v):
    """Parse 'YYYY-MM-DD' or ISO-like strings to datetime (no external deps)."""
    try:
        # Accept datetime/date objects
        if hasattr(v, 'year') and hasattr(v, 'month') and hasattr(v, 'day'):
            from datetime import datetime as _dt
            # If it's already datetime-like, normalize to datetime
            if hasattr(v, 'hour'):
                return v
            return _dt(v.year, v.month, v.day)
        s = str(v).strip()
        if not s:
            return None
        from datetime import datetime as _dt
        # Full datetime
        try:
            return _dt.fromisoformat(s.replace('Z',''))
        except Exception:
            pass
        # Date-only
        try:
            return _dt.fromisoformat(s.split('T')[0])
        except Exception:
            return None
    except Exception:
        return None

# REMOVED: Duplicate calculate_schedule_metrics function - using unified version below

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

def _local_schedule_texts_update_handler(scene, depsgraph):
    '''Update schedule text objects each frame. Week/Day/Progress use the same robust logic as HUD Schedule.'''
    print("🎬 3D Text Handler: Starting update...")
    try:

        coll = bpy.data.collections.get("Schedule_Display_Texts")
        if not coll:
            print("[WARNING] 3D Text Handler: No 'Schedule_Display_Texts' collection found")
            return
        
        print(f"📝 3D Text Handler: Found collection with {len(coll.objects)} objects")
        
        # CHECK FOR SNAPSHOT MODE
        snapshot_mode = False
        snapshot_date = None
        
        # Check if there's a snapshot date stored in scene properties
        if hasattr(scene, 'BIMWorkPlanProperties'):
            ws_props = tool.Sequence.get_work_schedule_props()
            snapshot_date_str = getattr(ws_props, "visualisation_start", None)
            
            # Check if we're in snapshot mode (same start and finish date, or specific snapshot flag)
            finish_date_str = getattr(ws_props, "visualisation_finish", None)
            
            if (snapshot_date_str and snapshot_date_str != "-" and 
                ((finish_date_str and finish_date_str == snapshot_date_str) or 
                 scene.get("is_snapshot_mode", False))):
                
                try:
                    snapshot_date = tool.Sequence.parse_isodate_datetime(snapshot_date_str)
                    if snapshot_date:
                        snapshot_mode = True
                        print(f"📸 3D Text Handler: SNAPSHOT MODE detected for date {snapshot_date.strftime('%Y-%m-%d')}")
                except Exception as e:
                    print(f"[WARNING] 3D Text Handler: Error parsing snapshot date: {e}")
        
        if snapshot_mode and snapshot_date:
            # SNAPSHOT MODE: Use fixed date, ignore frame-based calculation
            cur_dt = snapshot_date
            print(f"📸 Using snapshot date: {cur_dt.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            # ANIMATION MODE: Use frame-based calculation as before
            cur_frame = int(scene.frame_current)
            for obj in list(coll.objects):
                cdata = getattr(obj, "data", None)
                if not cdata:
                    continue
                meta = dict(cdata.get("animation_settings", {})) or {}
                start_frame = int(meta.get("start_frame", scene.frame_start))
                total_frames = int(meta.get("total_frames", max(1, scene.frame_end - scene.frame_start)))
                if total_frames <= 0:
                    total_frames = 1
                # Normalized progress along the configured WINDOW
                prog = (cur_frame - start_frame) / float(total_frames)
                prog = max(0.0, min(1.0, prog))

                # Window dates for mapping frame -> current date
                wnd_start = _parse_dt_any(meta.get("start_date"))
                wnd_finish = _parse_dt_any(meta.get("finish_date"))
                cur_dt = None
                if wnd_start and wnd_finish:
                    try:
                        delta_w = (wnd_finish - wnd_start)
                        cur_dt = wnd_start + prog * delta_w
                    except Exception:
                        cur_dt = wnd_start
                        
                # Process this object with its calculated cur_dt
                _update_single_3d_text_object(obj, cdata, cur_dt)
                
            return  # Early return for animation mode
        
        # SNAPSHOT MODE: Process all objects with the same snapshot date
        for obj in list(coll.objects):
            cdata = getattr(obj, "data", None)
            if not cdata: 
                continue
            _update_single_3d_text_object(obj, cdata, cur_dt)
            
    except Exception as e:
        print(f"[ERROR] 3D Text Handler error: {e}")
        import traceback
        traceback.print_exc()

def _update_single_3d_text_object(obj, cdata, cur_dt):
    """Update a single 3D text object with the given current date"""
    try:
        
        # --- ROBUST METHOD TO GET THE FULL SCHEDULE RANGE (like Viewport HUD) ---
        sch_start, sch_finish = None, None
        try:
            active_schedule = tool.Sequence.get_active_work_schedule()
            if active_schedule:
                sch_start, sch_finish = tool.Sequence.get_schedule_date_range()
                if not (sch_start and sch_finish):
                    # Fallback to task-based date extraction
                    import ifcopenshell.util.sequence
                    tasks = ifcopenshell.util.sequence.get_root_tasks(active_schedule)
                    if tasks:
                        all_dates = []
                        for task in tasks:
                            task_time = getattr(task, 'TaskTime', None)
                            if task_time:
                                start = getattr(task_time, 'ScheduleStart', None)
                                finish = getattr(task_time, 'ScheduleFinish', None)
                                if start: all_dates.append(start)
                                if finish: all_dates.append(finish)
                        
                        if all_dates:
                            datetime_dates = [dt for dt in (_parse_dt_any(d) for d in all_dates) if dt]
                            if datetime_dates:
                                sch_start = min(datetime_dates)
                                sch_finish = max(datetime_dates)
        except Exception as e:
            print(f"Bonsai WARNING: Could not get full schedule range for 3D texts: {e}")
        
        # DEBUG: Log what we got
        if sch_start and sch_finish:
            print(f"📊 3D Texts: Using schedule range {sch_start.strftime('%Y-%m-%d')} → {sch_finish.strftime('%Y-%m-%d')}")
        else:
            print(f"[WARNING] 3D Texts: No schedule range available (sch_start={sch_start}, sch_finish={sch_finish})")

        ttype = (cdata.get("text_type") or "").lower()

        if ttype == "schedule_name":
            try:
                # For schedule_name, we need to get the meta from the object
                meta = dict(cdata.get("animation_settings", {})) or {}
                schedule_name = meta.get("schedule_name", "No Schedule")
                cdata.body = f"Schedule: {schedule_name}"
            except Exception:
                cdata.body = "Schedule: --"
        elif ttype == "date":
            if cur_dt:
                try:
                    cdata.body = cur_dt.strftime("%d/%m/%Y")
                except Exception:
                    cdata.body = str(cur_dt).split("T")[0]

        elif ttype == "week":
            try:
                print(f"🔍 Week text: cur_dt={cur_dt}, sch_start={sch_start}, sch_finish={sch_finish}")
                if cur_dt and sch_start and sch_finish:
                    # Use the same robust logic as HUD Schedule
                    cd_d = cur_dt.date()
                    fss_d = sch_start.date() 
                    fse_d = sch_finish.date()
                    delta_days = (cd_d - fss_d).days
                    
                    if cd_d < fss_d:
                        week_number = 0
                    else:
                        week_number = max(1, (delta_days // 7) + 1)
                    
                    print(f"📊 Week calculation: current={cd_d}, start={fss_d}, delta_days={delta_days}, week={week_number}")
                    cdata.body = f"Week {week_number}"
                else:
                    print(f"[WARNING] Week text: Missing data, showing fallback")
                    cdata.body = "Week --"
            except Exception as e:
                print(f"[ERROR] Week text error: {e}")
                cdata.body = "Week --"

        elif ttype == "day_counter":
            try:
                print(f"🔍 Day text: cur_dt={cur_dt}, sch_start={sch_start}, sch_finish={sch_finish}")
                if cur_dt and sch_start and sch_finish:
                    # Use the same robust logic as HUD Schedule
                    cd_d = cur_dt.date()
                    fss_d = sch_start.date()
                    delta_days = (cd_d - fss_d).days
                    
                    if cd_d < fss_d:
                        day_from_schedule = 0
                    else:
                        day_from_schedule = max(1, delta_days + 1)
                    
                    print(f"📊 Day calculation: current={cd_d}, start={fss_d}, delta_days={delta_days}, day={day_from_schedule}")
                    cdata.body = f"Day {day_from_schedule}"
                else:
                    print(f"[WARNING] Day text: Missing data, showing fallback")
                    cdata.body = "Day --"
            except Exception as e:
                print(f"[ERROR] Day text error: {e}")
                cdata.body = "Day --"

        elif ttype == "progress":
            try:
                print(f"🔍 Progress text: cur_dt={cur_dt}, sch_start={sch_start}, sch_finish={sch_finish}")
                if cur_dt and sch_start and sch_finish:
                    # Use the same robust logic as HUD Schedule
                    cd_d = cur_dt.date()
                    fss_d = sch_start.date()
                    fse_d = sch_finish.date()
                    
                    if cd_d < fss_d:
                        progress_pct = 0
                    elif cd_d >= fse_d:
                        progress_pct = 100
                    else:
                        total_schedule_days = (fse_d - fss_d).days
                        if total_schedule_days <= 0:
                            progress_pct = 100
                        else:
                            delta_days = (cd_d - fss_d).days
                            progress_pct = (delta_days / total_schedule_days) * 100
                            progress_pct = round(progress_pct)
                            progress_pct = max(0, min(100, progress_pct))
                    
                    print(f"📊 Progress calculation: current={cd_d}, start={fss_d}, end={fse_d}, progress={progress_pct}%")
                    cdata.body = f"Progress: {progress_pct}%"
                else:
                    # Fallback: show percentage based on time
                    print(f"[WARNING] Progress text: Missing schedule data, showing fallback")
                    cdata.body = "Progress: --%"
            except Exception as e:
                print(f"[ERROR] Progress text error: {e}")
                cdata.body = "Progress: --%"
                
    except Exception as e:
        print(f"[ERROR] Error updating 3D text object: {e}")
    except Exception:
        pass

def _local_unregister_text_handler():
    global _LOCAL_TEXT_HANDLER
    try:

        if _LOCAL_TEXT_HANDLER and _LOCAL_TEXT_HANDLER in bpy.app.handlers.frame_change_post:
            bpy.app.handlers.frame_change_post.remove(_LOCAL_TEXT_HANDLER)
    except Exception:
        pass

def _local_register_text_handler(settings=None):
    """Register fallback handler once, attach settings to known text objects if passed."""
    global _LOCAL_TEXT_HANDLER
    try:
        _local_unregister_text_handler()
    except Exception:
        pass
    try:

        coll = bpy.data.collections.get("Schedule_Display_Texts")
        if coll and settings is not None:
            for obj in list(coll.objects):
                _ensure_local_text_settings_on_obj(obj, settings)
    except Exception:
        pass
    _LOCAL_TEXT_HANDLER = _local_schedule_texts_update_handler
    try:
        if _LOCAL_TEXT_HANDLER not in bpy.app.handlers.frame_change_post:
            bpy.app.handlers.frame_change_post.append(_LOCAL_TEXT_HANDLER)
        # Immediate refresh
        _LOCAL_TEXT_HANDLER(bpy.context.scene, None)
    except Exception:
        pass

def _unified_register_text_handler(settings=None):
    ok = False
    try:
        if hasattr(tool.Sequence, "_register_multi_text_handler"):
            tool.Sequence._register_multi_text_handler(settings)
            ok = True
    except Exception:
        ok = False
    if not ok:
        _local_register_text_handler(settings)

def _infer_schedule_date_range(work_schedule):
    '''Infer earliest start and latest finish across tasks of the given work_schedule.'''
    try:
        import ifcopenshell
    except Exception:
        return None, None
    try:
        tasks = []
        try:
            if getattr(work_schedule, "Controls", None):
                for rel in work_schedule.Controls:
                    for ob in getattr(rel, "RelatedObjects", []) or []:
                        if hasattr(ob, "is_a") and ob.is_a("IfcTask"):
                            tasks.append(ob)
        except Exception:
            pass
        if not tasks:
            try:
                file = work_schedule.wrapped_data.file
                tasks = [t for t in file.by_type("IfcTask")]
            except Exception:
                tasks = []
        earliest = None
        latest = None
        for t in tasks:
            tt = getattr(t, "TaskTime", None) or getattr(t, "Time", None)
            if not tt:
                continue
            start_raw = None
            finish_raw = None
            for k in ("ActualStart","ScheduleStart","EarlyStart","LateStart","StartTime","Start"):
                if hasattr(tt, k) and getattr(tt, k):
                    start_raw = getattr(tt, k); break
            for k in ("ActualFinish","ScheduleFinish","EarlyFinish","LateFinish","FinishTime","Finish"):
                if hasattr(tt, k) and getattr(tt, k):
                    finish_raw = getattr(tt, k); break
            s = _parse_dt_any(start_raw)
            f = _parse_dt_any(finish_raw)
            if s:
                earliest = s if earliest is None else min(earliest, s)
            if f:
                latest = f if latest is None else max(latest, f)
        return earliest, latest
    except Exception:
        return None, None

from typing import get_args, TYPE_CHECKING, assert_never

# --- Lazy Enum items providers to avoid circular import with bonsai.tool ---

# ---- Unified Animation Bridges ----




def snapshot_all_ui_state(context):
    """
    (SNAPSHOT) Captures the complete state of the profiles UI and saves it
    in temporary scene properties. It also maintains a persistent cache
    to support filter toggling (filter -> unfilter)
    without losing data from hidden tasks.
    """
    import json
    try:
        # 1. Snapshot of the profile configuration per task
        tprops = tool.Sequence.get_task_tree_props()
        task_snap = {}
        
        # NEW: Also capture data from all tasks of the active schedule
        # to avoid data loss when filters are applied/removed
        try:
            ws = tool.Sequence.get_active_work_schedule()
            if ws:
                import ifcopenshell.util.sequence
                
                def get_all_tasks_recursive(tasks):
                    """Recursively gets all tasks and subtasks."""
                    all_tasks = []
                    for task in tasks:
                        all_tasks.append(task)
                        nested = ifcopenshell.util.sequence.get_nested_tasks(task)
                        if nested:
                            all_tasks.extend(get_all_tasks_recursive(nested))
                    return all_tasks
                
                root_tasks = ifcopenshell.util.sequence.get_root_tasks(ws)
                all_tasks = get_all_tasks_recursive(root_tasks)
                
                # Create a snapshot of all tasks, not just the visible ones
                task_id_to_ui_data = {str(getattr(t, "ifc_definition_id", 0)): t for t in getattr(tprops, "tasks", [])}
                
                for task in all_tasks:
                    tid = str(task.id())
                    if tid == "0":
                        continue
                    
                    # If the task is visible in the UI, use its current data
                    if tid in task_id_to_ui_data:
                        t = task_id_to_ui_data[tid]
                        groups_list = []
                        for g in getattr(t, "colortype_group_choices", []):
                            sel_attr = None
                            for cand in ("selected_colortype", "selected", "active_colortype", "colortype"):
                                if hasattr(g, cand):
                                    sel_attr = cand
                                    break
                            groups_list.append({
                                "group_name": getattr(g, "group_name", ""),
                                "enabled": bool(getattr(g, "enabled", False)),
                                "selected_value": getattr(g, sel_attr, "") if sel_attr else "",
                                "selected_attr": sel_attr or "",
                            })
                        task_snap[tid] = {
                            "active": bool(getattr(t, "use_active_colortype_group", False)),
                            "selected_active_colortype": getattr(t, "selected_colortype_in_active_group", ""),
                            "animation_color_schemes": getattr(t, "animation_color_schemes", ""),
                            "groups": groups_list,
                        }
                    else:
                        # If the task is not visible (filtered), preserve data from the cache
                        cache_key = "_task_colortype_snapshot_cache_json"
                        cache_raw = context.scene.get(cache_key)
                        if cache_raw:
                            try:
                                cached_data = json.loads(cache_raw)
                                if tid in cached_data:
                                    task_snap[tid] = cached_data[tid]
                                else:
                                    # Create an empty entry for tasks without previous data
                                    task_snap[tid] = {
                                        "active": False,
                                        "selected_active_colortype": "",
                                        "animation_color_schemes": "",
                                        "groups": [],
                                    }
                            except Exception:
                                task_snap[tid] = {
                                    "active": False,
                                    "selected_active_colortype": "",
                                    "animation_color_schemes": "",
                                    "groups": [],
                                }
                        else:
                            task_snap[tid] = {
                                "active": False,
                                "selected_active_colortype": "",
                                "animation_color_schemes": "",
                                "groups": [],
                            }
        except Exception as e:
            print(f"Bonsai WARNING: Error capturando todas las tasks: {e}")
            # Fallback to the original method with only visible tasks
            for t in getattr(tprops, "tasks", []):
                tid = str(getattr(t, "ifc_definition_id", 0))
                if tid == "0":
                    continue
                groups_list = []
                for g in getattr(t, "colortype_group_choices", []):
                    sel_attr = None
                    for cand in ("selected_colortype", "selected", "active_colortype", "colortype"):
                        if hasattr(g, cand):
                            sel_attr = cand
                            break
                    groups_list.append({
                        "group_name": getattr(g, "group_name", ""),
                        "enabled": bool(getattr(g, "enabled", False)),
                        "selected_value": getattr(g, sel_attr, "") if sel_attr else "",
                        "selected_attr": sel_attr or "",
                    })
                task_snap[tid] = {
                    "active": bool(getattr(t, "use_active_colortype_group", False)),
                    "selected_active_colortype": getattr(t, "selected_colortype_in_active_group", ""),
                    "animation_color_schemes": getattr(t, "animation_color_schemes", ""),
                    "groups": groups_list,
                }

        # Detect the active WorkSchedule to scope the cache
        try:
            ws_props = tool.Sequence.get_work_schedule_props()
            ws_id = int(getattr(ws_props, "active_work_schedule_id", 0))
        except Exception:
            try:
                ws = tool.Sequence.get_active_work_schedule()
                ws_id = int(getattr(ws, "id", 0) or getattr(ws, "GlobalId", 0) or 0)
            except Exception:
                ws_id = 0

        # Reset cache if the active WS changed
        cache_ws_key = "_task_colortype_snapshot_cache_ws_id"
        cache_key = "_task_colortype_snapshot_cache_json"
        prior_ws = context.scene.get(cache_ws_key)
        if prior_ws is None or int(prior_ws) != ws_id:
            context.scene[cache_key] = "{}"
            context.scene[cache_ws_key] = str(ws_id)

        # Save ephemeral snapshot (current cycle) - BOTH KEYS for compatibility
        snap_key_specific = f"_task_colortype_snapshot_json_WS_{ws_id}"
        snap_key_generic = "_task_colortype_snapshot_json"
        
        # Save to specific key (for Copy 3D)
        context.scene[snap_key_specific] = json.dumps(task_snap)
        print(f"[DEBUG] SNAPSHOT: Saved {len(task_snap)} tasks to {snap_key_specific}")

        # ALSO save to generic key (for normal system)
        context.scene[snap_key_generic] = json.dumps(task_snap)

        # Update persistent cache (merge)
        merged = {}
        cache_raw = context.scene.get(cache_key)
        if cache_raw:
            try:
                merged = json.loads(cache_raw) or {}
            except Exception:
                merged = {}
        merged.update(task_snap)
        context.scene[cache_key] = json.dumps(merged)
        print(f"[DEBUG] SNAPSHOT: Updated cache with {len(merged)} total tasks")

        # 2. Snapshot of group selectors and animation stack
        anim_props = tool.Sequence.get_animation_props()
        anim_snap = {
            "ColorType_groups": getattr(anim_props, "ColorType_groups", "DEFAULT"),
            "task_colortype_group_selector": getattr(anim_props, "task_colortype_group_selector", ""),
            "animation_group_stack": [
                {"group": getattr(item, "group", ""), "enabled": bool(getattr(item, "enabled", False))}
                for item in getattr(anim_props, "animation_group_stack", [])
            ],
        }
        context.scene["_anim_state_snapshot_json"] = json.dumps(anim_snap)
        # 3. Snapshot of active selection/index of the task tree
        try:
            wprops = tool.Sequence.get_work_schedule_props()
            tprops = tool.Sequence.get_task_tree_props()
            active_idx = int(getattr(wprops, 'active_task_index', -1))
            active_id = int(getattr(wprops, 'active_task_id', 0))
            selected_ids = []
            for t in getattr(tprops, 'tasks', []):
                tid = int(getattr(t, 'ifc_definition_id', 0))
                sel = False
                for cand in ('is_selected','selected'):
                    if hasattr(t, cand) and bool(getattr(t, cand)):
                        sel = True
                        break
                if sel:
                    selected_ids.append(tid)
            sel_snap = {'active_index': active_idx, 'active_id': active_id, 'selected_ids': selected_ids}
            context.scene['_task_selection_snapshot_json'] = json.dumps(sel_snap)
        except Exception:
            pass


    except Exception as e:
        print(f"Bonsai WARNING: Could not create UI snapshot: {e}")

def restore_animation_group_settings(context):
    """Restore only animation group stack and selectors, not individual task colortype assignments"""
    import json
    try:
        # Restore animation group settings from snapshot
        anim_snap_raw = context.scene.get("_anim_state_snapshot_json")
        if anim_snap_raw:
            try:
                anim_snap = json.loads(anim_snap_raw) or {}
                anim_props = tool.Sequence.get_animation_props()
                
                # Restore group selectors
                try:
                    anim_props.ColorType_groups = anim_snap.get("ColorType_groups", "DEFAULT")
                    anim_props.task_colortype_group_selector = anim_snap.get("task_colortype_group_selector", "")
                except Exception as e:
                    print(f"Warning: Could not restore group selectors: {e}")
                
                # Restore animation group stack
                try:
                    anim_props.animation_group_stack.clear()
                    for item_data in anim_snap.get("animation_group_stack", []):
                        item = anim_props.animation_group_stack.add()
                        item.group = item_data.get("group", "")
                        if hasattr(item, "enabled"):
                            item.enabled = bool(item_data.get("enabled", False))
                except Exception as e:
                    print(f"Warning: Could not restore animation group stack: {e}")
                    
            except Exception as e:
                print(f"Warning: Could not parse animation snapshot: {e}")
    except Exception as e:
        print(f"Error in restore_animation_group_settings: {e}")


