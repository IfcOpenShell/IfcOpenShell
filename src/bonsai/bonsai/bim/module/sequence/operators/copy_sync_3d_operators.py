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
import bonsai.tool as tool
from .. import hud as hud_overlay
from .operator import snapshot_all_ui_state
from .schedule_task_operators import restore_all_ui_state
from .schedule_task_operators import _save_3d_texts_state, _restore_3d_texts_state
from .animation_operators import _get_animation_settings, _compute_product_frames, _ensure_default_group

# Helper function to get camera enums, now local to this file
def _get_4d_cameras(self, context):
    """EnumProperty items callback: returns available 4D cameras."""
    try:
        items = []
        for obj in bpy.data.objects:
            if tool.Sequence.is_bonsai_camera(obj):
                items.append((obj.name, obj.name, '4D/Snapshot camera'))
        if not items:
            items = [('NONE', '<No cameras found>', 'No 4D or Snapshot cameras detected')]
        return items
    except Exception:
        return [('NONE', '<No cameras found>', 'No 4D or Snapshot cameras detected')]

# ============================================================================
# COPY & SYNC OPERATORS
# ============================================================================

class Copy3D(bpy.types.Operator):
    """Copy configuration from active schedule to other schedules with matching task indicators"""
    bl_idname = "bim.copy_3d"
    bl_label = "Copy 3D"
    bl_description = "Copy task elements, PredefinedType, and colortype settings from active schedule to matching schedules"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        snapshot_all_ui_state(context)
        try:
            ifc_file = tool.Ifc.get()
            if not ifc_file:
                self.report({'ERROR'}, "No IFC file loaded.")
                return {'CANCELLED'}
            
            active_schedule = tool.Sequence.get_active_work_schedule()
            if not active_schedule:
                self.report({'ERROR'}, "No active work schedule.")
                return {'CANCELLED'}

            result = tool.Sequence.copy_3d_configuration(active_schedule)
            
            if result.get("success", False):
                copied_count = result.get("copied_schedules", 0)
                task_matches = result.get("task_matches", 0)
                self.report({'INFO'}, f"Configuration copied to {copied_count} schedules ({task_matches} task matches)")
            else:
                error_msg = result.get("error", "Unknown error during copy operation")
                self.report({'ERROR'}, error_msg)
                return {'CANCELLED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"Copy 3D failed: {str(e)}")
            return {'CANCELLED'}
        finally:
            restore_all_ui_state(context)
        return {'FINISHED'}

class Sync3D(bpy.types.Operator):
    """Sync task elements based on IFC property set values"""
    bl_idname = "bim.sync_3d"
    bl_label = "Sync 3D"
    bl_description = "Automatically map IFC elements to tasks based on property set values"
    bl_options = {"REGISTER", "UNDO"}

    property_set_name: bpy.props.StringProperty(
        name="Property Set Name",
        description="Name of the property set to use for syncing",
        default=""
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "property_set_name")

    def execute(self, context):
        if not self.property_set_name.strip():
            self.report({'ERROR'}, "Property set name is required")
            return {'CANCELLED'}

        snapshot_all_ui_state(context)
        try:
            ifc_file = tool.Ifc.get()
            if not ifc_file:
                self.report({'ERROR'}, "No IFC file loaded.")
                return {'CANCELLED'}
            
            active_schedule = tool.Sequence.get_active_work_schedule()
            if not active_schedule:
                self.report({'ERROR'}, "No active work schedule.")
                return {'CANCELLED'}

            result = tool.Sequence.sync_3d_elements(active_schedule, self.property_set_name.strip())
            
            if result.get("success", False):
                matched_elements = result.get("matched_elements", 0)
                processed_tasks = result.get("processed_tasks", 0)
                self.report({'INFO'}, f"Synced {matched_elements} elements across {processed_tasks} tasks")
            else:
                error_msg = result.get("error", "Unknown error during sync operation")
                self.report({'ERROR'}, error_msg)
                return {'CANCELLED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"Sync 3D failed: {str(e)}")
            return {'CANCELLED'}
        finally:
            restore_all_ui_state(context)
        return {'FINISHED'}

class SnapshotWithcolortypes(tool.Ifc.Operator, bpy.types.Operator):
    bl_idname = "bim.snapshot_with_colortypes"
    bl_label = "Snapshot (colortypes)"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        from ..prop import UnifiedColorTypeManager
        _ensure_default_group(context)

        # AUTOFIX: Ensure variance system is clean before creating snapshot
        try:
            tool.Sequence.detect_and_fix_variance_inconsistency()
        except Exception as e:
            print(f"[WARNING] Could not run variance autofix before snapshot: {e}")

        # SPECIFIC FIX: Clear any active variance colors from 3D objects
        try:
            cleared_variance_colors = tool.Sequence.detect_and_clear_active_variance_colors()
            if cleared_variance_colors:
                print("[SNAPSHOT] Cleared active variance colors to prevent color system conflicts")
        except Exception as e:
            print(f"[WARNING] Could not clear variance colors before snapshot: {e}")

        # Save UI state before applying snapshot
        try:
            snapshot_all_ui_state(context)
        except Exception as e:
            import traceback
            traceback.print_exc()

        try:
            ws_props = tool.Sequence.get_work_schedule_props()
            anim_props = tool.Sequence.get_animation_props()

            ws_id = getattr(ws_props, "active_work_schedule_id", None)
            if not ws_id:
                self.report({'ERROR'}, "No active Work Schedule selected.")
                return {'CANCELLED'}
            work_schedule = tool.Ifc.get().by_id(ws_id)
            if not work_schedule:
                self.report({'ERROR'}, "Active Work Schedule not found in IFC.")
                return {'CANCELLED'}

            # Set snapshot mode flag for Timeline HUD
            context.scene["is_snapshot_mode"] = True
            
            # CRITICAL: Register HUD handler for snapshots
            from .. import hud
            if not hud_overlay.is_hud_enabled():
                print("🎬 SNAPSHOT: Registering HUD handler for Timeline display")
                hud_overlay.register_hud_handler()
            else:
                print("🎬 SNAPSHOT: HUD handler already registered")

            # Force HUD refresh for snapshot mode
            hud_overlay.refresh_hud()
            print("🎬 SNAPSHOT: Forced HUD refresh")

            # Get snapshot date
            snapshot_date_str = getattr(ws_props, "visualisation_start", None)
            if not snapshot_date_str or snapshot_date_str == "-":
                self.report({'ERROR'}, "No snapshot date is set.")
                return {'CANCELLED'}
            
            try:
                snapshot_date = tool.Sequence.parse_isodate_datetime(snapshot_date_str)
                if not snapshot_date: raise ValueError("Invalid date format")
            except Exception as e:
                self.report({'ERROR'}, f"Invalid snapshot date: {snapshot_date_str}. Error: {e}")
                return {'CANCELLED'}

            # Process construction state and show snapshot
            date_source = getattr(ws_props, "date_source_type", "SCHEDULE")
            product_states = tool.Sequence.process_construction_state(
                work_schedule, snapshot_date, date_source=date_source
            )
            tool.Sequence.show_snapshot(product_states)
            
            # Stop animation if playing
            if context.screen.is_animation_playing:
                bpy.ops.screen.animation_cancel(restore_frame=False)

            # Check 3D texts after snapshot
            texts_collection = bpy.data.collections.get("Schedule_Display_Texts")
            if texts_collection:
                for obj in texts_collection.objects:
                    print(f"  - Text object: {obj.name}, visible: {not obj.hide_viewport}")
            else:
                print("  - No 3D texts collection found")

            self.report({'INFO'}, f"Snapshot created for date {snapshot_date.strftime('%Y-%m-%d')}")
            return {'FINISHED'}
            
        except Exception as e:
            # Restore UI state if there's an error
            try:
                restore_all_ui_state(context)
            except Exception:
                pass
            raise e

    def execute(self, context):
        try:
            return self._execute(context)
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.report({'ERROR'}, f"Unexpected error: {e}")
            return {'CANCELLED'}        

class SnapshotWithcolortypesFixed(tool.Ifc.Operator, bpy.types.Operator):
    bl_idname = "bim.snapshot_with_colortypes_fixed"
    bl_label = "Create Snapshot (Enhanced)"
    bl_description = "Create a snapshot of the current 4D state at a specific date with ColorType visualization. Shows objects as they appear at the selected date with proper colors and visibility."
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        # AUTOFIX: Ensure variance system is clean before creating snapshot
        try:
            tool.Sequence.detect_and_fix_variance_inconsistency()
        except Exception as e:
            print(f"[WARNING] Could not run variance autofix before snapshot: {e}")

        # SPECIFIC FIX: Clear any active variance colors from 3D objects
        try:
            cleared_variance_colors = tool.Sequence.detect_and_clear_active_variance_colors()
            if cleared_variance_colors:
                print("[SNAPSHOT] Cleared active variance colors to prevent color system conflicts")
        except Exception as e:
            print(f"[WARNING] Could not clear variance colors before snapshot: {e}")

        snapshot_all_ui_state(context)
        _save_3d_texts_state()
        context.scene["is_snapshot_mode"] = True
        
        # DO NOT register HUD handler in snapshots - must be static
        print("🎬 SNAPSHOT: No Timeline HUD registration (static mode)") # Do not register HUD handler in snapshots - it must be static
        
        try:
            tool.Sequence.sync_active_group_to_json() # Sync colortypes for snapshot
        except Exception as e:
            print(f"Error syncing colortypes for snapshot: {e}")

        ws_props = tool.Sequence.get_work_schedule_props()
        work_schedule_id = getattr(ws_props, "active_work_schedule_id", None)
        if not work_schedule_id:
            self.report({'ERROR'}, "No active Work Schedule selected.")
            return {'CANCELLED'}
        work_schedule = tool.Ifc.get().by_id(work_schedule_id)
        if not work_schedule:
            self.report({'ERROR'}, "Active Work Schedule not found in IFC.")
            return {'CANCELLED'}

        snapshot_date_str = getattr(ws_props, "visualisation_start", None)
        if not snapshot_date_str or snapshot_date_str == "-":
            self.report({'ERROR'}, "No snapshot date is set.")
            return {'CANCELLED'}
        
        try:
            snapshot_date = tool.Sequence.parse_isodate_datetime(snapshot_date_str)
            if not snapshot_date: raise ValueError("Invalid date format")
        except Exception as e:
            self.report({'ERROR'}, f"Invalid snapshot date: {snapshot_date_str}. Error: {e}")
            return {'CANCELLED'}

        date_source = getattr(ws_props, "date_source_type", "SCHEDULE")
        product_states = tool.Sequence.process_construction_state(
            work_schedule, snapshot_date, date_source=date_source
        )
        tool.Sequence.show_snapshot(product_states)
        
        # --- APPLY VISIBILITY AND REFRESH EXISTING 3D TEXTS ---
        try:
            # Check the checkbox state and apply visibility
            anim_props = tool.Sequence.get_animation_props()
            camera_props = anim_props.camera_orbit
            should_hide = not getattr(camera_props, "show_3d_schedule_texts", False)
            
            # Apply auto-disable logic if 3D HUD Render is disabled
            if should_hide:
                current_legend_enabled = getattr(camera_props, "enable_3d_legend_hud", False)
                if current_legend_enabled:
                    print("🔴 SNAPSHOT: 3D HUD Render disabled, auto-disabling 3D Legend HUD")
                    camera_props.enable_3d_legend_hud = False
            
            texts_collection = bpy.data.collections.get("Schedule_Display_Texts")
            if texts_collection:
                texts_collection.hide_viewport = should_hide
                texts_collection.hide_render = should_hide
                
            # Also apply to 3D Legend HUD collection
            legend_collection = bpy.data.collections.get("Schedule_Display_3D_Legend")
            if legend_collection:
                legend_collection.hide_viewport = should_hide
                legend_collection.hide_render = should_hide
            
            # Force viewport update to ensure everything is ready
            bpy.context.view_layer.update()
            
            # *** 3D TEXTS ARE CREATED WHEN SNAPSHOT CAMERA IS CREATED ***
            # Only refresh existing texts with snapshot date, don't create new ones
            try:
                texts_collection = bpy.data.collections.get("Schedule_Display_Texts")
                if texts_collection and len(texts_collection.objects) > 0:
                    bpy.ops.bim.refresh_snapshot_texts()
                else:
                    print("No existing 3D texts to refresh")

            except Exception as e:
                print(f"Error refreshing 3D texts: {e}")

        except Exception as e:
            print(f"Error applying visibility to 3D texts: {e}")

        # Check 3D texts after snapshot
        texts_collection = bpy.data.collections.get("Schedule_Display_Texts")
        if texts_collection:
            for obj in texts_collection.objects:
                print(f"  - Text object: {obj.name}, visible: {not obj.hide_viewport}")
        else:
            print("No 3D texts collection found")
        
        if context.screen.is_animation_playing:
            bpy.ops.screen.animation_cancel(restore_frame=False)

        self.report({'INFO'}, f"Snapshot created for date {snapshot_date.strftime('%Y-%m-%d')}")

        # Force UI redraw to update button states
        for area in context.screen.areas:
            if area.type in ['PROPERTIES', 'VIEW_3D']:
                area.tag_redraw()

        return {'FINISHED'}
