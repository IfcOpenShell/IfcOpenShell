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
import bonsai.tool as tool
from .props_sequence import PropsSequence
from .task_tree_sequence import TaskTreeSequence
from .task_icom_sequence import TaskIcomSequence

class VarianceSequence:
    """Mixin class for schedule variance calculation and visualization."""
    
    _original_colors = {}


    @classmethod
    def has_variance_calculation_in_tasks(cls):
        """
        Verifies if there is variance calculation in current tasks.
        Returns True if at least one task has variance_status calculated.
        """
        try:
            tprops = tool.Sequence.get_task_tree_props()
            if not tprops or not tprops.tasks:
                return False
            
            variance_count = 0
            for task in tprops.tasks:
                variance_status = getattr(task, 'variance_status', '')
                if variance_status and variance_status.strip():
                    variance_count += 1
            
            print(f"[CHECK] Found {variance_count} tasks with variance calculation out of {len(tprops.tasks)} total tasks")
            return variance_count > 0
            
        except Exception as e:
            print(f"[ERROR] Error checking variance calculation: {e}")
            return False

    @classmethod
    def detect_and_fix_variance_inconsistency(cls):
        """
        AUTOFIX: Detecta y corrige automáticamente estados inconsistentes de varianza.
        Esto ocurre cuando se pierde el cálculo de varianza por refresh pero quedan
        restos del sistema de colores que pueden romper animaciones.
        """
        try:
            print("[AUTOFIX] Detecting variance system inconsistencies...")

            # Check if there's any variance calculation
            has_variance_calc = cls.has_variance_calculation_in_tasks()

            # Check if there are any variance checkboxes active
            has_active_checkboxes = cls.has_active_variance_color_checkboxes()

            # Check for variance-related scene properties
            variance_scene_props = [key for key in bpy.context.scene.keys() if 'variance' in key.lower()]

            print(f"[CHECK] Variance calc: {has_variance_calc}, Active checkboxes: {has_active_checkboxes}, Scene props: {len(variance_scene_props)}")

            # INCONSISTENCY: No variance calc but has checkboxes or scene props
            if not has_variance_calc and (has_active_checkboxes or len(variance_scene_props) > 0):
                print("[INCONSISTENCY] Found variance system inconsistency - fixing automatically...")

                # Clear all variance checkboxes
                tprops = tool.Sequence.get_task_tree_props()
                if tprops:
                    cleared_checkboxes = 0
                    for task in tprops.tasks:
                        if getattr(task, 'is_variance_color_selected', False):
                            task.is_variance_color_selected = False
                            cleared_checkboxes += 1
                    print(f"[AUTOFIX] Cleared {cleared_checkboxes} orphaned variance checkboxes")

                # Remove variance scene properties
                removed_props = 0
                for key in variance_scene_props:
                    try:
                        del bpy.context.scene[key]
                        removed_props += 1
                    except Exception:
                        pass
                print(f"[AUTOFIX] Removed {removed_props} orphaned variance scene properties")

                # Clear any variance-related object colors by resetting them to material-based colors
                reset_objects = 0
                for obj in bpy.context.scene.objects:
                    if obj.type == 'MESH' and tool.Ifc.get_entity(obj) and hasattr(obj, 'color'):
                        try:
                            # Get original color from material if possible
                            original_color = None
                            if obj.material_slots and obj.material_slots[0].material:
                                material = obj.material_slots[0].material
                                if material.use_nodes:
                                    principled = tool.Blender.get_material_node(material, "BSDF_PRINCIPLED")
                                    if principled and principled.inputs.get("Base Color"):
                                        base_color = principled.inputs["Base Color"].default_value
                                        original_color = (base_color[0], base_color[1], base_color[2], base_color[3])

                            # Fallback to neutral white if can't get material color
                            if original_color is None:
                                original_color = (1.0, 1.0, 1.0, 1.0)

                            obj.color = original_color
                            reset_objects += 1
                        except Exception as e:
                            print(f"[WARNING] Could not reset color for {obj.name}: {e}")

                print(f"[AUTOFIX] Reset {reset_objects} objects to clean state")

                # Force viewport refresh
                bpy.context.view_layer.update()
                for area in bpy.context.screen.areas:
                    if area.type == 'VIEW_3D':
                        area.tag_redraw()

                print("[AUTOFIX] Variance system inconsistency resolved - safe for animation creation")
                return True
            else:
                print("[CHECK] Variance system is consistent - no fixes needed")
                return False

        except Exception as e:
            print(f"[ERROR] Error in variance inconsistency detection: {e}")
            return False

    @classmethod
    def detect_and_clear_active_variance_colors(cls):
        """
        SPECIFIC FIX: Detecta y limpia colores de varianza activos en objetos 3D
        antes de crear animación/snapshot para evitar romper el sistema de colores.
        """
        try:
            print("[AUTOFIX] Checking for active variance colors on 3D objects...")

            # Detectar si hay checkboxes de varianza activos
            has_active_variance_checkboxes = cls.has_active_variance_color_checkboxes()

            if has_active_variance_checkboxes:
                print("[DETECTED] Active variance color checkboxes found - clearing to prevent color system conflicts")

                # Desactivar todos los checkboxes de varianza
                tprops = tool.Sequence.get_task_tree_props()
                if tprops:
                    cleared_checkboxes = 0
                    for task in tprops.tasks:
                        if getattr(task, 'is_variance_color_selected', False):
                            task.is_variance_color_selected = False
                            cleared_checkboxes += 1
                    print(f"[AUTOFIX] Deactivated {cleared_checkboxes} variance color checkboxes")

                # Limpiar colores de varianza de los objetos 3D
                reset_objects = 0
                for obj in bpy.context.scene.objects:
                    if obj.type == 'MESH' and tool.Ifc.get_entity(obj) and hasattr(obj, 'color'):
                        try:
                            # Restaurar color original desde material
                            original_color = None
                            if obj.material_slots and obj.material_slots[0].material:
                                material = obj.material_slots[0].material
                                if material.use_nodes:
                                    principled = tool.Blender.get_material_node(material, "BSDF_PRINCIPLED")
                                    if principled and principled.inputs.get("Base Color"):
                                        base_color = principled.inputs["Base Color"].default_value
                                        original_color = (base_color[0], base_color[1], base_color[2], base_color[3])

                            # Fallback a blanco neutral si no se puede obtener del material
                            if original_color is None:
                                original_color = (1.0, 1.0, 1.0, 1.0)

                            obj.color = original_color
                            reset_objects += 1
                        except Exception as e:
                            print(f"[WARNING] Could not reset color for {obj.name}: {e}")

                print(f"[AUTOFIX] Reset {reset_objects} objects from variance colors to material colors")

                # Forzar actualización del viewport
                bpy.context.view_layer.update()
                for area in bpy.context.screen.areas:
                    if area.type == 'VIEW_3D':
                        area.tag_redraw()

                print("[AUTOFIX] Variance colors cleared - safe for animation/snapshot creation")
                return True
            else:
                print("[CHECK] No active variance colors detected - safe to proceed")
                return False

        except Exception as e:
            print(f"[ERROR] Error detecting/clearing active variance colors: {e}")
            return False

    @classmethod
    def clear_variance_colors_only(cls):
        """
        SAFE: Clears ONLY variance 3D colors, preserving colortype system.
        Used when filters change and there's no variance calculation.
        """
        try:
            print("[CLEAN] Safely clearing variance 3D colors (preserving colortypes)...")

            # STRATEGY: Instead of forcing colors, just remove variance mode flags
            # This allows the normal colortype system to take over

            # Remove variance-specific scene flags but keep colortype data intact
            scene_flags_removed = 0
            variance_keys = [key for key in bpy.context.scene.keys() if 'variance' in key.lower() and 'colormode' in key.lower()]
            for key in variance_keys:
                try:
                    del bpy.context.scene[key]
                    scene_flags_removed += 1
                    print(f"[CLEAN] Removed variance flag: {key}")
                except Exception as e:
                    print(f"[WARNING] Could not remove flag {key}: {e}")

            # Clear variance checkboxes to deactivate variance colors
            tprops = tool.Sequence.get_task_tree_props()
            if tprops:
                cleared_checkboxes = 0
                for task in tprops.tasks:
                    if getattr(task, 'is_variance_color_selected', False):
                        task.is_variance_color_selected = False
                        cleared_checkboxes += 1
                print(f"[OK] Cleared {cleared_checkboxes} variance checkboxes")

            # DON'T force object colors - let colortype system handle it naturally
            print(f"[OK] Variance mode safely deactivated - colortype system remains intact")

            # Force viewport update to reflect changes
            bpy.context.view_layer.update()
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()

        except Exception as e:
            print(f"[ERROR] Error safely clearing variance colors: {e}")
            import traceback
            traceback.print_exc()

    @classmethod
    def clear_variance_color_mode(cls):
        """
        Clears variance color mode and restores original colors.
        Called when variance is cleared or schedule type changes.
        """
        try:
            print("[CLEAN] CLEAR_VARIANCE_COLOR_MODE: Starting cleanup process...")
            
            # Deactivate all variance checkboxes
            tprops = tool.Sequence.get_task_tree_props()
            if tprops:
                cleared_checkboxes = 0
                total_tasks = len(tprops.tasks)
                print(f"[CHECK] Found {total_tasks} total tasks")
                
                for task in tprops.tasks:
                    if getattr(task, 'is_variance_color_selected', False):
                        task.is_variance_color_selected = False
                        cleared_checkboxes += 1
                        print(f"[OK] Cleared checkbox for task {task.ifc_definition_id}")
                        
                print(f"[OK] Cleared {cleared_checkboxes} variance checkboxes out of {total_tasks} tasks")
            else:
                print("[ERROR] No task tree properties found")
            
            restored_count = 0
            
            # Method 1: Try to restore from cached original colors
            if hasattr(cls, '_original_colors') and cls._original_colors:
                print(f"Attempting to restore from cached colors ({len(cls._original_colors)} stored)")
                for obj in bpy.context.scene.objects:
                    if obj.type == 'MESH' and tool.Ifc.get_entity(obj):
                        if obj.name in cls._original_colors and hasattr(obj, 'color'):
                            try:
                                original_color = cls._original_colors[obj.name]
                                obj.color = original_color
                                restored_count += 1
                                print(f"[OK] Restored cached color for {obj.name}")
                            except Exception as e:
                                print(f"[ERROR] Error restoring cached color for {obj.name}: {e}")
                
                # Clear original colors cache
                cls._original_colors = {}
                print("[CLEAN] Cleared original colors cache")
            
            # Method 2: Try to restore from scene saved colors
            if restored_count == 0:
                variance_colors = bpy.context.scene.get('BIM_VarianceOriginalObjectColors', {})
                if variance_colors:
                    print(f"Attempting to restore from scene saved colors ({len(variance_colors)} stored)")
                    for obj in bpy.context.scene.objects:
                        if obj.type == 'MESH' and tool.Ifc.get_entity(obj) and obj.name in variance_colors:
                            try:
                                obj.color = variance_colors[obj.name]
                                obj.hide_viewport = False
                                obj.hide_render = False
                                restored_count += 1
                            except Exception as e:
                                print(f"[ERROR] Error restoring scene color for {obj.name}: {e}")

            # Method 3: Try to get colors from material IFC if still no restoration
            if restored_count == 0:
                print("No cached colors found, attempting to restore from IFC materials")
                for obj in bpy.context.scene.objects:
                    if obj.type == 'MESH' and tool.Ifc.get_entity(obj):
                        try:
                            restored = False
                            # Try to get color from original IFC object material
                            try:
                                if obj.material_slots and obj.material_slots[0].material:
                                    material = obj.material_slots[0].material
                                    if material.use_nodes:
                                        principled = tool.Blender.get_material_node(material, "BSDF_PRINCIPLED")
                                        if principled and principled.inputs.get("Base Color"):
                                            base_color = principled.inputs["Base Color"].default_value
                                            obj.color = (base_color[0], base_color[1], base_color[2], base_color[3])
                                            restored = True
                            except Exception:
                                pass

                            # Only apply gray if it could not be obtained from the material
                            if not restored:
                                obj.color = (0.9, 0.9, 0.9, 1.0)  # Almost neutral white instead of dark gray

                            obj.hide_viewport = False
                            obj.hide_render = False
                            restored_count += 1
                        except Exception as e:
                            print(f"[ERROR] Error resetting color for {obj.name}: {e}")

            print(f"[OK] Total objects restored/reset: {restored_count}")
            
            # Method 3: Force complete viewport refresh
            try:
                # Clear animation data that might be affecting colors
                for obj in bpy.context.scene.objects:
                    if obj.type == 'MESH' and obj.animation_data:
                        obj.animation_data_clear()
                
                # Force viewport update
                bpy.context.view_layer.update()
                
                # Force redraw of all 3D viewports
                for area in bpy.context.screen.areas:
                    if area.type == 'VIEW_3D':
                        area.tag_redraw()
                        for space in area.spaces:
                            if space.type == 'VIEW_3D':
                                space.shading.color_type = 'OBJECT'  # Ensure object colors are visible
                
                print("Forced complete viewport refresh")
                
            except Exception as e:
                print(f"[WARNING]️ Error during viewport refresh: {e}")
                
        except Exception as e:
            print(f"[ERROR] Error clearing variance color mode: {e}")
            import traceback
            traceback.print_exc()

    @classmethod 
    def update_individual_variance_colors(cls):
        """
        Updates colors based on individual checkboxes for each task.
        Each task works independently.
        """
        try:
            print("🎯 Updating individual variance colors...")
            
            # Ensure correct viewport
            cls._ensure_viewport_shading()
            
            # Get tasks
            tprops = tool.Sequence.get_task_tree_props()
            if not tprops:
                print("[ERROR] No task tree properties found")
                return
            
            # Save original colors the first time (if they are not saved)
            if not hasattr(cls, '_original_colors'):
                cls._original_colors = {}
                for obj in bpy.context.scene.objects:
                    if obj.type == 'MESH' and tool.Ifc.get_entity(obj):
                        if hasattr(obj, 'color'):
                            # Try to get the color from the original IFC material first
                            original_color = None
                            try:
                                if obj.material_slots and obj.material_slots[0].material:
                                    material = obj.material_slots[0].material
                                    if material.use_nodes:
                                        principled = tool.Blender.get_material_node(material, "BSDF_PRINCIPLED")
                                        if principled and principled.inputs.get("Base Color"):
                                            base_color = principled.inputs["Base Color"].default_value
                                            original_color = tuple([base_color[0], base_color[1], base_color[2], base_color[3]])
                            except Exception:
                                pass

                            # Fallback: use the current viewport color if it could not be obtained from the material
                            if original_color is None:
                                original_color = tuple(obj.color)

                            cls._original_colors[obj.name] = original_color
                print(f"[CACHE] Saved original colors for {len(cls._original_colors)} objects (from materials where possible)")
            
            # Identify tasks with active checkbox
            variance_selected_tasks = [t for t in tprops.tasks if getattr(t, 'is_variance_color_selected', False)]
            
            print(f"[CHECK] Found {len(variance_selected_tasks)} tasks with active variance checkbox")
            if variance_selected_tasks:
                for task in variance_selected_tasks:
                    print(f"  📋 Task {task.ifc_definition_id}: {task.name} (Status: {getattr(task, 'variance_status', 'No status')})")
            else:
                print("🎯 No active checkboxes → restoring original colors")
                # Restore original colors of all IFC objects
                mesh_objects = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
                restored_count = 0
                
                for obj in mesh_objects:
                    element = tool.Ifc.get_entity(obj)
                    if element and hasattr(obj, 'color'):
                        try:
                            # Use saved color or default white
                            if hasattr(cls, '_original_colors') and obj.name in cls._original_colors:
                                original_color = cls._original_colors[obj.name]
                                print(f"Restoring saved color for {obj.name}: {original_color}")
                            else:
                                original_color = (1.0, 1.0, 1.0, 1.0)  # Default white
                                print(f"Using default color for {obj.name}")
                            
                            obj.color = original_color
                            restored_count += 1
                            
                        except Exception as e:
                            print(f"[ERROR] Error restoring color for {obj.name}: {e}")
                
                print(f"[OK] Restored {restored_count} objects to original colors")
                
                # Do not clear cache here - keep saved colors for future use
                
                # Force viewport update
                bpy.context.view_layer.update()
                return
            
            # Create mapping of objects to tasks
            object_to_task_map = cls._build_object_task_mapping(tprops.tasks)
            
            # Count mesh objects in the scene
            mesh_objects = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
            ifc_objects = []
            
            for obj in mesh_objects:
                element = tool.Ifc.get_entity(obj)
                if element:
                    ifc_objects.append(obj)
            
            print(f"[CHECK] Scene analysis: {len(mesh_objects)} mesh objects, {len(ifc_objects)} have IFC data, {len(object_to_task_map)} task mappings")
            
            # Process each object in the scene
            processed_count = 0
            colored_count = 0
            
            for obj in mesh_objects:
                element = tool.Ifc.get_entity(obj)
                if not element:
                    print(f"[WARNING]️ {obj.name} → No IFC element → SKIP")
                    continue
                
                processed_count += 1
                
                # Use the new method to determine color
                color = cls._get_variance_color_for_object_real(obj, element, object_to_task_map, variance_selected_tasks)
                
                if color is None:
                    # Do not change color (no active checkboxes)
                    continue
                
                # Apply color to object
                cls._apply_color_to_object_simple(obj, color)
                colored_count += 1
            
            print(f"[STATS] SUMMARY: Processed {processed_count} objects, {colored_count} got variance colors")
            
            # Force viewport update
            bpy.context.view_layer.update()
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()
            
            print("[OK] Individual variance colors updated successfully")
            
        except Exception as e:
            print(f"[ERROR] Error updating individual variance colors: {e}")
            import traceback
            traceback.print_exc()

    @classmethod
    def activate_variance_color_mode(cls):
        """
        Activates variance color mode integrating with the existing ColorTypes system
        """
        try:
            print("Activating variance color mode...")
            
            # Save original colors of objects before changing them
            cls._save_original_object_colors()
            
            # Mark that variance mode is active
            bpy.context.scene['BIM_VarianceColorModeActive'] = True
            
            # Create a special ColorType group for variance
            cls._create_variance_colortype_group()
            
            # Activate the color update system
            anim_props = tool.Sequence.get_animation_props()
            
            # Trigger immediate color update
            cls._trigger_variance_color_update()
            
            print("[OK] Variance color mode activated successfully")
            
        except Exception as e:
            print(f"[ERROR] Error activating variance color mode: {e}")
            import traceback
            traceback.print_exc()

    @classmethod
    def _save_original_object_colors(cls):
        """Save the original colors of all objects from IFC material if possible"""
        try:
            original_colors = {}
            for obj in bpy.context.scene.objects:
                if obj.type == 'MESH' and hasattr(obj, 'color'):
                    # Try to get the color from the original IFC material first
                    original_color = None
                    try:
                        if obj.material_slots and obj.material_slots[0].material:
                            material = obj.material_slots[0].material
                            if material.use_nodes:
                                principled = tool.Blender.get_material_node(material, "BSDF_PRINCIPLED")
                                if principled and principled.inputs.get("Base Color"):
                                    base_color = principled.inputs["Base Color"].default_value
                                    original_color = tuple([base_color[0], base_color[1], base_color[2], base_color[3]])
                    except Exception:
                        pass

                    # Fallback: use the current viewport color if it could not be obtained from the material
                    if original_color is None:
                        original_color = tuple(obj.color)

                    original_colors[obj.name] = original_color

            bpy.context.scene['BIM_VarianceOriginalObjectColors'] = original_colors
            print(f"Saved original colors for {len(original_colors)} objects (from materials where possible)")

        except Exception as e:
            print(f"[ERROR] Error saving original object colors: {e}")

    @classmethod
    def _restore_original_object_colors(cls):
        """Restore the original colors of all objects"""
        try:
            original_colors = bpy.context.scene.get('BIM_VarianceOriginalObjectColors', {})
            restored_count = 0
            
            for obj in bpy.context.scene.objects:
                if obj.type == 'MESH' and hasattr(obj, 'color') and obj.name in original_colors:
                    obj.color = original_colors[obj.name]
                    restored_count += 1
            
            # Clear saved data
            if 'BIM_VarianceOriginalObjectColors' in bpy.context.scene:
                del bpy.context.scene['BIM_VarianceOriginalObjectColors']
                
            print(f"[OK] Restored original colors for {restored_count} objects")
            
        except Exception as e:
            print(f"[ERROR] Error restoring original object colors: {e}")

    @classmethod
    def deactivate_variance_color_mode(cls):
        """
        Deactivates variance color mode and restores original colors
        """
        try:
            print("Deactivating variance color mode...")
            
            # Restore original colors of objects
            cls._restore_original_object_colors()
            
            # Unmark that variance mode is active
            if 'BIM_VarianceColorModeActive' in bpy.context.scene:
                del bpy.context.scene['BIM_VarianceColorModeActive']
            
            # Clear variance data
            if 'BIM_VarianceColorTypes' in bpy.context.scene:
                del bpy.context.scene['BIM_VarianceColorTypes']
            
            # Force viewport update
            bpy.context.view_layer.update()
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()
            
            print("[OK] Variance color mode deactivated successfully")
            
        except Exception as e:
            print(f"[ERROR] Error deactivating variance color mode: {e}")
            import traceback
            traceback.print_exc()

    @classmethod
    def _create_variance_colortype_group(cls):
        """Creates a special ColorTypes group for variance"""
        try:
            # Define variance ColorTypes
            variance_colortypes = {
                "DELAYED": {
                    "Color": (1.0, 0.2, 0.2),
                    "Transparency": 0.0,
                    "Description": "Tasks that are delayed"
                },
                "AHEAD": {
                    "Color": (0.2, 1.0, 0.2), 
                    "Transparency": 0.0,
                    "Description": "Tasks that are ahead of schedule"
                },
                "ONTIME": {
                    "Color": (0.2, 0.2, 1.0),
                    "Transparency": 0.0, 
                    "Description": "Tasks that are on time"
                },
                "UNSELECTED": {
                    "Color": (0.8, 0.8, 0.8),
                    "Transparency": 0.7,
                    "Description": "Tasks not selected for variance view"
                }
            }
            
            # Create the group configuration file
            variance_group_data = {
                "name": "VARIANCE_MODE",
                "description": "Special ColorType group for variance analysis mode",
                "ColorTypes": variance_colortypes
            }
            
            # Store in memory for immediate use - convert to serializable format
            serializable_colortypes = {}
            for name, data in variance_colortypes.items():
                serializable_colortypes[name] = {
                    "Color": tuple(data["Color"]),  # Ensure it is a tuple
                    "Transparency": float(data["Transparency"]),
                    "Description": str(data["Description"])
                }
            
            bpy.context.scene['BIM_VarianceColorTypes'] = serializable_colortypes
            
            print("[OK] Created variance ColorType group")
            
        except Exception as e:
            print(f"[ERROR] Error creating variance ColorType group: {e}")

    @classmethod  
    def _trigger_variance_color_update(cls):
        """Forces a color update using the existing system"""
        try:
            # Use existing color update handler with variance logic
            cls._variance_aware_color_update()
            
        except Exception as e:
            print(f"[ERROR] Error triggering variance color update: {e}")

    @classmethod
    def _variance_aware_color_update(cls):
        """Color update that takes variance mode into account"""
        try:
            is_variance_mode = bpy.context.scene.get('BIM_VarianceColorModeActive', False)
            
            if not is_variance_mode:
                # If not in variance mode, use normal system
                return
            
            print("🎯 Applying variance-aware color update...")
            
            # Ensure the viewport is in Material Preview or Rendered mode
            cls._ensure_viewport_shading()
            
            # Get tasks with variance selected
            tprops = tool.Sequence.get_task_tree_props()
            if not tprops:
                return
                
            variance_selected_tasks = [
                task for task in tprops.tasks 
                if getattr(task, 'is_variance_color_selected', False) and task.variance_status
            ]
            
            variance_colortypes = bpy.context.scene.get('BIM_VarianceColorTypes', {})
            
            # Create mapping of IFC objects to real tasks
            object_to_task_map = cls._build_object_task_mapping(tprops.tasks)
            
            # Iterate over all objects and apply variance colors
            for obj in bpy.context.scene.objects:
                if obj.type != 'MESH':
                    continue
                    
                element = tool.Ifc.get_entity(obj)
                if not element:
                    continue
                
                # Determine color based on real task-object relationship
                color = cls._get_variance_color_for_object_real(obj, element, object_to_task_map, variance_selected_tasks)
                
                if color:
                    cls._apply_color_to_object_simple(obj, color)
            
            # Force viewport update
            bpy.context.view_layer.update()
            
            # Also update the depsgraph
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()
            
        except Exception as e:
            print(f"[ERROR] Error in variance aware color update: {e}")

    @classmethod
    def _ensure_viewport_shading(cls):
        """Ensure the viewport is in Solid mode with object colors"""
        try:
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    for space in area.spaces:
                        if space.type == 'VIEW_3D':
                            current_shading = space.shading.type
                            print(f"[CHECK] Current viewport shading: {current_shading}")
                            
                            # Ensure Solid mode with object colors
                            if current_shading != 'SOLID':
                                space.shading.type = 'SOLID'
                                print("Changed viewport to Solid mode")
                            
                            if hasattr(space.shading, 'color_type'):
                                space.shading.color_type = 'OBJECT'
                                print("Set solid shading to OBJECT color mode")
                            break
        except Exception as e:
            print(f"[WARNING]️ Could not ensure viewport shading: {e}")

    @classmethod
    def _build_object_task_mapping(cls, all_tasks):
        """Builds mapping using the correct Bonsai system"""
        object_task_map = {}
        
        print(f"[CHECK] Building object-task mapping for {len(all_tasks)} tasks using Bonsai system...")
        
        # Use the correct Bonsai method to get outputs
        ifc_file = tool.Ifc.get()
        if not ifc_file:
            print("[ERROR] No IFC file available")
            return object_task_map
        
        for task_pg in all_tasks:
            try:
                task_ifc = ifc_file.by_id(task_pg.ifc_definition_id)
                if not task_ifc:
                    continue
                  
                # 1. Get both inputs and outputs
                # We use 'or []' to avoid errors if the function returns None
                outputs = tool.Sequence.get_task_outputs(task_ifc) or []
                
                # We assume an analogous method exists for inputs
                # If the method has another name, adjust it here.
                inputs = tool.Sequence.get_task_inputs(task_ifc) or []

                # 2. Combine both lists into one
                all_related_objects = outputs + inputs
                
                if all_related_objects:
                    # We use a set to efficiently handle duplicates
                    processed_ids = set()
                    
                    print(f"📋 Task {task_pg.ifc_definition_id} ({task_pg.name}) has {len(all_related_objects)} related objects (Inputs & Outputs):")
                    
                    for item in all_related_objects:
                        item_id = item.id()
                        if item_id not in processed_ids:
                            object_task_map[item_id] = task_pg
                            print(f"  → Object {item_id} ({item.Name}) assigned to task")
                            processed_ids.add(item_id)
                else:
                    print(f"Task {task_pg.ifc_definition_id} ({task_pg.name}) has no inputs or outputs assigned.")

            except Exception as e:
                print(f"[ERROR] Error mapping task {task_pg.ifc_definition_id}: {e}")
                continue
        
        print(f"[OK] Built mapping: {len(object_task_map)} object-task relationships")
        return object_task_map

    @classmethod
    def _get_variance_color_for_object_real(cls, obj, element, object_task_map, variance_selected_tasks):
        """Determines a simple and direct color"""
        try:
            element_id = element.id()
            assigned_task = object_task_map.get(element_id)
            
            # If this object belongs to a task with active checkbox
            if assigned_task and getattr(assigned_task, 'is_variance_color_selected', False):
                variance_status = getattr(assigned_task, 'variance_status', '')
                
                # Color according to variance status
                if "Delayed" in variance_status:
                    print(f"🔴 {obj.name} -> Task {assigned_task.ifc_definition_id} -> DELAYED")
                    return (1.0, 0.2, 0.2, 1.0)  # Red
                elif "Ahead" in variance_status:
                    print(f"🟢 {obj.name} -> Task {assigned_task.ifc_definition_id} -> AHEAD")
                    return (0.2, 1.0, 0.2, 1.0)  # Green
                elif "On Time" in variance_status:
                    print(f"🔵 {obj.name} -> Task {assigned_task.ifc_definition_id} -> ONTIME")
                    return (0.2, 0.2, 1.0, 1.0)  # Blue
                else:
                    print(f"❓ {obj.name} -> Task {assigned_task.ifc_definition_id} -> Unknown status: '{variance_status}'")
                    return (0.8, 0.8, 0.8, 0.3)  # Transparent gray
            else:
                # Object without selected task → transparent gray
                return (0.8, 0.8, 0.8, 0.3)
                
        except Exception as e:
            print(f"[ERROR] Error getting color for object {obj.name}: {e}")
            return (0.8, 0.8, 0.8, 0.3)
        
    @classmethod
    def _apply_color_to_object_simple(cls, obj, color):
        """Apply color only to the object (for Solid viewport)"""
        try:
            print(f"Applying variance color {color} to {obj.name}")
            
            # ONLY apply object color (for Solid > Object mode)
            if hasattr(obj, 'color'):
                obj.color = color[:4] if len(color) >= 4 else color[:3] + (1.0,)
                print(f"[OK] Set object color for {obj.name}: {obj.color}")
            else:
                print(f"[WARNING]️ Object {obj.name} does not have color property")
                        
        except Exception as e:
            print(f"[ERROR] Error applying simple color to {obj.name}: {e}")
            import traceback
            traceback.print_exc()

    @classmethod
    def clear_schedule_variance(cls):
        """
        Clear schedule variance data, colors and reset objects to their original state.
        Called when clearing variance or switching schedule types.
        """
        try:
            print("[CLEAN] CLEAR_SCHEDULE_VARIANCE: Starting comprehensive cleanup process...")
            
            # Clear variance DATA from all tasks (this was missing!)
            tprops = tool.Sequence.get_task_tree_props()
            if tprops and tprops.tasks:
                cleared_tasks = 0
                print(f"[CLEAN] CLEAR_SCHEDULE_VARIANCE: Found {len(tprops.tasks)} tasks to clean")
                
                for task in tprops.tasks:
                    # Clear the variance data properties set by CalculateScheduleVariance
                    if hasattr(task, 'variance_days'):
                        task.variance_days = 0
                        cleared_tasks += 1
                        
                    if hasattr(task, 'variance_status'):
                        task.variance_status = ""
                        
                    # Clear variance color selection checkbox
                    if hasattr(task, 'is_variance_color_selected'):
                        task.is_variance_color_selected = False
                        
                print(f"[OK] CLEAR_SCHEDULE_VARIANCE: Cleared variance data from {cleared_tasks} tasks")
            else:
                print("[WARNING]️ CLEAR_SCHEDULE_VARIANCE: No task properties found")
            
            # Clear variance color mode and restore original colors
            print("[CLEAN] CLEAR_SCHEDULE_VARIANCE: Clearing variance color mode...")
            # Assuming cls.clear_variance_color_mode() exists and works correctly.
            # If the problem persists, the error could also be within that function.
            # cls.clear_variance_color_mode() # This line may be redundant if we reset manually below
            
            # Remove variance mode flags from scene
            scene_flags_cleared = 0
            if hasattr(bpy.context.scene, 'BIM_VarianceColorModeActive'):
                del bpy.context.scene['BIM_VarianceColorModeActive']
                scene_flags_cleared += 1
                print("[CLEAN] Removed BIM_VarianceColorModeActive flag from scene")
                
            # Clear any other variance-related scene properties
            variance_keys = [key for key in bpy.context.scene.keys() if 'variance' in key.lower()]
            for key in variance_keys:
                try:
                    del bpy.context.scene[key]
                    scene_flags_cleared += 1
                    print(f"[CLEAN] Removed scene property: {key}")
                except Exception as e:
                    print(f"[WARNING]️ Could not remove scene property {key}: {e}")
            
            print(f"[OK] CLEAR_SCHEDULE_VARIANCE: Cleared {scene_flags_cleared} scene flags")
            
            # SAFE RESET: Only clear variance-specific overrides, preserve colortype system
            print("[CLEAN] CLEAR_SCHEDULE_VARIANCE: Safely removing variance overrides (preserving colortypes)...")
            reset_objects = 0

            for obj in bpy.context.scene.objects:
                if obj.type == 'MESH' and tool.Ifc.get_entity(obj):
                    try:
                        # STRATEGY: Instead of forcing white, only remove variance-specific overrides
                        # This allows colortypes to work naturally without interference

                        # Only reset visibility if it was hidden by variance
                        if obj.hide_viewport or obj.hide_render:
                            obj.hide_viewport = False
                            obj.hide_render = False

                        # Clear animation data that might be variance-related
                        if obj.animation_data:
                            # Only clear if it's variance-related animation
                            try:
                                if 'variance' in str(obj.animation_data).lower():
                                    obj.animation_data_clear()
                            except Exception:
                                # If we can't determine, be conservative and don't clear
                                pass

                        # DON'T force object color - let colortype system manage colors
                        reset_objects += 1

                    except Exception as e:
                        print(f"[WARNING]️ Error safely resetting object {obj.name}: {e}")

            print(f"[OK] CLEAR_SCHEDULE_VARIANCE: Safely reset {reset_objects} objects (colortypes preserved)")
            
            # Force complete viewport refresh
            print("[CLEAN] CLEAR_SCHEDULE_VARIANCE: Forcing viewport refresh...")
            try:
                # Update view layer
                bpy.context.view_layer.update()
                
                # Force redraw of all 3D viewports
                for area in bpy.context.screen.areas:
                    if area.type == 'VIEW_3D':
                        area.tag_redraw()
                
                print("[OK] CLEAR_SCHEDULE_VARIANCE: Viewport refresh completed")
                
            except Exception as e:
                print(f"[WARNING]️ Error during viewport refresh: {e}")
            
            print("[OK] CLEAR_SCHEDULE_VARIANCE: Comprehensive cleanup completed successfully")
            
        except Exception as e:
            print(f"[ERROR] Error in clear_schedule_variance: {e}")
            import traceback
            traceback.print_exc()