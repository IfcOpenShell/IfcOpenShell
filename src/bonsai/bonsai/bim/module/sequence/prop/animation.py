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
import bonsai.tool as tool
from bonsai.bim.module.sequence.data import SequenceData, AnimationColorSchemeData
from mathutils import Color
from bpy.types import PropertyGroup
from bpy.props import (
    PointerProperty,
    StringProperty,
    EnumProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    CollectionProperty,
)
from typing import TYPE_CHECKING, Dict, List, Set

# ============================================================================
# UNIFIED COLORTYPE MANAGER - CENTRAL CLASS FOR MANAGING PROFILES
# ============================================================================

class UnifiedColorTypeManager:
    @staticmethod
    def ensure_default_group(context):
        """Delegate to consolidated utility function."""
        from ..utils.color_schemes_utils import ensure_default_group
        return ensure_default_group(context)

    @staticmethod
    def _read_sets_json(context):
        """Ensures the DEFAULT group exists with 13 predefined profiles and complete properties.
        Only creates DEFAULT group if no custom groups exist to avoid confusion."""
        scene = context.scene
        key = "BIM_AnimationColorSchemesSets"
        raw = scene.get(key, "{}")
        try:
            data = json.loads(raw) if isinstance(raw, str) else (raw or {})
            if not isinstance(data, dict):
                data = {}
        except Exception:
            data = {}
        # Check if custom groups already exist
        user_groups = [g for g in data.keys() if g != "DEFAULT"]
        
        # Create DEFAULT if it does not exist AND there are no custom groups
        if "DEFAULT" not in data:
            if not user_groups:
                default_colortypes = [
                    {"name": "CONSTRUCTION", "start_color": [1,1,1,0], "in_progress_color": [0,1,0,1], "end_color": [0.3,1,0.3,1]},
                    {"name": "INSTALLATION", "start_color": [1,1,1,0], "in_progress_color": [0,1,0,1], "end_color": [0.3,0.8,0.5,1]},
                    {"name": "DEMOLITION", "start_color": [1,1,1,1], "in_progress_color": [1,0,0,1], "end_color": [0,0,0,0]},
                    {"name": "REMOVAL", "start_color": [1,1,1,1], "in_progress_color": [1,0,0,1], "end_color": [0,0,0,0]},
                    {"name": "DISPOSAL", "start_color": [1,1,1,1], "in_progress_color": [1,0,0,1], "end_color": [0,0,0,0]},
                    {"name": "DISMANTLE", "start_color": [1,1,1,1], "in_progress_color": [1,0,0,1], "end_color": [0,0,0,0]},
                    {"name": "OPERATION", "start_color": [1,1,1,1], "in_progress_color": [0,0,1,1], "end_color": [1,1,1,1]},
                    {"name": "MAINTENANCE", "start_color": [1,1,1,1], "in_progress_color": [0,0,1,1], "end_color": [1,1,1,1]},
                    {"name": "ATTENDANCE", "start_color": [1,1,1,1], "in_progress_color": [0,0,1,1], "end_color": [1,1,1,1]},
                    {"name": "RENOVATION", "start_color": [1,1,1,1], "in_progress_color": [0,0,1,1], "end_color": [0.9,0.9,0.9,1]},
                    {"name": "LOGISTIC", "start_color": [1,1,1,1], "in_progress_color": [1,1,0,1], "end_color": [1,0.8,0.3,1]},
                    {"name": "MOVE", "start_color": [1,1,1,1], "in_progress_color": [1,1,0,1], "end_color": [0.8,0.6,0,1]},
                    {"name": "NOTDEFINED", "start_color": [0.7,0.7,0.7,1], "in_progress_color": [0.5,0.5,0.5,1], "end_color": [0.3,0.3,0.3,1]},
                    {"name": "USERDEFINED", "start_color": [0.7,0.7,0.7,1], "in_progress_color": [0.5,0.5,0.5,1], "end_color": [0.3,0.3,0.3,1]},
                ] # Fill with complete fields
                for colortype in default_colortypes:
                    colortype.update({
                        "consider_start": False,
                        "consider_active": True,
                        "consider_end": True,
                        "use_start_original_color": False,
                        "use_active_original_color": False,
                        "use_end_original_color": colortype["name"] not in ["DEMOLITION", "REMOVAL", "DISPOSAL", "DISMANTLE"],
                        "start_transparency": 0.0,
                        "active_start_transparency": 0.0,
                        "active_finish_transparency": 0.0,
                        "active_transparency_interpol": 1.0,
                        "end_transparency": 0.0
                    })
                data["DEFAULT"] = {"ColorTypes": default_colortypes}
                scene[key] = json.dumps(data)
            else:
                print("[WARNING] Custom groups detected - DEFAULT group is not created automatically")
        
        # Ensure that DEFAULT has ALL the necessary profiles #
        # ONLY if there are no custom groups (avoids confusion) #
        if "DEFAULT" in data and not user_groups:
            existing_names = {p.get("name") for p in data["DEFAULT"].get("ColorTypes", [])}
            required_names = {
                "CONSTRUCTION", "INSTALLATION", "DEMOLITION", "REMOVAL", 
                "DISPOSAL", "DISMANTLE", "OPERATION", "MAINTENANCE", 
                "ATTENDANCE", "RENOVATION", "LOGISTIC", "MOVE", "NOTDEFINED"
            }
            
            # Add missing profiles #
            for missing_name in required_names - existing_names:
                missing_colortype = UnifiedColorTypeManager._create_default_colortype_data(missing_name)
                data["DEFAULT"]["ColorTypes"].append(missing_colortype)
            
            # Save changes if profiles were added #
            if required_names - existing_names:
                scene[key] = json.dumps(data)
        
        return data
    
    @staticmethod
    def _read_sets_json(context):
        """Safely reads the profiles JSON from the scene."""
        import json
        try:
            scene = context.scene
            key = "BIM_AnimationColorSchemesSets"
            raw = scene.get(key, "{}")
            data = json.loads(raw) if isinstance(raw, str) else (raw or {})
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    @staticmethod
    def _write_sets_json(context, data):
        """Safely writes the ColorTypes JSON to the scene."""
        import json
        try:
            context.scene["BIM_AnimationColorSchemesSets"] = json.dumps(data)
        except Exception:
            pass

    @staticmethod
    def get_all_predefined_types(context) -> list:
        """Gets all PredefinedTypes from loaded tasks to ensure ColorTypes exist for them."""
        try:
            from bonsai.bim.module.sequence.data import SequenceData
            if not SequenceData.is_loaded:
                SequenceData.load()
            
            types = {"NOTDEFINED", "USERDEFINED"} # Always include these
            tasks_data = (SequenceData.data or {}).get("tasks", {})
            for task in tasks_data.values():
                if predef_type := task.get("PredefinedType"):
                    types.add(predef_type)
            return sorted(list(types))
        except Exception:
            # Fallback with common types if reading fails
            return [
                "ATTENDANCE", "CONSTRUCTION", "DEMOLITION", "DISMANTLE",
                "DISPOSAL", "INSTALLATION", "LOGISTIC", "MAINTENANCE",
                "MOVE", "OPERATION", "REMOVAL", "RENOVATION", "NOTDEFINED"
            ]

    @staticmethod
    def ensure_colortype_in_group(context, group_name: str, colortype_name: str):
        """Ensures that a specific ColorType exists within a group in the JSON."""
        if not group_name or not colortype_name:
            return
        data = UnifiedColorTypeManager._read_sets_json(context)
        group = data.setdefault(group_name, {"ColorTypes": []})

        existing_colortypes = {p.get("name") for p in group.get("ColorTypes", [])}

        if colortype_name not in existing_colortypes:
            # DEFAULT: Start disabled by default #
            consider_start = False if (group_name == "DEFAULT") else True
            # Use distinctive colors based on colortype name instead of generic green/gray #
            color_map = {
                "LOGISTIC": {"active": [1,1,0,1], "end": [1,0.8,0.3,1]},        # Yellow->Orange
                "DEMOLITION": {"active": [1,0,0,1], "end": [0.5,0,0,1]},       # Red->Dark Red
                "REMOVAL": {"active": [1,0,0,1], "end": [0.5,0,0,1]},          # Red->Dark Red
                "RENOVATION": {"active": [0,0,1,1], "end": [0.5,0.5,1,1]},     # Blue->Light Blue
                "CONSTRUCTION": {"active": [0,1,0,1], "end": [0.3,1,0.3,1]},   # Green->Light Green
                "INSTALLATION": {"active": [0,1,0,1], "end": [0.3,0.8,0.5,1]}, # Green->Aqua Green
            }
            colors = color_map.get(colortype_name, {"active": [1,0,1,1], "end": [1,0.5,1,1]})  # Magenta fallback #

            colortype_payload = {
                "name": colortype_name,
                "start_color": [1,1,1,0],
                "in_progress_color": colors["active"],
                "end_color": colors["end"],
                "use_end_original_color": True,
                # Complete fields for consistency #
                "consider_start": consider_start,
                "consider_active": True, 
                "consider_end": True,
                "use_start_original_color": False, 
                "use_active_original_color": False,
                "start_transparency": 0.0, 
                "active_start_transparency": 0.0, 
                "active_finish_transparency": 0.0,
                "active_transparency_interpol": 1.0, 
                "end_transparency": 0.0
            }
            group["ColorTypes"].append(colortype_payload)
            UnifiedColorTypeManager._write_sets_json(context, data)
    
    @staticmethod
    def ensure_default_group_has_predefined_types(context):
        """Ensures that the DEFAULT group contains a ColorType for each existing PredefinedType."""
        all_types = UnifiedColorTypeManager.get_all_predefined_types(context)
        for p_type in all_types:
            UnifiedColorTypeManager.ensure_colortype_in_group(context, "DEFAULT", p_type)
    
    @staticmethod
    def ensure_default_group_has_all_predefined_types(context):
        """Ensures that the DEFAULT group contains ALL 13 predefined ColorTypes, regardless of tasks.""" #
        # Complete list of all possible PredefinedTypes (13 types) #
        all_predefined_types = [
            "CONSTRUCTION", "INSTALLATION", "DEMOLITION", "REMOVAL",
            "DISPOSAL", "DISMANTLE", "OPERATION", "MAINTENANCE", 
            "ATTENDANCE", "RENOVATION", "LOGISTIC", "MOVE", "NOTDEFINED"
        ]
        
        for p_type in all_predefined_types:
            UnifiedColorTypeManager.ensure_colortype_in_group(context, "DEFAULT", p_type)
        

    @staticmethod
    def sync_default_group_to_predefinedtype(context, task_pg):
        """
        Key function: Synchronizes the DEFAULT entry of a task with its current PredefinedType.
        This function is responsible for updating the data that will be displayed in the UI.
        """
        if not task_pg: return
        
        # 1. Get the current PredefinedType of the task from the cached data. #
        try:
            from bonsai.bim.module.sequence.data import SequenceData
            tid = getattr(task_pg, "ifc_definition_id", None)
            task_data = (SequenceData.data.get("tasks", {}) or {}).get(tid)
            predef_type = (task_data.get("PredefinedType") or "NOTDEFINED") if task_data else "NOTDEFINED"
        except Exception:
            predef_type = "NOTDEFINED" # 2. Make sure the profile for this type exists in the DEFAULT group.

        # 2. Make sure the profile for this type exists in the DEFAULT group.
        UnifiedColorTypeManager.ensure_colortype_in_group(context, "DEFAULT", predef_type)

        # 3. Update the 'DEFAULT' entry in the task's collection.
        try:
            coll = getattr(task_pg, "colortype_group_choices", None)
            if coll is None: return

            default_entry = next((item for item in coll if item.group_name == "DEFAULT"), None)

            if not default_entry:
                default_entry = coll.add()
                default_entry.group_name = "DEFAULT"

            # 4. Assign the profile and make sure it is enabled. #
            # Use safe property setting to avoid ID class writing restrictions
            try:
                default_entry.selected_colortype = predef_type
                default_entry.enabled = True # The DEFAULT group is always active. #
            except Exception as prop_error:
                # If we can't write properties now, schedule for later
                if "Writing to ID classes" in str(prop_error):
                    # Use timer to defer the property update
                    import bpy
                    def deferred_update():
                        try:
                            default_entry.selected_colortype = predef_type
                            default_entry.enabled = True
                        except Exception:
                            pass
                        return None  # Don't repeat timer
                    bpy.app.timers.register(deferred_update, first_interval=0.01)
                else:
                    raise prop_error

        except Exception as e:
            print(f"[ERROR] Error synchronizing DEFAULT for the task: {e}")

    @staticmethod
    def initialize_default_for_all_tasks(context) -> bool: #
        """Iterates through all tasks and ensures their DEFAULT group is initialized and synchronized."""
        try:
            tprops = tool.Sequence.get_task_tree_props()
            if not tprops or not hasattr(tprops, 'tasks'):
                return False
            
            # First ensure that all necessary profiles exist.
            UnifiedColorTypeManager.ensure_default_group_has_predefined_types(context)

            for task in tprops.tasks:
                UnifiedColorTypeManager.sync_default_group_to_predefinedtype(context, task)
            
            return True
        except Exception as e:
            print(f"[ERROR] Error al inicializar perfiles DEFAULT para todas las tasks: {e}")
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
                # Here we force the use of the method we have already corrected #
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

    @staticmethod
    def _create_default_colortype_data(colortype_name: str) -> dict:
        """Creates default colortype data for a given colortype name""" #
        # Define specific colors for each type #
        color_map = {
            "CONSTRUCTION": {"start": [1,1,1,0], "active": [0,1,0,1], "end": [0.3,1,0.3,1]},
            "INSTALLATION": {"start": [1,1,1,0], "active": [0,1,0,1], "end": [0.3,0.8,0.5,1]},
            "DEMOLITION": {"start": [1,1,1,1], "active": [1,0,0,1], "end": [0,0,0,0], "hide": True},
            "REMOVAL": {"start": [1,1,1,1], "active": [1,0,0,1], "end": [0,0,0,0], "hide": True},
            "DISPOSAL": {"start": [1,1,1,1], "active": [1,0,0,1], "end": [0,0,0,0], "hide": True},
            "DISMANTLE": {"start": [1,1,1,1], "active": [1,0,0,1], "end": [0,0,0,0], "hide": True},
            "OPERATION": {"start": [1,1,1,1], "active": [0,0,1,1], "end": [1,1,1,1]},
            "MAINTENANCE": {"start": [1,1,1,1], "active": [0,0,1,1], "end": [1,1,1,1]},
            "ATTENDANCE": {"start": [1,1,1,1], "active": [0,0,1,1], "end": [1,1,1,1]},
            "RENOVATION": {"start": [1,1,1,1], "active": [0,0,1,1], "end": [0.9,0.9,0.9,1]},
            "LOGISTIC": {"start": [1,1,1,1], "active": [1,1,0,1], "end": [1,0.8,0.3,1]},
            "MOVE": {"start": [1,1,1,1], "active": [1,1,0,1], "end": [0.8,0.6,0,1]},
            "NOTDEFINED": {"start": [0.7,0.7,0.7,1], "active": [0.5,0.5,0.5,1], "end": [0.3,0.3,0.3,1]},
            "USERDEFINED": {"start": [0.7,0.7,0.7,1], "active": [0.5,0.5,0.5,1], "end": [0.3,0.3,0.3,1]},
        }
        
        colors = color_map.get(colortype_name, color_map["NOTDEFINED"])
        
        return {
            "name": colortype_name,
            "start_color": colors["start"],
            "in_progress_color": colors["active"],
            "end_color": colors["end"],
            "consider_start": False,
            "consider_active": True,
            "consider_end": True,
            "use_start_original_color": False,
            "use_active_original_color": False,
            "use_end_original_color": not colors.get("hide", False),
            "start_transparency": 0.0,
            "active_start_transparency": 0.8,
            "active_finish_transparency": 0.3,
            "active_transparency_interpol": 1.0,
            "end_transparency": 0.0,
            "hide_at_end": colors.get("hide", False)
        }

    @staticmethod
    def _apply_colortype_data_to_property(property_obj, colortype_data: dict):
        """Applies colortype data to a property object with safe fallbacks"""
        try: #
            # Colors with safe fallbacks #
            for attr in ("start_color", "in_progress_color", "end_color"):
                col = colortype_data.get(attr, [1, 1, 1, 1])
                if isinstance(col, (list, tuple)) and len(col) >= 3:
                    rgba = list(col) + [1.0] * (4 - len(col))
                    setattr(property_obj, attr, rgba[:4])
                else:
                    setattr(property_obj, attr, [1.0, 1.0, 1.0, 1.0])
        
            # Booleans with fallbacks #
            bool_attrs = {
                "use_start_original_color": False,
                "use_active_original_color": False, 
                "use_end_original_color": True,
                "consider_start": False,
                "consider_active": True,
                "consider_end": True,
                "hide_at_end": False
            }
            for attr, default in bool_attrs.items():
                if hasattr(property_obj, attr):
                    setattr(property_obj, attr, bool(colortype_data.get(attr, default)))
        
            # Transparencies with fallbacks #
            float_attrs = {
                "active_start_transparency": 0.0,
                "active_finish_transparency": 0.0,
                "active_transparency_interpol": 1.0,
                "start_transparency": 0.0,
                "end_transparency": 0.0
            }
            for attr, default in float_attrs.items():
                if hasattr(property_obj, attr):
                    try:
                        val = float(colortype_data.get(attr, default))
                        setattr(property_obj, attr, max(0.0, min(1.0, val)))
                    except (TypeError, ValueError):
                        setattr(property_obj, attr, default)
                        
        except Exception as e:
            print(f"Error applying colortype data: {e}")

