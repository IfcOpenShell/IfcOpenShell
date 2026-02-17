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
import isodate
import ifcopenshell.api
import ifcopenshell.api.sequence
import ifcopenshell.util.attribute
import ifcopenshell.util.date
import bonsai.core.sequence as core
import bonsai.tool as tool
from bonsai.bim.module.sequence.data import SequenceData, AnimationColorSchemeData, refresh as refresh_sequence_data

# Import snapshot functions
try:
    from ..operators.operator import snapshot_all_ui_state
    from ..operators.schedule_task_operators import restore_all_ui_state
except ImportError:
    # Fallback functions if imports fail
    def snapshot_all_ui_state(context):
        pass
    def restore_all_ui_state(context):
        pass

# Global flag to prevent recursive callback execution during restore
_CALLBACK_LOCK = False

def debug_colortype_values(operation_name):
    """Debug function to see current colorType values"""
    print(f"\n=== DEBUG {operation_name} ===")
    try:
        tprops = tool.Sequence.get_task_tree_props()
        if not tprops:
            print("No task tree properties found")
            return

        print(f"Total tasks in UI: {len(tprops.tasks)}")
        colortype_count = 0

        for i, task in enumerate(tprops.tasks):
            task_id = getattr(task, 'ifc_definition_id', 0)
            animation_color_schemes = getattr(task, 'animation_color_schemes', '')
            selected_colortype = getattr(task, 'selected_colortype_in_active_group', '')

            if animation_color_schemes or selected_colortype:
                colortype_count += 1
                print(f"Task {i}: ID={task_id}")
                print(f"  animation_color_schemes: '{animation_color_schemes}'")
                print(f"  selected_colortype_in_active_group: '{selected_colortype}'")

        print(f"Tasks with colorType values: {colortype_count}")
    except Exception as e:
        print(f"Debug failed: {e}")
    print(f"=== END DEBUG {operation_name} ===\n")
import bonsai.bim.module.resource.data
import bonsai.bim.module.pset.data
from mathutils import Color
from bonsai.bim.prop import Attribute, ISODuration
from dateutil import parser
from typing import TYPE_CHECKING, Literal, get_args, Optional, Dict, List, Set

# We import the manager that we already separated
from .color_manager_prop import UnifiedColorTypeManager


# We do a safe circular import
from . import enums_prop
from .enums_prop import get_custom_group_colortype_items




def update_date_source_type(self, context):
    """
    Simple callback when the user changes schedule type.
    Only updates date range using Guess functionality.
    """
    try:
        print(f"📅 Date source changed to: {self.date_source_type}")
        
        # Store previous dates for sync animation
        previous_start = self.visualisation_start
        previous_finish = self.visualisation_finish

        # Update date range for the new schedule type using Guess
        bpy.ops.bim.guess_date_range('INVOKE_DEFAULT', work_schedule=self.active_work_schedule_id)
        
        # Call sync animation if it exists
        try:
            bpy.ops.bim.sync_animation_by_date(
                'INVOKE_DEFAULT',
                previous_start_date=previous_start,
                previous_finish_date=previous_finish
            )
        except Exception as e:
            print(f"[WARNING] Animation sync failed: {e}")
                
    except Exception as e:
        print(f"[ERROR] update_date_source_type: Error: {e}")
        import traceback
        traceback.print_exc()


def update_schedule_display_parent_constraint(context):
    """
    Finds the 'Schedule_Display_Parent' empty and updates its rotation and location constraints.
    Rotation and location can follow the active camera or custom targets.
    """
    import bpy
    import bonsai.tool as tool
    parent_name = "Schedule_Display_Parent"
    parent_empty = bpy.data.objects.get(parent_name)

    if not parent_empty:
        # Create the empty if it doesn't exist
        parent_empty = bpy.data.objects.new(parent_name, None)
        bpy.context.scene.collection.objects.link(parent_empty)
        parent_empty.empty_display_type = 'PLAIN_AXES'
        parent_empty.empty_display_size = 2

    # ALWAYS CLEAR anchor modes (as in the script that worked)
    if 'anchor_mode' in parent_empty:
        del parent_empty['anchor_mode']
    if 'hud_anchor_mode' in context.scene:
        del context.scene['hud_anchor_mode']


    # Get camera orbit properties to check for custom targets
    try:
        anim_props = tool.Sequence.get_animation_props()
        camera_props = anim_props.camera_orbit

        # Rotation properties
        use_custom_rot_target = getattr(camera_props, 'use_custom_rotation_target', False)
        custom_rotation_target = getattr(camera_props, 'schedule_display_rotation_target', None)

        # Location properties
        use_custom_loc_target = getattr(camera_props, 'use_custom_location_target', False)
        custom_location_target = getattr(camera_props, 'schedule_display_location_target', None)

    except Exception:
        use_custom_rot_target = False
        custom_rotation_target = None
        use_custom_loc_target = False
        custom_location_target = None

    active_camera = getattr(context.scene, 'camera', None)

    # Clear existing constraints
    for c in list(parent_empty.constraints):
        parent_empty.constraints.remove(c)

    # If ANY checkbox is checked, create BOTH constraints
    if use_custom_rot_target or use_custom_loc_target:
        # Determine targets
        rotation_target = custom_rotation_target if (use_custom_rot_target and custom_rotation_target) else active_camera
        location_target = custom_location_target if (use_custom_loc_target and custom_location_target) else active_camera

        # Create rotation constraint
        if rotation_target:
            rot_constraint = parent_empty.constraints.new(type='COPY_ROTATION')
            rot_constraint.target = rotation_target

        # Create location constraint
        if location_target:
            loc_constraint = parent_empty.constraints.new(type='COPY_LOCATION')
            loc_constraint.target = location_target


def update_legend_3d_hud_constraint(context):
    """
    Finds the 'HUD_3D_Legend' empty and updates its rotation and location constraints.
    Rotation and location can follow the active camera or custom targets.
    """
    import bpy
    import bonsai.tool as tool

    hud_empty = None
    for obj in bpy.data.objects:
        if obj.get("is_3d_legend_hud", False):
            hud_empty = obj
            break


    if not hud_empty:
        return

    # --- WORLD ORIGIN ANCHOR (Snapshot / Forced) for Legend HUD ---
    scene = getattr(context, 'scene', None)
    if scene is None:
        import bpy as _bpy
        scene = _bpy.context.scene

    force_world_origin = False
    try:
        # Prefer object-level override if present
        if hud_empty.get('anchor_mode') == 'WORLD_ORIGIN':
            force_world_origin = True
        elif scene and scene.get('hud_anchor_mode') == 'WORLD_ORIGIN':
            force_world_origin = True
        else:
            active_cam = getattr(scene, 'camera', None)
            if active_cam and (active_cam.get('is_snapshot_camera') or
                                active_cam.get('camera_context') == 'snapshot' or
                                'Snapshot_Camera' in getattr(active_cam, 'name', '')):
                force_world_origin = True
    except Exception:
        pass

    if force_world_origin:
        try:
            hud_empty.constraints.clear()
        except Exception:
            try:
                for c in list(hud_empty.constraints):
                    hud_empty.constraints.remove(c)
            except Exception:
                pass
        try:
            hud_empty.location = (0.0, 0.0, 0.0)
            hud_empty.rotation_euler = (0.0, 0.0, 0.0)
            hud_empty.scale = (1.0, 1.0, 1.0)
        except Exception:
            pass
        # Persist intent - COMMENTED to allow custom constraints
        # try:
        #     hud_empty['anchor_mode'] = 'WORLD_ORIGIN'
        #     if scene is not None:
        #         scene['hud_anchor_mode'] = 'WORLD_ORIGIN'
        # except Exception:
        #     pass
        return

    # Get camera orbit properties to check for custom targets
    try:
        anim_props = tool.Sequence.get_animation_props()
        camera_props = anim_props.camera_orbit
        
        # Rotation properties for 3D Legend HUD
        use_custom_rot_target = getattr(camera_props, 'legend_3d_hud_use_custom_rotation_target', False)
        custom_rotation_target = getattr(camera_props, 'legend_3d_hud_rotation_target', None)
        
        # Location properties for 3D Legend HUD
        use_custom_loc_target = getattr(camera_props, 'legend_3d_hud_use_custom_location_target', False)
        custom_location_target = getattr(camera_props, 'legend_3d_hud_location_target', None)
    except Exception:
        use_custom_rot_target = False
        custom_rotation_target = None
        use_custom_loc_target = False
        custom_location_target = None

    active_camera = getattr(context.scene, 'camera', None)

    # --- Clear existing constraints to ensure a clean state ---
    for c in list(hud_empty.constraints):
        hud_empty.constraints.remove(c)

    # ONLY create constraints if the checkboxes are checked

    # Add rotation constraint ONLY if the checkbox is checked
    if use_custom_rot_target:
        rotation_target = custom_rotation_target if custom_rotation_target else active_camera
        if rotation_target:
            rot_constraint = hud_empty.constraints.new(type='COPY_ROTATION')
            rot_constraint.target = rotation_target
        else:
            print(f"[WARNING] Rotation checkbox checked but no target for '{hud_empty.name}'")

    # Add location constraint ONLY if the checkbox is checked
    if use_custom_loc_target:
        location_target = custom_location_target if custom_location_target else active_camera
        if location_target:
            loc_constraint = hud_empty.constraints.new(type='COPY_LOCATION')
            loc_constraint.target = location_target
        else:
            print(f"[WARNING] Location checkbox checked but no target for '{hud_empty.name}'")

    # If no checkbox is checked, no constraints are created
    if not use_custom_rot_target and not use_custom_loc_target:
        print(f"📝 No checkboxes checked - '{hud_empty.name}' without constraints (free)")



