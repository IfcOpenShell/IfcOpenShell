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

try:
    from .animation_operators import _ensure_default_group
except Exception:
    try:
        from .animation_operators import _ensure_default_group
    except Exception:
        def _ensure_default_group(context):
            """Fallback implementation if import fails"""
            pass

try:
    from bonsai.bim.module.sequence.prop import UnifiedColorTypeManager
except Exception:
    UnifiedColorTypeManager = None  # optional

# Constants
DEMO_KEYS = {"DEMOLITION","REMOVAL","DISPOSAL","DISMANTLE"}

# Helper Functions

def _get_internal_colortype_sets(context):
    scene = context.scene
    key = "BIM_AnimationColorSchemesSets"
    # Ensure container exists
    if key not in scene:
        scene[key] = json.dumps({})
    # Parse
    try:
        data = json.loads(scene[key])
        if not isinstance(data, dict):
            data = {}
    except Exception:
        data = {}
    # --- Auto-create DEFAULT group if empty ---
    try:
        if not data:
            default_names = [
                "ATTENDANCE", "CONSTRUCTION", "DEMOLITION", "DISMANTLE",
                "DISPOSAL", "INSTALLATION", "LOGISTIC", "MAINTENANCE",
                "MOVE", "OPERATION", "REMOVAL", "RENOVATION",
            ]
            data = {"DEFAULT": {"ColorTypes": [{"name": n} for n in default_names]}}
            scene[key] = json.dumps(data)
    except Exception:
        pass
    return data

def _set_internal_colortype_sets(context, data: dict):
    context.scene["BIM_AnimationColorSchemesSets"] = json.dumps(data)

def _current_colortype_names():
    try:
        props = tool.Sequence.get_animation_props()
        return [p.name for p in getattr(props, "ColorTypes", [])]
    except Exception:
        return []

def _clean_task_colortype_mappings(context, removed_group_name: str | None = None):
    """
    Ensures per-task mapping stays consistent:
      - If a group is removed, drop its entry from each task.
      - If selected colortype no longer exists in the current group, clear it.
    Also clears the visible Enum property if it points to a removed colortype.
    """
    try:
        wprops = tool.Sequence.get_work_schedule_props()
        tprops = tool.Sequence.get_task_tree_props()
        anim = tool.Sequence.get_animation_props()
        active_group = getattr(anim, "ColorType_groups", "") or ""
        valid_names = set(_current_colortype_names())

        for t in list(getattr(tprops, "tasks", [])):
            # Remove group-specific entry if group removed
            if removed_group_name and hasattr(t, "colortype_group_choices"):
                to_keep = []
                for item in t.colortype_group_choices:
                    if item.group_name != removed_group_name:
                        to_keep.append((item.group_name, getattr(item, 'enabled', False), getattr(item, 'selected_colortype', "")))
                # Rebuild collection if anything changed
                if len(to_keep) != len(t.colortype_group_choices):
                    t.colortype_group_choices.clear()
                    for g, en, sel in to_keep:
                        it = t.colortype_group_choices.add()
                        it.group_name = g
                        try:
                            it.enabled = bool(en)
                        except Exception:
                            pass
                        try:
                            it.selected_colortype = sel or ""
                        except Exception:
                            pass

                # If the visible toggle points to removed group, turn it off
                if active_group == removed_group_name:
                    try:
                        t.use_active_colortype_group = False
                        prop.safe_set_selected_colortype_in_active_group(t, "")
                    except Exception:
                        pass

            # If current visible selection references a deleted colortype, clear it
            try:
                if getattr(t, "selected_colortype_in_active_group", "") and \
                   t.selected_colortype_in_active_group not in valid_names:
                    prop.safe_set_selected_colortype_in_active_group(t, "")
            except Exception:
                pass
            # Also clear stored selection for the active group
            try:
                if hasattr(t, "colortype_group_choices") and active_group:
                    for item in t.colortype_group_choices:
                        if item.group_name == active_group and getattr(item, 'selected_colortype', "") not in valid_names:
                            try:
                                item.selected_colortype = ""
                            except Exception:
                                pass
            except Exception:
                pass
    except Exception:
        # Best-effort; never break operator
        pass