# ============================================================================
# ANIMATION CALLBACK FUNCTIONS
# ============================================================================

def get_animation_color_schemes_items(self, context):
    """Gets colortype items for dropdown"""
    props = tool.Sequence.get_animation_props()
    items = []
    try:
        for i, p in enumerate(props.ColorTypes):
            name = p.name or f"colortype {i+1}"
            items.append((name, name, "", i))
    except Exception:
        pass
    if not items:
        items = [("", "<no colortypes>", "", 0)]
    return items

def get_custom_group_colortype_items(self, context):
    """
    Gets colortype items ONLY from the selected custom group (excludes DEFAULT).
    This version reads directly from the JSON and is more lenient to allow UI selection
    even if colortype data is incomplete.
    """
    items = []
    try:
        anim_props = tool.Sequence.get_animation_props()
        selected_group = getattr(anim_props, "task_colortype_group_selector", "")
        
        print(f"🔍 get_custom_group_colortype_items called for task {getattr(self, 'ifc_definition_id', 'unknown')}")
        print(f"🔍 selected_group: '{selected_group}'")
        
        if selected_group and selected_group != "DEFAULT":
            # Direct and flexible reading from JSON #
            all_sets = UnifiedColorTypeManager._read_sets_json(context)
            group_data = all_sets.get(selected_group, {})
            colortypes_list = group_data.get("ColorTypes", [])
            
            colortype_names = []
            for colortype in colortypes_list: #
                if isinstance(colortype, dict) and "name" in colortype:
                    # Ensure we only add valid non-numeric string names
                    name = str(colortype["name"])
                    if name and not name.isdigit():
                        colortype_names.append(name)
            
            # Always include an empty option first to prevent enum errors
            items.append(("", "<none>", "No colortype selected", 0)) #
            
            for i, name in enumerate(sorted(colortype_names)):
                items.append((name, name, f"colortype from {selected_group}", i + 1))
            
            print(f"🔍 Found {len(colortype_names)} colortypes: {colortype_names}")
        else:
            print(f"🔍 No valid group selected: '{selected_group}'")
    
    # If there are no profiles, ensure that at least the null option exists to avoid enum errors. #
    except Exception as e: #
        print(f"Error getting custom group colortypes: {e}")
        items.append(("", "<error loading colortypes>", "", 0))

    if not items:
        anim_props = tool.Sequence.get_animation_props()
        selected_group = getattr(anim_props, "task_colortype_group_selector", "")
        if not selected_group:
            items.append(("", "<select custom group first>", "", 0))
        elif selected_group == "DEFAULT":
            items.append(("", "<DEFAULT not allowed here>", "", 0))
        else:
            items.append(("", f"<no colortypes in {selected_group}>", "", 0))
    
    # Ensure that the null option is always present if there are no other items #
    if not items:
        items.append(("", "<none>", "No colortypes available", 0))
    
    print(f"🔍 Final items returned: {[(item[0], item[1]) for item in items]}")
    
    # Ensure empty option is ALWAYS first and present #
    if not any(item[0] == "" for item in items):
        print("🚨 CRITICAL: No empty option found, forcing one")
        items.insert(0, ("", "<none>", "No colortype selected", 0))
    
    # Ensure the empty option is always first #
    empty_item = None
    non_empty_items = []
    for item in items:
        if item[0] == "":
            empty_item = item
        else:
            non_empty_items.append(item)
    
    if empty_item:
        final_items = [empty_item] + non_empty_items
    else:
        final_items = [("", "<none>", "No colortype selected", 0)] + non_empty_items
    
    print(f"🔍 FINAL SORTED items: {[(item[0], item[1]) for item in final_items]}")
    return final_items