def update_variance_calculation(self, context):
    """Callback when chronogram types change - does NOT automatically calculate variance."""
    # FIXED: Remove automatic calculation when changing chronogram type
    # User must press Calculate button to calculate variance
    pass


def update_task_checkbox_selection(self, context):
    """
    Callback that is executed when checking/unchecking a checkbox.
    Uses a timer to execute the 3D selection logic safely.
    """
    def apply_selection():
        try:
            # PROTECTION: Check if animation is active to avoid crashes
            import bonsai.tool as tool
            try:
                anim_props = tool.Sequence.get_animation_props()
                is_animation_active = getattr(anim_props, 'is_animation_created', False)
                if is_animation_active:
                    print("[WARNING] Skipping checkbox update during active animation to prevent crashes")
                    return None
            except Exception:
                pass  # If it cannot be verified, continue normally

            # --- START OF MODIFICATION ---
            # Get the properties to check if 3D selection is active
            props = tool.Sequence.get_work_schedule_props()
            if props.should_select_3d_on_task_click:
                tool.Sequence.apply_selection_from_checkboxes()
            # If the main checkbox is off, do nothing.
        except Exception as e:
            print(f"Error in delayed checkbox selection update: {e}")
        return None  # The timer only runs once

    # Register the function with a timer to avoid context issues
    import bpy
    if not bpy.app.timers.is_registered(apply_selection):
        bpy.app.timers.register(apply_selection, first_interval=0.01)



def update_variance_color_mode(self, context):
    """
    Callback that runs when checking/unchecking the variance color mode checkbox.
    Each task works independently.
    """
    try:
        print(f"🔄 Variance checkbox changed for task {self.ifc_definition_id} ({self.name}): {self.is_variance_color_selected}")
        # Always update colors immediately, regardless of other checkboxes
        print("🎨 Updating variance colors for individual task...")
        tool.Sequence.update_individual_variance_colors()
            
    except Exception as e:
        print(f"[ERROR] Error in variance color mode update: {e}")
        import traceback
        traceback.print_exc()


    @staticmethod
    def initialize_default_for_all_tasks(context) -> bool:
        """Iterates through all tasks and ensures their DEFAULT group is initialized and synchronized."""
        try:
            tprops = tool.Sequence.get_task_tree_props()
            if not tprops or not hasattr(tprops, 'tasks'):
                return False
            
            # First, ensure that all necessary profiles exist.
            UnifiedColorTypeManager.ensure_default_group_has_predefined_types(context)

            for task in tprops.tasks:
                UnifiedColorTypeManager.sync_default_group_to_predefinedtype(context, task)
            
            return True
        except Exception as e:
            print(f"[ERROR] Error initializing DEFAULT profiles for all tasks: {e}")
            return False

    @staticmethod
    def get_user_created_groups(context) -> list:
        """Returns a list of group names that are not 'DEFAULT'."""
        try:
            all_groups = list(UnifiedColorTypeManager._read_sets_json(context).keys())
            return sorted([g for g in all_groups if g != "DEFAULT"])
        except Exception:
            return []
            
    # Methods from the original implementation that are still needed and relevant
    @staticmethod
    def validate_colortype_data(colortype_data: dict) -> bool:
        """Validates the complete data structure of the colortype"""
        required_fields = ['name', 'start_color', 'in_progress_color', 'end_color']
        if not all(field in colortype_data for field in required_fields):
            return False
    
        # Validate colors
        for color_field in ['start_color', 'in_progress_color', 'end_color']:
            color = colortype_data.get(color_field)
            if not isinstance(color, (list, tuple)) or len(color) not in (3, 4):
                return False
    
        # Validate optional values
        optional_floats = [
            'start_transparency', 'active_start_transparency', 
            'active_finish_transparency', 'active_transparency_interpol', 
            'end_transparency'
        ]
        for field in optional_floats:
            if field in colortype_data:
                try:
                    val = float(colortype_data[field])
                    if not 0.0 <= val <= 1.0:
                        return False
                except (TypeError, ValueError):
                    return False
    
        return True

    @staticmethod
    def get_group_colortypes(context, group_name: str) -> Dict[str, dict]:
        """Gets colortypes from a specific group"""
        # For the DEFAULT group, always return the authoritative, hardcoded list of profiles.
        # This prevents inconsistencies from the JSON store and ensures the Legend HUD
        # and other components always have the complete, correct data.
        if group_name == "DEFAULT":
            default_order = [
                "CONSTRUCTION", "INSTALLATION", "DEMOLITION", "REMOVAL",
                "DISPOSAL", "DISMANTLE", "OPERATION", "MAINTENANCE",
                "ATTENDANCE", "RENOVATION", "LOGISTIC", "MOVE", "NOTDEFINED", "USERDEFINED"
            ]
            colortypes = {}
            for name in default_order:
                # Here we force the use of the method we have already corrected
                colortypes[name] = UnifiedColorTypeManager._create_default_colortype_data(name)
            return colortypes

        try:
            data = UnifiedColorTypeManager._read_sets_json(context)
            if isinstance(data, dict) and group_name in data:
                colortypes = {}
                for colortype in data[group_name].get("ColorTypes", []):
                    if UnifiedColorTypeManager.validate_colortype_data(colortype):
                        colortypes[colortype["name"]] = colortype
                return colortypes
        except Exception:
            pass
        return {}
    
    @staticmethod
    def get_all_groups(context) -> list:
        """Returns a list of names of all groups."""
        try:
            return sorted(list(UnifiedColorTypeManager._read_sets_json(context).keys()))
        except Exception:
            return []

    @staticmethod
    def get_colortypes_from_specific_group(context, group_name: str) -> list:
        """Get colortype names from a specific group (for use in enums)"""
        try:
            colortypes_data = UnifiedColorTypeManager.get_group_colortypes(context, group_name)
            return sorted(list(colortypes_data.keys()))
        except Exception as e:
            print(f"[ERROR] Error getting colortypes from group '{group_name}': {e}")
            return []

    @staticmethod
    def debug_colortype_state(context, task_id: int = None):
        """Debug helper to show profile status"""
        try:
            
            # Show all groups
            all_groups = UnifiedColorTypeManager.get_all_groups(context)
            user_groups = UnifiedColorTypeManager.get_user_created_groups(context)
            print(f"All groups: {all_groups}")
            print(f"User groups (no DEFAULT): {user_groups}")
            
            # Show animation props
            try:
                anim_props = tool.Sequence.get_animation_props()
                print(f"Active ColorType_groups: {getattr(anim_props, 'ColorType_groups', 'N/A')}")
                print(f"Task colortype selector: {getattr(anim_props, 'task_colortype_group_selector', 'N/A')}")
                print(f"Loaded ColorTypes count: {len(getattr(anim_props, 'ColorTypes', []))}")
                
                for i, p in enumerate(getattr(anim_props, 'ColorTypes', [])):
                    print(f"  [{i}] {getattr(p, 'name', 'NO_NAME')}")
            except Exception as e:
                print(f"Error getting anim props: {e}")
            
            # Show specific task data
            if task_id:
                try:
                    tprops = tool.Sequence.get_task_tree_props()
                    wprops = tool.Sequence.get_work_schedule_props()
                    if tprops.tasks and wprops.active_task_index < len(tprops.tasks):
                        task = tprops.tasks[wprops.active_task_index]
                        print(f"Task {task.ifc_definition_id} colortype mappings:")
                        for choice in getattr(task, 'colortype_group_choices', []):
                            print(f"  {choice.group_name} -> {choice.selected_colortype} (enabled: {choice.enabled})")
                        print(f"  use_active_colortype_group: {getattr(task, 'use_active_colortype_group', 'N/A')}")
                        print(f"  selected_colortype_in_active_group: {getattr(task, 'selected_colortype_in_active_group', 'N/A')}")
                except Exception as e:
                    print(f"Error getting task data: {e}")
            
        except Exception as e:
            print(f"[ERROR] Debug failed: {e}")


    @staticmethod
    def sync_task_colortypes(context, task, group_name: str):
        """Synchronizes task colortypes with the active group - eliminates duplication"""
        valid_colortypes = UnifiedColorTypeManager.get_group_colortypes(context, group_name)
    
        if hasattr(task, 'colortype_group_choices'):
            # Find or create an entry for the group
            entry = None
            for choice in task.colortype_group_choices:
                if choice.group_name == group_name:
                    entry = choice
                    break
        
            if not entry:
                entry = task.colortype_group_choices.add()
                entry.group_name = group_name
                entry.enabled = False
                entry.selected_colortype = ""
        
            # Validate selected colortype
            if entry.selected_colortype and entry.selected_colortype not in valid_colortypes:
                entry.selected_colortype = ""
        
            return entry
        return None

    @staticmethod
    def cleanup_invalid_mappings(context):
        """Cleans up all invalid colortype mappings"""
        valid_groups = set(UnifiedColorTypeManager._read_sets_json(context).keys())
    
        try:
            tprops = tool.Sequence.get_task_tree_props()
            for task in getattr(tprops, "tasks", []):
                if hasattr(task, 'colortype_group_choices'):
                    # Collect indices to remove
                    to_remove = []
                    for idx, choice in enumerate(task.colortype_group_choices):
                        if choice.group_name not in valid_groups:
                            to_remove.append(idx)
                        else:
                            # Validate colortype within the group
                            colortypes = UnifiedColorTypeManager.get_group_colortypes(context, choice.group_name)
                            if choice.selected_colortype and choice.selected_colortype not in colortypes:
                                choice.selected_colortype = ""
                
                    # Remove invalid entries
                    for offset, idx in enumerate(to_remove):
                        task.colortype_group_choices.remove(idx - offset)
        except Exception as e:
            print(f"Error cleaning invalid mappings: {e}")

    @staticmethod
    def load_colortypes_into_collection(props, context, group_name: str):
        """Loads colortypes from a group into the property collection"""
        
        # Guard to prevent unnecessary reloading if already correctly populated
        if group_name == "DEFAULT":
            default_order = [
                "CONSTRUCTION", "INSTALLATION", "DEMOLITION", "REMOVAL", 
                "DISPOSAL", "DISMANTLE", "OPERATION", "MAINTENANCE", 
                "ATTENDANCE", "RENOVATION", "LOGISTIC", "MOVE", "NOTDEFINED", "USERDEFINED"
            ]
            
            # Check if collection is already correctly populated
            if (len(props.ColorTypes) == len(default_order) and 
                all(props.ColorTypes[i].name == default_order[i] for i in range(len(default_order)))):
                # Collection is already correctly populated, no need to reload
                return
        
        # For DEFAULT, ensure that ALL profiles exist
        # Always ensure DEFAULT profiles exist when DEFAULT group is specifically loaded
        if group_name == "DEFAULT":
            user_groups = UnifiedColorTypeManager.get_user_created_groups(context)
            # Always load DEFAULT profiles when explicitly loading DEFAULT group
            UnifiedColorTypeManager.ensure_default_group_has_predefined_types(context)
            if user_groups:
                print("[WARNING] Custom groups detected - but DEFAULT group is being explicitly loaded with full profiles")
        
        colortypes_data = UnifiedColorTypeManager.get_group_colortypes(context, group_name)

        try:
            props.ColorTypes.clear()
            
            # For DEFAULT, ensure specific order and completeness
            if group_name == "DEFAULT":
                # Complete list in specific order
                default_order = [
                    "CONSTRUCTION", "INSTALLATION", "DEMOLITION", "REMOVAL", 
                    "DISPOSAL", "DISMANTLE", "OPERATION", "MAINTENANCE", 
                    "ATTENDANCE", "RENOVATION", "LOGISTIC", "MOVE", "NOTDEFINED", "USERDEFINED"
                ]
                
                # Load in the specified order
                for colortype_name in default_order:
                    # ALWAYS use the hardcoded default data for the DEFAULT group to ensure correctness.
                    # This ignores any potentially incorrect data stored in the JSON.
                    colortype_data = UnifiedColorTypeManager._create_default_colortype_data(colortype_name)
                    p = props.ColorTypes.add()
                    p.name = colortype_name
                    UnifiedColorTypeManager._apply_colortype_data_to_property(p, colortype_data)
            else:
                # For custom groups, normal behavior
                for colortype_name, colortype_data in colortypes_data.items():
                    p = props.ColorTypes.add()
                    p.name = colortype_name
                    UnifiedColorTypeManager._apply_colortype_data_to_property(p, colortype_data)
        
            if props.ColorTypes:
                props.active_ColorType_index = 0
        except Exception as e:
            print(f"Error loading colortypes: {e}")



