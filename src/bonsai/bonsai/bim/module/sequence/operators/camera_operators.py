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

# --- HELPER FUNCTIONS ---

def _is_animation_camera_simple(obj):
    """Simplified detection for animation cameras without external dependencies"""
    if not obj or obj.type != 'CAMERA':
        return False

    # Check by camera_context property (primary method)
    if obj.get('camera_context') == 'animation':
        return True

    # Fallback to name pattern (ensure it's not a snapshot camera)
    if '4D_Animation_Camera' in obj.name and 'Snapshot' not in obj.name:
        return True

    return False

def _is_snapshot_camera_simple(obj):
    """Simplified detection for snapshot cameras without external dependencies"""
    if not obj or obj.type != 'CAMERA':
        return False

    # Check by camera_context property (primary method)
    if obj.get('camera_context') == 'snapshot':
        return True

    # Fallback to name pattern
    if 'Snapshot_Camera' in obj.name:
        return True

    return False

def _get_animation_cameras(self, context):
    """Callback that returns ONLY the Animation cameras."""
    print("🔥 _get_animation_cameras called")
    items = []
    total_cameras = 0
    animation_cameras = 0

    try:
        # Check if animation cameras are hidden by the UI toggle
        try:
            anim_props = tool.Sequence.get_animation_props()
            camera_props = anim_props.camera_orbit if anim_props else None
            cameras_hidden = getattr(camera_props, 'hide_all_animation_cameras', False) if camera_props else False

            if cameras_hidden:
                print("📹 Animation cameras are hidden by UI toggle - returning empty list")
                items = [('NONE', '<Cameras Hidden>', 'Animation cameras are hidden by visibility toggle')]
                return items
        except Exception as e:
            print(f"[WARNING] Could not check camera visibility state: {e}")

        for obj in bpy.data.objects:
            if obj.type == 'CAMERA':
                total_cameras += 1
                camera_context = obj.get('camera_context', 'N/A')

                # Use simplified detection function
                if _is_animation_camera_simple(obj):
                    animation_cameras += 1
                    items.append((obj.name, obj.name, f'Animation Camera 4D'))
                    print(f"📹 Animation camera found: {obj.name} (context: {camera_context})")

        print(f"📹 Animation camera scan: {animation_cameras}/{total_cameras} cameras are animation cameras")

    except Exception as e:
        print(f"[ERROR] Error in _get_animation_cameras: {e}")
        import traceback
        traceback.print_exc()

    if not items:
        items = [('NONE', '<No animation cameras>', 'No animation cameras detected')]
        print("📹 No animation cameras found, showing empty selector")

    print(f"📹 Returning {len(items)} animation camera items")
    return items

def _get_snapshot_cameras(self, context):
    """Callback that returns ONLY the Snapshot cameras."""
    print("🔥 _get_snapshot_cameras called")
    items = []
    total_cameras = 0
    snapshot_cameras = 0

    try:
        for obj in bpy.data.objects:
            if obj.type == 'CAMERA':
                total_cameras += 1
                camera_context = obj.get('camera_context', 'N/A')

                # Use simplified detection function
                if _is_snapshot_camera_simple(obj):
                    snapshot_cameras += 1
                    items.append((obj.name, obj.name, f'Snapshot Camera 4D'))
                    print(f"📸 Snapshot camera found: {obj.name} (context: {camera_context})")

        print(f"📸 Snapshot camera scan: {snapshot_cameras}/{total_cameras} cameras are snapshot cameras")

    except Exception as e:
        print(f"[ERROR] Error in _get_snapshot_cameras: {e}")
        import traceback
        traceback.print_exc()

    if not items:
        items = [('NONE', '<No snapshot cameras>', 'No snapshot cameras detected')]
        print("📸 No snapshot cameras found, showing empty selector")

    print(f"📸 Returning {len(items)} snapshot camera items")
    return items


# --- DEBUG OPERATORS ---