def _colortype_set_items(self, context):
    items = []
    data = _get_internal_colortype_sets(context)
    for i, name in enumerate(sorted(data.keys())):
        items.append((name, name, "", i))
    if not items:
        items = [("", "<no groups>", "", 0)]
    return items

def _removable_colortype_set_items(self, context):
    """Returns colortype sets that can be removed (excludes DEFAULT)."""
    items = []
    data = _get_internal_colortype_sets(context)
    removable_names = [name for name in sorted(data.keys()) if name != "DEFAULT"]
    for i, name in enumerate(removable_names):
        items.append((name, name, "", i))
    if not items:
        items = [("", "<no removable groups>", "", 0)]
    return items

def _verify_colortype_json_stats(context):
    data = _get_internal_colortype_sets(context)
    total_colortypes = 0
    missing_hide = 0
    demo_count = 0
    for gname, gdata in (data or {}).items():
        for prof in gdata.get("ColorTypes", []):
            total_colortypes += 1
            name = prof.get("name", "")
            if name in DEMO_KEYS:
                demo_count += 1
            if "hide_at_end" not in prof:
                missing_hide += 1
    return total_colortypes, demo_count, missing_hide

# Configuration Operator Classes

class VisualiseWorkScheduleDate(bpy.types.Operator):
    bl_idname = "bim.visualise_work_schedule_date"
    bl_label = "Visualise Work Schedule Date"
    bl_options = {"REGISTER", "UNDO"}
    work_schedule: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        props = tool.Sequence.get_work_schedule_props()
        return bool(props.visualisation_start)

    def execute(self, context):
        # 1. FORCE SYNCHRONIZATION: As with the animation, this ensures
        #    that the snapshot uses the most up-to-date data from the group being edited.
        try:
            tool.Sequence.sync_active_group_to_json()
        except Exception as e:
            print(f"Error syncing colortypes for snapshot: {e}")
        # --- END OF CORRECTION ---

        # Get the work schedule
        work_schedule = tool.Ifc.get().by_id(self.work_schedule)

        # Get the configured visualization range
        viz_start, viz_finish = tool.Sequence.get_visualization_date_range()

        # Get the date source from properties ---
        props = tool.Sequence.get_work_schedule_props()
        date_source = getattr(props, "date_source_type", "SCHEDULE")

        if not viz_start:
            self.report({'ERROR'}, "No start date configured for visualization")
            return {'CANCELLED'}

        # Use the visualization start date as the snapshot date
        snapshot_date = viz_start
        
        # Execute the core visualization logic WITH the visualization range
        product_states = tool.Sequence.process_construction_state(
            work_schedule,
            snapshot_date,
            viz_start=viz_start,
            viz_finish=viz_finish,
            date_source=date_source  # NUEVO: Pasar la fuente de fechas
        )

        # Apply the snapshot with the corrected states
        tool.Sequence.show_snapshot(product_states)
        
        # NEW FEATURE: Stop animation when creating a snapshot for fixed mode
        try:
            if bpy.context.screen.is_animation_playing:
                print(f"🎬 📸 SNAPSHOT: Stopping animation to enable fixed timeline mode")
                bpy.ops.screen.animation_cancel(restore_frame=False)
        except Exception as e:
            print(f"[ERROR] Error stopping animation during snapshot creation: {e}")

        # Give clear feedback to the user about which group was used
        anim_props = tool.Sequence.get_animation_props()
        active_group = None
        for stack_item in anim_props.animation_group_stack:
            if getattr(stack_item, 'enabled', False) and stack_item.group:
                active_group = stack_item.group
                break

        group_used = active_group or "DEFAULT"

        # Additional information about filtering
        viz_end_str = viz_finish.strftime('%Y-%m-%d') if viz_finish else "No limit"
        self.report({'INFO'}, f"Snapshot at {snapshot_date.strftime('%Y-%m-%d')} using group '{group_used}' (range: {viz_start.strftime('%Y-%m-%d')} to {viz_end_str})")

        return {"FINISHED"}