def update_color_full(self, context):
    """Updates full bar color"""
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

def get_internal_ColorType_sets_enum(self, context):
    """Gets enum of ALL available colortype groups, including DEFAULT."""
    try:
        # Get all groups directly from the source #
        all_groups = sorted(list(UnifiedColorTypeManager._read_sets_json(context).keys()))
        
        if all_groups:
            # Ensure "DEFAULT" appears first for convenience #
            if "DEFAULT" in all_groups:
                all_groups.remove("DEFAULT")
                all_groups.insert(0, "DEFAULT")
            return [(name, name, f"colortype group: {name}") for name in all_groups] #
    except Exception:
        pass
    
    # Fallback - always have at least DEFAULT
    return [("DEFAULT", "DEFAULT", "Auto-managed default group")]

def get_all_groups_enum(self, context):
    """Enum for all groups (including DEFAULT)."""
    try:
        groups = UnifiedColorTypeManager.get_all_groups(context)
        items = []
        for i, group in enumerate(sorted(groups)):
            desc = "Auto-managed colortypes by PredefinedType" if group == "DEFAULT" else "Custom colortype group"
            items.append((group, group, desc, i))
        return items if items else [("DEFAULT", "DEFAULT", "Auto-managed default group", 0)]
    except Exception:
        return [("DEFAULT", "DEFAULT", "Auto-managed default group", 0)]