class RefreshCameraSelectors(bpy.types.Operator):
    bl_idname = "bim.refresh_camera_selectors"
    bl_label = "Refresh Camera Selectors"
    bl_description = "Force refresh of camera selector dropdowns to show current cameras"
    bl_options = {"REGISTER"}

    def execute(self, context):
        try:
            print(f"🔄 FORCE Camera selectors refresh requested")

            # Force refresh by accessing the properties
            import bonsai.tool as tool
            anim_props = tool.Sequence.get_animation_props()
            camera_props = anim_props.camera_orbit

            # Force update the enum properties by accessing them
            current_anim = getattr(camera_props, 'active_animation_camera', 'NONE')
            current_snapshot = getattr(camera_props, 'active_snapshot_camera', 'NONE')

            print(f"📹 Current animation camera: {current_anim}")
            print(f"📸 Current snapshot camera: {current_snapshot}")

            # Test the callback functions directly
            print(f"🧪 Testing callback functions directly:")
            try:
                anim_items = _get_animation_cameras(self, context)
                snap_items = _get_snapshot_cameras(self, context)
            except Exception as e:
                print(f"[ERROR] Callback error: {e}")

            # Force UI refresh
            try:
                for window in context.window_manager.windows:
                    for area in window.screen.areas:
                        area.tag_redraw()
            except Exception as e:
                print(f"[ERROR] UI refresh error: {e}")

            self.report({'INFO'}, "Camera selectors refresh attempted")
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Failed to refresh selectors: {e}")
            print(f"[ERROR] RefreshCameraSelectors error: {e}")
            import traceback
            traceback.print_exc()
            return {'CANCELLED'}


class ForceCameraPropertyUpdate(bpy.types.Operator): # type: ignore
    bl_idname = "bim.force_camera_property_update"
    bl_label = "FORCE: Update Camera Properties"
    bl_description = "Force complete update of camera selector properties"
    bl_options = {"REGISTER"}

    def execute(self, context):
        try:
            print(f"🔥 FORCING camera property updates...")

            import bonsai.tool as tool
            anim_props = tool.Sequence.get_animation_props()
            camera_props = anim_props.camera_orbit

            # Method 1: Try to force property updates by setting to dummy values
            try:
                old_anim = getattr(camera_props, 'active_animation_camera', 'NONE')
                old_snap = getattr(camera_props, 'active_snapshot_camera', 'NONE')

                print(f"📹 Old animation camera: {old_anim}")
                print(f"📸 Old snapshot camera: {old_snap}")

                # Force property refresh by setting to different value then back
                camera_props.active_animation_camera = 'NONE'
                camera_props.active_snapshot_camera = 'NONE'

                # Test if we have any real cameras
                anim_items = _get_animation_cameras(self, context)
                snap_items = _get_snapshot_cameras(self, context)

                print(f"📹 Available animation cameras: {[item[0] for item in anim_items if item[0] != 'NONE']}")
                print(f"📸 Available snapshot cameras: {[item[0] for item in snap_items if item[0] != 'NONE']}")

                # Set back to a real camera if available
                if len(anim_items) > 0 and anim_items[0][0] != 'NONE':
                    camera_props.active_animation_camera = anim_items[0][0]
                    print(f"📹 Set animation camera to: {anim_items[0][0]}")

                if len(snap_items) > 0 and snap_items[0][0] != 'NONE':
                    camera_props.active_snapshot_camera = snap_items[0][0]
                    print(f"📸 Set snapshot camera to: {snap_items[0][0]}")

            except Exception as e:
                print(f"[ERROR] Property update error: {e}")

            # Method 2: Force UI refresh
            for area in context.screen.areas:
                area.tag_redraw()

            # Method 3: Update depsgraph
            bpy.context.view_layer.update()

            self.report({'INFO'}, "Force update completed")
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Force update failed: {e}")
            print(f"[ERROR] ForceCameraPropertyUpdate error: {e}")
            import traceback
            traceback.print_exc()
            return {'CANCELLED'}


class SetActiveAnimationCamera(bpy.types.Operator): # type: ignore
    bl_idname = "bim.set_active_animation_camera"
    bl_label = "Set Active Animation Camera"
    bl_description = "Manually set the active animation camera"
    bl_options = {"REGISTER", "UNDO"}

    camera_name: bpy.props.StringProperty(name="Camera Name")

    def execute(self, context):
        try:
            if not self.camera_name or self.camera_name == 'NONE':
                self.report({'WARNING'}, "No camera specified")
                return {'CANCELLED'}

            # Find the camera object
            cam_obj = bpy.data.objects.get(self.camera_name)
            if not cam_obj or cam_obj.type != 'CAMERA':
                self.report({'ERROR'}, f"Camera '{self.camera_name}' not found")
                return {'CANCELLED'}

            # Verify it's an animation camera
            if not _is_animation_camera_simple(cam_obj):
                self.report({'ERROR'}, f"'{self.camera_name}' is not an animation camera")
                return {'CANCELLED'}

            # Set as active camera
            import bonsai.tool as tool
            anim_props = tool.Sequence.get_animation_props()
            camera_props = anim_props.camera_orbit
            camera_props.active_animation_camera = self.camera_name

            # Also set as scene camera
            context.scene.camera = cam_obj

            self.report({'INFO'}, f"Set '{self.camera_name}' as active animation camera")
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Failed to set camera: {e}")
            return {'CANCELLED'}