def update_active_work_schedule_id(self, context):
    """
    Callback that runs when the active schedule changes.
    Automatically saves the profiles of the previous schedule and loads those of the new one.
    """
    try:
        import bonsai.tool as tool
        # DEBUG: Check that the callback is running
        current_ws_id = getattr(self, 'active_work_schedule_id', 0)
        previous_ws_id = getattr(context.scene, '_previous_work_schedule_id', 0)
        
        # Avoid infinite loops during temporary changes
        if getattr(context.scene, '_updating_work_schedule_id', False):
            return
            
        # Only process if the active schedule actually changed
        if current_ws_id == previous_ws_id:
            return  # No real change
            
        # Import the necessary functions from operator.py
        from ..operators.operator import snapshot_all_ui_state
        
        # 1. Save profiles from the previous schedule (if there was one)
        if previous_ws_id != 0:
            try:
                
                # Mark that we are in the process of updating
                context.scene['_updating_work_schedule_id'] = True
                
                # Temporarily restore the previous ID to make a correct snapshot
                old_id = self.active_work_schedule_id
                self.active_work_schedule_id = previous_ws_id
                snapshot_all_ui_state(context)
                self.active_work_schedule_id = old_id
                
                
            except Exception as e:
                print(f"[ERROR] Error updating work schedule: {e}")
            finally:
                context.scene['_updating_work_schedule_id'] = False
        
        # 2. Update the previous ID in the context
        context.scene['_previous_work_schedule_id'] = current_ws_id
        
        # Note: The restoration will be done in the operator AFTER load_task_tree
        print("ℹ️ Variance colors will remain active - use Clear Variance button to reset")
                
    except Exception as e:
        print(f"[ERROR] Error in work schedule update: {e}")


def update_active_task_index(self, context):
    """
    Updates active task index, synchronizes colortypes,
    and selects associated 3D objects in the viewport (for single click).
    """
    import bonsai.tool as tool
    task_ifc = tool.Sequence.get_highlighted_task()
    self.highlighted_task_id = task_ifc.id() if task_ifc else 0
    tool.Sequence.update_task_ICOM(task_ifc)
    bonsai.bim.module.pset.data.refresh()

    if self.editing_task_type == "SEQUENCE":
        tool.Sequence.load_task_properties()

    try:
        tprops = tool.Sequence.get_task_tree_props()
        if tprops.tasks and self.active_task_index < len(tprops.tasks):
            task_pg = tprops.tasks[self.active_task_index]
            try:
                # Only sync DEFAULT if there are no custom groups
                user_groups = UnifiedColorTypeManager.get_user_created_groups(context)
                if not user_groups:
                    UnifiedColorTypeManager.sync_default_group_to_predefinedtype(context, task_pg)
                
                anim_props = tool.Sequence.get_animation_props()
                if anim_props.ColorType_groups:
                    UnifiedColorTypeManager.sync_task_colortypes(context, task_pg, anim_props.ColorType_groups)
            except NameError:
                # UnifiedColorTypeManager not available, skip colortype syncing
                pass
    except Exception as e:
        print(f"[ERROR] Error syncing colortypes in update_active_task_index: {e}")

    # --- 3D SELECTION LOGIC FOR SINGLE CLICK ---
    props = tool.Sequence.get_work_schedule_props()
    if props.should_select_3d_on_task_click:
        if not task_ifc:
            try:
                bpy.ops.object.select_all(action='DESELECT')
            except RuntimeError:
                # Occurs if we are not in object mode, it is safe to ignore it.
                pass
            # Early exit from the update function - do not continue with 3D selection
            return

        try:

            # INCLUDE BOTH OUTPUTS AND INPUTS
            outputs = tool.Sequence.get_task_outputs(task_ifc) or []
            inputs = tool.Sequence.get_task_inputs(task_ifc) or []

            # Combine both, removing duplicates
            all_products = list(set(outputs + inputs))

            # Deselect everything else first
            if bpy.context.view_layer.objects.active:
                bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')

            if all_products:
                objects_to_select = [tool.Ifc.get_object(p) for p in all_products if tool.Ifc.get_object(p)]

                if objects_to_select:
                    for obj in objects_to_select:
                        # <-- STEP 1: Make sure the object is visible and selectable
                        obj.hide_set(False)
                        obj.hide_select = False

                        # <-- STEP 2: Select the object
                        obj.select_set(True)

                    # <-- STEP 3: Set the first object as active
                    context.view_layer.objects.active = objects_to_select[0]

                    # <-- STEP 4: Center the 3D view ONLY if a 3D view is available
                    try:
                        if bpy.context.area and bpy.context.area.type == 'VIEW_3D':
                            bpy.ops.view3d.view_selected()
                        else:
                            print("🔍 3D view not active, skipping view_selected()")
                    except Exception as view_error:
                        print(f"[WARNING] Could not center 3D view: {view_error}")
                else:
                    print("🔍 No objects to select for this task")
            else:
                print("🔍 Task has no associated products")

        except Exception as e:
            print(f"Error selecting 3D objects for task: {e}")

def update_active_task_outputs(self, context):
    import bonsai.tool as tool
    task = tool.Sequence.get_highlighted_task()
    outputs = tool.Sequence.get_task_outputs(task)
    tool.Sequence.load_task_outputs(outputs)

def update_active_task_resources(self, context):
    import bonsai.tool as tool
    task = tool.Sequence.get_highlighted_task()
    resources = tool.Sequence.get_task_resources(task)
    tool.Sequence.load_task_resources(resources)

def update_active_task_inputs(self, context):
    import bonsai.tool as tool
    task = tool.Sequence.get_highlighted_task()
    inputs = tool.Sequence.get_task_inputs(task)
    tool.Sequence.load_task_inputs(inputs)

def updateTaskName(self: "Task", context: bpy.types.Context) -> None:
    import bonsai.tool as tool
    props = tool.Sequence.get_work_schedule_props()
    if not props.is_task_update_enabled or self.name == "Unnamed":
        return
    ifc_file = tool.Ifc.get()
    ifcopenshell.api.sequence.edit_task(
        ifc_file,
        task=ifc_file.by_id(self.ifc_definition_id),
        attributes={"Name": self.name},
    )
    SequenceData.load()
    if props.active_task_id == self.ifc_definition_id:
        attribute = props.task_attributes["Name"]
        attribute.string_value = self.name