def get_user_created_groups_enum(self, context):
    """Returns EnumProperty items for user-created groups, excluding 'DEFAULT'."""
    try:
        user_groups = UnifiedColorTypeManager.get_user_created_groups(context)
        if user_groups:
            return [(name, name, f"colortype group: {name}") for name in user_groups]
    except Exception:
        pass
    return [("NONE", "<no custom groups>", "Create custom groups in the Animation Color Schemes panel")]

def update_task_colortype_group_selector(self, context):
    """Update when custom group selector changes - ensures colortypes are loaded"""
    try:
        # 'self' is BIMAnimationProperties #
        if self.task_colortype_group_selector and self.task_colortype_group_selector not in ("", "NONE"):
            print(f"📄 Custom group selected: {self.task_colortype_group_selector}")
            
            # Load profiles from this group into the UI to make them available #
            UnifiedColorTypeManager.load_colortypes_into_collection(self, context, self.task_colortype_group_selector)
            
            # OPTIONALLY sync to ColorType_groups for editing if user wants #
            # Only sync if user hasn't manually selected a different group for editing #
            if not hasattr(self, '_ColorType_groups_manually_set') or not self._ColorType_groups_manually_set:
                self.ColorType_groups = self.task_colortype_group_selector
                print(f"🔄 Auto-synced ColorType_groups to '{self.task_colortype_group_selector}' for editing")
            
            # Update enum to refresh profile dropdown #
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

