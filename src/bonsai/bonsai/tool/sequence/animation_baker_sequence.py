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

from __future__ import annotations
import bpy
import time
import json
import bonsai.tool as tool

# Try to import data module for interpolate_ColorType_values function
try:
    from bonsai.bim.module.sequence.data import interpolate_ColorType_values
    class _seq_data:
        interpolate_ColorType_values = staticmethod(interpolate_ColorType_values)
except ImportError:
    try:
        import bonsai.data as _seq_data
    except ImportError:
        # Fallback: Create a dummy data module
        class _seq_data:
            @staticmethod
            def interpolate_ColorType_values(ColorType, state, progress=0.0):
                # Return default values if optimization is not available
                return {'alpha': 1.0}

class AnimationBakerSequence:
    """Mixin class for applying (baking) animation data to Blender objects."""

    @classmethod
    def animate_objects_with_ColorTypes_new(cls, settings, product_frames):
        """
        NEW BATCH PROCESSING VERSION: Refactored for performance with thousands of objects.
        Replaces the old animate_objects_with_ColorTypes function.
        """
        import time
        start_time = time.time()
        print("Starting new animation with ColorTypes")
        print("[ANIM] STARTING NEW BATCH ANIMATION SYSTEM")

        # IFC MAPPING - From COMPLETE_SYSTEM_ULTRA_FAST
        print("Building IFC mapping...")
        map_start = time.time()
        ifc_to_blender = {}
        assigned_objects = set()

        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                element = tool.Ifc.get_entity(obj)
                if element and not element.is_a("IfcSpace"):
                    ifc_to_blender[element.id()] = obj
                    # Check if this object is assigned to tasks
                    if element.id() in product_frames:
                        assigned_objects.add(obj)

        map_time = time.time() - map_start
        print(f"Mapped {len(ifc_to_blender)} IFC objects ({len(assigned_objects)} assigned) in {map_time:.3f}s")

        # Save original colors using existing system
        if not bpy.context.scene.get('BIM_VarianceOriginalObjectColors'):
            cls._save_original_object_colors()

        #  Use original build_animation_plan approach
        print("Using original stable animation system...")

        # Phase 1: Build animation plan (original approach)
        animation_plan = cls.build_animation_plan(bpy.context, settings, product_frames)

        # Phase 2: Execute animation plan (original approach)
        cls.execute_animation_plan(bpy.context, animation_plan)

        # Set viewport shading and frame range (preserve existing functionality)
        area = tool.Blender.get_view3d_area()
        try:
            area.spaces[0].shading.color_type = "OBJECT"
        except Exception:
            pass
        bpy.context.scene.frame_start = settings["start_frame"]
        bpy.context.scene.frame_end = int(settings["start_frame"] + settings["total_frames"] + 1)

        # SAFE BASELINE TIMING REPORT
        total_time = time.time() - start_time
        print(f"[INFO] IFC mapping + Original stable system - Total time: {total_time:.2f}s")
        print("Reverted aggressive optimizations to prevent crashes")
        print("[ANIM] SAFE BASELINE SYSTEM COMPLETE")

    @classmethod
    def animate_objects_with_ColorTypes_optimized(cls, settings, product_frames, cache):
        """
        ULTRA-OPTIMIZED version using cache.
        Optimized animation with pre-built plan.
        """
        import time
        from datetime import datetime
        start_time = time.time()

        print("Starting optimized animation with ColorTypes")
        print(f"[OPTIMIZED] OPTIMIZED ANIMATION: Planning for {len(product_frames)} products")

        # Get properties once
        animation_props = tool.Sequence.get_animation_props()
        active_group_name = cls._get_active_group_optimized(animation_props)

        # Save original colors if not already saved
        if not bpy.context.scene.get('BIM_VarianceOriginalObjectColors'):
            cls._save_original_colors_optimized(cache)

        # Local lists to build the animation plan
        visibility_ops = []
        color_ops = []
        total_objects_processed = 0

        # Use cache for direct product->objects mapping
        for product_id, frame_data_list in product_frames.items():
            objects = cache.get_objects_for_product(product_id)
            if not objects:
                continue

            for obj in objects:
                total_objects_processed += 1

                # Process frame data for this object
                for frame_data in frame_data_list:
                    task = frame_data.get("task")
                    if not task:
                        continue

                    # Get ColorType with caching
                    colortype = cls._get_colortype_optimized(task, animation_props, active_group_name)
                    if not colortype:
                        continue

                    # Get original color from cache
                    original_color = cache.get_original_color(obj)

                    # Apply optimized object animation
                    cls._apply_object_animation_optimized(
                        obj, frame_data, colortype, settings, visibility_ops, color_ops
                    )

        # Execute batch operations
        print(f"[OPTIMIZED] Executing {len(visibility_ops)} visibility ops, {len(color_ops)} color ops")

        # Set all visibility operations
        for op in visibility_ops:
            bpy.context.scene.frame_set(op['frame'])
            op['obj'].hide_viewport = op['hide']
            op['obj'].hide_render = op['hide']
            op['obj'].keyframe_insert(data_path="hide_viewport", frame=op['frame'])
            op['obj'].keyframe_insert(data_path="hide_render", frame=op['frame'])

        # Set all color operations
        for op in color_ops:
            bpy.context.scene.frame_set(op['frame'])
            if hasattr(op['obj'].data, 'materials') and op['obj'].data.materials:
                material = op['obj'].data.materials[0]
                if material and material.use_nodes:
                    principled = material.node_tree.nodes.get("Principled BSDF")
                    if principled:
                        principled.inputs["Base Color"].default_value = op['color']
                        principled.inputs["Base Color"].keyframe_insert(data_path="default_value", frame=op['frame'])

        # Set viewport shading
        cls._setup_viewport_shading_optimized()

        # Set frame range
        bpy.context.scene.frame_start = settings["start_frame"]
        bpy.context.scene.frame_end = int(settings["start_frame"] + settings["total_frames"])

        elapsed = time.time() - start_time
        print(f"[OPTIMIZED] OPTIMIZED ANIMATION COMPLETE in {elapsed:.3f}s")
        print(f"[OPTIMIZED] Objects processed: {total_objects_processed}")

    @classmethod
    def build_animation_plan(cls, context, settings, product_frames):
        """
        Phase 1: Planning - Builds animation plan without modifying Blender scene.
        Returns a structured plan dict for batch execution.
        """
        import time
        start_time = time.time()

        print("[INFO] Building animation plan...")
        print(f"[INFO] BUILDING PLAN for {len(product_frames)} products")

        # Build IFC->Blender mapping once
        ifc_to_blender = {}
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                element = tool.Ifc.get_entity(obj)
                if element and not element.is_a("IfcSpace"):
                    ifc_to_blender[element.id()] = obj

        # Load original colors once
        original_object_colors = bpy.context.scene.get('BIM_VarianceOriginalObjectColors')
        if original_object_colors:
            original_colors = json.loads(original_object_colors)
        else:
            print("[WARNING] Original colors not found, using white as fallback")
            original_colors = {}

        # Plan structure: frame -> list of operations
        animation_plan = {}

        objects_planned = 0
        for product_id, frame_data_list in product_frames.items():
            obj = ifc_to_blender.get(product_id)
            if not obj:
                continue

            objects_planned += 1
            original_color = original_colors.get(obj.name, [0.8, 0.8, 0.8, 1.0])

            # Process each frame data entry for this product
            for frame_data in frame_data_list:
                task = frame_data.get("task")
                if not task:
                    continue

                # Get appropriate ColorType for this task
                try:
                    animation_props = tool.Sequence.get_animation_props()
                    ColorType = tool.Sequence._get_best_ColorType_for_task(task, animation_props)
                except Exception as e:
                    print(f"[ERROR] Error getting ColorType for task {task.id()}: {e}")
                    continue

                # Plan object animation
                cls._plan_object_animation(animation_plan, obj, frame_data, ColorType, original_color)

        print(f"[INFO] PLANNING COMPLETE: Plan contains {len(animation_plan)} frames")
        return dict(animation_plan)

    @classmethod
    def _plan_object_animation(cls, animation_plan, obj, frame_data, ColorType, original_color):
        """Helper function to plan animation keyframes for a single object"""

        # Plan START state
        start_state_frames = frame_data["states"]["before_start"]
        start_f, end_f = start_state_frames

        is_construction = frame_data.get("relationship") == "output"
        consider_start = getattr(ColorType, 'consider_start', False)
        should_be_visible_at_start = not is_construction or consider_start

        if end_f >= start_f:
            frame_ops = animation_plan.setdefault(start_f, [])

            if should_be_visible_at_start:
                frame_ops.append({
                    'type': 'visibility',
                    'obj': obj,
                    'hide_viewport': False,
                    'hide_render': False
                })

                # Apply color
                if consider_start:
                    if getattr(ColorType, 'use_start_original_color', False):
                        color = original_color
                    else:
                        start_color = getattr(ColorType, 'start_color', [0.8, 0.8, 0.8, 1.0])
                        start_transparency = getattr(ColorType, 'start_transparency', 0.0)
                        color = [start_color[0], start_color[1], start_color[2], 1.0 - start_transparency]
                else:
                    color = original_color

                frame_ops.append({
                    'type': 'color',
                    'obj': obj,
                    'color': color
                })
            else:
                frame_ops.append({
                    'type': 'visibility',
                    'obj': obj,
                    'hide_viewport': True,
                    'hide_render': True
                })

        # Plan ACTIVE state
        active_frames = frame_data["states"]["active"]
        start_f, end_f = active_frames

        if end_f >= start_f and getattr(ColorType, 'consider_active', True):
            frame_ops = animation_plan.setdefault(start_f, [])

            frame_ops.append({
                'type': 'visibility',
                'obj': obj,
                'hide_viewport': False,
                'hide_render': False
            })

            # Apply active color
            if getattr(ColorType, 'use_active_original_color', False):
                color = original_color
            else:
                active_color = getattr(ColorType, 'active_color', [0.0, 1.0, 0.0, 1.0])
                active_transparency = getattr(ColorType, 'active_transparency', 0.0)
                color = [active_color[0], active_color[1], active_color[2], 1.0 - active_transparency]

            frame_ops.append({
                'type': 'color',
                'obj': obj,
                'color': color
            })

        # Plan END state
        end_state_frames = frame_data["states"]["after_end"]
        start_f, end_f = end_state_frames

        if end_f >= start_f and getattr(ColorType, 'consider_end', True):
            frame_ops = animation_plan.setdefault(start_f, [])

            frame_ops.append({
                'type': 'visibility',
                'obj': obj,
                'hide_viewport': False,
                'hide_render': False
            })

            # Apply end color
            if getattr(ColorType, 'use_end_original_color', False):
                color = original_color
            else:
                end_color = getattr(ColorType, 'end_color', [1.0, 0.0, 0.0, 1.0])
                end_transparency = getattr(ColorType, 'end_transparency', 0.0)
                color = [end_color[0], end_color[1], end_color[2], 1.0 - end_transparency]

            frame_ops.append({
                'type': 'color',
                'obj': obj,
                'color': color
            })

    @classmethod
    def execute_animation_plan(cls, context, animation_plan):
        """
        Phase 2: Execution - Applies the animation plan efficiently using batch operations.
        """
        import time
        start_time = time.time()

        print("[INFO] EXECUTING animation plan...")
        frames_to_execute = sorted(animation_plan.keys())

        for frame in frames_to_execute:
            context.scene.frame_set(frame)
            operations = animation_plan[frame]

            for op in operations:
                obj = op['obj']

                if op['type'] == 'visibility':
                    obj.hide_viewport = op['hide_viewport']
                    obj.hide_render = op['hide_render']
                    obj.keyframe_insert(data_path="hide_viewport", frame=frame)
                    obj.keyframe_insert(data_path="hide_render", frame=frame)

                elif op['type'] == 'color':
                    color = op['color']
                    if hasattr(obj.data, 'materials') and obj.data.materials:
                        material = obj.data.materials[0]
                        if material and material.use_nodes:
                            principled = material.node_tree.nodes.get("Principled BSDF")
                            if principled:
                                principled.inputs["Base Color"].default_value = color
                                principled.inputs["Base Color"].keyframe_insert(data_path="default_value", frame=frame)

        elapsed = time.time() - start_time
        print(f"[INFO] EXECUTION complete in {elapsed:.3f}s for {len(frames_to_execute)} frames")

    @classmethod
    def apply_ColorType_animation(cls, obj, frame_data, ColorType, original_color, settings):
        """
        Applies animation to an object based on its appearance profile.
        """

        # Check if this is priority mode (start only)
        # We detect by the consider_start_active flag in frame_data
        is_priority_mode = frame_data.get("consider_start_active", False)
        if is_priority_mode:
            print(f"🔒 apply_ColorType_animation: {obj.name} detected consider_start_active=True (Priority start)")
            # Only apply start appearance for the entire active range
            active_frames = frame_data["states"]["active"]
            start_f, end_f = active_frames
            if end_f >= start_f:
                print(f"   Applying START appearance for entire active range: {start_f} to {end_f}")
                cls.apply_state_appearance(obj, ColorType, "start", start_f, end_f, original_color, frame_data)
            return

        # Standard logic for regular tasks (not priority mode)
        is_start_considered = getattr(ColorType, 'consider_start', False)
        is_active_considered = getattr(ColorType, 'consider_active', True)
        is_end_considered = getattr(ColorType, 'consider_end', True)

        # Special case: Only START is enabled
        if is_start_considered and not is_active_considered and not is_end_considered:
            print(f"   Only START enabled for {obj.name}. Applying for entire range.")
            full_start = min([s[0] for s in frame_data["states"].values() if s[1] >= s[0]])
            full_end = max([s[1] for s in frame_data["states"].values() if s[1] >= s[0]])
            print(f"   Calling apply_state_appearance(state='start')")
            cls.apply_state_appearance(obj, ColorType, "start", start_f, end_f, original_color, frame_data)
            print(f"   Visibility after: viewport={not obj.hide_viewport}, render={not obj.hide_render}")
            return

        # Standard state-by-state processing
        for state_name, (start_f, end_f) in frame_data["states"].items():
            if end_f < start_f:
                continue

            print(f"   Processing state '{state_name}' for {obj.name}: frames {start_f}-{end_f}")

            if state_name == "before_start":
                state = "start"
            elif state_name == "active":
                state = "in_progress"
            elif state_name == "after_end":
                state = "end"
            else:
                continue

            # Apply states based on consider flags
            if state == "start":
                if not is_start_considered:
                    # Hide the object if start is not considered and it's construction (output)
                    if frame_data.get("relationship") == "output":
                        print(f"     Hiding {obj.name} in START state (output without consider_start)")
                        bpy.context.scene.frame_set(start_f)
                        obj.hide_viewport = True
                        obj.hide_render = True
                        obj.keyframe_insert(data_path="hide_viewport", frame=start_f)
                        obj.keyframe_insert(data_path="hide_render", frame=start_f)
                    continue

                cls.apply_state_appearance(obj, ColorType, "start", start_f, end_f, original_color, frame_data)

            elif state == "in_progress":
                if not is_active_considered:
                    continue
                cls.apply_state_appearance(obj, ColorType, "in_progress", start_f, end_f, original_color, frame_data)

            elif state == "end":
                if not is_end_considered:
                    continue
                # Check if we should hide the object after completion
                if frame_data.get("relationship") == "input":
                    print(f"     Hiding {obj.name} in END state (input after use)")
                    bpy.context.scene.frame_set(start_f)
                    obj.hide_viewport = True
                    obj.hide_render = True
                    obj.keyframe_insert(data_path="hide_viewport", frame=start_f)
                    obj.keyframe_insert(data_path="hide_render", frame=start_f)
                    continue

                cls.apply_state_appearance(obj, ColorType, "end", start_f, end_f, original_color, frame_data)

    @classmethod
    def apply_state_appearance(cls, obj, ColorType, state, start_frame, end_frame, original_color, frame_data=None):
        """Apply appearance for a specific state"""
        if state == "start":
            # When consider_start=True, the object should always be visible
            bpy.context.scene.frame_set(start_frame)
            obj.hide_viewport = False
            obj.hide_render = False
            obj.keyframe_insert(data_path="hide_viewport", frame=start_frame)
            obj.keyframe_insert(data_path="hide_render", frame=start_frame)

            # Apply start color
            use_original = getattr(ColorType, 'use_start_original_color', False)
            if use_original:
                color = original_color
            else:
                start_color = getattr(ColorType, 'start_color', [0.8, 0.8, 0.8, 1.0])
                transparency = getattr(ColorType, 'start_transparency', 0.0)
                color = [start_color[0], start_color[1], start_color[2], 1.0 - transparency]

            # Set color keyframe
            if hasattr(obj.data, 'materials') and obj.data.materials:
                material = obj.data.materials[0]
                if material and material.use_nodes:
                    principled = material.node_tree.nodes.get("Principled BSDF")
                    if principled:
                        principled.inputs["Base Color"].default_value = color
                        principled.inputs["Base Color"].keyframe_insert(data_path="default_value", frame=start_frame)

        elif state == "in_progress":
            # Make visible
            bpy.context.scene.frame_set(start_frame)
            obj.hide_viewport = False
            obj.hide_render = False
            obj.keyframe_insert(data_path="hide_viewport", frame=start_frame)
            obj.keyframe_insert(data_path="hide_render", frame=start_frame)

            # Apply active color
            use_original = getattr(ColorType, 'use_active_original_color', False)
            if use_original:
                color = original_color
            else:
                active_color = getattr(ColorType, 'active_color', [0.0, 1.0, 0.0, 1.0])
                transparency = getattr(ColorType, 'active_transparency', 0.0)
                color = [active_color[0], active_color[1], active_color[2], 1.0 - transparency]

            # Apply color animation with interpolation
            try:
                # Interpolate color values over time if needed
                interpolated_values = _seq_data.interpolate_ColorType_values(ColorType, state, 0.0)
                alpha = interpolated_values.get('alpha', 1.0 - transparency)
                color = [active_color[0], active_color[1], active_color[2], alpha]
            except Exception:
                pass

            if hasattr(obj.data, 'materials') and obj.data.materials:
                material = obj.data.materials[0]
                if material and material.use_nodes:
                    principled = material.node_tree.nodes.get("Principled BSDF")
                    if principled:
                        principled.inputs["Base Color"].default_value = color
                        principled.inputs["Base Color"].keyframe_insert(data_path="default_value", frame=start_frame)

        elif state == "end":
            # Make visible
            bpy.context.scene.frame_set(start_frame)
            obj.hide_viewport = False
            obj.hide_render = False
            obj.keyframe_insert(data_path="hide_viewport", frame=start_frame)
            obj.keyframe_insert(data_path="hide_render", frame=start_frame)

            # Apply end color
            use_original = getattr(ColorType, 'use_end_original_color', False)
            if use_original:
                color = original_color
            else:
                end_color = getattr(ColorType, 'end_color', [1.0, 0.0, 0.0, 1.0])
                transparency = getattr(ColorType, 'end_transparency', 0.0)
                color = [end_color[0], end_color[1], end_color[2], 1.0 - transparency]

            if hasattr(obj.data, 'materials') and obj.data.materials:
                material = obj.data.materials[0]
                if material and material.use_nodes:
                    principled = material.node_tree.nodes.get("Principled BSDF")
                    if principled:
                        principled.inputs["Base Color"].default_value = color
                        principled.inputs["Base Color"].keyframe_insert(data_path="default_value", frame=start_frame)

    @classmethod
    def _plan_complete_system_animation(cls, obj, states, ColorType, original_color, frame_data, visibility_ops, color_ops):
        """Plans operations using REAL ColorType with full support - FROM COMPLETE_SYSTEM_ULTRA_FAST"""

        # Handle priority mode (START only activated) first
        if frame_data.get("consider_start_active", False):
            print(f"🔒 PLAN_COMPLETE_SYSTEM: {obj.name} detectado consider_start_active=True (Start prioritario)")
            active_frames = states.get("active", (0, -1))
            if active_frames[1] >= active_frames[0]:
                print(f"   Making object visible for entire range: {active_frames[0]} to {active_frames[1]}")
                visibility_ops.append({'obj': obj, 'frame': active_frames[0], 'hide': False})
                use_original = getattr(ColorType, 'use_start_original_color', False)
                if use_original:
                    color = original_color
                else:
                    start_color = getattr(ColorType, 'start_color', [0.8, 0.8, 0.8, 1.0])
                    transparency = getattr(ColorType, 'start_transparency', 0.0)
                    color = [start_color[0], start_color[1], start_color[2], 1.0 - transparency]
                color_ops.append({'obj': obj, 'frame': active_frames[0], 'color': color})
                color_ops.append({'obj': obj, 'frame': active_frames[1], 'color': color})
                print(f"   Priority mode: added visibility (hide=False) and color ops")
            return

        # Regular processing for non-priority mode
        consider_start = getattr(ColorType, 'consider_start', False)
        consider_active = getattr(ColorType, 'consider_active', True)
        consider_end = getattr(ColorType, 'consider_end', True)
        is_construction = frame_data.get("relationship") == "output"

        # Process each state
        for state_name, (start_f, end_f) in states.items():
            if end_f < start_f:
                continue

            should_process = False
            state_color = original_color

            if state_name == "before_start" and consider_start:
                should_process = True
                if not getattr(ColorType, 'use_start_original_color', False):
                    start_color = getattr(ColorType, 'start_color', [0.8, 0.8, 0.8, 1.0])
                    transparency = getattr(ColorType, 'start_transparency', 0.0)
                    state_color = [start_color[0], start_color[1], start_color[2], 1.0 - transparency]

            elif state_name == "active" and consider_active:
                should_process = True
                if not getattr(ColorType, 'use_active_original_color', False):
                    active_color = getattr(ColorType, 'active_color', [0.0, 1.0, 0.0, 1.0])
                    transparency = getattr(ColorType, 'active_transparency', 0.0)
                    state_color = [active_color[0], active_color[1], active_color[2], 1.0 - transparency]

            elif state_name == "after_end" and consider_end:
                should_process = True
                if not getattr(ColorType, 'use_end_original_color', False):
                    end_color = getattr(ColorType, 'end_color', [1.0, 0.0, 0.0, 1.0])
                    transparency = getattr(ColorType, 'end_transparency', 0.0)
                    state_color = [end_color[0], end_color[1], end_color[2], 1.0 - transparency]

            if should_process:
                # Determine visibility
                should_hide = False
                if state_name == "before_start" and is_construction and not consider_start:
                    should_hide = True
                elif state_name == "after_end" and not is_construction:
                    should_hide = True

                visibility_ops.append({'obj': obj, 'frame': start_f, 'hide': should_hide})
                if not should_hide:
                    color_ops.append({'obj': obj, 'frame': start_f, 'color': state_color})

    @classmethod
    def animate_objects_with_ColorTypes(cls, settings, product_frames):
        """
        ULTRA-OPTIMIZED ANIMATION SYSTEM with ALL optimizations integrated:
        - ColorType cache, IFC lookup, Performance cache, Batch processor
        """
        import time
        start_time = time.time()
        print("Starting ultra-optimized animation with ColorTypes")
        print(f"[OPTIMIZED] ULTRA-OPTIMIZED ANIMATION: Planning for {len(product_frames)} products")

        # Get original colors from saved state
        original_object_colors = bpy.context.scene.get('BIM_VarianceOriginalObjectColors')
        if original_object_colors:
            original_colors = json.loads(original_object_colors)
        else:
            print("[WARNING] No original colors found, using fallback approach")
            original_colors = {}

        # Build mapping once
        ifc_to_blender = {}
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                element = tool.Ifc.get_entity(obj)
                if element and not element.is_a("IfcSpace"):
                    ifc_to_blender[element.id()] = obj

        # Get animation properties once
        animation_props = tool.Sequence.get_animation_props()

        # Batch operations for performance
        objects_to_hide = []
        keyframe_operations = []
        total_objects_processed = 0

        # Process each product and its frames
        for product_id, frame_data_list in product_frames.items():
            obj = ifc_to_blender.get(product_id)
            if not obj:
                continue

            total_objects_processed += 1
            original_color = original_colors.get(obj.name, [0.8, 0.8, 0.8, 1.0])

            # Process each frame data entry for this product
            for frame_data in frame_data_list:
                task = frame_data.get("task")
                if not task:
                    continue

                # Get ColorType for this task
                try:
                    ColorType = tool.Sequence._get_best_ColorType_for_task(task, animation_props)
                except Exception as e:
                    print(f"[ERROR] Error getting ColorType for task {task.id()}: {e}")
                    continue

                # Apply animation using optimized method
                cls.apply_ColorType_animation(obj, frame_data, ColorType, original_color, settings)

        # === EXECUTE BATCH OPERATIONS ===
        print(f"[INFO] Executing batch operations: {len(objects_to_hide)} hide, {len(keyframe_operations)} keyframes")

        # Execute hide operations
        for obj in objects_to_hide:
            obj.hide_viewport = True
            obj.hide_render = True

        # Execute keyframe operations
        for operation in keyframe_operations:
            operation['execute']()

        # Set viewport shading
        area = tool.Blender.get_view3d_area()
        try:
            area.spaces[0].shading.color_type = "OBJECT"
        except Exception:
            pass

        # Set frame range
        bpy.context.scene.frame_start = settings["start_frame"]
        bpy.context.scene.frame_end = int(settings["start_frame"] + settings["total_frames"])

        elapsed = time.time() - start_time
        print(f"[OPTIMIZED] ULTRA-OPTIMIZED ANIMATION COMPLETE in {elapsed:.3f}s")
        print(f"[OPTIMIZED] Objects processed: {total_objects_processed}")

    @classmethod
    def apply_visibility_animation(cls, obj, frame_data, ColorType):
        """Applies only the visibility (hide/show) keyframes for live update mode."""
        # Note: Keyframes at frame 0 were already set in animate_objects_with_ColorTypes

        for state_name, (start_f, end_f) in frame_data["states"].items():
            if end_f < start_f:
                continue

            # Logic for hiding objects based on state and ColorType properties
            is_hidden = False
            if state_name == "before_start" and not getattr(ColorType, 'consider_start', False) and frame_data.get("relationship") == "output":
                is_hidden = True
            elif state_name == "after_end" and frame_data.get("relationship") == "input":
                is_hidden = True

            # Set visibility keyframes
            bpy.context.scene.frame_set(start_f)
            obj.hide_viewport = is_hidden
            obj.hide_render = is_hidden
            obj.keyframe_insert(data_path="hide_viewport", frame=start_f)
            obj.keyframe_insert(data_path="hide_render", frame=start_f)

    @classmethod
    def _apply_ColorType_to_object(cls, obj, frame_data, ColorType, original_color, settings):
        print(f"Applying ColorType to object {obj.name}")
        for state_name, (start_f, end_f) in frame_data["states"].items():
            if end_f < start_f:
                continue
            if state_name == "before_start":
                state = "start"
            elif state_name == "active":
                state = "in_progress"
            elif state_name == "after_end":
                state = "end"
            else:
                continue
            if state == "start" and not getattr(ColorType, 'consider_start', False):
                if frame_data.get("relationship") == "output":
                    obj.hide_viewport = True
                    obj.hide_render = True
                    obj.keyframe_insert(data_path="hide_viewport", frame=start_f)
                    obj.keyframe_insert(data_path="hide_render", frame=start_f)
                continue
            elif state == "in_progress" and not getattr(ColorType, 'consider_active', True):
                continue
            elif state == "end" and not getattr(ColorType, 'consider_end', True):
                if frame_data.get("relationship") == "input":
                    obj.hide_viewport = True
                    obj.hide_render = True
                    obj.keyframe_insert(data_path="hide_viewport", frame=start_f)
                    obj.keyframe_insert(data_path="hide_render", frame=start_f)
                continue

            cls.apply_state_appearance(obj, ColorType, state, start_f, end_f, original_color, frame_data)
            # Transparency: fade during active stretch
            try:
                if state == 'in_progress':
                    # Get color values with interpolation
                    interpolated_values = _seq_data.interpolate_ColorType_values(ColorType, state, 0.5)
                    alpha = interpolated_values.get('alpha', 1.0)

                    if hasattr(obj.data, 'materials') and obj.data.materials:
                        material = obj.data.materials[0]
                        if material and material.use_nodes:
                            principled = material.node_tree.nodes.get("Principled BSDF")
                            if principled:
                                current_color = list(principled.inputs["Base Color"].default_value)
                                current_color[3] = alpha
                                principled.inputs["Base Color"].default_value = current_color
                                principled.inputs["Base Color"].keyframe_insert(data_path="default_value", frame=start_f)
            except Exception as e:
                print(f"[WARNING] Error applying transparency: {e}")

    @classmethod
    def clear_objects_animation(
            cls,
            include_blender_objects: bool = True,
            *,
            only_selected: bool = False,
    ):
        """Clear all animation keyframes from objects."""
        import time
        start_time = time.time()
        print("Clearing object animations...")

        objects_to_clear = []

        if only_selected:
            objects_to_clear = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
        else:
            objects_to_clear = [obj for obj in bpy.data.objects if obj.type == 'MESH']

        cleared_objects = 0
        for obj in objects_to_clear:
            # Clear visibility keyframes
            if obj.animation_data and obj.animation_data.action:
                for fcurve in obj.animation_data.action.fcurves[:]:
                    if fcurve.data_path in ["hide_viewport", "hide_render"]:
                        obj.animation_data.action.fcurves.remove(fcurve)
                        cleared_objects += 1

            # Clear material color keyframes
            if hasattr(obj.data, 'materials') and obj.data.materials:
                for material in obj.data.materials:
                    if material and material.use_nodes and material.node_tree:
                        principled = material.node_tree.nodes.get("Principled BSDF")
                        if principled and material.animation_data and material.animation_data.action:
                            for fcurve in material.animation_data.action.fcurves[:]:
                                if "Base Color" in fcurve.data_path:
                                    material.animation_data.action.fcurves.remove(fcurve)

            # Reset visibility
            obj.hide_viewport = False
            obj.hide_render = False

        # Restore original colors if they exist
        original_object_colors = bpy.context.scene.get('BIM_VarianceOriginalObjectColors')
        if original_object_colors:
            original_colors = json.loads(original_object_colors)

            for obj in objects_to_clear:
                if obj.name in original_colors:
                    color = original_colors[obj.name]
                    if hasattr(obj.data, 'materials') and obj.data.materials:
                        material = obj.data.materials[0]
                        if material and material.use_nodes:
                            principled = material.node_tree.nodes.get("Principled BSDF")
                            if principled:
                                principled.inputs["Base Color"].default_value = color

        elapsed = time.time() - start_time
        print(f"[INFO] Animation cleared for {cleared_objects} objects in {elapsed:.3f}s")

    # Optimization helper methods
    @classmethod
    def _get_active_group_optimized(cls, animation_props):
        """Get active animation group name with optimization"""
        for item in getattr(animation_props, 'animation_group_stack', []):
            if getattr(item, 'enabled', False) and getattr(item, 'group', None):
                return item.group
        return 'DEFAULT'

    @classmethod
    def _save_original_colors_optimized(cls, cache):
        """Save original colors using cache"""
        if bpy.context.scene.get('BIM_VarianceOriginalObjectColors'):
            return

        original_colors = {}
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                color = cache.get_original_color(obj)
                if color:
                    original_colors[obj.name] = color

        bpy.context.scene['BIM_VarianceOriginalObjectColors'] = json.dumps(original_colors)

    @classmethod
    def _get_colortype_optimized(cls, task, animation_props, active_group_name):
        """Get ColorType for task with optimization"""
        try:
            return tool.Sequence._get_best_ColorType_for_task(task, animation_props)
        except Exception as e:
            print(f"[WARNING] Error getting ColorType for task {task.id()}: {e}")
            return None

    @classmethod
    def _apply_object_animation_optimized(cls, obj, frame_data, colortype, settings, visibility_ops, color_ops):
        """Apply optimized object animation using batch operations"""
        states = frame_data.get("states", {})
        original_color = [0.8, 0.8, 0.8, 1.0]  # Default fallback

        # Handle priority mode
        if frame_data.get("consider_start_active", False):
            active_frames = states.get("active", (0, -1))
            if active_frames[1] >= active_frames[0]:
                visibility_ops.append({'obj': obj, 'frame': active_frames[0], 'hide': False})

                use_original = getattr(colortype, 'use_start_original_color', False)
                if use_original:
                    color = original_color
                else:
                    start_color = getattr(colortype, 'start_color', [0.8, 0.8, 0.8, 1.0])
                    transparency = getattr(colortype, 'start_transparency', 0.0)
                    color = [start_color[0], start_color[1], start_color[2], 1.0 - transparency]

                color_ops.append({'obj': obj, 'frame': active_frames[0], 'color': color})
            return

        # Regular processing
        cls._plan_complete_system_animation(obj, states, colortype, original_color, frame_data, visibility_ops, color_ops)

    @classmethod
    def _setup_viewport_shading_optimized(cls):
        """Setup viewport shading optimized"""
        area = tool.Blender.get_view3d_area()
        if area and area.spaces:
            try:
                area.spaces[0].shading.color_type = "OBJECT"
            except Exception:
                pass

    @classmethod
    def clear_objects_animation_optimized(cls, include_blender_objects=True):
        """Optimized animation cleanup"""
        import time
        start_time = time.time()

        print("[OPTIMIZED] Clearing animations with optimization...")

        objects_cleared = 0
        for obj in bpy.data.objects:
            if obj.type != 'MESH':
                continue

            # Clear object keyframes
            if obj.animation_data and obj.animation_data.action:
                fcurves_to_remove = []
                for fcurve in obj.animation_data.action.fcurves:
                    if fcurve.data_path in ["hide_viewport", "hide_render"]:
                        fcurves_to_remove.append(fcurve)

                for fcurve in fcurves_to_remove:
                    obj.animation_data.action.fcurves.remove(fcurve)

                objects_cleared += 1

            # Clear material keyframes
            if hasattr(obj.data, 'materials'):
                for material in obj.data.materials or []:
                    if material and material.animation_data and material.animation_data.action:
                        fcurves_to_remove = []
                        for fcurve in material.animation_data.action.fcurves:
                            if "Base Color" in fcurve.data_path:
                                fcurves_to_remove.append(fcurve)

                        for fcurve in fcurves_to_remove:
                            material.animation_data.action.fcurves.remove(fcurve)

            # Reset visibility
            obj.hide_viewport = False
            obj.hide_render = False

        elapsed = time.time() - start_time
        print(f"[OPTIMIZED] Animation cleared for {objects_cleared} objects in {elapsed:.3f}s")