class SetActiveSnapshotCamera(bpy.types.Operator): # type: ignore
    bl_idname = "bim.set_active_snapshot_camera"
    bl_label = "Set Active Snapshot Camera"
    bl_description = "Manually set the active snapshot camera"
    bl_options = {"REGISTER", "UNDO"}

    camera_name: bpy.props.StringProperty(name="Camera Name")

    def execute(self, context):
        try:
            if not self.camera_name or self.camera_name == 'NONE':
                self.report({'WARNING'}, "No camera specified")
                return {'CANCELLED'}

            # Find the camera object
            cam_obj = bpy.data.objects.get(self.camera_name)
            if not cam_obj or cam_obj.type != 'CAMERA':
                self.report({'ERROR'}, f"Camera '{self.camera_name}' not found")
                return {'CANCELLED'}

            # Verify it's a snapshot camera
            if not _is_snapshot_camera_simple(cam_obj):
                self.report({'ERROR'}, f"'{self.camera_name}' is not a snapshot camera")
                return {'CANCELLED'}

            # Set as active camera
            import bonsai.tool as tool
            anim_props = tool.Sequence.get_animation_props()
            camera_props = anim_props.camera_orbit
            camera_props.active_snapshot_camera = self.camera_name

            # Also set as scene camera
            context.scene.camera = cam_obj

            self.report({'INFO'}, f"Set '{self.camera_name}' as active snapshot camera")
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Failed to set camera: {e}")
            return {'CANCELLED'}


class TestCameraDetection(bpy.types.Operator): # type: ignore
    bl_idname = "bim.test_camera_detection"
    bl_label = "TEST: Camera Detection"
    bl_description = "Quick test to see what cameras are detected right now"
    bl_options = {"REGISTER"}

    def execute(self, context):

        # Basic test without complex dependencies
        total_cameras = 0
        animation_found = 0
        snapshot_found = 0

        for obj in bpy.data.objects: # type: ignore
            if obj.type == 'CAMERA':
                total_cameras += 1
                name = obj.name
                context_prop = obj.get('camera_context', 'None')

                print(f"📷 Camera: {name}")
                print(f"   camera_context: {context_prop}")

                # Test direct detection with simplified functions
                if _is_animation_camera_simple(obj):
                    animation_found += 1
                elif _is_snapshot_camera_simple(obj):
                    snapshot_found += 1
                else:
                    print(f"   ⚪ OTHER CAMERA")

        print(f"\n📊 RESULT: {total_cameras} total, {animation_found} animation, {snapshot_found} snapshot")

        # Test callbacks directly
        try:
            anim_items = _get_animation_cameras(self, context)
            snap_items = _get_snapshot_cameras(self, context)
            print(f"Animation callback returned: {len(anim_items)} items")
            print(f"Snapshot callback returned: {len(snap_items)} items")
        except Exception as e:
            print(f"[ERROR] Callback error: {e}")

        self.report({'INFO'}, f"Test complete: {animation_found} animation, {snapshot_found} snapshot cameras")
        return {'FINISHED'}