def update_ColorType_group(self, context):
    """Updates active colortype group - FIXED: No auto-sync to prevent data corruption""" #

    # Mark that user manually changed ColorType_groups for editing #
    self._ColorType_groups_manually_set = True
    print(f"🎯 User manually selected '{self.ColorType_groups}' for editing")

    # sync_active_group_to_json() - This was causing data corruption #
    # When switching groups, the editor content would overwrite the wrong group #
    # Users must manually save groups with "Save Group" button #
    print(f"[WARNING]  Group switched to '{self.ColorType_groups}' - use 'Save Group' to persist changes")

    # Clean up invalid mappings #
    UnifiedColorTypeManager.cleanup_invalid_mappings(context)

    # Load colortypes of the selected group #
    if self.ColorType_groups:
        UnifiedColorTypeManager.load_colortypes_into_collection(self, context, self.ColorType_groups)

    # Task synchronization that was corrupting data #
    # When switching groups in editor, we should NOT modify task colortype assignments
    # This was causing the last custom group to get overwritten with wrong values
    print(f"ℹ️  Editor group changed to '{self.ColorType_groups}' - task assignments unchanged")

def safe_set_animation_color_schemes(task_obj, value):
    """Safely sets the animation_color_schemes property with validation"""
    try:
        # Try to set the value directly first #
        try:
            task_obj.animation_color_schemes = value
            return
        except Exception as enum_error:
            # If the value is not valid for the current enum, try fallback options #
            if "enum" in str(enum_error).lower():
                print(f"🔄 Value '{value}' not valid for animation_color_schemes enum, trying fallbacks...")
                
                # Get current valid items to find a fallback #
                try:
                    valid_items = get_animation_color_schemes_items(task_obj, bpy.context)
                    valid_values = [item[0] for item in valid_items]
                    
                    # Try to use the first valid option (usually empty string) #
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
        try: #
            # Final fallback - try empty string or first available option #
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
        
        # Validate the value before assignment #
        if value and (value.isdigit() or value == "0"):
            print(f"🚫 Prevented assignment of invalid enum value '{value}' to selected_colortype_in_active_group")
            value = ""
        
        # Skip validation during copy operations to allow setting values that might be valid later #
        if not skip_validation:
            # Get context for validation #
            context = bpy.context
            valid_items = get_custom_group_colortype_items(task_obj, context)
            valid_values = [item[0] for item in valid_items]
            
            if value and value not in valid_values:
                print(f"🚫 Value '{value}' not in valid enum options: {valid_values}, using empty string")
                value = ""
        
        # Safely set the property with fallback handling #
        try: #
            # Final validation just before assignment #
            if str(value) in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or str(value).isdigit():
                print(f"🚫 CRITICAL: Blocking numeric value '{value}' just before setattr")
                value = ""
            
            print(f"🔧 About to setattr selected_colortype_in_active_group = '{value}'")
            setattr(task_obj, "selected_colortype_in_active_group", value)
            
        except Exception as enum_error:
            print(f"[ERROR] setattr failed with error: {enum_error}")
            # If the value is not valid for the current enum, try fallback options #
            if "enum" in str(enum_error).lower():
                # Get current valid items to find a fallback #
                try:
                    valid_items = get_custom_group_colortype_items(task_obj, bpy.context)
                    valid_values = [item[0] for item in valid_items]
                    
                    # Try to use the first valid option (usually empty string) #
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
                except Exception as fallback_error: #
                    print(f"[ERROR] Fallback assignment also failed: {fallback_error}")
                    # Last resort - don't assign anything
                    pass
            else:
                raise enum_error
        
    except Exception as e: #
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