def updateTaskIdentification(self: "Task", context: bpy.types.Context) -> None:
    import bonsai.tool as tool
    props = tool.Sequence.get_work_schedule_props()
    if not props.is_task_update_enabled or self.identification == "XXX":
        return
    ifc_file = tool.Ifc.get()
    ifcopenshell.api.sequence.edit_task(
        ifc_file,
        task=ifc_file.by_id(self.ifc_definition_id),
        attributes={"Identification": self.identification},
    )
    SequenceData.load()
    if props.active_task_id == self.ifc_definition_id:
        attribute = props.task_attributes["Identification"]
        attribute.string_value = self.identification

def updateTaskTimeStart(self: "Task", context: bpy.types.Context) -> None:
    updateTaskTimeDateTime(self, context, "start", "Schedule")


def updateTaskTimeFinish(self: "Task", context: bpy.types.Context) -> None:
    updateTaskTimeDateTime(self, context, "finish", "Schedule")


def updateTaskTimeActualStart(self: "Task", context: bpy.types.Context) -> None:
    updateTaskTimeDateTime(self, context, "actual_start", "Actual")


def updateTaskTimeActualFinish(self: "Task", context: bpy.types.Context) -> None:
    updateTaskTimeDateTime(self, context, "actual_finish", "Actual")


def updateTaskTimeEarlyStart(self: "Task", context: bpy.types.Context) -> None:
    updateTaskTimeDateTime(self, context, "early_start", "Early")


def updateTaskTimeEarlyFinish(self: "Task", context: bpy.types.Context) -> None:
    updateTaskTimeDateTime(self, context, "early_finish", "Early")


def updateTaskTimeLateStart(self: "Task", context: bpy.types.Context) -> None:
    updateTaskTimeDateTime(self, context, "late_start", "Late")


def updateTaskTimeLateFinish(self: "Task", context: bpy.types.Context) -> None:
    updateTaskTimeDateTime(self, context, "late_finish", "Late")

def updateTaskTimeDateTime(
    self: "Task",
    context: bpy.types.Context,
    prop_name: str,
    ifc_date_type: Literal["Schedule", "Actual", "Early", "Late"],
) -> None:
    props = tool.Sequence.get_work_schedule_props()

    if not props.is_task_update_enabled:
        return

    prop_value = getattr(self, prop_name)

    if prop_value == "-":
        return

    ifc_file = tool.Ifc.get()

    try:
        dt_value = parser.isoparse(prop_value)
    except:
        try:
            dt_value = parser.parse(prop_value, dayfirst=True, fuzzy=True)
        except:
            setattr(self, prop_name, "-")
            return

    task = ifc_file.by_id(self.ifc_definition_id)
    if task.TaskTime:
        task_time = task.TaskTime
    else:
        task_time = ifcopenshell.api.sequence.add_task_time(ifc_file, task=task)
        SequenceData.load()

    ifc_attribute_name = "Schedule" + startfinish.capitalize()

    if SequenceData.data["task_times"][task_time.id()][ifc_attribute_name] == dt_value:
        canonical_value = canonicalise_time(dt_value)
        if prop_value != canonical_value:
            setattr(self, startfinish, canonical_value)
        return

    ifcopenshell.api.sequence.edit_task_time(
        ifc_file,
        task_time=task_time,
        attributes={ifc_attribute_name: dt_value},
    )
    SequenceData.load()
    bpy.ops.bim.load_task_properties()



def updateTaskDuration(self: "Task", context: bpy.types.Context) -> None:
    props = tool.Sequence.get_work_schedule_props()
    if not props.is_task_update_enabled:
        return

    if self.duration == "-":
        return

    duration = ifcopenshell.util.date.parse_duration(self.duration)
    if not duration:
        self.duration = "-"
        return

    ifc_file = tool.Ifc.get()
    task = ifc_file.by_id(self.ifc_definition_id)
    if task.TaskTime:
        task_time = task.TaskTime
    else:
        task_time = ifcopenshell.api.sequence.add_task_time(ifc_file, task=task)
    ifcopenshell.api.sequence.edit_task_time(
        ifc_file,
        task_time=task_time,
        attributes={"ScheduleDuration": duration},
    )
    core.load_task_properties(tool.Sequence)
    tool.Sequence.refresh_task_resources()


def updateTaskPredefinedType(self: "Task", context: bpy.types.Context) -> None:
    """Callback when PredefinedType changes - auto-syncs to DEFAULT group"""
    props = tool.Sequence.get_work_schedule_props()
    if not props.is_task_update_enabled:
        return
    try:
        # The IFC attribute editing logic is already handled by the attribute's callback.
        # This callback should only be concerned with UI synchronization.

        # 1. Get the new PredefinedType value directly from the task.
        #    This is more robust than searching the attribute collection.
        try:
            from bonsai.bim.module.sequence.data import SequenceData
            task_data = SequenceData.data["tasks"][self.ifc_definition_id]
            new_predefined_type = task_data.get("PredefinedType", "NOTDEFINED") or "NOTDEFINED"
        except Exception:
            # Fallback if data is not loaded
            new_predefined_type = "NOTDEFINED"

        # 2. Synchronize the task's DEFAULT profile with this new type.
        # Only if there are no custom groups
        user_groups = UnifiedColorTypeManager.get_user_created_groups(context)
        if not user_groups:
            UnifiedColorTypeManager.sync_default_group_to_predefinedtype(context, self)

        print(f"[AUTO-SYNC] Task {self.ifc_definition_id}: PredefinedType changed, DEFAULT colortype synced to '{new_predefined_type}'.")
    except Exception as e:
        print(f"[ERROR] updateTaskPredefinedType: {e}")




def update_work_schedule_predefined_type(self: "BIMWorkScheduleProperties", context: bpy.types.Context) -> None:
    """Runs when the schedule type changes - DO NOT clean automatically"""
    try:
        print(f"🔄 Work schedule predefined type changed to: {self.work_schedule_predefined_types}")
        print("ℹ️ Variance colors will remain active - use Clear Variance button to reset")
            
    except Exception as e:
        print(f"[WARNING] Error in update_work_schedule_predefined_type: {e}")


def update_visualisation_start(self: "BIMWorkScheduleProperties", context: bpy.types.Context) -> None:
    update_visualisation_start_finish(self, context, "visualisation_start")


def update_visualisation_finish(self: "BIMWorkScheduleProperties", context: bpy.types.Context) -> None:
    update_visualisation_start_finish(self, context, "visualisation_finish")


def update_visualisation_start_finish(
    self: "BIMWorkScheduleProperties",
    context: bpy.types.Context,
    startfinish: Literal["visualisation_start", "visualisation_finish"],
) -> None:
    startfinish_value = getattr(self, startfinish)
    try:
        startfinish_datetime = parser.isoparse(startfinish_value)
    except Exception:
        try:
            startfinish_datetime = parser.parse(startfinish_value, dayfirst=True, fuzzy=True)
        except Exception:
            # If parsing fails, set to "-" only if it's not already "-" to prevent infinite loop
            if startfinish_value != "-":
                setattr(self, startfinish, "-")
            return

    # Canonicalize using tool.Sequence.isodate_datetime to ensure consistent string format
    canonical_value_str = tool.Sequence.isodate_datetime(startfinish_datetime, include_time=True)
    if getattr(self, startfinish) != canonical_value_str:
        setattr(self, startfinish, canonical_value_str)


def update_color_full(self, context):
    """Updates full bar color"""
    import bonsai.tool as tool
    material = bpy.data.materials.get("color_full")
    if material:
        props = tool.Sequence.get_animation_props()
        inputs = tool.Blender.get_material_node(material, "BSDF_PRINCIPLED").inputs
        color = inputs["Base Color"].default_value
        color[0] = props.color_full[0]
        color[1] = props.color_full[1]
        color[2] = props.color_full[2]
        try:
            inputs["Alpha"].default_value = (props.color_full[3] if len(props.color_full) > 3 else 1.0)
            material.blend_method = 'BLEND'
            material.shadow_method = 'HASHED'
        except Exception:
            pass


def update_color_progress(self, context):
    """Updates progress bar color"""
    import bonsai.tool as tool
    material = bpy.data.materials.get("color_progress")
    if material:
        props = tool.Sequence.get_animation_props()
        inputs = tool.Blender.get_material_node(material, "BSDF_PRINCIPLED").inputs
        color = inputs["Base Color"].default_value
        color[0] = props.color_progress[0]
        color[1] = props.color_progress[1]
        color[2] = props.color_progress[2]
        try:
            inputs["Alpha"].default_value = (props.color_progress[3] if len(props.color_progress) > 3 else 1.0)
            material.blend_method = 'BLEND'
            material.shadow_method = 'HASHED'
        except Exception:
            pass