class DebugListAllCameras(bpy.types.Operator): # type: ignore
    bl_idname = "bim.debug_list_all_cameras"
    bl_label = "Debug: List All Cameras"
    bl_description = "List all cameras with their properties for debugging"
    bl_options = {"REGISTER"}

    def execute(self, context):
        try:
            import bonsai.tool as tool

            print("\n" + "="*60)
            print("🔍 DEBUG: LISTING ALL CAMERAS")
            print("="*60)

            total_cameras = 0
            animation_cameras = 0
            snapshot_cameras = 0
            other_cameras = 0

            for obj in bpy.data.objects: # type: ignore
                if obj.type == 'CAMERA':
                    total_cameras += 1

                    # Get all custom properties
                    camera_context = obj.get('camera_context', 'N/A')
                    is_4d_camera = obj.get('is_4d_camera', False)
                    is_animation_camera = obj.get('is_animation_camera', False)
                    is_snapshot_camera = obj.get('is_snapshot_camera', False)

                    # Test the detection functions
                    is_bonsai_animation = tool.Sequence.is_bonsai_animation_camera(obj)
                    is_bonsai_snapshot = tool.Sequence.is_bonsai_snapshot_camera(obj)

                    print(f"\n📷 Camera: {obj.name}")
                    print(f"   📋 Properties:")
                    print(f"      camera_context: {camera_context}")
                    print(f"      is_4d_camera: {is_4d_camera}")
                    print(f"      is_animation_camera: {is_animation_camera}")
                    print(f"      is_snapshot_camera: {is_snapshot_camera}")
                    print(f"   🔍 Detection results:")
                    print(f"      is_bonsai_animation_camera: {is_bonsai_animation}")
                    print(f"      is_bonsai_snapshot_camera: {is_bonsai_snapshot}")

                    if is_bonsai_animation:
                        animation_cameras += 1
                    elif is_bonsai_snapshot:
                        snapshot_cameras += 1
                    else:
                        other_cameras += 1
                        print(f"   ⚪ OTHER CAMERA")

            print(f"\n📊 SUMMARY:")
            print(f"   Total cameras: {total_cameras}")
            print(f"   Animation cameras: {animation_cameras}")
            print(f"   Snapshot cameras: {snapshot_cameras}")
            print(f"   Other cameras: {other_cameras}")

            # Test the callback functions
            try:
                animation_items = _get_animation_cameras(self, context)
                snapshot_items = _get_snapshot_cameras(self, context)
                print(f"   Animation selector items: {len(animation_items)}")
                for item in animation_items:
                    print(f"      - {item[0]}: {item[1]}")
                print(f"   Snapshot selector items: {len(snapshot_items)}")
                for item in snapshot_items:
                    print(f"      - {item[0]}: {item[1]}")
            except Exception as e:
                print(f"   [ERROR] Error in callbacks: {e}")

            print("="*60 + "\n")

            self.report({'INFO'}, f"Listed {total_cameras} cameras ({animation_cameras} animation, {snapshot_cameras} snapshot)")
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Failed to list cameras: {e}")
            return {'CANCELLED'}


# --- OPERATORS ---

class ResetCameraSettings(bpy.types.Operator):
    bl_idname = "bim.reset_camera_settings" # type: ignore
    bl_label = "Reset Camera Settings"
    bl_description = "Reset camera and orbit settings to their default values (HUD and UI settings are preserved)"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        try:
            anim_props = tool.Sequence.get_animation_props()
            camera_props = anim_props.camera_orbit

            # --- Reset all properties to their default values ---

            # Camera Properties
            camera_props.camera_focal_mm = 35.0
            camera_props.camera_clip_start = 0.1
            camera_props.camera_clip_end = 10000.0

            # Orbit Properties
            camera_props.orbit_mode = "CIRCLE_360"
            camera_props.orbit_radius_mode = "AUTO"
            camera_props.orbit_radius = 10.0
            camera_props.orbit_height = 8.0
            camera_props.orbit_start_angle_deg = 0.0
            camera_props.orbit_direction = "CCW"
            
            # Look At Properties
            camera_props.look_at_mode = "AUTO"
            camera_props.look_at_object = None # Clear any selected object

            # Trajectory and Animation Properties
            camera_props.orbit_path_shape = "CIRCLE"
            camera_props.custom_orbit_path = None # Limpiar cualquier trayectoria personalizada
            camera_props.orbit_path_method = "FOLLOW_PATH"
            camera_props.interpolation_mode = "LINEAR"
            camera_props.bezier_smoothness_factor = 0.35
            camera_props.orbit_use_4d_duration = True
            camera_props.orbit_duration_frames = 250.0
            camera_props.hide_orbit_path = False

            self.report({'INFO'}, "Camera and orbit settings have been reset")
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Reset failed: {str(e)}")
            return {'CANCELLED'}