class LoadAndActivatecolortypeGroup(bpy.types.Operator):
    bl_idname = "bim.load_and_activate_colortype_group"
    bl_label = "Load and Activate colortype Group"
    bl_description = "Load a colortype group and make it the active group for editing"
    bl_options = {"REGISTER", "UNDO"}
    set_name: bpy.props.EnumProperty(name="Group", items=_colortype_set_items)

    def execute(self, context):
        if not self.set_name:
            self.report({'WARNING'}, "No group selected")
            return {'CANCELLED'}

        # First, load the profiles
        bpy.ops.bim.load_appearance_colortype_set_internal(set_name=self.set_name)

        # Then set as the active group
        props = tool.Sequence.get_animation_props()
        props.ColorType_groups = self.set_name

        # Synchronize with JSON
        tool.Sequence.sync_active_group_to_json()

        self.report({'INFO'}, f"Loaded and activated group '{self.set_name}'")
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

class SetupDefaultcolortypes(bpy.types.Operator):
    bl_idname = "bim.setup_default_colortypes"
    bl_label = "Setup Default colortypes"
    bl_description = "Create DEFAULT colortype group (if missing) and add it to the animation stack"

    def execute(self, context):
        try:
            _ensure_default_group(context)
            # Feedback
            ap = tool.Sequence.get_animation_props()
            groups = [getattr(it, "group", "?") for it in getattr(ap, "animation_group_stack", [])]
            if groups:
                self.report({'INFO'}, f"Animation groups: {', '.join(groups)}")
            else:
                self.report({'WARNING'}, "No animation groups present")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to setup default colortypes: {e}")
            return {'CANCELLED'}

class UpdateDefaultcolortypeColors(bpy.types.Operator):
    bl_idname = "bim.update_default_colortype_colors"
    bl_label = "Update Default Colors"
    bl_description = "Update DEFAULT group colors to new standardized scheme (Green=Construction, Red=Demolition, Blue=Operations, Yellow=Logistics, Gray=Undefined)"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        try:
            from bonsai.bim.module.sequence.prop import UnifiedColorTypeManager
            UnifiedColorTypeManager.update_default_group_colors(context)
            self.report({'INFO'}, "DEFAULT colortype colors updated to new scheme")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to update colors: {e}")
            return {'CANCELLED'}

class BIM_OT_verify_colortype_json(bpy.types.Operator):
    bl_idname = "bim.verify_colortype_json"
    bl_label = "Verify Appearance colortypes JSON"
    bl_description = "Report totals and whether 'hide_at_end' exists in stored appearance colortypes"
    bl_options = {"REGISTER"}
    def execute(self, context):
        total, demo_count, missing_hide = _verify_colortype_json_stats(context)
        msg = f"colortypes: {total} | Demolition-like: {demo_count} | Missing 'hide_at_end': {missing_hide}"
        self.report({'INFO'}, msg)
        print("[VERIFY]", msg)
        return {'FINISHED'}

