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
import ifcopenshell.util.sequence
from .. import hud as hud_overlay
from datetime import datetime, timedelta
from .operator import snapshot_all_ui_state
from .schedule_task_operators import restore_all_ui_state

# === Animation operators ===

class CreateAnimation(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.create_animation"
    bl_label = "Create 4D Animation"
    bl_options = {"REGISTER", "UNDO"}

    preserve_current_frame: bpy.props.BoolProperty(default=False)

    def _execute(self, context):
        import time
        total_start_time = time.time()

        print("🚨🚨🚨 OPERATOR CreateAnimation._execute STARTED 🚨🚨🚨")

        stored_frame = context.scene.frame_current
        work_schedule = tool.Sequence.get_active_work_schedule()
        anim_props = tool.Sequence.get_animation_props()

        if not work_schedule:
            self.report({'ERROR'}, "No active work schedule found.")
            return {'CANCELLED'}

        settings = _get_animation_settings(context)
        print("🚀 STARTING CORRECTED 4D ANIMATION CREATION") # This seems to be a debug print, I'll leave it as is but it could be translated to "STARTING CORRECTED 4D ANIMATION CREATION"

        # AUTOFIX: Ensure variance system is clean before creating animation
        try:
            tool.Sequence.detect_and_fix_variance_inconsistency()
        except Exception as e:
            print(f"[WARNING] Could not run variance autofix before animation: {e}")

        # SPECIFIC FIX: Clear any active variance colors from 3D objects
        try:
            cleared_variance_colors = tool.Sequence.detect_and_clear_active_variance_colors()
            if cleared_variance_colors:
                print("[ANIMATION] Cleared active variance colors to prevent color system conflicts")
        except Exception as e:
            print(f"[WARNING] Could not clear variance colors before animation: {e}")

        try:
            # --- STAGE 1: FRAME COMPUTATION ---
            frames_start = time.time()
            frames = {}
            try:
                print("[OPTIMIZED] Attempting to use FULL optimization path for frames...")
                from . import ifc_lookup
                lookup = ifc_lookup.get_ifc_lookup()
                date_cache = ifc_lookup.get_date_cache()

                if not lookup.lookup_built:
                    print("[OPTIMIZED] Building lookup tables...")
                    lookup.build_lookup_tables(work_schedule)

                print("[OPTIMIZED] Using enhanced optimized frame computation...")
                frames = tool.Sequence.get_animation_product_frames_enhanced_optimized(
                    work_schedule, settings, lookup, date_cache
                )
                print("[SUCCESS] Optimized frame computation was successful.")

            except Exception as e:
                print(f"[CRITICAL WARNING] Optimized frames method failed, falling back to slow method: {e}")
                frames = _compute_product_frames(context, work_schedule, settings)

            frames_time = time.time() - frames_start
            print(f"📊 FRAMES COMPUTED: {len(frames)} products in {frames_time:.3f}s")

            if not frames:
                 self.report({'INFO'}, "No frames found to animate.")
                 return {'CANCELLED'}

            # --- STAGE 2: ANIMATION APPLICATION (OPTIMIZED) ---
            anim_start = time.time()
            print("🔥🔥🔥 [OPERATOR] STAGE 2 - ANIMATION APPLICATION STARTED!")

            try:

                # Build performance cache for optimization
                from . import performance_cache
                cache = performance_cache.get_performance_cache()

                if not cache.cache_valid:
                    print("[OPTIMIZED] Building performance cache...")
                    cache.build_scene_cache()

                # Call optimized function
                tool.Sequence.animate_objects_with_ColorTypes_optimized(settings, frames, cache)

            except Exception as e:
                print(f"🔥🔥🔥 [ERROR] Optimized method failed, falling back to standard method: {e}")
                import traceback
                traceback.print_exc()

                # Fallback to standard method
                tool.Sequence.animate_objects_with_ColorTypes(settings, frames)

            anim_time = time.time() - anim_start
            print(f"🎬 ANIMATION APPLIED: Completed in {anim_time:.3f}s")

        except Exception as e:
            self.report({'ERROR'}, f"Animation process failed: {e}")
            import traceback
            traceback.print_exc()
            return {'CANCELLED'}

        if self.preserve_current_frame:
            context.scene.frame_set(stored_frame)

        total_time = time.time() - total_start_time
        print("-" * 60)
        print("-" * 60)
        self.report({'INFO'}, f"Animation created for {len(frames)} elements in {total_time:.2f}s.")

        anim_props.is_animation_created = True

        try:
            camera_props = tool.Sequence.get_animation_props().camera_orbit
            if camera_props.enable_3d_legend_hud:
                bpy.ops.bim.setup_3d_legend_hud()
        except Exception as e:
            print(f"[WARNING] Could not auto-create 3D Legend HUD: {e}")

        return {'FINISHED'}

    def execute(self, context):
        try:
            return self._execute(context)
        except Exception as e:
            self.report({'ERROR'}, f"Unexpected error: {e}")
            return {'CANCELLED'}

    def _get_unified_date_range(self, work_schedule):
        from datetime import datetime
        if not work_schedule: return None, None
        all_starts, all_finishes = [], []
        for schedule_type in ["SCHEDULE", "ACTUAL", "EARLY", "LATE"]:
            start_attr = f"{schedule_type.capitalize()}Start"
            finish_attr = f"{schedule_type.capitalize()}Finish"
            root_tasks = ifcopenshell.util.sequence.get_root_tasks(work_schedule)
            def get_all_tasks_recursive(tasks):
                result = []
                for task in tasks:
                    result.append(task)
                    nested = ifcopenshell.util.sequence.get_nested_tasks(task)
                    if nested: result.extend(get_all_tasks_recursive(nested))
                return result
            all_tasks = get_all_tasks_recursive(root_tasks)
            for task in all_tasks:
                start_date = ifcopenshell.util.sequence.derive_date(task, start_attr, is_earliest=True)
                if start_date: all_starts.append(start_date)
                finish_date = ifcopenshell.util.sequence.derive_date(task, finish_attr, is_latest=True)
                if finish_date: all_finishes.append(finish_date)
        if not all_starts or not all_finishes: return None, None
        return min(all_starts), max(all_finishes)

class ClearAnimation(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.clear_animation"
    bl_label = "Clear 4D Animation"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        _clear_previous_animation(context)
        self.report({'INFO'}, "Previous animation cleared")
        return {'FINISHED'}

    def execute(self, context):
        try:
            return self._execute(context)
        except Exception as e:
            self.report({'ERROR'}, f"Unexpected error: {e}")
            return {'CANCELLED'}


class AddAnimationTaskType(bpy.types.Operator):
    bl_idname = "bim.add_animation_task_type"
    bl_label = "Add Task Type"
    bl_options = {"REGISTER", "UNDO"}
    group: bpy.props.EnumProperty(items=[('INPUT','INPUT',''),('OUTPUT','OUTPUT','')], name="Group", default='INPUT')
    name: bpy.props.StringProperty(name="Name", default="New Type")
    animation_type: bpy.props.StringProperty(name="Type", default="")

    def execute(self, context):
        props = tool.Sequence.get_animation_props()
        coll = props.task_input_colors if self.group == 'INPUT' else props.task_output_colors
        item = coll.add()
        item.name = self.name or "New Type"
        item.animation_type = self.animation_type or item.name
        try:
            item.color = (1.0, 0.0, 0.0, 1.0)
        except Exception:
            pass
        if self.group == 'INPUT':
            props.active_color_component_inputs_index = len(coll)-1
        else:
            props.active_color_component_outputs_index = len(coll)-1
        try:
            from bonsai.bim.module.sequence.prop import cleanup_all_tasks_colortype_mappings
            cleanup_all_tasks_colortype_mappings(context)
        except Exception:
            pass
        return {'FINISHED'}


class RemoveAnimationTaskType(bpy.types.Operator):
    bl_idname = "bim.remove_animation_task_type"
    bl_label = "Remove Task Type"
    bl_options = {"REGISTER", "UNDO"}
    group: bpy.props.EnumProperty(items=[('INPUT','INPUT',''),('OUTPUT','OUTPUT','')], name="Group", default='INPUT')

    def execute(self, context):
        props = tool.Sequence.get_animation_props()
        if self.group == 'INPUT':
            idx = getattr(props, "active_color_component_inputs_index", 0)
            coll = getattr(props, "task_input_colors", None)
        else:
            idx = getattr(props, "active_color_component_outputs_index", 0)
            coll = getattr(props, "task_output_colors", None)
        if coll is not None and 0 <= idx < len(coll):
            coll.remove(idx)
            if self.group == 'INPUT':
                props.active_color_component_inputs_index = max(0, idx-1)
            else:
                props.active_color_component_outputs_index = max(0, idx-1)
        return {'FINISHED'}


class AddAnimationCamera(bpy.types.Operator):
    """Add a camera specifically for Animation Settings"""
    bl_idname = "bim.add_animation_camera"
    bl_label = "Add Animation Camera"
    bl_description = "Create a new camera for Animation Settings with orbital animation"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        try:
            # For animation cameras, we should try to call the full method if possible
            # but have a fallback to simple creation
            try:
                from . import tool
                cam_obj = tool.Sequence.add_animation_camera()
            except:
                # Fallback to simple camera creation
                cam_data = bpy.data.cameras.new(name="4D_Animation_Camera")
                cam_obj = bpy.data.objects.new(name="4D_Animation_Camera", object_data=cam_data)
                
                # Mark as animation camera
                cam_obj['is_4d_camera'] = True
                cam_obj['is_animation_camera'] = True
                cam_obj['camera_context'] = 'animation'
                
                # Link to scene
                context.collection.objects.link(cam_obj)
                
                # Configure camera settings
                cam_data.lens = 50
                cam_data.clip_start = 0.1
                cam_data.clip_end = 1000
                
                # Position camera with a good default view
                cam_obj.location = (15, -15, 10)
                cam_obj.rotation_euler = (1.1, 0.0, 0.785)
                
                # Set as active camera
                context.scene.camera = cam_obj
            
            # Validate that camera was created successfully
            if not cam_obj:
                self.report({'ERROR'}, "Failed to create animation camera: Camera object is None")
                return {'CANCELLED'}

            # Validate that camera object has required attributes
            if not hasattr(cam_obj, 'select_set'):
                self.report({'ERROR'}, f"Camera object is invalid: {type(cam_obj)}")
                return {'CANCELLED'}

            # Select the camera
            bpy.ops.object.select_all(action='DESELECT')
            cam_obj.select_set(True)
            context.view_layer.objects.active = cam_obj
            
            self.report({'INFO'}, f"Animation camera '{cam_obj.name}' created and set as active")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to create animation camera: {str(e)}")
            return {'CANCELLED'}


# === Helper functions ===

def _sequence_has(attr: str) -> bool:
    try:
        return hasattr(tool.Sequence, attr)
    except Exception:
        return False

def _clear_previous_animation(context) -> None:
    """Unified and robust cleanup function for all 4D animation."""
    print("🧹 Starting complete and optimized animation cleanup...")

    try:
        # --- 1. STOP ANIMATION AND UNREGISTER ALL HANDLERS ---
        # It's crucial to do this first to stop any background processes.

        # Stop playback if active
        if bpy.context.screen.is_animation_playing:
            bpy.ops.screen.animation_cancel(restore_frame=False)
            print("  - Animation stopped.")

        # Unregister the 2D HUD handler (GPU Overlay)
        if hud_overlay.is_hud_enabled():
            hud_overlay.unregister_hud_handler()
            print("  - 2D HUD handler unregistered.")


        # Unregister the 3D texts handler
        if hasattr(tool.Sequence, '_unregister_frame_change_handler'):
            tool.Sequence._unregister_frame_change_handler()
            print("  - 3D texts handler unregistered.")

        # --- 2. CLEAN UP SCENE OBJECTS ---
        # Delete objects generated by the animation (texts, bars, etc.)
        for coll_name in ["Schedule_Display_Texts", "Bar Visual", "Schedule_Display_3D_Legend"]:
            if coll_name in bpy.data.collections:
                collection = bpy.data.collections[coll_name]
                for obj in list(collection.objects):
                    bpy.data.objects.remove(obj, do_unlink=True)
                bpy.data.collections.remove(collection)
                print(f"  - Collection '{coll_name}' and its objects deleted.")

        # Delete the parent 'empty' object
        parent_empty = bpy.data.objects.get("Schedule_Display_Parent")
        if parent_empty:
            bpy.data.objects.remove(parent_empty, do_unlink=True)
            print("  - 'Schedule_Display_Parent' object deleted.")

        # --- 3. CLEAR ANIMATION DATA FROM 3D OBJECTS (IFC PRODUCTS) ---
        print("  - Clearing keyframes and restoring visibility of 3D objects...")
        cleaned_count = 0
        for obj in bpy.data.objects:
            if obj.type == 'MESH' and tool.Ifc.get_entity(obj):
                if obj.animation_data:
                    obj.animation_data_clear()
                    cleaned_count += 1

                # Restore default state
                obj.hide_viewport = False
                obj.hide_render = False
                obj.color = (0.8, 0.8, 0.8, 1.0)
        print(f"  - Keyframes removed from {cleaned_count} objects.")

        # --- 4. RESTORE TIMELINE AND UI ---
        if "is_snapshot_mode" in context.scene:
            del context.scene["is_snapshot_mode"]

        restore_all_ui_state(context)
        print("  - UI state restored.")

        context.scene.frame_set(context.scene.frame_start)
        print(f"  - Timeline reset to frame {context.scene.frame_start}.")


    except Exception as e:
        print(f"Bonsai WARNING: An error occurred during animation cleanup: {e}")
        import traceback
        traceback.print_exc()

def _get_animation_settings(context):
    """Get animation settings with fallback for snapshot independence"""
    try:
        if _sequence_has("get_animation_settings"):
            result = tool.Sequence.get_animation_settings()
            if result is not None:
                return result
    except Exception:
        pass
    
    # Fallback to basic settings independent of Animation Settings
    ws = tool.Sequence.get_work_schedule_props()
    ap = tool.Sequence.get_animation_props()
    
    fallback_settings = {
        "start": getattr(ws, "visualisation_start", None),
        "finish": getattr(ws, "visualisation_finish", None),
        "speed": getattr(ws, "visualisation_speed", 1.0),
        "ColorType_system": getattr(ap, "active_ColorType_system", "ColorTypeS"),
        "ColorType_stack": getattr(ap, "ColorType_stack", None),
        "start_frame": getattr(context.scene, "frame_start", 1),
        "total_frames": max(1, getattr(context.scene, "frame_end", 250) - getattr(context.scene, "frame_start", 1)),
    }
    
    return fallback_settings

def _apply_final_optimized_animation(context, frames, settings):
    """
    FINAL IMPLEMENTATION: Direct replica of the ultra-fast script.
    Minimizes external calls and uses the same batch processing logic.
    """
    print("🚀 APPLYING FINAL OPTIMIZED ANIMATION (Direct Script Logic)")
    opt_start = time.time()

    # 1. FAST AND DIRECT MAPPING: IFC to Blender
    map_start = time.time()
    ifc_to_blender = {}
    all_ifc_objects = []
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            element = tool.Ifc.get_entity(obj)
            if element and not element.is_a("IfcSpace"):
                ifc_to_blender[element.id()] = obj
                all_ifc_objects.append(obj)
    print(f"   - Mapped {len(ifc_to_blender)} objects in {time.time() - map_start:.3f}s") # This seems to be a debug print, I'll leave it as is but it could be translated to "Mapped {len(ifc_to_blender)} objects in {time.time() - map_start:.3f}s"

    # 2. EXACT VISIBILITY LOGIC FROM THE SCRIPT
    hide_start = time.time()
    for obj in all_ifc_objects:
        if obj.animation_data:
            obj.animation_data_clear()

    assigned_objects = set()
    for obj in all_ifc_objects:
        element = tool.Ifc.get_entity(obj)
        if not element or element.id() not in frames:
            obj.hide_viewport = True
            obj.hide_render = True
        else:
            obj.hide_viewport = True
            obj.hide_render = True
            obj.keyframe_insert(data_path="hide_viewport", frame=0)
            obj.keyframe_insert(data_path="hide_render", frame=0)
            assigned_objects.add(obj)
    print(f"   - Visibility configured in {time.time() - hide_start:.3f}s for {len(assigned_objects)} assigned objects") # This seems to be a debug print, I'll leave it as is but it could be translated to "Visibility configured in {time.time() - hide_start:.3f}s for {len(assigned_objects)} assigned objects"

    # 3. GET ORIGINAL COLORS (ASSIGNED OBJECTS ONLY)
    colors_start = time.time()
    original_colors = {obj.name: list(obj.color) for obj in assigned_objects}
    print(f"   - Original colors stored in {time.time() - colors_start:.3f}s") # This seems to be a debug print, I'll leave it as is but it could be translated to "Original colors stored in {time.time() - colors_start:.3f}s"

    # 4. OPERATION PLANNING (SCRIPT'S CORE LOGIC)
    process_start = time.time()
    visibility_ops = []
    color_ops = []
    
    animation_props = tool.Sequence.get_animation_props()
    active_group_name = "DEFAULT"
    for item in getattr(animation_props, "animation_group_stack", []):
        if getattr(item, "enabled", False) and getattr(item, "group", None):
            active_group_name = item.group
            break
    
    colortype_cache = {}
    processed_count = 0

    for product_id, frame_data_list in frames.items():
        obj = ifc_to_blender.get(product_id)
        if not obj or obj not in assigned_objects:
            continue

        original_color = original_colors.get(obj.name, [1.0, 1.0, 1.0, 1.0])

        for frame_data in frame_data_list:
            task = frame_data.get("task")
            task_key = task.id() if task else "None"
            
            if task_key not in colortype_cache:
                colortype_cache[task_key] = tool.Sequence.get_assigned_ColorType_for_task(
                    task, animation_props, active_group_name
                )
            
            ColorType = colortype_cache.get(task_key)
            if not ColorType:
                continue

            states = frame_data.get("states", {})
            if states:
                _plan_animation_operations(obj, states, ColorType, original_color, frame_data, visibility_ops, color_ops)
                processed_count += 1
    
    print(f"   - {processed_count} frames planned in {time.time() - process_start:.3f}s") # This seems to be a debug print, I'll leave it as is but it could be translated to "{processed_count} frames planned in {time.time() - process_start:.3f}s"

    # 5. FINAL BATCH EXECUTION
    exec_start = time.time()
    for op in visibility_ops:
        op['obj'].hide_viewport = op['hide']
        op['obj'].hide_render = op['hide']
        op['obj'].keyframe_insert(data_path="hide_viewport", frame=op['frame'])
        op['obj'].keyframe_insert(data_path="hide_render", frame=op['frame'])

    for op in color_ops:
        op['obj'].color = op['color']
        op['obj'].keyframe_insert(data_path="color", frame=op['frame'])
    
    print(f"   - {len(visibility_ops) + len(color_ops)} keyframes inserted in {time.time() - exec_start:.3f}s") # This seems to be a debug print, I'll leave it as is but it could be translated to "{len(visibility_ops) + len(color_ops)} keyframes inserted in {time.time() - exec_start:.3f}s"
    print(f"   - Total optimization time: {time.time() - opt_start:.3f}s") # This seems to be a debug print, I'll leave it as is but it could be translated to "Total optimization time: {time.time() - opt_start:.3f}s"

    return processed_count


def _plan_animation_operations(obj, states, ColorType, original_color, frame_data, visibility_ops, color_ops):
    is_construction = frame_data.get("relationship") == "output"

    before_start = states.get("before_start", (0, -1))
    if before_start[1] >= before_start[0]:
        if not (is_construction and not getattr(ColorType, 'consider_start', False)):
            visibility_ops.append({'obj': obj, 'frame': before_start[0], 'hide': False})
            color = original_color if getattr(ColorType, 'use_start_original_color', False) else [
                *getattr(ColorType, 'start_color', [0.8, 0.8, 0.8])[:3],
                1.0 - getattr(ColorType, 'start_transparency', 0.0)
            ]
            color_ops.append({'obj': obj, 'frame': before_start[0], 'color': color})

    active = states.get("active", (0, -1))
    if active[1] >= active[0] and getattr(ColorType, 'consider_active', True):
        visibility_ops.append({'obj': obj, 'frame': active[0], 'hide': False})
        color = [
            *getattr(ColorType, 'in_progress_color', [0.5, 0.9, 0.5])[:3],
            1.0 - getattr(ColorType, 'in_progress_transparency', 0.0)
        ]
        color_ops.append({'obj': obj, 'frame': active[0], 'color': color})

    after_end = states.get("after_end", (0, -1))
    if after_end[1] >= after_end[0] and getattr(ColorType, 'consider_end', True):
        # FIXED: Check hide_at_end as in v110
        should_hide_at_end = getattr(ColorType, 'hide_at_end', False)
        if should_hide_at_end:
            # Hide object at the end (e.g., demolitions)
            visibility_ops.append({'obj': obj, 'frame': after_end[0], 'hide': True})
        else:
            # Show object at the end with END color
            visibility_ops.append({'obj': obj, 'frame': after_end[0], 'hide': False})
            color = original_color if getattr(ColorType, 'use_end_original_color', False) else [
                *getattr(ColorType, 'end_color', [0.7, 0.7, 0.7])[:3],
                1.0 - getattr(ColorType, 'end_transparency', 0.0)
            ]
            color_ops.append({'obj': obj, 'frame': after_end[0], 'color': color})


def _compute_product_frames(context, work_schedule, settings):
    # This function now only calls the tool function, keeping the logic separate.
    return tool.Sequence.get_animation_product_frames(work_schedule, settings)

def _plan_animation_operations(obj, frame_data, ColorType, original_color, visibility_ops, color_ops):
    """
    Helper function to plan keyframe operations without inserting them.
    """
    states = frame_data.get("states", {})
    is_construction = frame_data.get("relationship") == "output"

    # State BEFORE START
    before_start = states.get("before_start")
    if before_start and not (is_construction and not getattr(ColorType, 'consider_start', False)):
        visibility_ops.append({'obj': obj, 'frame': before_start[0], 'hide': False})
        color = original_color if getattr(ColorType, 'use_start_original_color', False) else [
            *getattr(ColorType, 'start_color', [0.8, 0.8, 0.8])[:3],
            1.0 - getattr(ColorType, 'start_transparency', 0.0)
        ]
        color_ops.append({'obj': obj, 'frame': before_start[0], 'color': color})

    # ACTIVE state
    active = states.get("active")
    if active and getattr(ColorType, 'consider_active', True):
        visibility_ops.append({'obj': obj, 'frame': active[0], 'hide': False})
        color = [
            *getattr(ColorType, 'in_progress_color', [0.5, 0.9, 0.5])[:3],
            1.0 - getattr(ColorType, 'in_progress_transparency', 0.0)
        ]
        color_ops.append({'obj': obj, 'frame': active[0], 'color': color})

    # State AFTER FINISH
    after_end = states.get("after_end")
    if after_end and getattr(ColorType, 'consider_end', True):
        # FIXED: Check hide_at_end as in v110
        should_hide_at_end = getattr(ColorType, 'hide_at_end', False)
        if should_hide_at_end:
            # Hide object at the end (e.g., demolitions)
            visibility_ops.append({'obj': obj, 'frame': after_end[0], 'hide': True})
        else:
            # Show object at the end with END color
            visibility_ops.append({'obj': obj, 'frame': after_end[0], 'hide': False})
            color = original_color if getattr(ColorType, 'use_end_original_color', False) else [
                *getattr(ColorType, 'end_color', [0.7, 0.7, 0.7])[:3],
                1.0 - getattr(ColorType, 'end_transparency', 0.0)
            ]
            color_ops.append({'obj': obj, 'frame': after_end[0], 'color': color})


def _safe_set(obj, name, value):
    try:
        setattr(obj, name, value)
    except Exception:
        # Silently ignore when the target property doesn't exist
        pass

def _ensure_default_group(context):
    # Ensure internal DEFAULT exists
    try:
        # Note: UnifiedColorTypeManager would need to be imported if available
        # For now, we'll skip this part
        pass
    except Exception:
        pass
    # Ensure UI stack has at least one item (animation_group_stack or colortype_stack)
    try:
        ap = tool.Sequence.get_animation_props()
        # Newer stack
        if hasattr(ap, "animation_group_stack") and len(ap.animation_group_stack) == 0:
            it = ap.animation_group_stack.add()
            it.group = getattr(ap, "ColorType_groups", "") or "DEFAULT"
            _safe_set(it, 'enabled', True)
        # Older stack
        if hasattr(ap, "colortype_stack") and len(ap.colortype_stack) == 0:
            it = ap.colortype_stack.add()
            it.group = getattr(ap, "ColorType_groups", "") or "DEFAULT"
            _safe_set(it, 'enabled', True)
    except Exception:
        pass


# ============================================================================
# ANIMATION CLEANUP OPERATORS (moved from operator.py)
# ============================================================================

class ClearPreviousAnimation(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.clear_previous_animation"
    bl_label = "Reset Animation"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        # --- START OF MODIFICATION ---
        # Lower the flag BEFORE cleaning, to invalidate the state.
        try:
            anim_props = tool.Sequence.get_animation_props()
            anim_props.is_animation_created = False
            print("[ERROR] Animation flag SET to FALSE.")
        except Exception as e:
            print(f"Could not reset animation flag: {e}")
        # --- END OF MODIFICATION ---
            
        try:
            if bpy.context.screen.is_animation_playing:
                bpy.ops.screen.animation_cancel(restore_frame=False)
        except Exception as e:
            print(f"Could not stop animation: {e}")

        # ... (rest of the function code unchanged) ...
        
        try:
            _clear_previous_animation(context)
            # ... (HUD cleanup code) ...
            self.report({'INFO'}, "Previous animation cleared.")
            context.scene.frame_set(context.scene.frame_start)
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to clear previous animation: {e}")
            return {"CANCELLED"}

    def execute(self, context):
        return self._execute(context)


class ClearPreviousSnapshot(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.clear_previous_snapshot"
    bl_label = "Reset Snapshot"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        print(f"🔄 Reset snapshot started")
        
        # CORRECTION: Stop the animation if it is playing
        try:
            if bpy.context.screen.is_animation_playing:
                bpy.ops.screen.animation_cancel(restore_frame=False)
        except Exception as e:
            print(f"[ERROR] Could not stop animation: {e}")

        # Clear snapshot mode flag
        if "is_snapshot_mode" in context.scene:
            del context.scene["is_snapshot_mode"]

        # Restore UI state (3D texts, Timeline HUD, etc.)
        try:
            restore_all_ui_state(context)
        except Exception as e:
            print(f"[ERROR] Could not restore UI state: {e}")

        # CORRECTION: Complete cleanup of previous snapshot
        try:
            # CRITICAL: Reset all objects to original state (use existing function)
            print(f"🔄 Clearing previous animation...")
            _clear_previous_animation(context)
            
            # Clear temporary snapshot data
            if hasattr(bpy.context.scene, 'snapshot_data'):
                del bpy.context.scene.snapshot_data
            
            # Clear the active profile group in HUD Legend
            try:
                anim_props = tool.Sequence.get_animation_props()
                if anim_props and hasattr(anim_props, 'camera_orbit'):
                    camera_props = anim_props.camera_orbit

                    # Get all active profiles to hide them
                    if hasattr(anim_props, 'animation_group_stack') and anim_props.animation_group_stack:
                        all_colortype_names = []
                        for group_item in anim_props.animation_group_stack:
                            group_name = group_item.group
                            from ..prop import UnifiedColorTypeManager
                            group_colortypes = UnifiedColorTypeManager.get_group_colortypes(bpy.context, group_name)
                            if group_colortypes:
                                all_colortype_names.extend(group_colortypes.keys())
                        
                        # Hide all profiles by putting their names in legend_hud_visible_colortypes
                        if all_colortype_names:
                            hidden_colortypes_str = ','.join(set(all_colortype_names))  # use set() to remove duplicates
                            camera_props.legend_hud_visible_colortypes = hidden_colortypes_str
                            print(f"🧹 Hidden colortypes in HUD Legend: {hidden_colortypes_str}")
                    
                    # Clear selected_colortypes just in case
                    if hasattr(camera_props, 'legend_hud_selected_colortypes'):
                        camera_props.legend_hud_selected_colortypes = set()
                    
                    # Invalidate legend HUD cache
                    from ..hud import invalidate_legend_hud_cache
                    invalidate_legend_hud_cache()
                    print("🧹 Active colortype group cleared from HUD Legend")
            except Exception as legend_e:
                print(f"[WARNING] Could not clear colortype group: {legend_e}")
            
            # --- SNAPSHOT 3D TEXTS RESTORATION ---
            # Clear snapshot mode and restore previous state
            if "is_snapshot_mode" in context.scene:
                del context.scene["is_snapshot_mode"]
                print("📸 Snapshot mode deactivated for 3D texts")
            _restore_3d_texts_state()
            
            self.report({'INFO'}, "Snapshot reset completed")
        except Exception as e:
            print(f"Error during snapshot reset: {e}")
            self.report({'WARNING'}, f"Snapshot reset completed with warnings: {e}")
        
        return {'FINISHED'}
    
    def execute(self, context):
        return self._execute(context)

class SyncAnimationByDate(bpy.types.Operator):
    bl_idname = "bim.sync_animation_by_date"
    bl_label = "Sync Animation by Date"
    bl_options = {"INTERNAL"}
    previous_start_date: bpy.props.StringProperty()
    previous_finish_date: bpy.props.StringProperty()

    def execute(self, context):
        # Sync functionality removed - always proceed
        # anim_props = tool.Sequence.get_animation_props()
        # if not getattr(anim_props, "auto_update_on_date_source_change", False):
        #     return {'CANCELLED'}
        was_playing = bpy.context.screen.is_animation_playing
        if was_playing:
            bpy.ops.screen.animation_cancel(restore_frame=False)
        try:
            start_date = datetime.fromisoformat(self.previous_start_date)
            finish_date = datetime.fromisoformat(self.previous_finish_date)
            current_frame = context.scene.frame_current
            start_frame = context.scene.frame_start
            end_frame = context.scene.frame_end
            progress = (current_frame - start_frame) / (end_frame - start_frame) if (end_frame - start_frame) > 0 else 0
            current_date = start_date + (finish_date - start_date) * progress
            props = tool.Sequence.get_work_schedule_props()
            new_start_date = datetime.fromisoformat(props.visualisation_start)
            new_finish_date = datetime.fromisoformat(props.visualisation_finish)
            new_duration = (new_finish_date - new_start_date).total_seconds()
            new_progress = (current_date - new_start_date).total_seconds() / new_duration if new_duration > 0 else 0
            new_progress = max(0.0, min(1.0, new_progress))
            new_frame = start_frame + (end_frame - start_frame) * new_progress
            context.scene.frame_set(int(round(new_frame)))
        except (ValueError, TypeError) as e:
            print(f"Sync failed: {e}")
        if was_playing:
            bpy.ops.screen.animation_play()
        return {'FINISHED'}



# Removed SyncAnimationDateSource - sync auto functionality eliminated


def _clear_previous_animation(context) -> None:
    print("🧹 Iniciando cleanup complete y optimized de la animation...")
    try:
        # --- 1. STOP ANIMATION AND HANDLERS (Same as before) ---
        if bpy.context.screen.is_animation_playing:
            bpy.ops.screen.animation_cancel(restore_frame=False)
        if hud_overlay.is_hud_enabled():
            hud_overlay.unregister_hud_handler()
        if hasattr(tool.Sequence, '_unregister_frame_change_handler'):
            tool.Sequence._unregister_frame_change_handler()

        # --- 2. CLEAN COLLECTIONS AND ANIMATION OBJECTS (Same as before) ---
        for coll_name in ["Schedule_Display_Texts", "Bar Visual", "Schedule_Display_3D_Legend"]:
            if coll_name in bpy.data.collections:
                collection = bpy.data.collections[coll_name]
                for obj in list(collection.objects):
                    bpy.data.objects.remove(obj, do_unlink=True)
                bpy.data.collections.remove(collection)
        parent_empty = bpy.data.objects.get("Schedule_Display_Parent")
        if parent_empty:
            bpy.data.objects.remove(parent_empty, do_unlink=True)

        # --- 3. OPTIMIZED RESET OF IFC OBJECTS ---
        print("🧹 Efficiently resetting the state of IFC objects...")
        cleaned_count = 0
        reset_count = 0
        for obj in bpy.data.objects:
            if obj.type == 'MESH' and tool.Ifc.get_entity(obj):
                # Clears all animation data from the object
                if obj.animation_data:
                    obj.animation_data_clear()
                    cleaned_count += 1

                # Restore default visibility
                obj.hide_viewport = False
                obj.hide_render = False

                # Resets the object's color to white (neutral value).
                # This disables the override and allows the material color to be seen.
                # It is a very fast operation.
                obj.color = (1.0, 1.0, 1.0, 1.0)
                
                reset_count += 1

        print(f"🧹 COMPLETE CLEANUP: {cleaned_count} animations cleared, {reset_count} objects reset.")

        # --- 4. RESTORE UI AND TIMELINE (Same as before) ---
        if "is_snapshot_mode" in context.scene:
            del context.scene["is_snapshot_mode"]
        restore_all_ui_state(context)
        context.scene.frame_set(context.scene.frame_start)

        # Force a single redraw at the end to ensure the view updates
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

    except Exception as e:
        print(f"Bonsai WARNING: An error occurred during animation cleanup: {e}")
        import traceback
        traceback.print_exc()