def update_legend_hud_on_group_change(self, context):
    """Callback that runs when the enabled state of a group changes"""
    try:
        # When a group is enabled/disabled, update the UI state snapshot #
        from ..operators.operator import snapshot_all_ui_state
        snapshot_all_ui_state(context)

        print(f"🔄 GROUP CHANGE CALLBACK: Group '{self.group}' enabled changed to: {self.enabled}")
        
        # Automatically synchronize animation_color_schemes #
        _sync_animation_color_schemes_with_active_groups(context)
        
        # Invalidate legend HUD cache to refresh #
        from ..hud import invalidate_legend_hud_cache, refresh_hud
        invalidate_legend_hud_cache()

        refresh_hud()

        print("🔄 Legend HUD cache invalidated and viewport refreshed")
    except Exception as e:
        import traceback
        print(f"[WARNING] Could not auto-update Legend HUD: {e}")
        traceback.print_exc()

def _sync_animation_color_schemes_with_active_groups(context):
    """
    Automatically synchronizes the animation_color_schemes field of tasks
    with the ColorType of the active group when a group checkbox is enabled/disabled.
    """
    try:
        import bonsai.tool as tool
        
        # Get task properties #
        tprops = tool.Sequence.get_task_tree_props()
        if not tprops or not hasattr(tprops, 'tasks'): #
            return
        
        synced_tasks = 0
        
        for task in tprops.tasks:
            try:
                # Only process tasks that use active groups #
                use_active_group = getattr(task, 'use_active_colortype_group', False)
                if not use_active_group:
                    continue
                
                # Find active group (enabled=True) that is not DEFAULT #
                active_group_colortype = ''
                group_choices = getattr(task, 'colortype_group_choices', [])
                
                for choice in group_choices:
                    group_name = getattr(choice, 'group_name', '')
                    enabled = getattr(choice, 'enabled', False)
                    colortype = getattr(choice, 'selected_colortype', '')
                    
                    if enabled and group_name != 'DEFAULT' and colortype:
                        active_group_colortype = colortype
                        break
                
                # Synchronize animation_color_schemes with the active group #
                if active_group_colortype:
                    current_animation_schemes = getattr(task, 'animation_color_schemes', '')
                    if active_group_colortype != current_animation_schemes:
                        print(f"🔄 AUTO-SYNC: Task {task.ifc_definition_id} - '{current_animation_schemes}' → '{active_group_colortype}'")
                        safe_set_animation_color_schemes(task, active_group_colortype)
                        synced_tasks += 1
                
            except Exception as e: #
                print(f"[ERROR] Error syncing task {getattr(task, 'ifc_definition_id', '?')}: {e}")
                continue
        
        if synced_tasks > 0:
            print(f"✅ Auto-synchronized {synced_tasks} tasks")

    except Exception as e:
        print(f"[ERROR] Error in auto-sync animation_color_schemes: {e}")