class Align4DCameraToView(bpy.types.Operator): # type: ignore
    bl_idname = "bim.align_4d_camera_to_view"
    bl_label = "Align Active Camera to View"
    bl_description = "Aligns the active 4D camera to the current 3D view and sets it to static"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        if not context.scene or not context.scene.camera:
            return False
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                return True
        return False

    def execute(self, context):
        try:
            cam_obj = context.scene.camera
            if not cam_obj:
                self.report({'ERROR'}, "No active camera in scene.")
                return {'CANCELLED'}

            rv3d = None
            for area in context.screen.areas:
                if area.type == 'VIEW_3D':
                    rv3d = area.spaces.active.region_3d
                    break
            
            if not rv3d:
                self.report({'ERROR'}, "No active 3D viewport found.")
                return {'CANCELLED'}

            cam_obj.matrix_world = rv3d.view_matrix.inverted()

            tool.Sequence.clear_camera_animation(cam_obj)
            
            anim_props = tool.Sequence.get_animation_props()
            camera_props = anim_props.camera_orbit
            camera_props.orbit_mode = 'NONE'

            if getattr(camera_props, 'enable_text_hud', False):
                try:
                    bpy.ops.bim.refresh_schedule_hud()
                except Exception as e:
                    print(f"HUD refresh after align failed: {e}")
            
            self.report({'INFO'}, "Camera aligned to view and set to static.")
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Failed to align camera: {str(e)}")
            return {'CANCELLED'}

# --- ANIMATION CAMERA DELETION OPERATOR (NEW) ---
 # --- ANIMATION CAMERA DELETION OPERATOR (NEW) ---
class DeleteAnimationCamera(bpy.types.Operator): # type: ignore
    """Deletes a 4D Animation camera and its associated objects."""
    bl_idname = "bim.delete_animation_camera"
    bl_label = "Delete an Animation Camera"
    bl_options = {'REGISTER', 'UNDO'}

    camera_to_delete: bpy.props.EnumProperty(
        name="Animation Camera",
        description="Select the Animation camera to delete",
        items=_get_animation_cameras
    )

    def execute(self, context):
        cam_name = self.camera_to_delete
        if cam_name == "NONE" or not cam_name:
            self.report({'INFO'}, "No camera selected to delete.")
            return {'CANCELLED'}

        cam_obj = bpy.data.objects.get(cam_name)
        if not cam_obj:
            self.report({'ERROR'}, f"Camera '{cam_name}' not found.")
            return {'CANCELLED'}

        # Objects associated with the animation camera
        path_name = f"4D_OrbitPath_for_{cam_name}"
        target_name = f"4D_OrbitTarget_for_{cam_name}"
        objects_to_remove = [cam_obj]
        if bpy.data.objects.get(path_name): objects_to_remove.append(bpy.data.objects[path_name])
        if bpy.data.objects.get(target_name): objects_to_remove.append(bpy.data.objects[target_name])

        for obj in objects_to_remove:
            bpy.data.objects.remove(obj, do_unlink=True)
        self.report({'INFO'}, f"Successfully deleted '{cam_name}' and associated objects.")
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


# --- SNAPSHOT CAMERA DELETION OPERATOR (NEW) ---
class DeleteSnapshotCamera(bpy.types.Operator): # type: ignore
    """Deletes a Snapshot camera and its associated objects."""
    bl_idname = "bim.delete_snapshot_camera"
    bl_label = "Delete a Snapshot Camera"
    bl_options = {'REGISTER', 'UNDO'}

    camera_to_delete: bpy.props.EnumProperty(
        name="Snapshot Camera",
        description="Select the Snapshot camera to delete",
        items=_get_snapshot_cameras
    )

    def execute(self, context):
        cam_name = self.camera_to_delete
        if cam_name == "NONE" or not cam_name:
            self.report({'INFO'}, "No camera selected to delete.")
            return {'CANCELLED'}

        cam_obj = bpy.data.objects.get(cam_name)
        if not cam_obj:
            self.report({'ERROR'}, f"Camera '{cam_name}' not found.")
            return {'CANCELLED'}

        # Objects associated with the snapshot camera
        target_name = "Snapshot_Target"
        objects_to_remove = [cam_obj]
        if bpy.data.objects.get(target_name): objects_to_remove.append(bpy.data.objects[target_name])

        for obj in objects_to_remove:
            bpy.data.objects.remove(obj, do_unlink=True)
        self.report({'INFO'}, f"Successfully deleted '{cam_name}' and associated objects.")
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