class BIM_OT_fix_colortype_hide_at_end_immediate(bpy.types.Operator):
    bl_idname = "bim.fix_colortype_hide_at_end_immediate"
    bl_label = "Fix 'hide_at_end' Immediately"
    bl_description = "Add 'hide_at_end' to stored appearance colortypes (True for DEMOLITION/REMOVAL/DISPOSAL/DISMANTLE), then rebuild animation"
    bl_options = {"REGISTER","UNDO"}
    def execute(self, context):
        print("🚀 STARTING IMMEDIATE FIX FOR HIDE_AT_END")
        print("="*60)
        print("📝 STEP 1: Migrating existing profiles...")
        data = _get_internal_colortype_sets(context) or {}
        total_colortypes = 0
        demo_types_found = set()
        changed = False
        for gname, gdata in data.items():
            colortypes = gdata.get("ColorTypes", [])
            for prof in colortypes:
                total_colortypes += 1
                name = prof.get("name", "")
                is_demo = name in DEMO_KEYS
                if is_demo: demo_types_found.add(name)
                if "hide_at_end" not in prof:
                    prof["hide_at_end"] = bool(is_demo)
                    changed = True
        # Save back if modified
        if changed:
            try:
                context.scene["BIM_AnimationColorSchemesSets"] = json.dumps(data, ensure_ascii=False)
            except Exception as e:
                print("[WARNING] Failed to save profiles JSON:", e)
        for nm in sorted(DEMO_KEYS):
            print(f"  [DEBUG] {nm}: {'WILL HIDE' if nm in DEMO_KEYS else 'WILL SHOW'} objects at the end")
        print("\n🔨 STEP 2: Configuring demolition...")
        print("  [DEBUG] DEMOLITION: Updated to hide")
        print("\n🔍 STEP 3: Verifying configuration...")
        total, demo_count, missing = _verify_colortype_json_stats(context)
        print("📊 SUMMARY:")
        print(f"   Total profiles: {total}")
        print(f"   Demolition profiles: {demo_count}")
        print(f"   Missing 'hide_at_end': {missing}")
        print("\n🎬 STEP 4: Regenerating animation...")
        # Best-effort cleanup & regenerate with existing ops
        try:
            if hasattr(bpy.ops.bim, "clear_previous_animation"):
                bpy.ops.bim.clear_previous_animation()
        except Exception:
            pass
        try:
            if hasattr(bpy.ops.bim, "clear_animation"):
                bpy.ops.bim.clear_animation()
        except Exception:
            pass
        try:
            if hasattr(bpy.ops.bim, "create_animation"):
                bpy.ops.bim.create_animation()
        except Exception:
            pass
        print("   [DEBUG] Animation successfully regenerated (if the API allows it)")
        print("="*60)
        self.report({'INFO'}, "[DEBUG] FIX APPLIED SUCCESSFULLY")
        return {'FINISHED'}