def get_saved_color_schemes(self, context):
    """Gets saved color schemes (legacy - maintain for compatibility)"""
    if not AnimationColorSchemeData.is_loaded:
        AnimationColorSchemeData.load()
    return AnimationColorSchemeData.data.get("saved_color_schemes", [])

def update_colortype_considerations(self, context):
    """Validation logic for colortype states - without auto-activation of ACTIVE mode"""
    try:
        # Keep essential validation and sync functionality #
        # BUT DO NOT force consider_active = True automatically #

        # Basic validation can remain (without auto-changing user settings) #
        print(f"ColorType considerations updated for: {getattr(self, 'name', 'Unknown')}")

        # Keep only non-intrusive sync functionality #
        # REMOVED: Any logic that automatically enables consider_active #

    except Exception as e:
        print(f"Error in colortype considerations update: {e}")


# ============================================================================
# ANIMATION PROPERTY GROUP CLASSES
# ============================================================================

class AnimationColorSchemes(PropertyGroup):
    """Animation Color Scheme for 4D animation"""
    name: StringProperty(name="Color Type Name", default="New Color Type")
    
    # Considered States
    consider_start: BoolProperty(
        name="Start state",
        default=False,
        description="When enabled, elements use start appearance throughout the entire animation, "
                    "useful for existing elements, demolition context, or persistent visibility",
        update=update_colortype_considerations)
    consider_active: BoolProperty(
        name="Active state",
        default=True,
        description="Apply appearance during task execution period",
        update=update_colortype_considerations)
    consider_end: BoolProperty(
        name="End state",
        default=True,
        description="Apply appearance after task completion",
        update=update_colortype_considerations)
    
    # Colors by State
    start_color: FloatVectorProperty(
        name="Start Color",
        subtype="COLOR",
        size=4, min=0.0, max=1.0,
        default=(1.0, 1.0, 1.0, 1.0),
    )
    in_progress_color: FloatVectorProperty(
        name="In Progress Color",
        subtype="COLOR",
        size=4, min=0.0, max=1.0,
        default=(0.8, 0.8, 0.0, 1.0),
    )
    end_color: FloatVectorProperty(
        name="End Color",
        subtype="COLOR",
        size=4, min=0.0, max=1.0,
        default=(0.0, 1.0, 0.0, 1.0),
    )
    
    # Option to keep original color
    use_start_original_color: BoolProperty(name="Start: Use Original Color", default=False)
    use_active_original_color: BoolProperty(name="Active: Use Original Color", default=False)
    use_end_original_color: BoolProperty(name="End: Use Original Color", default=True)
    
    # Transparency Control
    start_transparency: FloatProperty(name="Start Transparency", min=0.0, max=1.0, default=0.0)
    active_start_transparency: FloatProperty(name="Active Start Transparency", min=0.0, max=1.0, default=0.0)
    active_finish_transparency: FloatProperty(name="Active Finish Transparency", min=0.0, max=1.0, default=0.0)
    active_transparency_interpol: FloatProperty(name="Transparency Interpol.", min=0.0, max=1.0, default=1.0)
    end_transparency: FloatProperty(name="End Transparency", min=0.0, max=1.0, default=0.0)

    hide_at_end: BoolProperty(name="Hide When Finished", description="If enabled, the object will become invisible in the End phase", default=False)
    
    if TYPE_CHECKING:
        name: str
        start_color: tuple[float, float, float, float]
        in_progress_color: tuple[float, float, float, float]
        end_color: tuple[float, float, float, float]
        use_start_original_color: bool
        use_active_original_color: bool
        use_end_original_color: bool
        start_transparency: float
        active_start_transparency: float
        active_finish_transparency: float
        active_transparency_interpol: float
        end_transparency: float
        hide_at_end: bool

class AnimationColorTypeGroupItem(PropertyGroup):
    """Item for animation group stack"""
    group: EnumProperty(name="Group", items=get_internal_ColorType_sets_enum)
    enabled: BoolProperty(name="Use", default=True, update=update_legend_hud_on_group_change)