# ... (the rest of the camera operators like AddSnapshotCamera and AddAnimationCamera do not change) ...
class AddSnapshotCamera(bpy.types.Operator): # type: ignore
    bl_idname = "bim.add_snapshot_camera"
    bl_label = "Add Snapshot Camera"
    bl_description = "Create a new static camera positioned for snapshot viewing"
    bl_options = {"REGISTER", "UNDO"}
    def execute(self, context):
        try:
            cam_obj = tool.Sequence.add_snapshot_camera()
            
            # *** FIX FOR SNAPSHOT 3D TEXT ANIMATION ISSUE ***
            # Only refresh HUD if there's already an existing animation - prevents registering
            # animation handlers for static snapshot-only usage
            try:
                anim_props = tool.Sequence.get_animation_props()
                camera_props = anim_props.camera_orbit

                # Check if an animation has been created before (check for animated objects)
                has_existing_animation = False
                for obj in bpy.data.objects:
                    if (obj.animation_data and obj.animation_data.action) or obj.get('is_animated_by_4d', False):
                        has_existing_animation = True
                        break

                # Check if there are existing 3D texts that were created with animation
                has_animated_texts = False
                texts_collection = bpy.data.collections.get("Schedule_Display_Texts")
                if texts_collection:
                    for obj in texts_collection.objects:
                        # If text object has animation settings, it was created with animation handler
                        if hasattr(obj, "data") and obj.data and obj.data.get("animation_settings"):
                            has_animated_texts = True
                            break

                if getattr(camera_props, 'enable_text_hud', False):
                    if has_existing_animation or has_animated_texts:
                        # There's already an animation, safe to refresh HUD
                        bpy.ops.bim.refresh_schedule_hud()
                        print("📸 Snapshot Camera: HUD refreshed (existing animation detected)")
                    else:
                        # First time snapshot camera creation - don't register animation handlers
                        print("📸 Snapshot Camera: Skipping HUD refresh to prevent animation handler registration")
                        print("📸 This prevents 3D text from animating in snapshot-only mode")

            except Exception as e:
                print(f"[WARNING] Snapshot Camera: Could not check for existing animation: {e}")

            # *** AUTO-UPDATE CAMERA SELECTOR ***
            # Force refresh of snapshot camera selector to show the new camera
            try:
                anim_props = tool.Sequence.get_animation_props()
                camera_props = anim_props.camera_orbit
                # Set the newly created camera as active in the selector
                camera_props.active_snapshot_camera = cam_obj.name
                print(f"📸 Snapshot camera selector updated: {cam_obj.name}")
            except Exception as e:
                print(f"[WARNING] Could not update snapshot camera selector: {e}")

            self.report({'INFO'}, f"Snapshot camera '{cam_obj.name}' created and set as active")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to create snapshot camera: {str(e)}")
            return {'CANCELLED'}