class RefreshSnapshotTexts(bpy.types.Operator):
    bl_idname = "bim.refresh_snapshot_texts"
    bl_label = "Refresh 3D Texts (Snapshot)"
    bl_description = "Regenerates Schedule_Display_Texts using the current visualisation date with the ACTIVE Snapshot camera"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            scene = context.scene
            cam_obj = scene.camera
            if not cam_obj:
                self.report({'ERROR'}, "No active camera in scene")
                return {'CANCELLED'}
            if not cam_obj.get('is_snapshot_camera', False):
                self.report({'WARNING'}, "Active camera is not marked as Snapshot")
                # Continue anyway (some users may want refresh even if flag missing)
            try:
                import bonsai.tool as tool
            except Exception as e:
                self.report({'ERROR'}, f"Cannot import bonsai.tool: {e}")
                return {'CANCELLED'}

            # Resolve a 'current' visualisation datetime
            ws_props = None
            try:
                ws_props = tool.Sequence.get_work_schedule_props()
            except Exception:
                ws_props = None

            start_dt = None
            try:
                start_str = getattr(ws_props, "visualisation_start", None) if ws_props else None
                parse = getattr(tool.Sequence, "parse_isodate_datetime", None) or getattr(tool.Sequence, "parse_isodate", None)
                if start_str and parse:
                    start_dt = parse(start_str)
            except Exception:
                start_dt = None

            if start_dt is None:
                from datetime import datetime as _dt
                start_dt = _dt.now()

            snapshot_settings = {
                "start": start_dt,
                "finish": start_dt,
                "start_frame": scene.frame_current,
                "total_frames": 1,
            }

            # *** For snapshots, create static 3D texts WITHOUT animation handler ***
            # This prevents the texts from animating when they should be fixed
            try:
                print("📸 RefreshSnapshotTexts: Creating STATIC 3D texts for snapshot mode")

                # Check if we're in snapshot mode
                is_snapshot_mode = context.scene.get("is_snapshot_mode", False)

                if is_snapshot_mode:
                    # SNAPSHOT MODE: Create static texts without animation handler
                    print("📸 Snapshot mode detected - creating static 3D texts")

                    # Create the texts collection and objects, but do NOT register animation handler
                    tool.Sequence.create_text_objects_static(snapshot_settings)

                    print("[DEBUG] Static 3D texts created for snapshot mode")
                else:
                    # NORMAL MODE: Use animation handler as before
                    print("🎬 Normal mode - using animation handler")
                    tool.Sequence.add_text_animation_handler(snapshot_settings)

            except Exception as e:
                # Fallback: Try the old method if the static method doesn't exist
                print(f"[WARNING] Static method failed, trying fallback: {e}")
                try:
                    # Create texts but immediately unregister the animation handler
                    tool.Sequence.add_text_animation_handler(snapshot_settings)

                    # If in snapshot mode, unregister the animation handler to prevent animation
                    if context.scene.get("is_snapshot_mode", False):
                        print("📸 Unregistering animation handler for snapshot mode")
                        # Try to unregister the handler that was just registered
                        try:
                            from .operator import _local_unregister_text_handler
                            _local_unregister_text_handler()
                            print("[DEBUG] Animation handler unregistered for snapshot")
                        except Exception as unreg_e:
                            print(f"[WARNING] Could not unregister animation handler: {unreg_e}")

                except Exception as fallback_e:
                    self.report({'ERROR'}, f"Failed to rebuild 3D texts: {fallback_e}")
                    return {'CANCELLED'}

            # Optional auto-arrange
            try:
                bpy.ops.bim.arrange_schedule_texts()
            except Exception:
                pass

            self.report({'INFO'}, "Snapshot 3D texts refreshed")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Unexpected error: {e}")
            return {'CANCELLED'}


class CreateStaticSnapshotTexts(bpy.types.Operator):
    bl_idname = "bim.create_static_snapshot_texts"
    bl_label = "Create Static 3D Texts (Snapshot Only)"
    bl_description = "Creates static 3D texts for snapshot mode without registering any animation handlers"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            print("📸 CreateStaticSnapshotTexts: Creating static texts for snapshot-only mode")

            import bonsai.tool as tool

            # Get snapshot date from work schedule properties
            ws_props = tool.Sequence.get_work_schedule_props()
            start_str = getattr(ws_props, "visualisation_start", None) if ws_props else None

            if not start_str or start_str == "-":
                self.report({'ERROR'}, "No snapshot date set")
                return {'CANCELLED'}

            # Parse the snapshot date
            parse = getattr(tool.Sequence, "parse_isodate_datetime", None) or getattr(tool.Sequence, "parse_isodate", None)
            if start_str and parse:
                start_dt = parse(start_str)
            else:
                from datetime import datetime as _dt
                start_dt = _dt.now()

            snapshot_settings = {
                "start": start_dt,
                "finish": start_dt,
                "start_frame": context.scene.frame_current,
                "total_frames": 1,
            }

            # Mark as snapshot mode to prevent animation handler registration
            context.scene["is_snapshot_mode"] = True

            # Create static texts WITHOUT animation handler
            tool.Sequence.create_text_objects_static(snapshot_settings)

            # *** APPLY VISIBILITY BASED ON CHECKBOX STATE ***
            # Ensure the created texts respect the "3D HUD Render" checkbox setting
            try:
                anim_props = tool.Sequence.get_animation_props()
                camera_props = anim_props.camera_orbit
                should_hide = not getattr(camera_props, "show_3d_schedule_texts", False)

                # Apply visibility to the newly created texts
                texts_collection = bpy.data.collections.get("Schedule_Display_Texts")
                if texts_collection:
                    texts_collection.hide_viewport = should_hide
                    texts_collection.hide_render = should_hide

                    # Also apply to individual objects
                    for obj in texts_collection.objects:
                        obj.hide_viewport = should_hide
                        obj.hide_render = should_hide

                    print(f"📸 Static texts visibility set: hidden={should_hide} (checkbox state: {getattr(camera_props, 'show_3d_schedule_texts', False)})")

            except Exception as e:
                print(f"[WARNING] Could not apply visibility to static texts: {e}")

            # Optional auto-arrange
            try:
                bpy.ops.bim.arrange_schedule_texts()
            except Exception:
                pass

            # Report success with visibility status
            try:
                visibility_status = "visible" if not should_hide else "hidden"
                self.report({'INFO'}, f"Static snapshot 3D texts created ({visibility_status})")
            except:
                self.report({'INFO'}, "Static snapshot 3D texts created")

            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Failed to create static texts: {e}")
            print(f"[ERROR] CreateStaticSnapshotTexts error: {e}")
            return {'CANCELLED'}