def update_sort_reversed(self: "BIMWorkScheduleProperties", context: bpy.types.Context) -> None:
    """
    Callback when is_sort_reversed property changes.
    Uses the same snapshot/restore system as column operations to preserve colortype data.
    """
    global _CALLBACK_LOCK

    # Prevent recursive execution during restore operations
    if _CALLBACK_LOCK:
        return

    if self.active_work_schedule_id:
        try:
            # Import the persistence functions used by column operations
            from ..operators.task_column_persistence import save_combined_state, restore_combined_state

            # Save state BEFORE reloading
            save_combined_state()

            # Reload task tree with new sort order
            core.load_task_tree(
                tool.Sequence,
                work_schedule=tool.Ifc.get().by_id(self.active_work_schedule_id),
            )
            tool.Sequence.load_task_properties()

            # Use delayed restore to allow Blender to finish enum initialization
            def delayed_restore():
                global _CALLBACK_LOCK
                _CALLBACK_LOCK = True
                try:
                    restore_combined_state()

                    # Force UI refresh
                    for window in bpy.context.window_manager.windows:
                        for area in window.screen.areas:
                            area.tag_redraw()

                    # Force update the task tree UI list
                    if hasattr(context.scene, 'BIMTaskTreeProperties'):
                        ws_props = tool.Sequence.get_work_schedule_props()
                        ws_props.active_task_index = ws_props.active_task_index
                finally:
                    _CALLBACK_LOCK = False
                return None

            import bpy
            bpy.app.timers.register(delayed_restore, first_interval=0.05)

        except Exception as e:
            print(f"[ERROR] update_sort_reversed failed: {e}")
            import traceback
            traceback.print_exc()


def update_filter_by_active_schedule(self: "BIMWorkScheduleProperties", context: bpy.types.Context) -> None:
    if obj := context.active_object:
        product = tool.Ifc.get_entity(obj)
        assert product
        core.load_product_related_tasks(tool.Sequence, product=product)


def switch_options(self, context):
    """Toggles between visualization and snapshot"""
    if self.should_show_visualisation_ui:
        self.should_show_snapshot_ui = False
    else:
        if not self.should_show_snapshot_ui:
            self.should_show_snapshot_ui = True


def switch_options2(self, context):
    """Toggles between snapshot and visualization"""
    if self.should_show_snapshot_ui:
        self.should_show_visualisation_ui = False
    else:
        if not self.should_show_visualisation_ui:
            self.should_show_visualisation_ui = True


def update_task_colortype_group_selector(self, context):
    """Update when custom group selector changes - ensures colortypes are loaded"""
    import bonsai.tool as tool
    try:
        # 'self' is BIMAnimationProperties
        if self.task_colortype_group_selector and self.task_colortype_group_selector not in ("", "NONE"):
            print(f"📄 Custom group selected: {self.task_colortype_group_selector}")

            # Load profiles from this group into the UI to make them available
            from bonsai.bim.module.sequence.prop import UnifiedColorTypeManager
            UnifiedColorTypeManager.load_colortypes_into_collection(self, context, self.task_colortype_group_selector)

            # OPTIONALLY sync to ColorType_groups for editing if user wants
            # Only sync if user hasn't manually selected a different group for editing
            if not hasattr(self, '_ColorType_groups_manually_set') or not self._ColorType_groups_manually_set:
                self.ColorType_groups = self.task_colortype_group_selector
                print(f"🔄 Auto-synced ColorType_groups to '{self.task_colortype_group_selector}' for editing")

            # Update enum to refresh profile dropdown
            try:
                tprops = tool.Sequence.get_task_tree_props()
                wprops = tool.Sequence.get_work_schedule_props()
                if tprops.tasks and wprops.active_task_index < len(tprops.tasks):
                    task = tprops.tasks[wprops.active_task_index]
                    # Synchronize profiles for the active task with the new group
                    UnifiedColorTypeManager.sync_task_colortypes(context, task, self.task_colortype_group_selector)
                    
                    # Force enum update to refresh profile dropdown
                    task.selected_colortype_in_active_group = task.selected_colortype_in_active_group
                    
            except Exception as e:
                print(f"⚠ Error syncing task colortypes: {e}")


    except Exception as e:
        print(f"[ERROR] Error in update_task_colortype_group_selector: {e}")


def monitor_predefined_type_change(context):
    """Monitors changes in PredefinedType and auto-syncs DEFAULT"""
    try:
        tprops = tool.Sequence.get_task_tree_props()
        wprops = tool.Sequence.get_work_schedule_props()

        if not (tprops.tasks and wprops.active_task_index < len(tprops.tasks)):
            return

        task_pg = tprops.tasks[wprops.active_task_index]
        # Only sync DEFAULT if there are no custom groups
        user_groups = UnifiedColorTypeManager.get_user_created_groups(context)
        if not user_groups:
            UnifiedColorTypeManager.sync_default_group_to_predefinedtype(context, task_pg)

    except Exception as e:
        print(f"[ERROR] monitor_predefined_type_change: {e}")


def update_ColorType_group(self, context):
    """Updates active colortype group - FIXED: No auto-sync to prevent data corruption"""

    # Mark that user manually changed ColorType_groups for editing
    self._ColorType_groups_manually_set = True
    print("=" * 80)
    print(f"🚨🚨🚨 CALLBACK EXECUTED: update_ColorType_group 🚨🚨🚨")
    print(f"🎯 User manually selected '{self.ColorType_groups}' for editing")
    print("=" * 80)

    # When switching groups, the editor content would overwrite the wrong group
    # Users must manually save groups with "Save Group" button
    print(f"[WARNING]  Group switched to '{self.ColorType_groups}' - use 'Save Group' to persist changes")

    # Clean up invalid mappings
    UnifiedColorTypeManager.cleanup_invalid_mappings(context)

    # Load colortypes of the selected group
    if self.ColorType_groups:
        UnifiedColorTypeManager.load_colortypes_into_collection(self, context, self.ColorType_groups)

    # When switching groups in editor, we should NOT modify task colortype assignments
    # This was causing the last custom group to get overwritten with wrong values
    print(f"ℹ️  Editor group changed to '{self.ColorType_groups}' - task assignments unchanged")



def updateAssignedResourceName(self, context):
    pass


def updateAssignedResourceUsage(self: "TaskResource", context: object) -> None:
    import bonsai.tool as tool
    props = tool.Resource.get_resource_props()
    if not props.is_resource_update_enabled:
        return
    if not self.schedule_usage:
        return
    resource = tool.Ifc.get().by_id(self.ifc_definition_id)
    if resource.Usage and resource.Usage.ScheduleUsage == self.schedule_usage:
        return
    tool.Resource.run_edit_resource_time(resource, attributes={"ScheduleUsage": self.schedule_usage})
    tool.Sequence.load_task_properties()
    tool.Resource.load_resource_properties()
    tool.Sequence.refresh_task_resources()
    bonsai.bim.module.resource.data.refresh()
    refresh_sequence_data()
    bonsai.bim.module.pset.data.refresh()



def update_task_bar_list(self: "Task", context: bpy.types.Context) -> None:
    props = tool.Sequence.get_work_schedule_props()
    if not props.is_task_update_enabled:
        return
    
    # Add or remove from the list
    if self.has_bar_visual:
        tool.Sequence.add_task_bar(self.ifc_definition_id)
    else:
        tool.Sequence.remove_task_bar(self.ifc_definition_id)
    
    # Update visualization immediately
    try:
        tool.Sequence.refresh_task_bars()
    except Exception as e:
        print(f"[WARNING] Error refreshing task bars: {e}")



def update_use_active_colortype_group(self: "Task", context):
    """Updates usage of the active colortype group"""
    try:
        anim_props = tool.Sequence.get_animation_props()
        selected_group = getattr(anim_props, "task_colortype_group_selector", "")
        
        # CRITICAL: Use the group selected in task_colortype_group_selector, NOT ColorType_groups
        if selected_group and selected_group != "DEFAULT":
            entry = UnifiedColorTypeManager.sync_task_colortypes(context, self, selected_group)
            if entry:
                entry.enabled = bool(self.use_active_colortype_group)
                print(f"📄 Task {self.ifc_definition_id}: Group {selected_group} enabled = {entry.enabled}")
    except Exception as e:
        print(f"[ERROR] Error updating use_active_colortype_group: {e}")


def safe_set_animation_color_schemes(task_obj, value):
    """Safely sets the animation_color_schemes property with validation"""
    try:
        # Try to set the value directly first
        try:
            task_obj.animation_color_schemes = value
            return
        except Exception as enum_error:
            # If the value is not valid for the current enum, try fallback options
            if "enum" in str(enum_error).lower():
                print(f"🔄 Value '{value}' not valid for animation_color_schemes enum, trying fallbacks...")
                
                # Get current valid items to find a fallback
                try:
                    valid_items = get_animation_color_schemes_items(task_obj, bpy.context)
                    valid_values = [item[0] for item in valid_items]
                    
                    # Try to use the first valid option (usually empty string)
                    if valid_values:
                        fallback_value = valid_values[0]
                        task_obj.animation_color_schemes = fallback_value
                        print(f"🔄 Used fallback value '{fallback_value}' instead of '{value}' for animation_color_schemes")
                    else:
                        print(f"[WARNING] No valid enum options available for animation_color_schemes, skipping assignment")
                except Exception as fallback_error:
                    print(f"[ERROR] Fallback assignment for animation_color_schemes also failed: {fallback_error}")
                    pass
            else:
                raise enum_error
        
    except Exception as e:
        print(f"[ERROR] Error in safe_set_animation_color_schemes: {e}")
        try:
            # Final fallback - try empty string or first available option
            valid_items = get_animation_color_schemes_items(task_obj, bpy.context)
            if valid_items:
                fallback_value = valid_items[0][0]  # First valid option
                task_obj.animation_color_schemes = fallback_value
                print(f"🔄 Final fallback for animation_color_schemes: using '{fallback_value}'")
        except:
            print("[ERROR] All fallback attempts failed for animation_color_schemes, skipping assignment")
            pass

