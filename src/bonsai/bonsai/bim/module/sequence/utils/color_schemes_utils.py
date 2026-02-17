# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021, 2022 Dion Moult <dion@thinkmoult.com>, Yassine Oualid <yassine@sigmadimensions.com>, Federico Eraso <feraso@svisuals.net>
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

"""
Color scheme utility functions for animation and display management.
Consolidated from duplicate implementations to maintain consistency.
"""

import json


def ensure_default_group(context):
    """Ensures the DEFAULT group exists with 13 predefined profiles and complete properties.
    Only creates DEFAULT group if no custom groups exist to avoid confusion.

    Args:
        context: Blender context

    Returns:
        bool: True if DEFAULT group was created or already existed
    """
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
            ]

            # Add complete properties to each colortype
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
            print("✅ DEFAULT ColorType group created with 13 predefined profiles")
            return True
        else:
            print("ℹ️  DEFAULT group not created - custom groups already exist")
            return False
    else:
        print("ℹ️  DEFAULT group already exists")
        return True


def ensure_colortype_in_group(context, group_name, colortype_name):
    """Ensures a specific colortype exists in a group with default properties.

    Args:
        context: Blender context
        group_name (str): Name of the group
        colortype_name (str): Name of the colortype to ensure exists

    Returns:
        bool: True if colortype was created or already existed
    """
    scene = context.scene
    key = "BIM_AnimationColorSchemesSets"
    raw = scene.get(key, "{}")

    try:
        data = json.loads(raw) if isinstance(raw, str) else (raw or {})
        if not isinstance(data, dict):
            data = {}
    except Exception:
        data = {}

    # Ensure group exists
    if group_name not in data:
        data[group_name] = {"ColorTypes": []}

    # Check if colortype already exists in group
    existing_colortypes = data[group_name].get("ColorTypes", [])
    colortype_names = [ct.get("name") for ct in existing_colortypes]

    if colortype_name not in colortype_names:
        # Create default colortype based on name
        default_colortype = _get_default_colortype_properties(colortype_name)
        existing_colortypes.append(default_colortype)
        data[group_name]["ColorTypes"] = existing_colortypes
        scene[key] = json.dumps(data)
        print(f"✅ ColorType '{colortype_name}' added to group '{group_name}'")
        return True
    else:
        print(f"ℹ️  ColorType '{colortype_name}' already exists in group '{group_name}'")
        return False


def _get_default_colortype_properties(colortype_name):
    """Get default properties for a colortype based on its name.

    Args:
        colortype_name (str): Name of the colortype

    Returns:
        dict: Default properties for the colortype
    """
    # Define color schemes based on colortype category
    demolition_types = ["DEMOLITION", "REMOVAL", "DISPOSAL", "DISMANTLE"]
    construction_types = ["CONSTRUCTION", "INSTALLATION"]
    operation_types = ["OPERATION", "MAINTENANCE", "ATTENDANCE"]
    logistic_types = ["LOGISTIC", "MOVE"]

    if colortype_name in demolition_types:
        base_colors = {
            "start_color": [1,1,1,1],
            "in_progress_color": [1,0,0,1],
            "end_color": [0,0,0,0]
        }
    elif colortype_name in construction_types:
        base_colors = {
            "start_color": [1,1,1,0],
            "in_progress_color": [0,1,0,1],
            "end_color": [0.3,1,0.3,1] if colortype_name == "CONSTRUCTION" else [0.3,0.8,0.5,1]
        }
    elif colortype_name in operation_types:
        base_colors = {
            "start_color": [1,1,1,1],
            "in_progress_color": [0,0,1,1],
            "end_color": [1,1,1,1] if colortype_name in ["OPERATION", "MAINTENANCE", "ATTENDANCE"] else [0.9,0.9,0.9,1]
        }
    elif colortype_name in logistic_types:
        base_colors = {
            "start_color": [1,1,1,1],
            "in_progress_color": [1,1,0,1],
            "end_color": [1,0.8,0.3,1] if colortype_name == "LOGISTIC" else [0.8,0.6,0,1]
        }
    else:
        # Default for NOTDEFINED, USERDEFINED, or unknown types
        base_colors = {
            "start_color": [0.7,0.7,0.7,1],
            "in_progress_color": [0.5,0.5,0.5,1],
            "end_color": [0.3,0.3,0.3,1]
        }

    return {
        "name": colortype_name,
        **base_colors,
        "consider_start": False,
        "consider_active": True,
        "consider_end": True,
        "use_start_original_color": False,
        "use_active_original_color": False,
        "use_end_original_color": colortype_name not in demolition_types,
        "start_transparency": 0.0,
        "active_start_transparency": 0.0,
        "active_finish_transparency": 0.0,
        "active_transparency_interpol": 1.0,
        "end_transparency": 0.0
    }


def get_available_colortypes():
    """Get list of all available standard colortypes.

    Returns:
        list: List of standard colortype names
    """
    return [
        "CONSTRUCTION", "INSTALLATION", "DEMOLITION", "REMOVAL",
        "DISPOSAL", "DISMANTLE", "OPERATION", "MAINTENANCE",
        "ATTENDANCE", "RENOVATION", "LOGISTIC", "MOVE",
        "NOTDEFINED", "USERDEFINED"
    ]