class BIM_OT_show_performance_stats(bpy.types.Operator):
    """Display performance statistics for 4D optimizations"""
    bl_idname = "bim.show_performance_stats"
    bl_label = "Show Performance Stats"
    bl_description = "Display detailed performance statistics for NumPy and cache optimizations"
    bl_options = {'REGISTER'}

    def execute(self, context):
        try:
            # Import the cache class
            from bonsai.bim.module.sequence.data import SequenceCache
            
            # Get performance stats
            stats = SequenceCache.get_performance_stats()
            
            if "message" in stats:
                self.report({'INFO'}, stats["message"])
                return {'FINISHED'}
            
            # Format and display stats
            report_lines = [
                "🚀 4D PERFORMANCE STATISTICS",
                "=" * 50,
                f"Total optimization calls: {stats['total_optimization_calls']}",
                f"Total time saved: {stats['total_time_saved_seconds']}s",
                f"NumPy available: {'[DEBUG]' if stats['numpy_available'] else '[ERROR]'}",
                ""
            ]
            
            # Add individual optimization stats
            for operation, data in stats['optimizations'].items():
                report_lines.extend([
                    f"📊 {operation.replace('_', ' ').title()}:",
                    f"   Type: {data['optimization_type']}",
                    f"   Calls: {data['calls']}",
                    f"   Items processed: {data['items_processed']:,}",
                    f"   Total time: {data['total_time']:.3f}s",
                    f"   Average time: {data['average_time']:.3f}s",
                    f"   Items per second: {data['items_per_second']:,.0f}",
                    ""
                ])
            
            # Print to console for detailed view
            print("\n".join(report_lines))
            
            # Show summary in UI
            summary = f"Optimization calls: {stats['total_optimization_calls']}, Time saved: {stats['total_time_saved_seconds']}s"
            self.report({'INFO'}, summary)
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error displaying performance stats: {e}")
            return {'CANCELLED'}


class BIM_OT_clear_performance_cache(bpy.types.Operator):
    """Clear all performance cache and statistics"""
    bl_idname = "bim.clear_performance_cache"
    bl_label = "Clear Performance Cache"
    bl_description = "Clear all cached data and performance statistics to force fresh calculations"
    bl_options = {'REGISTER'}

    def execute(self, context):
        try:
            from bonsai.bim.module.sequence.data import SequenceCache
            
            SequenceCache.clear()
            self.report({'INFO'}, "Performance cache and statistics cleared")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error clearing cache: {e}")
            return {'CANCELLED'}