def safe_set_selected_colortype_in_active_group(task_obj, value, skip_validation=False):
    """Safely sets the selected_colortype_in_active_group property with validation"""
    try:
        task_id = getattr(task_obj, 'ifc_definition_id', 'unknown')
        print(f"🔧 safe_set_selected_colortype_in_active_group called for task {task_id} with value='{value}' (type: {type(value)})")
        
        # Validate the value before assignment
        if value and (value.isdigit() or value == "0"):
            print(f"🚫 Prevented assignment of invalid enum value '{value}' to selected_colortype_in_active_group")
            value = ""
        
        # Skip validation during copy operations to allow setting values that might be valid later
        if not skip_validation:
            # Get context for validation
            context = bpy.context
            valid_items = get_custom_group_colortype_items(task_obj, context)
            valid_values = [item[0] for item in valid_items]
            
            if value and value not in valid_values:
                print(f"🚫 Value '{value}' not in valid enum options: {valid_values}, using empty string")
                value = ""
        
        # Safely set the property with fallback handling
        try:
            # Final validation just before assignment
            if str(value) in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or str(value).isdigit():
                print(f"🚫 CRITICAL: Blocking numeric value '{value}' just before setattr")
                value = ""
            
            print(f"🔧 About to setattr selected_colortype_in_active_group = '{value}'")
            setattr(task_obj, "selected_colortype_in_active_group", value)
            
        except Exception as enum_error:
            print(f"[ERROR] setattr failed with error: {enum_error}")
            # If the value is not valid for the current enum, try fallback options
            if "enum" in str(enum_error).lower():
                # Get current valid items to find a fallback
                try:
                    valid_items = get_custom_group_colortype_items(task_obj, bpy.context)
                    valid_values = [item[0] for item in valid_items]
                    
                    # Try to use the first valid option (usually empty string)
                    if valid_values:
                        fallback_value = valid_values[0]
                        print(f"🔄 Trying fallback value '{fallback_value}' instead of '{value}' for enum")
                        
                        # If empty string still fails, try the first non-empty ColorType
                        if fallback_value == "" and len(valid_values) > 1:
                            fallback_value = valid_values[1]  # First actual ColorType
                            print(f"🔄 Empty string failed, trying first ColorType: '{fallback_value}'")
                        
                        setattr(task_obj, "selected_colortype_in_active_group", fallback_value)
                    else:
                        print(f"[WARNING] No valid enum options available, skipping assignment")
                except Exception as fallback_error:
                    print(f"[ERROR] Fallback assignment also failed: {fallback_error}")
                    # Last resort - don't assign anything
                    pass
            else:
                raise enum_error
        
    except Exception as e:
        print(f"[ERROR] Error in safe_set_selected_colortype_in_active_group: {e}")
        # Try to get any valid fallback instead of forcing empty string
        try:
            valid_items = get_custom_group_colortype_items(task_obj, bpy.context)
            if valid_items:
                fallback_value = valid_items[0][0]  # First valid option
                setattr(task_obj, "selected_colortype_in_active_group", fallback_value)
                print(f"🔄 Final fallback: using '{fallback_value}'")
        except:
            print("[ERROR] All fallback attempts failed, skipping assignment")
            pass

def update_selected_colortype_in_active_group(self: "Task", context):
    """Updates the selected colortype in the active group"""
    try:
        # Validate that the current value is not a numeric string or invalid
        current_value = self.selected_colortype_in_active_group
        
        # Get valid enum items to check against
        valid_items = get_custom_group_colortype_items(self, context)
        valid_values = [item[0] for item in valid_items]
        
        # Check for invalid values
        if current_value and (current_value.isdigit() or current_value not in valid_values):
            print(f"[WARNING] Invalid enum value '{current_value}' detected for selected_colortype_in_active_group, resetting to empty")
            # Don't recursively call the update function - directly access the property
            self.__dict__["selected_colortype_in_active_group"] = ""
            return
        
        anim_props = tool.Sequence.get_animation_props()
        selected_group = getattr(anim_props, "task_colortype_group_selector", "")
        
        # CRITICAL: Use the group selected in task_colortype_group_selector, NOT ColorType_groups
        if selected_group and selected_group != "DEFAULT":
            entry = UnifiedColorTypeManager.sync_task_colortypes(context, self, selected_group)
            if entry:
                entry.selected_colortype = self.selected_colortype_in_active_group
                print(f"📄 Task {self.ifc_definition_id}: Selected colortype = {entry.selected_colortype} in group {selected_group}")
    except Exception as e:
        print(f"[ERROR] Error updating selected_colortype_in_active_group: {e}")




# ============================================================================
# PROPERTY GROUPS
# ============================================================================

# === Helper invoked by operator.py (safe no-op if nothing to clean) ==========================
def cleanup_all_tasks_colortype_mappings(context):
    """
    Best-effort cleanup to keep task→colortype mappings consistent.
    This is intentionally resilient: if the data structure isn't present or differs
    between Bonsai versions, it silently returns.
    """
    try:
        # Reuse our UPM persistence hooks; if no data, nothing to do
        data = UnifiedColorTypeManager._read_sets_json(context)
        if not isinstance(data, dict):
            return
        # Optionally prune obviously empty groups/entries if they appear as None/[]
        for gkey, gval in list(data.items()):
            if gval is None or gval == {}:
                del data[gkey]
                continue
            if isinstance(gval, dict):
                for pkey, plist in list(gval.items()):
                    if plist in (None, [], {}, "null"):
                        del gval[pkey]
        UnifiedColorTypeManager._write_sets_json(context, data)
    except Exception:
        # Do not raise; operators call this after user actions and must not crash
        pass


# === HUD CALLBACKS (GPU-based) ====================================
def update_gpu_hud_visibility(self, context):
    """
    SAFE callback to register/unregister the main GPU HUD handler.
    The handler is active if ANY of the HUD components are enabled.
    CRASH-PROTECTED VERSION.
    """
    try:
        print("🔧 3D HUD checkbox toggled - SAFE MODE")
        is_any_hud_enabled = (
            getattr(self, "enable_text_hud", False) or
            getattr(self, "enable_timeline_hud", False) or
            getattr(self, "enable_legend_hud", False) or
            getattr(self, "enable_3d_legend_hud", False)
        )

        from .. import hud as hud_overlay

        def deferred_update():
            try:
                # SAFE HUD handler management
                if is_any_hud_enabled:
                    if not hud_overlay.is_hud_enabled():
                        hud_overlay.register_hud_handler()
                else:
                    if hud_overlay.is_hud_enabled():
                        hud_overlay.unregister_hud_handler()
                        print("[ERROR] GPU HUD handler unregistered")

                # Handle 3D Legend HUD toggle specifically 
                enable_3d_legend = getattr(self, "enable_3d_legend_hud", False)
                print(f"📋 3D Legend HUD checkbox: {enable_3d_legend}")

                if enable_3d_legend:
                    # Check if 3D Legend HUD exists, if not create it
                    hud_exists = any(obj.get("is_3d_legend_hud", False) for obj in bpy.data.objects)
                    if not hud_exists:
                        try:
                            bpy.ops.bim.setup_3d_legend_hud()
                            print("🟢 3D Legend HUD auto-created on enable")
                        except Exception as e:
                            print(f"[WARNING] Failed to auto-create 3D Legend HUD: {e}")
                    else:
                        # Just show existing HUD
                        legend_collection = bpy.data.collections.get("Schedule_Display_3D_Legend")
                        if legend_collection:
                            legend_collection.hide_viewport = False
                            legend_collection.hide_render = False
                        for obj in bpy.data.objects:
                            if obj.get("is_3d_legend_hud", False):
                                obj.hide_viewport = False
                                obj.hide_render = False
                        print("👁️ 3D Legend HUD made visible")
                else:
                    # Clear 3D Legend HUD if it exists
                    hud_exists = any(obj.get("is_3d_legend_hud", False) for obj in bpy.data.objects)
                    if hud_exists:
                        try:
                            bpy.ops.bim.clear_3d_legend_hud()
                            print("🔴 3D Legend HUD auto-cleared on disable")
                        except Exception as e:
                            print(f"[WARNING] Failed to auto-clear 3D Legend HUD: {e}")
                            # Fallback: just hide
                            legend_collection = bpy.data.collections.get("Schedule_Display_3D_Legend")
                            if legend_collection:
                                legend_collection.hide_viewport = True
                                legend_collection.hide_render = True
                            for obj in bpy.data.objects:
                                if obj.get("is_3d_legend_hud", False):
                                    obj.hide_viewport = True
                                    obj.hide_render = True
                            print("👁️‍🗨️ 3D Legend HUD hidden as fallback")

                # Safe HUD refresh
                try:
                    force_hud_refresh(self, context)
                except Exception as refresh_e:
                    print(f"[WARNING] HUD refresh failed: {refresh_e}")

            except Exception as e:
                print(f"[ERROR] Deferred HUD update failed: {e}")
                import traceback
                traceback.print_exc()
            return None

        # Register timer with error protection
        if not bpy.app.timers.is_registered(deferred_update):
            bpy.app.timers.register(deferred_update, first_interval=0.05)
            print("⏱️ Safe HUD update timer scheduled")

    except Exception as main_e:
        print(f"[ERROR] CRITICAL: HUD callback failed: {main_e}")
        import traceback
        traceback.print_exc()
        # Ensure we don't crash Blender
        return


def update_hud_gpu(self, context):
    """Callback to update GPU HUD"""
    try:
        if getattr(self, "enable_text_hud", False):
            def refresh_hud():
                try:
                    bpy.ops.bim.refresh_schedule_hud()
                except Exception:
                    pass
            bpy.app.timers.register(refresh_hud, first_interval=0.05)
    except Exception:
        pass

