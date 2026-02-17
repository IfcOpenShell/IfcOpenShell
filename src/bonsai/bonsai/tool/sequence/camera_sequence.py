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
import math
import mathutils
from mathutils import Vector
import traceback

from .props_sequence import PropsSequence
import bonsai.tool as tool


class CameraSequence:
    """Mixin class for managing 4D animation and snapshot cameras."""


    @classmethod
    def is_bonsai_camera(cls, obj):
        """Checks if an object is a camera managed by Bonsai 4D/Snapshot tools."""
        if not obj or obj.type != 'CAMERA':
            return False
        # Most reliable way is to check the custom property
        if obj.get('camera_context') in ['animation', 'snapshot']:
            return True
        # Fallback to name conventions for compatibility
        if '4D_Animation_Camera' in obj.name or 'Snapshot_Camera' in obj.name:
            return True
        return False


    @classmethod
    def is_bonsai_animation_camera(cls, obj):
            """Checks if an object is a camera specific for Animation Settings."""
            if not obj or obj.type != 'CAMERA':
                return False

            # DURING ANIMATION: Only allow STATIC cameras
            try:
                anim_props = cls.get_animation_props()
                if getattr(anim_props, 'is_animation_created', False):
                    # During active animation, only show static cameras
                    if (obj.get('camera_type') == 'STATIC' or
                        '4D_Camera_Static' in obj.name or
                        obj.get('orbit_mode') == 'NONE'):
                        return True
                    else:
                        # Don't show 360°/ping-pong cameras during animation
                        return False
            except Exception:
                pass

            # Normal behavior
            # Primary identification is through custom property
            if obj.get('camera_context') == 'animation':
                return True
            # Fallback to name convention (ensuring it's not a snapshot camera)
            if '4D_Animation_Camera' in obj.name and 'Snapshot' not in obj.name:
                return True
            # Also include static cameras created from animation align view
            if (obj.get('camera_type') == 'STATIC' and
                obj.get('created_from') == 'animation_align_view'):
                return True
            return False


    @classmethod
    def is_bonsai_snapshot_camera(cls, obj):
            """Checks if an object is a camera specific for Snapshot Settings."""
            if not obj or obj.type != 'CAMERA':
                return False
            # Primary identification is through custom property
            if obj.get('camera_context') == 'snapshot':
                return True
            # Fallback to name convention
            if 'Snapshot_Camera' in obj.name:
                return True
            return False


    @classmethod
    def _get_active_schedule_bbox(cls):
            """Return (center (Vector), dims (Vector), obj_list) for active WorkSchedule products.
            Fallbacks to visible mesh objects if empty."""
            import bpy, mathutils
            ws = cls.get_active_work_schedule()
            objs = []
            if ws:
                try:
                    products = cls.get_work_schedule_products(ws)  # IFC entities
                    want_ids = {p.id() for p in products if hasattr(p, "id")}
                    for obj in bpy.data.objects:
                        try:
                            if not hasattr(obj, "type") or obj.type not in {"MESH", "CURVE", "SURFACE", "META", "FONT"}:
                                continue
                            if (ifc_id := tool.Blender.get_ifc_definition_id(obj)) and ifc_id in want_ids:
                                objs.append(obj)
                        except Exception:
                            continue
                except Exception:
                    pass

            if not objs:
                # Fallback: all visible mesh objs
                objs = [o for o in bpy.data.objects if getattr(o, "type", "") == "MESH" and not o.hide_get()]

            if not objs:
                c = mathutils.Vector((0.0, 0.0, 0.0))
                d = mathutils.Vector((10.0, 10.0, 5.0))
                return c, d, []

            mins = mathutils.Vector(( 1e18,  1e18,  1e18))
            maxs = mathutils.Vector((-1e18, -1e18, -1e18))
            for o in objs:
                try:
                    for corner in o.bound_box:
                        wc = o.matrix_world @ mathutils.Vector(corner)
                        mins.x = min(mins.x, wc.x); mins.y = min(mins.y, wc.y); mins.z = min(mins.z, wc.z)
                        maxs.x = max(maxs.x, wc.x); maxs.y = max(maxs.y, wc.y); maxs.z = max(maxs.z, wc.z)
                except Exception:
                    continue
            center = (mins + maxs) * 0.5
            dims = (maxs - mins)
            return center, dims, objs


    @classmethod
    def _get_or_create_target(cls, center, name="4D_OrbitTarget", should_hide=False):
        name = name or "4D_OrbitTarget"
        obj = bpy.data.objects.get(name)
        if obj is None:
            obj = bpy.data.objects.new(name, None)
            obj.empty_display_type = 'PLAIN_AXES'
            try:
                bpy.context.collection.objects.link(obj)
            except Exception:
                bpy.context.scene.collection.objects.link(obj)
        obj.location = center
        obj.hide_viewport = should_hide
        obj.hide_render = should_hide
        return obj


    @classmethod
    def add_animation_camera(cls):
        """Create a camera using Animation Settings (Camera/Orbit) and optionally animate it."""
        import bpy, math, mathutils
        from mathutils import Vector
        import traceback

        
        
        anim = cls.get_animation_props()
        camera_props = anim.camera_orbit  
        ws_props = cls.get_work_schedule_props()
        
        current_orbit_mode = getattr(camera_props, 'orbit_mode', 'NONE')
        existing_camera = bpy.context.scene.camera
        
        center, dims, _ = cls._get_active_schedule_bbox()
        
        cam_data = bpy.data.cameras.new("4D_Animation_Camera")
        cam_data.lens = camera_props.camera_focal_mm
        cam_data.clip_start = max(0.0001, camera_props.camera_clip_start)

        
        clip_end = camera_props.camera_clip_end
        auto_scale = max(dims.x, dims.y, dims.z) * 5.0  
        cam_data.clip_end = max(clip_end, auto_scale)


        cam_obj = bpy.data.objects.new("4D_Animation_Camera", cam_data)
        cam_obj['is_4d_camera'] = True
        cam_obj['is_animation_camera'] = True
        cam_obj['camera_context'] = 'animation'
        try:
            bpy.context.collection.objects.link(cam_obj)
        except Exception:
            bpy.context.scene.collection.objects.link(cam_obj)

        
        target_name = f"4D_OrbitTarget_for_{cam_obj.name}"
        if camera_props.look_at_mode == "OBJECT" and camera_props.look_at_object:
            target = camera_props.look_at_object
        else:
            # Check if animation cameras are globally hidden for target visibility
            cameras_globally_hidden = getattr(camera_props, 'hide_all_animation_cameras', False)
            target = cls._get_or_create_target(center, target_name, should_hide=cameras_globally_hidden)

        
        tcon = cam_obj.constraints.new(type='TRACK_TO')
        tcon.target = target
        tcon.track_axis = 'TRACK_NEGATIVE_Z'
        tcon.up_axis = 'UP_Y'

        
        if camera_props.orbit_radius_mode == "AUTO":
            
            base = max(dims.x, dims.y)
            if base > 0:
                r = base * 1.5  # More generous factor
            else:
                r = 15.0  # Larger fallback
        else:
            r = max(0.01, camera_props.orbit_radius)

        z = center.z + camera_props.orbit_height
        sign = -1.0 if camera_props.orbit_direction == "CW" else 1.0
        angle0 = 0.0  # Fixed at 0 degrees (Start Angle only controls offset_factor)

        # Initial placement (fixed at 0 degrees, Start Angle only controls offset_factor)
        initial_x = center.x + r  # Start at angle 0 (east position)
        initial_y = center.y
        cam_obj.location = Vector((initial_x, initial_y, z))

        # Orbit animation
        mode = camera_props.orbit_mode
        
        if mode == "NONE":

            # For STATIC mode, generate unique name and markers
            base_name = "4D_Camera_Static"
            counter = 1
            unique_name = base_name
            while bpy.data.objects.get(unique_name):
                unique_name = f"{base_name}_{counter:02d}"
                counter += 1

            cam_obj.name = unique_name
            cam_obj.data.name = unique_name
            cam_obj['orbit_mode'] = 'NONE'
            cam_obj['camera_type'] = 'STATIC'

            bpy.context.scene.camera = cam_obj
            return cam_obj

        # Determine timeline
        try:
            settings = cls.get_animation_settings()
            if settings:
                total_frames_4d = int(settings["total_frames"])
                start_frame = int(settings["start_frame"])
            else:
                raise Exception("No animation settings")
        except Exception as e:
            total_frames_4d = 250
            start_frame = 1

        # Timeline calculation
        if camera_props.orbit_use_4d_duration:
            end_frame = start_frame + max(1, total_frames_4d - 1)
        else:
            end_frame = start_frame + int(max(1, camera_props.orbit_duration_frames))

        dur = max(1, end_frame - start_frame)

        # Orbit animation implementation
        # Keep original method but with fluidity improvements
        if camera_props.orbit_path_method == "FOLLOW_PATH":
            cls._create_follow_path_orbit(cam_obj, center, r, z, angle0, start_frame, end_frame, sign, mode)
        else:
            cls._create_keyframe_orbit(cam_obj, center, r, z, angle0, start_frame, end_frame, sign, mode)

        bpy.context.scene.camera = cam_obj
        return cam_obj

    @classmethod
    def add_snapshot_camera(cls):
        """Create a camera specifically for Snapshot Settings."""
        import bpy, math, mathutils
        from mathutils import Vector

        # Props - use animation structure for basic configuration
        anim = cls.get_animation_props()
        camera_props = anim.camera_orbit


        # Get scene bounding box
        center, dims, _ = cls._get_active_schedule_bbox()

        # Camera data
        cam_data = bpy.data.cameras.new("Snapshot_Camera")
        cam_data.lens = camera_props.camera_focal_mm
        cam_data.clip_start = max(0.0001, camera_props.camera_clip_start)

        # Scale clip_end with scene size
        clip_end = camera_props.camera_clip_end
        auto_scale = max(dims.length * 2.0, 100.0)
        cam_data.clip_end = max(clip_end, auto_scale)


        cam_obj = bpy.data.objects.new("Snapshot_Camera", cam_data)
        cam_obj['is_4d_camera'] = True
        cam_obj['is_snapshot_camera'] = True
        cam_obj['camera_context'] = 'snapshot'
        
        try:
            bpy.context.collection.objects.link(cam_obj)
        except Exception:
            bpy.context.scene.collection.objects.link(cam_obj)

        # Position camera at a reasonable distance from scene center
        radius = max(dims.length * 1.5, 20.0)
        height = center.z + dims.z * 0.5
        
        cam_obj.location = Vector((center.x + radius, center.y + radius, height))
        
        # Create and track target
        target = cls._get_or_create_target(center, "Snapshot_Target")
        tcon = cam_obj.constraints.new(type='TRACK_TO')
        tcon.target = target
        tcon.track_axis = 'TRACK_NEGATIVE_Z'
        tcon.up_axis = 'UP_Y'
        
        bpy.context.scene.camera = cam_obj

        # --- ALWAYS CREATE PARENT EMPTY (needed for 3D texts) ---
        try:
            # Create the parent Empty if it doesn't exist
            parent_name = "Schedule_Display_Parent"
            parent_empty = bpy.data.objects.get(parent_name)
            if not parent_empty:
                parent_empty = bpy.data.objects.new(parent_name, None)
                bpy.context.scene.collection.objects.link(parent_empty)
                parent_empty.empty_display_type = 'PLAIN_AXES'
                parent_empty.empty_display_size = 2
            else:
                pass

            # Now create the 3D Legend HUD if enabled
            anim_props = cls.get_animation_props()
            camera_props = anim_props.camera_orbit
            legend_hud_enabled = getattr(camera_props, "enable_3d_legend_hud", False)
            show_3d_texts = getattr(camera_props, "show_3d_schedule_texts", False)

            legend_hud_exists = any(obj.get("is_3d_legend_hud", False) for obj in bpy.data.objects)
            if not legend_hud_exists and legend_hud_enabled:
                if show_3d_texts:
                    bpy.ops.bim.setup_3d_legend_hud()
                else:
                    bpy.ops.bim.setup_3d_legend_hud()
                    # Hide immediately if the option is disabled
                    for obj in bpy.data.objects:
                        if obj.get("is_3d_legend_hud", False):
                            obj.hide_viewport = True
                            obj.hide_render = True
            elif legend_hud_exists:
                pass

        except Exception as e:
            import traceback
            traceback.print_exc()

        # --- CREATE 3D TEXTS LATER (so they can be parented to the Empty) ---
        # 3D texts are created when adding the camera, not when creating the snapshot
        try:
            # Get basic configurations for texts
            ws_props = cls.get_work_schedule_props()
            active_schedule_id = getattr(ws_props, "active_work_schedule_id", None)

            if active_schedule_id:
                import bonsai.tool as tool
                work_schedule = tool.Ifc.get().by_id(active_schedule_id)
                schedule_name = work_schedule.Name if work_schedule and hasattr(work_schedule, 'Name') else 'No Schedule'

                # --- CREATE STATIC TEXTS FOR THE SNAPSHOT ---
                try:
                    from datetime import datetime
                    snapshot_date = datetime.now()  # Default date

                    # Try to get the actual snapshot date
                    snapshot_date_str = getattr(ws_props, "visualisation_start", None)
                    if snapshot_date_str and snapshot_date_str != "-":
                        try:
                            snapshot_date = cls.parse_isodate_datetime(snapshot_date_str)
                        except Exception:
                            pass

                    snapshot_settings = {
                        "start": snapshot_date,
                        "finish": snapshot_date,
                        "start_frame": bpy.context.scene.frame_current,
                        "total_frames": 1,
                    }

                    # Create specific static texts for snapshot
                    cls.create_text_objects_static(snapshot_settings)

                except Exception as static_error:
                    # FALLBACK: Create basic texts if the above fails
                    cls._create_basic_snapshot_texts(schedule_name)

                # --- APPLY VISIBILITY ACCORDING TO THE UI CHECKBOX ---
                anim_props = cls.get_animation_props()
                camera_props = anim_props.camera_orbit
                should_hide = not getattr(camera_props, "show_3d_schedule_texts", False)

                # Update the collection after creating it
                texts_collection = bpy.data.collections.get("Schedule_Display_Texts")
                if texts_collection:
                    texts_collection.hide_viewport = should_hide
                    texts_collection.hide_render = should_hide

                # Auto-arrange texts for default positioning
                try:
                    bpy.ops.bim.arrange_schedule_texts()
                except Exception as e:
                    pass

            else:
                pass

        except Exception as e:
            import traceback
            traceback.print_exc()
        
        return cam_obj


    @classmethod
    def align_snapshot_camera_to_view(cls):
        """Aligns the active snapshot camera to the current 3D view."""
        import bpy

        # 1. Find the active 3D viewport
        area = next((a for a in bpy.context.screen.areas if a.type == 'VIEW_3D'), None)
        if not area:
            raise Exception("No 3D viewport found.")

        space = next((s for s in area.spaces if s.type == 'VIEW_3D'), None)
        if not space:
            raise Exception("No 3D space data found.")

        # 2. Get the active camera from the scene
        cam_obj = bpy.context.scene.camera
        if not cam_obj:
            raise Exception("No active camera in the scene.")

        # 3. (Optional) Verify it's a snapshot camera
        if not cls.is_bonsai_snapshot_camera(cam_obj):
            pass

        # 4. Get the view matrix and apply it to the camera
        # The view matrix gives us the transformation from the view's perspective.
        # We need its inverse to position the camera correctly in the world.
        region_3d = space.region_3d
        if region_3d:
            cam_obj.matrix_world = region_3d.view_matrix.inverted()
        else:
            raise Exception("Could not get 3D view region data.")
        

    @classmethod
    def align_animation_camera_to_view(cls):
        """
        Aligns the active animation camera to the 3D view and converts it to static.
        """
        import bpy

        area = next((a for a in bpy.context.screen.areas if a.type == 'VIEW_3D'), None)
        space = next((s for s in area.spaces if s.type == 'VIEW_3D'), None) if area else None
        cam_obj = bpy.context.scene.camera

        if not all([area, space, cam_obj]):
            raise Exception("Camera or 3D view not found.")

        # Clear animation and camera constraints to stop the orbit
        if cam_obj.animation_data:
            cam_obj.animation_data_clear()
        for c in list(cam_obj.constraints):
            cam_obj.constraints.remove(c)

        # Move the camera to the view position
        region_3d = space.region_3d
        if region_3d:
            cam_obj.matrix_world = region_3d.view_matrix.inverted()
        else:
            raise Exception("Could not get 3D region data.")

        # (Key Step) Update the UI so that the orbit mode is set to "Static"
        try:
            anim_props = cls.get_animation_props()
            camera_props = anim_props.camera_orbit
            camera_props.orbit_mode = 'NONE' # 'NONE' se muestra como "Static" en la UI
        except Exception as e:
            pass


    @classmethod
    def update_animation_camera(cls, cam_obj):
        """
        Updates an existing 4D camera. Cleans its old data and applies
        the current UI configuration.
        """
        import bpy, math, mathutils
        from mathutils import Vector

        # 1. Clear previous camera configuration - but preserve TRACK_TO for static cameras
        if cam_obj.animation_data:
            cam_obj.animation_data_clear()

        # Check if this is a static camera before clearing constraints
        is_static_camera = cam_obj.get('camera_type') == 'STATIC' or cam_obj.get('orbit_mode') == 'NONE'

        # PRESERVE offset_factor from Follow Path constraint (set by Start Angle callback)
        preserved_offset_factor = None
        for c in cam_obj.constraints:
            if c.type == 'FOLLOW_PATH':
                preserved_offset_factor = c.offset_factor
                break

        for c in list(cam_obj.constraints):
            # For static cameras, preserve TRACK_TO constraint
            if is_static_camera and c.type == 'TRACK_TO':
                continue
            cam_obj.constraints.remove(c)

        # Clear the orbit path and target if they exist (unique names per camera) - but preserve target for static cameras
        path_name = f"4D_OrbitPath_for_{cam_obj.name}"
        path_obj = bpy.data.objects.get(path_name)
        if path_obj:
            bpy.data.objects.remove(path_obj, do_unlink=True)

        # Try both target naming conventions
        target_names = [f"4D_Target_for_{cam_obj.name}", f"4D_OrbitTarget_for_{cam_obj.name}"]
        for target_name in target_names:
            tgt_obj = bpy.data.objects.get(target_name)
            if tgt_obj:
                # For static cameras, preserve the target object
                if is_static_camera:
                    pass
                else:
                    bpy.data.objects.remove(tgt_obj, do_unlink=True)


        # 1.5. Save panel values to the camera object BEFORE updating
        anim = cls.get_animation_props()
        camera_props = anim.camera_orbit


        # Save all panel values to the camera
        cam_obj['orbit_mode'] = camera_props.orbit_mode
        cam_obj['orbit_radius'] = camera_props.orbit_radius
        cam_obj['orbit_height'] = camera_props.orbit_height
        cam_obj['orbit_start_angle_deg'] = camera_props.orbit_start_angle_deg
        cam_obj['orbit_direction'] = camera_props.orbit_direction
        cam_obj['orbit_radius_mode'] = camera_props.orbit_radius_mode
        cam_obj['orbit_path_shape'] = camera_props.orbit_path_shape
        cam_obj['orbit_path_method'] = camera_props.orbit_path_method
        cam_obj['interpolation_mode'] = camera_props.interpolation_mode


        # 2. Re-apply all settings, using the logic of add_animation_camera
        camera_props = anim.camera_orbit

        # Recalculate target and dimensions
        center, dims, _ = cls._get_active_schedule_bbox()
        target_name = f"4D_OrbitTarget_for_{cam_obj.name}"

        if camera_props.look_at_mode == "OBJECT" and camera_props.look_at_object:
            target = camera_props.look_at_object
        else:
            target = cls._get_or_create_target(center, target_name)

        # Reconfigure camera data (lens, clipping)
        cam_data = cam_obj.data
        cam_data.lens = camera_props.camera_focal_mm
        cam_data.clip_start = camera_props.camera_clip_start
        cam_data.clip_end = max(camera_props.camera_clip_end, max(dims.x, dims.y, dims.z) * 5.0)

        # Check if we're in static mode BEFORE repositioning the camera
        mode = camera_props.orbit_mode
        
        if mode == "NONE":
            # In static mode, do NOT reposition the camera or add tracking constraints
            # Keep the manually aligned position intact
            pass
        else:
            # Recalculate position only for non-static modes
            if camera_props.orbit_radius_mode == "AUTO":
                r = max(dims.x, dims.y) * 1.5 if max(dims.x, dims.y) > 0 else 15.0
            else:
                r = max(0.01, camera_props.orbit_radius)

            z = center.z + camera_props.orbit_height
            angle0 = 0.0  # Fixed at 0 degrees (Start Angle only controls offset_factor)
            # Fixed position at 0 degrees (Start Angle only controls offset_factor)
            cam_obj.location = Vector((center.x + r, center.y, z))

            # Re-create tracking constraint only for non-static modes
            tcon = cam_obj.constraints.new(type='TRACK_TO')
            tcon.target = target
            tcon.track_axis = 'TRACK_NEGATIVE_Z'
            tcon.up_axis = 'UP_Y'

        # Re-create orbit animation if configured
        if mode != "NONE":
            settings = cls.get_animation_settings()
            start_frame = settings["start_frame"]

            if camera_props.orbit_use_4d_duration:
                end_frame = start_frame + settings["total_frames"] -1
            else:
                end_frame = start_frame + int(camera_props.orbit_duration_frames)

            sign = -1.0 if camera_props.orbit_direction == "CW" else 1.0

            if camera_props.orbit_path_method == "FOLLOW_PATH":
                # Pass preserved offset_factor to maintain Start Angle setting
                cls._create_follow_path_orbit(cam_obj, center, r, z, angle0, start_frame, end_frame, sign, mode, preserved_offset_factor)
            else:
                cls._create_keyframe_orbit(cam_obj, center, r, z, angle0, start_frame, end_frame, sign, mode)

        bpy.context.scene.camera = cam_obj
        return cam_obj

    @classmethod
    def clear_camera_animation(cls, cam_obj):
        """
        Robustly cleans the animation, constraints, and associated objects (path, target) of a camera.
        """
        import bpy
        if not cam_obj:
            return

        try:
            # 1. Clear animation data (keyframes)
            if getattr(cam_obj, "animation_data", None):
                cam_obj.animation_data_clear()

            # 2. Clear constraints - but preserve TRACK_TO for static cameras
            is_static_camera = cam_obj.get('camera_type') == 'STATIC' or cam_obj.get('orbit_mode') == 'NONE'

            for c in list(getattr(cam_obj, "constraints", [])):
                try:
                    # For static cameras, preserve TRACK_TO constraint
                    if is_static_camera and c.type == 'TRACK_TO':
                        continue
                    cam_obj.constraints.remove(c)
                except Exception:
                    pass

            # 3. Clear auxiliary objects (path and target) - but preserve target for static cameras
            path_name = f"4D_OrbitPath_for_{cam_obj.name}"
            path_obj = bpy.data.objects.get(path_name)
            if path_obj:
                bpy.data.objects.remove(path_obj, do_unlink=True)

            target_name = f"4D_OrbitTarget_for_{cam_obj.name}"
            tgt_obj = bpy.data.objects.get(target_name)
            if tgt_obj:
                # For static cameras, preserve the target object
                if is_static_camera:
                    pass
                else:
                    bpy.data.objects.remove(tgt_obj, do_unlink=True)

        except Exception as e:
            pass


    @classmethod
    def _create_follow_path_orbit(cls, cam_obj, center, radius, z, angle0, start_frame, end_frame, sign, mode, preserved_offset_factor=None):
        import bpy, math, mathutils
        anim = cls.get_animation_props()
        camera_props = anim.camera_orbit
        path_object = None

        if camera_props.orbit_path_shape == 'CUSTOM' and camera_props.custom_orbit_path:
            path_object = camera_props.custom_orbit_path
            # Check if animation cameras are globally hidden
            cameras_globally_hidden = getattr(camera_props, 'hide_all_animation_cameras', False)
            # Hide path if either the orbit path setting OR the global camera visibility is disabled
            should_hide_path = camera_props.hide_orbit_path or cameras_globally_hidden
            path_object.hide_viewport = should_hide_path
            path_object.hide_render = should_hide_path
        else:
            path_name = f"4D_OrbitPath_for_{cam_obj.name}"

            # Check if path already exists (to preserve Follow Path constraint connection)
            existing_path = bpy.data.objects.get(path_name)
            if existing_path and existing_path.data:
                path_object = existing_path
                curve = path_object.data
                # Clear existing splines to rebuild
                curve.splines.clear()
            else:
                # Create new path only if it doesn't exist
                curve = bpy.data.curves.new(path_name, type='CURVE')
                curve.dimensions = '3D'
                curve.resolution_u = 64
                path_object = bpy.data.objects.new(path_name, curve)
                try:
                    bpy.context.collection.objects.link(path_object)
                except Exception:
                    bpy.context.scene.collection.objects.link(path_object)

            # Check if animation cameras are globally hidden
            cameras_globally_hidden = getattr(camera_props, 'hide_all_animation_cameras', False)
            # Hide path if either the orbit path setting OR the global camera visibility is disabled
            should_hide_path = camera_props.hide_orbit_path or cameras_globally_hidden

            path_object.hide_viewport = should_hide_path
            path_object.hide_render = should_hide_path

            # Create a mathematically perfect circle with only 4 Bezier points
            spline = curve.splines.new('BEZIER')
            spline.bezier_points.add(3)  # 4 points total (0,1,2,3)
            
            # Calculate perfect circle control points (4-point Bezier circle)
            kappa = 4 * (math.sqrt(2) - 1) / 3  # Magic number for perfect Bezier circle
            
            points = [
                (radius, 0),          # Right
                (0, radius),          # Top  
                (-radius, 0),         # Left
                (0, -radius)          # Bottom
            ]
            
            for i, (x, y) in enumerate(points):
                bp = spline.bezier_points[i]
                bp.co = mathutils.Vector((center.x + x, center.y + y, z))
                bp.handle_left_type = 'ALIGNED'
                bp.handle_right_type = 'ALIGNED'
                
                # Perfect circle handles using kappa constant
                if i == 0:    # Right point
                    bp.handle_left = mathutils.Vector((center.x + x, center.y + y - radius * kappa, z))
                    bp.handle_right = mathutils.Vector((center.x + x, center.y + y + radius * kappa, z))
                elif i == 1:  # Top point  
                    bp.handle_left = mathutils.Vector((center.x + x + radius * kappa, center.y + y, z))
                    bp.handle_right = mathutils.Vector((center.x + x - radius * kappa, center.y + y, z))
                elif i == 2:  # Left point
                    bp.handle_left = mathutils.Vector((center.x + x, center.y + y + radius * kappa, z))
                    bp.handle_right = mathutils.Vector((center.x + x, center.y + y - radius * kappa, z))
                else:         # Bottom point
                    bp.handle_left = mathutils.Vector((center.x + x - radius * kappa, center.y + y, z))
                    bp.handle_right = mathutils.Vector((center.x + x + radius * kappa, center.y + y, z))
                    
            spline.use_cyclic_u = True

        # Check if Follow Path constraint already exists (to preserve offset_factor from Start Angle)
        existing_fcon = None
        for constraint in cam_obj.constraints:
            if constraint.type == 'FOLLOW_PATH':
                existing_fcon = constraint
                break

        if existing_fcon:
            # Use existing constraint (preserves offset_factor set by Start Angle callback)
            fcon = existing_fcon
            fcon.target = path_object  # Update target to new path
        else:
            # Create new constraint only if none exists
            fcon = cam_obj.constraints.new(type='FOLLOW_PATH')
            fcon.target = path_object

            # Restore preserved offset_factor from Update operation (Start Angle setting)
            if preserved_offset_factor is not None:
                fcon.offset_factor = preserved_offset_factor
            else:
                pass

        # RESTORED: Settings that worked well with tracking
        fcon.use_curve_follow = True   # Allows the object to follow the curve's rotation
        fcon.use_fixed_location = True  # Maintains position on the path

        def key_offset(offset, frame):
            fcon.offset_factor = offset
            fcon.keyframe_insert("offset_factor", frame=frame)

        # Start Angle now controls offset_factor via callback
        # Get current offset_factor from constraint (set by Start Angle callback or preserved from Update)
        current_offset = fcon.offset_factor
        if preserved_offset_factor is not None:
            pass
        else:
            pass

        if sign > 0:  # Counter-clockwise
            s0, s1 = current_offset, current_offset + 1.0
        else:  # Clockwise
            s0, s1 = current_offset, current_offset - 1.0

        if mode == "CIRCLE_360":
            # SIMPLE METHOD: Only 2 keyframes for perfectly smooth rotation
            key_offset(s0, start_frame)
            key_offset(s1, end_frame)
        elif mode == "PINGPONG":
            # SIMPLE PINGPONG: Only 3 keyframes for smooth constant velocity
            mid_frame = start_frame + (end_frame - start_frame) // 2
            
            # Go from start angle to 180° and back - perfectly linear
            key_offset(s0, start_frame)                    # Start position
            key_offset(s0 + (s1 - s0) * 0.5, mid_frame)   # Opposite side (180°)
            key_offset(s0, end_frame)                      # Back to start

        # AGGRESSIVE FORCE: Always LINEAR for 360° (ignore all user settings)
        if cam_obj.animation_data and cam_obj.animation_data.action:
            for fcurve in cam_obj.animation_data.action.fcurves:
                if "offset_factor" in fcurve.data_path:
                    if mode == "CIRCLE_360":
                        # Force LINEAR for all keyframes - no exceptions
                        for kf in fcurve.keyframe_points:
                            kf.interpolation = 'LINEAR'
                            # Also reset handles to avoid any Bezier remnants
                            kf.handle_left_type = 'AUTO'
                            kf.handle_right_type = 'AUTO'
                        fcurve.update()
                    else:
                        # PINGPONG: Always use LINEAR for consistency and smoothness
                        for kf in fcurve.keyframe_points:
                            kf.interpolation = 'LINEAR'

        # RESTORED: Add Track-To constraint for proper camera aiming
        target_name = f"4D_Target_for_{cam_obj.name}"
        target_obj = bpy.data.objects.get(target_name)
        if target_obj:
            tcon = cam_obj.constraints.new(type='TRACK_TO')
            tcon.target = target_obj
            tcon.track_axis = 'TRACK_NEGATIVE_Z'
            tcon.up_axis = 'UP_Y'

    @classmethod
    def _create_empty_pivot_orbit(cls, cam_obj, center, radius, z, angle0, start_frame, end_frame, sign):
        """OPTIMIZED method for 360° orbit using Empty pivot - maximum smoothness"""
        import bpy, math
        
        # 1. Create Empty pivot at center
        empty_name = f"Camera_Pivot_{cam_obj.name}"
        
        # Remove existing pivot if it exists
        if empty_name in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects[empty_name], do_unlink=True)
        
        # Create new empty at center
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=center)
        pivot = bpy.context.active_object
        pivot.name = empty_name
        
        # 2. Clear any existing camera constraints to avoid conflicts
        for constraint in list(cam_obj.constraints):
            cam_obj.constraints.remove(constraint)
        
        # 3. Parent camera to empty and position it
        cam_obj.parent = pivot
        cam_obj.parent_type = 'OBJECT'
        cam_obj.location = (radius, 0, z - center.z)  # Relative to pivot
        
        # 4. Set initial rotation for starting angle
        pivot.rotation_euler[2] = angle0
        
        # 5. Animate pivot rotation with only 2 keyframes (PERFECTION!)
        pivot.rotation_euler[2] = angle0
        pivot.keyframe_insert("rotation_euler", index=2, frame=start_frame)
        
        pivot.rotation_euler[2] = angle0 + sign * 2 * math.pi
        pivot.keyframe_insert("rotation_euler", index=2, frame=end_frame)
        
        # 6. FORCE LINEAR interpolation for constant velocity + micro-jitter elimination
        if pivot.animation_data and pivot.animation_data.action:
            for fcurve in pivot.animation_data.action.fcurves:
                if fcurve.data_path == "rotation_euler" and fcurve.array_index == 2:
                    for kf in fcurve.keyframe_points:
                        kf.interpolation = 'LINEAR'
                        kf.handle_left_type = 'AUTO'
                        kf.handle_right_type = 'AUTO'
                    fcurve.update()
                    
                    # MEJORA: Lock other rotation axes to prevent micro-jitter
                    pivot.lock_rotation[0] = True  # Lock X rotation
                    pivot.lock_rotation[1] = True  # Lock Y rotation
                    # Z rotation remains unlocked for animation
                    
                    
        # 7. Add Track-To constraint to camera for proper aim
        tcon = cam_obj.constraints.new(type='TRACK_TO')
        tcon.target = bpy.data.objects.get(f"4D_Target_for_{cam_obj.name}")  # Use existing target
        if tcon.target:
            tcon.track_axis = 'TRACK_NEGATIVE_Z'
            tcon.up_axis = 'UP_Y'

    @classmethod
    def _create_keyframe_orbit(cls, cam_obj, center, radius, z, angle0, start_frame, end_frame, sign, mode):
        import math, mathutils
        anim = cls.get_animation_props()
        camera_props = anim.camera_orbit

        def pt(theta):
            x = center.x + radius * math.cos(theta)
            y = center.y + radius * math.sin(theta)
            return mathutils.Vector((x, y, z))

        def key_loc(obj, loc, frame):
            obj.location = loc
            obj.keyframe_insert("location", frame=frame)

        if mode == "CIRCLE_360":
            # Use Empty pivot with only 2 keyframes for perfect smoothness
            
            # 1. Create Empty pivot at center
            import bpy
            empty_name = f"Camera_Pivot_{cam_obj.name}"
            
            # Remove existing pivot if it exists
            if empty_name in bpy.data.objects:
                bpy.data.objects.remove(bpy.data.objects[empty_name], do_unlink=True)
            
            # Create new empty at center
            bpy.ops.object.empty_add(type='PLAIN_AXES', location=center)
            pivot = bpy.context.active_object
            pivot.name = empty_name
            
            # 2. Parent camera to empty and position it
            cam_obj.parent = pivot
            cam_obj.parent_type = 'OBJECT'
            cam_obj.location = (radius, 0, z - center.z)  # Relative to pivot
            
            # 3. Set initial rotation for starting angle
            pivot.rotation_euler[2] = angle0
            
            # 4. Animate pivot rotation with only 2 keyframes
            pivot.rotation_euler[2] = angle0
            pivot.keyframe_insert("rotation_euler", index=2, frame=start_frame)
            
            pivot.rotation_euler[2] = angle0 + sign * 2 * math.pi
            pivot.keyframe_insert("rotation_euler", index=2, frame=end_frame)
            
            # 5. AGGRESSIVE FORCE LINEAR interpolation for constant velocity
            if pivot.animation_data and pivot.animation_data.action:
                for fcurve in pivot.animation_data.action.fcurves:
                    if fcurve.data_path == "rotation_euler" and fcurve.array_index == 2:
                        for kf in fcurve.keyframe_points:
                            kf.interpolation = 'LINEAR'
                            kf.handle_left_type = 'AUTO'
                            kf.handle_right_type = 'AUTO'
                        fcurve.update()
        elif mode == "PINGPONG":
            # SIMPLE PINGPONG: Only 3 keyframes for smooth constant velocity
            mid_frame = start_frame + (end_frame - start_frame) // 2
            
            # Go from start angle to 180° and back - perfectly linear
            key_loc(cam_obj, pt(angle0), start_frame)                    # Start position
            key_loc(cam_obj, pt(angle0 + sign * math.pi), mid_frame)     # Opposite side (180°) 
            key_loc(cam_obj, pt(angle0), end_frame)                      # Back to start

        # AGGRESSIVE FORCE: Always LINEAR for 360° keyframe method  
        if cam_obj.animation_data and cam_obj.animation_data.action:
            for fcurve in cam_obj.animation_data.action.fcurves:
                if fcurve.data_path == "location":
                    if mode == "CIRCLE_360":
                        # Force LINEAR for all keyframes - no exceptions
                        for kp in fcurve.keyframe_points:
                            kp.interpolation = 'LINEAR'
                            kp.handle_left_type = 'AUTO'
                            kp.handle_right_type = 'AUTO'
                        fcurve.update()
                    else:
                        # PINGPONG: Always use LINEAR for consistency
                        for kp in fcurve.keyframe_points:
                            kp.interpolation = 'LINEAR'