class BIMAnimationProperties(PropertyGroup):
    """Animation properties with improved colortype system"""
    
    # Unified colortype system
    active_ColorType_system: EnumProperty(
        name="ColorType System",
        items=[
            ("ColorTypeS", "Animation Color Schemes", "Use advanced ColorType system"),
        ],
        default="ColorTypeS"
    )
    
    # Animation group stack
    animation_group_stack: CollectionProperty(name="Animation Group Stack", type=AnimationColorTypeGroupItem)
    animation_group_stack_index: IntProperty(name="Animation Group Stack Index", default=-1)
    
    # State and configuration
    is_editing: BoolProperty(name="Is Loaded", default=False)
    saved_colortype_name: StringProperty(name="colortype Set Name", default="Default")
    
    # Animation Color Scheme
    ColorTypes: CollectionProperty(name="Animation Color Scheme", type=AnimationColorSchemes)
    active_ColorType_index: IntProperty(name="Active ColorType Index")
    ColorType_groups: EnumProperty(name="ColorType Group", items=get_internal_ColorType_sets_enum, update=update_ColorType_group)

    # Flag to control if the animation has been created at least once. #
    is_animation_created: BoolProperty(
        name="Is Animation Created",
        description="Internal flag to check if the main animation has been created at least once",
        default=False
    )

    # New property, only for the Tasks panel UI, which excludes 'DEFAULT' #
    task_colortype_group_selector: EnumProperty(
        name="Custom colortype Group",
        items=get_user_created_groups_enum,
        update=update_task_colortype_group_selector
    )
   
    # UI toggles
    show_saved_task_colortypes_panel: BoolProperty(name="Show Saved colortypes", default=False)
    should_show_task_bar_options: BoolProperty(name="Show Task Bar Options", default=False)

    
    # Task bar colors
    color_full: FloatVectorProperty(
        name="Full Bar",
        subtype="COLOR", size=4,
        default=(1.0, 0.0, 0.0, 1.0),
        min=0.0, max=1.0,
        description="Color for full task bar",
        update=update_color_full,
    )
    color_progress: FloatVectorProperty(
        name="Progress Bar",
        subtype="COLOR", size=4,
        default=(0.0, 1.0, 0.0, 1.0),
        min=0.0, max=1.0,
        description="Color for progress task bar",
        update=update_color_progress,
    )
    
    # Legacy properties (maintain for compatibility)
    saved_color_schemes: EnumProperty(items=get_saved_color_schemes, name="Saved Colour Schemes")
    active_color_component_outputs_index: IntProperty(name="Active Color Component Index")
    active_color_component_inputs_index: IntProperty(name="Active Color Component Index")
    
    if TYPE_CHECKING:
        active_ColorType_system: str
        animation_group_stack: bpy.types.bpy_prop_collection_idprop[AnimationColorTypeGroupItem]
        animation_group_stack_index: int
        is_editing: bool
        saved_colortype_name: str
        ColorTypes: bpy.types.bpy_prop_collection_idprop[AnimationColorSchemes]
        active_ColorType_index: int
        ColorType_groups: str
        task_colortype_group_selector: str
        show_saved_task_colortypes_panel: bool
        should_show_task_bar_options: bool
        color_full: Color
        color_progress: Color
        saved_color_schemes: str
        active_color_component_outputs_index: int
        active_color_component_inputs_index: int

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

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
                del data[gkey] #
                continue
            if isinstance(gval, dict):
                for pkey, plist in list(gval.items()):
                    if plist in (None, [], {}, "null"):
                        del gval[pkey]
        UnifiedColorTypeManager._write_sets_json(context, data)
    except Exception:
        # Do not raise; operators call this after user actions and must not crash
        pass

def monitor_predefined_type_change(context):
    """Monitors changes in PredefinedType and auto-syncs DEFAULT"""
    try:
        tprops = tool.Sequence.get_task_tree_props()
        wprops = tool.Sequence.get_work_schedule_props()

        if not (tprops.tasks and wprops.active_task_index < len(tprops.tasks)):
            return

        task_pg = tprops.tasks[wprops.active_task_index]
        # Only sync DEFAULT if there are no custom groups #
        user_groups = UnifiedColorTypeManager.get_user_created_groups(context)
        if not user_groups:
            UnifiedColorTypeManager.sync_default_group_to_predefinedtype(context, task_pg)

    except Exception as e:
        print(f"[ERROR] monitor_predefined_type_change: {e}")

# ============================================================================
# ENUM HELPER FUNCTIONS FOR COLOR TYPE MANAGEMENT
# ============================================================================




def get_task_colortype_items(self, context):
    """Task-specific colortype items"""
    try:
        # Get current task's available colortypes #
        tprops = tool.Sequence.get_task_tree_props()
        wprops = tool.Sequence.get_work_schedule_props()
        
        if not (tprops.tasks and wprops.active_task_index < len(tprops.tasks)):
            return [("NONE", "No Task", "No active task selected")]
            
        task_pg = tprops.tasks[wprops.active_task_index] #
        
        # Get colortypes for current task
        items = []
        try:
            colortype_data = UnifiedColorTypeManager.get_all_colortypes_for_task(context, task_pg)
            for colortype, info in colortype_data.items():
                items.append((colortype, colortype, f"Colortype: {colortype}"))
        except:
            pass
            
        return items if items else [("DEFAULT", "Default", "Default colortype")]
        
    except Exception:
        return [("DEFAULT", "Default", "Default colortype")]