# Context-specific visibility update functions
def update_animation_camera_visibility(self, context):
    """Toggles the visibility of animation cameras and their related objects in the viewport."""
    try:
        # Find animation cameras using simple checks
        cameras_to_toggle = []
        for obj in bpy.data.objects:
            if obj.type == 'CAMERA':
                # Check if it's an animation camera
                if (obj.get('is_animation_camera') or 
                    obj.get('camera_context') == 'animation' or 
                    ('4D_Animation_Camera' in obj.name and 'Snapshot' not in obj.name)):
                    cameras_to_toggle.append(obj)

        objects_to_toggle = []
        for cam_obj in cameras_to_toggle:
            objects_to_toggle.append(cam_obj)

            # Find associated path and target objects by name convention
            path_name = f"4D_OrbitPath_for_{cam_obj.name}"
            target_name = f"4D_OrbitTarget_for_{cam_obj.name}"

            path_obj = bpy.data.objects.get(path_name)
            if path_obj:
                objects_to_toggle.append(path_obj)

            target_obj = bpy.data.objects.get(target_name)
            if target_obj:
                objects_to_toggle.append(target_obj)

        for obj in objects_to_toggle:
            obj.hide_viewport = self.hide_all_animation_cameras
            obj.hide_render = self.hide_all_animation_cameras

        # Force redraw
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()

        print(f"Animation cameras visibility: {'Hidden' if self.hide_all_animation_cameras else 'Shown'} ({len(cameras_to_toggle)} cameras)")

    except Exception as e:
        print(f"Error toggling animation camera visibility: {e}")

def update_snapshot_camera_visibility(self, context):
    """Toggles the visibility of snapshot cameras and their related objects in the viewport."""
    try:
        # Find snapshot cameras using simple checks
        cameras_to_toggle = []
        for obj in bpy.data.objects:
            if obj.type == 'CAMERA':
                # Check if it's a snapshot camera
                if (obj.get('is_snapshot_camera') or 
                    obj.get('camera_context') == 'snapshot' or 
                    'Snapshot_Camera' in obj.name):
                    cameras_to_toggle.append(obj)

        objects_to_toggle = []
        for cam_obj in cameras_to_toggle:
            objects_to_toggle.append(cam_obj)

            # Find associated target objects
            target_name = f"Snapshot_Target"
            target_obj = bpy.data.objects.get(target_name)
            if target_obj:
                objects_to_toggle.append(target_obj)

        for obj in objects_to_toggle:
            obj.hide_viewport = self.hide_all_snapshot_cameras
            obj.hide_render = self.hide_all_snapshot_cameras

        # Force redraw
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()

        print(f"Snapshot cameras visibility: {'Hidden' if self.hide_all_snapshot_cameras else 'Shown'} ({len(cameras_to_toggle)} cameras)")

    except Exception as e:
        print(f"Error toggling snapshot camera visibility: {e}")

def force_hud_refresh(self, context):
    """Improved callback that forces HUD update with delay"""
    try:
        def delayed_refresh():
            try:
                # Ensure handlers are registered
                import bonsai.bim.module.sequence.hud as hud_overlay
                
                # Also update 3D Legend HUD when Legend HUD settings change
                try:
                    print(f"🔍 Checking if 3D Legend HUD should auto-update...")
                    enable_3d_legend = getattr(self, 'enable_3d_legend_hud', False)
                    print(f"  📋 enable_3d_legend_hud: {enable_3d_legend}")
                    
                    if enable_3d_legend:
                        # Check if 3D Legend HUD exists
                        hud_exists = any(obj.get("is_3d_legend_hud", False) for obj in bpy.data.objects)
                        print(f"  📋 3D Legend HUD exists in scene: {hud_exists}")
                        
                        if hud_exists:
                            print("🔄 AUTO-UPDATING 3D Legend HUD due to Legend HUD setting change")
                            bpy.ops.bim.update_3d_legend_hud()
                        else:
                            print("[WARNING] 3D Legend HUD enabled but no 3D HUD found in scene")
                    else:
                        print("ℹ️ 3D Legend HUD not enabled, skipping auto-update")
                except Exception as e:
                    print(f"[ERROR] Failed to auto-update 3D Legend HUD during refresh: {e}")
                    import traceback
                    traceback.print_exc()
                hud_overlay.ensure_hud_handlers()
                
                bpy.ops.bim.refresh_schedule_hud()
                
                # Force redraw of 3D viewports
                for area in bpy.context.screen.areas:
                    if area.type == 'VIEW_3D':
                        area.tag_redraw()
                        
            except Exception as e:
                print(f"[WARNING] Delayed HUD refresh failed: {e}")
            return None  # Do not repeat
        
        # Register timer for delayed update
        bpy.app.timers.register(delayed_refresh, first_interval=0.1)
        
    except Exception as e:
        print(f"[ERROR] Force HUD refresh failed: {e}")

# === END HUD CALLBACKS (GPU) ================================================

# === Camera & Orbit Properties ===

def update_active_animation_camera(self, context):
    """
    Callback to set the animation camera as active in the scene.
    """
    camera_obj = self.active_animation_camera
    print(f"🔄 CALLBACK: update_active_animation_camera called")
    print(f"🔄 CALLBACK: camera_obj = {camera_obj}")
    print(f"🔄 CALLBACK: camera_obj type = {type(camera_obj)}")

    if not camera_obj:
        print(f"[WARNING] CALLBACK: No camera object, returning")
        return

    print(f"🔄 CALLBACK: Will load values from camera '{camera_obj.name}'")

    # PROTECTION: During animation, only allow static cameras
    try:
        import bonsai.tool as tool
        anim_props = tool.Sequence.get_animation_props()
        is_animation_active = getattr(anim_props, 'is_animation_created', False)

        if is_animation_active:
            # Check if it is a static camera (allowed during animation)
            if (camera_obj.get('camera_type') == 'STATIC' or
                '4D_Camera_Static' in camera_obj.name or
                camera_obj.get('orbit_mode') == 'NONE'):
                # Static camera is allowed during animation
                pass
            else:
                print(f"[WARNING] Cannot change to orbit camera ({camera_obj.name}) during animation. Only static cameras allowed.")
                return
    except Exception as e:
        print(f"[WARNING] Could not check animation status: {e}")

    def set_camera_deferred():
        print(f"🔄 TIMER: set_camera_deferred called for '{camera_obj.name}'")
        try:
            if camera_obj and bpy.context.scene:
                bpy.context.scene.camera = camera_obj

                # NEW: Load values from the selected camera to the panel
                try:
                    import bonsai.tool as tool
                    anim_props = tool.Sequence.get_animation_props()
                    camera_props = anim_props.camera_orbit

                    print(f"🔄 LOADING: Loading camera values from '{camera_obj.name}' to panel...")

                    # Show all values saved in the camera
                    print(f"🔍 CAMERA VALUES: orbit_height stored = {camera_obj.get('orbit_height', 'NOT SET')}")
                    print(f"🔍 CAMERA VALUES: orbit_start_angle_deg stored = {camera_obj.get('orbit_start_angle_deg', 'NOT SET')}")
                    print(f"🔍 CAMERA VALUES: orbit_direction stored = {camera_obj.get('orbit_direction', 'NOT SET')}")
                    print(f"🔍 CAMERA VALUES: orbit_radius stored = {camera_obj.get('orbit_radius', 'NOT SET')}")

                    # Load basic camera properties
                    if hasattr(camera_obj, 'data') and camera_obj.data:
                        camera_props.camera_focal_mm = camera_obj.data.lens
                        camera_props.camera_clip_start = camera_obj.data.clip_start
                        camera_props.camera_clip_end = camera_obj.data.clip_end

                    # Load orbit properties from the camera
                    old_height = camera_props.orbit_height
                    camera_props.orbit_mode = camera_obj.get('orbit_mode', 'CIRCLE_360')
                    camera_props.orbit_radius = camera_obj.get('orbit_radius', 10.0)
                    camera_props.orbit_height = camera_obj.get('orbit_height', 8.0)
                    camera_props.orbit_start_angle_deg = camera_obj.get('orbit_start_angle_deg', 0.0)
                    camera_props.orbit_direction = camera_obj.get('orbit_direction', 'CCW')
                    camera_props.orbit_radius_mode = camera_obj.get('orbit_radius_mode', 'AUTO')
                    camera_props.orbit_path_shape = camera_obj.get('orbit_path_shape', 'CIRCLE')
                    camera_props.orbit_path_method = camera_obj.get('orbit_path_method', 'FOLLOW_PATH')
                    camera_props.interpolation_mode = camera_obj.get('interpolation_mode', 'LINEAR')


                except Exception as load_error:
                    print(f"[WARNING] Error loading camera values to panel: {load_error}")

                # Force UI update
                for window in bpy.context.window_manager.windows:
                    for area in window.screen.areas:
                        if area.type == 'VIEW_3D':
                            area.tag_redraw()
        except Exception as e:
            print(f"[ERROR] Error setting animation camera: {e}")
        return None

    # Use a timer to avoid context issues
    bpy.app.timers.register(set_camera_deferred, first_interval=0.01)