class AlignSnapshotCameraToView(bpy.types.Operator):
    bl_idname = "bim.align_snapshot_camera_to_view" # type: ignore
    bl_label = "Align Snapshot Camera to View"
    bl_description = "Align the snapshot camera to match the current 3D viewport view"
    bl_options = {'REGISTER', 'UNDO'}
    @classmethod
    def poll(cls, context):
        if not getattr(context.scene, "camera", None): return False
        for area in context.screen.areas:
            if area.type == 'VIEW_3D': return True
        return False
    def execute(self, context):
        try:
            tool.Sequence.align_snapshot_camera_to_view()

            # *** CREATE EMPTY 3D HUD RENDER AND 3D TEXTS FOR SNAPSHOT ***
            print("📊 Creating/updating 3D HUD components for snapshot camera...")
            try:
                # Create Empty parent if it doesn't exist
                parent_name = "Schedule_Display_Parent"
                parent_empty = bpy.data.objects.get(parent_name)
                if not parent_empty:
                    parent_empty = bpy.data.objects.new(parent_name, None)
                    bpy.context.scene.collection.objects.link(parent_empty)
                    parent_empty.empty_display_type = 'PLAIN_AXES'
                    parent_empty.empty_display_size = 2
                else:
                    print("📍 Using existing parent empty for camera")

                # Create 3D Legend HUD if enabled
                anim_props = tool.Sequence.get_animation_props()
                camera_props = anim_props.camera_orbit
                legend_hud_enabled = getattr(camera_props, "enable_3d_legend_hud", False)
                show_3d_texts = getattr(camera_props, "show_3d_schedule_texts", False)

                legend_hud_exists = any(obj.get("is_3d_legend_hud", False) for obj in bpy.data.objects)
                if not legend_hud_exists and legend_hud_enabled: # type: ignore
                    bpy.ops.bim.setup_3d_legend_hud()

                # Crear 3D texts si no existen
                texts_collection = bpy.data.collections.get("Schedule_Display_Texts")
                if not texts_collection or len(texts_collection.objects) == 0:
                    print("📝 Creating 3D texts for snapshot...")

                    # Get schedule data
                    ws_props = tool.Sequence.get_work_schedule_props()
                    active_schedule_id = getattr(ws_props, "active_work_schedule_id", None)

                    if active_schedule_id:
                        work_schedule = tool.Ifc.get().by_id(active_schedule_id)

                        from datetime import datetime
                        snapshot_date = datetime.now()
                        snapshot_date_str = getattr(ws_props, "visualisation_start", None)
                        if snapshot_date_str and snapshot_date_str != "-":
                            try:
                                snapshot_date = tool.Sequence.parse_isodate_datetime(snapshot_date_str)
                            except Exception:
                                pass

                        snapshot_settings = {
                            "start": snapshot_date,
                            "finish": snapshot_date,
                            "start_frame": bpy.context.scene.frame_current,
                            "total_frames": 1,
                        }

                        tool.Sequence.create_text_objects_static(snapshot_settings)

                        # *** APPLY VISIBILITY ACCORDING TO CHECKBOX ***
                        should_hide = not getattr(camera_props, "show_3d_schedule_texts", False)
                        texts_collection = bpy.data.collections.get("Schedule_Display_Texts")
                        if texts_collection:
                            texts_collection.hide_viewport = should_hide
                            texts_collection.hide_render = should_hide

                        # *** ORGANIZE AND ALIGN 3D TEXTS ***
                        try:
                            bpy.ops.bim.arrange_schedule_texts()
                        except Exception as arrange_e:
                            print(f"[WARNING] Could not arrange 3D texts: {arrange_e}")

                    else:
                        print("[WARNING] No active work schedule for 3D texts")
                else:
                    print("📸 3D schedule texts disabled")

            except Exception as hud_e:
                print(f"[WARNING] Could not create 3D HUD components: {hud_e}")

            self.report({'INFO'}, f"Snapshot camera aligned and 3D HUD components updated")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to align snapshot camera: {str(e)}")
            return {'CANCELLED'}

class AddAnimationCamera(bpy.types.Operator):
    bl_idname = "bim.add_animation_camera" # type: ignore
    bl_label = "Add Animation Camera"
    bl_description = "Create a new camera for Animation Settings with orbital animation"
    bl_options = {"REGISTER", "UNDO"}
    def execute(self, context):
        try:
            cam_obj = tool.Sequence.add_animation_camera()

            # Validate that camera was created successfully
            if not cam_obj:
                self.report({'ERROR'}, "Failed to create animation camera: Camera object is None")
                return {'CANCELLED'}

            # Validate that camera object has required attributes
            if not hasattr(cam_obj, 'select_set'):
                self.report({'ERROR'}, f"Camera object is invalid: {type(cam_obj)}")
                return {'CANCELLED'}

            bpy.ops.object.select_all(action='DESELECT')
            cam_obj.select_set(True)
            context.view_layer.objects.active = cam_obj

            # *** AUTO-UPDATE CAMERA SELECTOR ***
            # Force refresh of animation camera selector to show the new camera
            try:
                anim_props = tool.Sequence.get_animation_props()
                camera_props = anim_props.camera_orbit
                # Set the newly created camera as active in the selector
                camera_props.active_animation_camera = cam_obj.name
                print(f"📹 Animation camera selector updated: {cam_obj.name}")
            except Exception as e:
                print(f"[WARNING] Could not update animation camera selector: {e}")

            self.report({'INFO'}, f"Animation camera '{cam_obj.name}' created and set as active")
            return {'FINISHED'}
        except AttributeError as e:
            if "'NoneType' object has no attribute 'select_set'" in str(e):
                self.report({'ERROR'}, "Failed to create animation camera: Camera creation returned None. Check that you have an active work schedule with tasks.")
            else:
                self.report({'ERROR'}, f"Failed to create animation camera: {str(e)}")
            return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to create animation camera: {str(e)}")
            return {'CANCELLED'}