def update_active_snapshot_camera(self, context):
    """
    Callback to set the snapshot camera as active in the scene.
    """
    camera_obj = self.active_snapshot_camera
    if not camera_obj:
        return

    # NOTE: For snapshots, camera changes ARE allowed - no protection

    def set_camera_deferred():
        try:
            if camera_obj and bpy.context.scene:
                bpy.context.scene.camera = camera_obj
                
                # Force UI update
                for window in bpy.context.window_manager.windows:
                    for area in window.screen.areas:
                        if area.type == 'VIEW_3D':
                            area.tag_redraw()
        except Exception as e:
            print(f"[ERROR] Error setting snapshot camera: {e}")
        return None

    # Use a timer to avoid context issues
    bpy.app.timers.register(set_camera_deferred, first_interval=0.01)

def update_active_4d_camera(self, context):
    """
    Legacy callback to set the scene camera when the active 4D camera changes.
    Uses a timer to avoid context issues when modifying `scene.camera`.
    """
    camera_name = self.active_4d_camera.name if self.active_4d_camera else None
    if not camera_name:
        return

    # PROTECTION: Only block if an animation is active (snapshots DO allow changes)
    try:
        import bonsai.tool as tool
        anim_props = tool.Sequence.get_animation_props()
        is_animation_active = getattr(anim_props, 'is_animation_created', False)

        if is_animation_active:
            print(f"[WARNING] Cannot change 4D camera while animation is active. Reset animation first.")
            return
    except Exception as e:
        print(f"[WARNING] Could not check animation status: {e}")

    def set_camera_deferred():
        try:
            cam_obj = bpy.data.objects.get(camera_name)
            if cam_obj and bpy.context.scene:
                bpy.context.scene.camera = cam_obj
                # Force UI update to reflect the change
                for window in bpy.context.window_manager.windows:
                    for area in window.screen.areas:
                        if area.type in ('PROPERTIES', 'VIEW_3D'):
                            area.tag_redraw()
        except Exception as e:
            print(f"Error in deferred camera set: {e}")
        return None  # The timer runs only once

    bpy.app.timers.register(set_camera_deferred)

def toggle_3d_text_visibility(self, context):
    """Shows/hides the 3D text collection AND the 3D Legend HUD collection."""
    should_hide = not self.show_3d_schedule_texts
    print(f"🔄 toggle_3d_text_visibility called: show_3d_schedule_texts={self.show_3d_schedule_texts}, should_hide={should_hide}")

    # --- AUTOMATIC DEACTIVATION LOGIC ---
    # If 3D HUD Render is disabled, automatically disable the 3D Legend HUD
    try:
        import bonsai.tool as tool
        anim_props = tool.Sequence.get_animation_props()
        camera_props = anim_props.camera_orbit
        
        if should_hide:  # If 3D HUD Render is being disabled
            current_legend_enabled = getattr(camera_props, "enable_3d_legend_hud", False)
            if current_legend_enabled:
                print("🔴 3D HUD Render disabled: Auto-disabling 3D Legend HUD checkbox")
                camera_props.enable_3d_legend_hud = False
                
    except Exception as e:
        print(f"[WARNING] Error in auto-disable logic: {e}")
    
    # Toggle visibility for "Schedule_Display_Texts"
    try:
        collection_texts = bpy.data.collections.get("Schedule_Display_Texts")
        if collection_texts:
            collection_texts.hide_viewport = should_hide
            collection_texts.hide_render = should_hide
            # Also iterate over objects to ensure visibility
            for obj in collection_texts.objects:
                obj.hide_viewport = should_hide
                obj.hide_render = should_hide
    except Exception as e:
        print(f"[ERROR] Error toggling 3D text visibility: {e}")

    # Toggle visibility for "Schedule_Display_3D_Legend" (controlled by show_3d_schedule_texts)
    try:
        import bonsai.tool as tool
        camera_props = tool.Sequence.get_animation_props().camera_orbit
        legend_should_be_hidden = should_hide or not camera_props.enable_3d_legend_hud

        collection_legend = bpy.data.collections.get("Schedule_Display_3D_Legend")
        if collection_legend:
            collection_legend.hide_viewport = legend_should_be_hidden
            collection_legend.hide_render = legend_should_be_hidden
            # Iterate over the legend objects to ensure visibility
            for obj in collection_legend.objects:
                obj.hide_viewport = legend_should_be_hidden
                obj.hide_render = legend_should_be_hidden
    except Exception as e:
        print(f"[ERROR] Error toggling 3D Legend HUD visibility: {e}")

    # Force screen refresh
    try:
        for window in context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()
    except Exception:
        pass
        
    # SEPARATE control for individual 3D Legend HUD objects (controlled by enable_3d_legend_hud)
    try:
        import bonsai.tool as tool
        anim_props = tool.Sequence.get_animation_props()
        camera_props = anim_props.camera_orbit
        legend_hud_enabled = getattr(camera_props, "enable_3d_legend_hud", False)
        
        # If 3D Legend HUD is disabled individually, hide all its objects regardless of show_3d_schedule_texts
        if not legend_hud_enabled:
            objects_hidden = 0
            for obj in bpy.data.objects:
                if obj.get("is_3d_legend_hud", False):
                    obj.hide_viewport = True
                    obj.hide_render = True
                    objects_hidden += 1
            if objects_hidden > 0:
                print(f"🔴 3D Legend HUD disabled: {objects_hidden} objects hidden individually")
        else:
            # If enabled, follow the main 3D HUD visibility setting
            objects_shown = 0
            for obj in bpy.data.objects:
                if obj.get("is_3d_legend_hud", False):
                    obj.hide_viewport = should_hide  # Follow main 3D HUD setting
                    obj.hide_render = should_hide
                    objects_shown += 1
            if objects_shown > 0:
                print(f"🟢 3D Legend HUD enabled: {objects_shown} objects follow main HUD visibility (hide={should_hide})")
                
    except Exception as e:
        print(f"[ERROR] Error handling individual 3D Legend HUD visibility: {e}")

    # Force refresh of all 3D areas
    try:
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()
    except Exception:
        pass



def update_colortype_considerations(self, context):
    """Validation logic for colortype states - preserving user configurations"""
    try:
        # Keep essential functionality while preserving user settings
        # DO NOT automatically set consider_active = True

        print(f"ColorType update called - user settings preserved")

        # Any validation logic can go here, but without changing user checkboxes

    except Exception as e:
        print(f"Error in colortype considerations update: {e}")



def update_legend_hud_on_group_change(self, context):
    """Callback that runs when the enabled state of a group changes"""
    try:
        print("=" * 80)
        print(f"🚨🚨🚨 CALLBACK EXECUTED: update_legend_hud_on_group_change 🚨🚨🚨")
        print(f"🔄 GROUP CHANGE CALLBACK: Group '{self.group}' enabled changed to: {self.enabled}")
        print("=" * 80)

    
        # When a group is activated/deactivated, update the UI state snapshot
        from ..operators.operator import snapshot_all_ui_state
        snapshot_all_ui_state(context)
        # --- END OF CORRECTION ---
        
        # Automatically synchronize animation_color_schemes
        _sync_animation_color_schemes_with_active_groups(context)
        

        # Invalidate legend HUD cache to refresh
        from ..hud import invalidate_legend_hud_cache, refresh_hud
        invalidate_legend_hud_cache()

        # Force a viewport redraw
        refresh_hud()

        print("🔄 Legend HUD cache invalidated and viewport refreshed")


    except Exception as e:
        import traceback
        print(f"[WARNING] Could not auto-update Legend HUD: {e}")
        traceback.print_exc()


def _sync_animation_color_schemes_with_active_groups(context):
    """
    Automatically synchronizes the animation_color_schemes field of tasks
    with the ColorType of the active group when a group checkbox is checked/unchecked.
    """
    try:
        import bonsai.tool as tool
        
        # Get task properties
        tprops = tool.Sequence.get_task_tree_props()
        if not tprops or not hasattr(tprops, 'tasks'):
            return
        
        synced_tasks = 0
        
        for task in tprops.tasks:
            try:
                # Only process tasks that use active groups
                use_active_group = getattr(task, 'use_active_colortype_group', False)
                if not use_active_group:
                    continue
                
                # Find active group (enabled=True) that is not DEFAULT
                active_group_colortype = ''
                group_choices = getattr(task, 'colortype_group_choices', [])
                
                for choice in group_choices:
                    group_name = getattr(choice, 'group_name', '')
                    enabled = getattr(choice, 'enabled', False)
                    colortype = getattr(choice, 'selected_colortype', '')
                    
                    if enabled and group_name != 'DEFAULT' and colortype:
                        active_group_colortype = colortype
                        break
                
                # Synchronize animation_color_schemes with the active group
                if active_group_colortype:
                    current_animation_schemes = getattr(task, 'animation_color_schemes', '')
                    if active_group_colortype != current_animation_schemes:
                        print(f"🔄 AUTO-SYNC: Task {task.ifc_definition_id} - '{current_animation_schemes}' → '{active_group_colortype}'")
                        safe_set_animation_color_schemes(task, active_group_colortype)
                        synced_tasks += 1
                
            except Exception as e:
                print(f"[ERROR] Error syncing task {getattr(task, 'ifc_definition_id', '?')}: {e}")
                continue
        
        if synced_tasks > 0:
            print(f"✅ Auto-synchronized {synced_tasks} tasks")

    except Exception as e:
        print(f"[ERROR] Error in auto-sync animation_color_schemes: {e}")

def update_selected_date(self: "DatePickerProperties", context: bpy.types.Context) -> None:
    include_time = True
    selected_date = tool.Sequence.parse_isodate_datetime(self.selected_date, include_time)
    selected_date = selected_date.replace(hour=self.selected_hour, minute=self.selected_min, second=self.selected_sec)
    self.selected_date = tool.Sequence.isodate_datetime(selected_date, include_time)