class UpdateCameraOnly(bpy.types.Operator): # type: ignore
    bl_idname = "bim.update_camera_only"
    bl_label = "Update Camera"
    bl_description = "Update selected camera with current panel settings (no animation creation)"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        try:
            print(f"🔄 UPDATE CAMERA ONLY: Updating camera without creating animation...")

            import bonsai.tool as tool
            anim_props = tool.Sequence.get_animation_props()
            camera_props = anim_props.camera_orbit

            # Get selected 4D camera
            selected_camera_name = getattr(camera_props, 'active_animation_camera', 'NONE')

            if selected_camera_name == 'NONE':
                self.report({'WARNING'}, "No 4D camera selected in selector")
                return {'CANCELLED'}

            # Ensure we have a string name
            if hasattr(selected_camera_name, 'name'):
                selected_camera_name = selected_camera_name.name
            elif not isinstance(selected_camera_name, str):
                selected_camera_name = str(selected_camera_name)

            # Find the selected camera object
            if selected_camera_name not in bpy.data.objects:
                self.report({'ERROR'}, f"Selected camera '{selected_camera_name}' not found")
                return {'CANCELLED'}

            selected_camera = bpy.data.objects[selected_camera_name]
            print(f"📹 UPDATE ONLY: Updating camera '{selected_camera_name}' with panel settings...")

            try:
                # 1. Save panel values to camera (same as Update Animation)
                print(f"💾 SAVING panel values to camera '{selected_camera_name}'...")
                selected_camera['orbit_mode'] = camera_props.orbit_mode
                selected_camera['orbit_radius'] = camera_props.orbit_radius
                selected_camera['orbit_height'] = camera_props.orbit_height
                selected_camera['orbit_start_angle_deg'] = camera_props.orbit_start_angle_deg
                selected_camera['orbit_direction'] = camera_props.orbit_direction
                selected_camera['orbit_radius_mode'] = camera_props.orbit_radius_mode
                selected_camera['orbit_path_shape'] = camera_props.orbit_path_shape
                selected_camera['orbit_path_method'] = camera_props.orbit_path_method
                selected_camera['interpolation_mode'] = camera_props.interpolation_mode


                # 2. Update basic camera properties
                if hasattr(selected_camera, 'data') and selected_camera.data:
                    selected_camera.data.lens = camera_props.camera_focal_mm
                    selected_camera.data.clip_start = camera_props.camera_clip_start
                    selected_camera.data.clip_end = camera_props.camera_clip_end

                # 3. Update camera using same logic as Update Animation (but no animation creation)
                tool.Sequence.update_animation_camera(selected_camera)

            except Exception as e:
                print(f"[ERROR] Camera update failed: {e}")
                self.report({'ERROR'}, f"Camera update failed: {e}")
                return {'CANCELLED'}

            # Force UI refresh
            for area in context.screen.areas:
                area.tag_redraw()

            self.report({'INFO'}, f"Camera '{selected_camera_name}' updated successfully")
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Update failed: {e}")
            print(f"[ERROR] Update error: {e}")
            return {'CANCELLED'}


class AddCameraByMode(bpy.types.Operator): # type: ignore
    bl_idname = "bim.add_camera_by_mode"
    bl_label = "Add Camera"
    bl_description = "Add camera based on selected orbit mode"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            animation_props = tool.Sequence.get_animation_props()
            camera_props = animation_props.camera_orbit
            orbit_mode = camera_props.orbit_mode

            print(f"🎬 Adding camera for orbit mode: {orbit_mode}")

            if orbit_mode in ['NONE']:
                # Create 4D Camera Static (animation camera with NONE mode)
                bpy.ops.bim.add_animation_camera()
                self.report({'INFO'}, "4D Camera Static created")
                print("📸 Created 4D Camera Static")

            elif orbit_mode in ['CIRCLE_360', 'PINGPONG']:
                # Create animation camera
                bpy.ops.bim.add_animation_camera()
                self.report({'INFO'}, "4D Camera Animation created")
                print("🎥 Created 4D Camera Animation")

            else:
                self.report({'WARNING'}, f"Unknown orbit mode: {orbit_mode}")
                print(f"[WARNING] Unknown orbit mode: {orbit_mode}")

            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Failed to add camera: {e}")
            print(f"[ERROR] Add camera error: {e}")
            return {'CANCELLED'}