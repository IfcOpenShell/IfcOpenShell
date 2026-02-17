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





import bonsai.tool as tool
from bonsai.bim.module.sequence.data import SequenceData, AnimationColorSchemeData
from .color_manager_prop import UnifiedColorTypeManager


def get_operator_items(self, context):
    """
    Genera dinámicamente la lista de operadores según el tipo de dato de la columna seleccionada.
    """
    data_type = getattr(self, 'data_type', 'string')

    common_ops = [
        ('EQUALS', "Equals", "The value is exactly the same"),
        ('NOT_EQUALS', "Does not equal", "The value is different"),
        ('EMPTY', "Is empty", "The field has no value"),
        ('NOT_EMPTY', "Is not empty", "The field has a value"),
    ]

    if data_type in ('integer', 'real', 'float'):
        return [
            ('GREATER', "Greater than", ">"),
            ('LESS', "Less than", "<"),
            ('GTE', "Greater or Equal", ">="),
            ('LTE', "Less or Equal", "<="),
        ] + common_ops
    elif data_type == 'date':
        return [
            ('GREATER', "After Date", "The date is after the specified one"),
            ('LESS', "Before Date", "The date is before the specified one"),
            ('GTE', "On or After Date", "The date is on or after the specified one"),
            ('LTE', "On or Before Date", "The date is on or before the specified one"),
        ] + common_ops
    elif data_type == 'boolean':
        return [
            ('EQUALS', "Is", "The value is true or false"),
            ('NOT_EQUALS', "Is not", "The value is the opposite"),
        ]
    else:  # string, enum, y otros por defecto
        return [
            ('CONTAINS', "Contains", "The text string is contained"),
            ('NOT_CONTAINS', "Does not contain", "The text string is not contained"),
        ] + common_ops


# ============================================================================
# CALLBACK FUNCTIONS - Improved with the new system
# ============================================================================

def getTaskColumns(self, context):
    if not SequenceData.is_loaded:
        SequenceData.load()
    return SequenceData.data["task_columns_enum"]


def getTaskTimeColumns(self, context):
    if not SequenceData.is_loaded:
        SequenceData.load()
    return SequenceData.data["task_time_columns_enum"]


def getWorkSchedules(self, context):
    if not SequenceData.is_loaded:
        SequenceData.load()
    return SequenceData.data["work_schedules_enum"]


def getWorkCalendars(self, context):
    if not SequenceData.is_loaded:
        SequenceData.load()
    return SequenceData.data["work_calendars_enum"]


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
        
        # Debug prints removed for performance - were causing spam
        
        if selected_group and selected_group != "DEFAULT":
            # Direct and flexible reading from JSON
            all_sets = UnifiedColorTypeManager._read_sets_json(context)
            group_data = all_sets.get(selected_group, {})
            colortypes_list = group_data.get("ColorTypes", [])
            
            colortype_names = []
            for colortype in colortypes_list:
                if isinstance(colortype, dict) and "name" in colortype:
                    # Ensure we only add valid non-numeric string names
                    name = str(colortype["name"])
                    if name and not name.isdigit():
                        colortype_names.append(name)
            
            # Always include an empty option first to prevent enum errors
            items.append(("", "<none>", "No colortype selected", 0))
            
            for i, name in enumerate(sorted(colortype_names)):
                items.append((name, name, f"colortype from {selected_group}", i + 1))
            
            # Debug: Found {len(colortype_names)} colortypes for {selected_group}
        else:
            pass  # No valid group selected
    
    # If there are no profiles, ensure that at least the null option exists to avoid enum errors.
    except Exception as e:
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
    
    # Ensure that the null option is always present if there are no other items
    if not items:
        items.append(("", "<none>", "No colortypes available", 0))
    # --- END OF CORRECTION ---
    
    print(f"🔍 Final items returned: {[(item[0], item[1]) for item in items]}")
    
    # Ensure empty option is ALWAYS first and present
    if not any(item[0] == "" for item in items):
        print("🚨 CRITICAL: No empty option found, forcing one")
        items.insert(0, ("", "<none>", "No colortype selected", 0))
    
    # Ensure the empty option is always first
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

def get_task_colortype_items(self, context):
    """Enum items function for task colortypes - separated from update function"""
    items = []
    try:
        anim_props = tool.Sequence.get_animation_props()
        selected_group = getattr(anim_props, "task_colortype_group_selector", "")
        
        print(f"🔍 Getting colortypes for custom group: '{selected_group}'")
        
        # Solo mostrar perfiles si hay un grupo personalizado seleccionado
        if selected_group and selected_group != "DEFAULT":
            from bonsai.bim.module.sequence.prop import UnifiedColorTypeManager
            colortypes = UnifiedColorTypeManager.get_group_colortypes(context, selected_group)
            
            for i, name in enumerate(sorted(colortypes.keys())):
                items.append((name, name, f"colortype from {selected_group}", i))
            
            print(f"[DEBUG] Found {len(items)} colortypes in group '{selected_group}'")

    except Exception as e:
        print(f"[ERROR] Error getting custom group colortypes: {e}")
        items = [("", "<error loading colortypes>", "", 0)]

    if not items:
        anim_props = tool.Sequence.get_animation_props()
        selected_group = getattr(anim_props, "task_colortype_group_selector", "")
        if not selected_group:
            items = [("", "<select custom group first>", "", 0)]
        elif selected_group == "DEFAULT":
            items = [("", "<DEFAULT not allowed here>", "", 0)]
        else:
            items = [("", f"<no colortypes in {selected_group}>", "", 0)]
            
    return items

def get_schedule_predefined_types(self, context):
    if not SequenceData.is_loaded:
        SequenceData.load()
    return SequenceData.data["schedule_predefined_types_enum"]

def get_saved_color_schemes(self, context):
    """Gets saved color schemes (legacy - maintain for compatibility)"""
    if not AnimationColorSchemeData.is_loaded:
        AnimationColorSchemeData.load()
    return AnimationColorSchemeData.data.get("saved_color_schemes", [])

def get_internal_ColorType_sets_enum(self, context):
    """Gets enum of ALL available colortype groups, including DEFAULT."""
    from bonsai.bim.module.sequence.prop import UnifiedColorTypeManager
    try:
        # Get all groups directly from the source
        all_groups = sorted(list(UnifiedColorTypeManager._read_sets_json(context).keys()))
        
        if all_groups:
            # Ensure "DEFAULT" appears first for convenience
            if "DEFAULT" in all_groups:
                all_groups.remove("DEFAULT")
                all_groups.insert(0, "DEFAULT")
            return [(name, name, f"colortype group: {name}") for name in all_groups]
    except Exception:
        pass
    
    # Fallback - always have at least DEFAULT
    return [("DEFAULT", "DEFAULT", "Auto-managed default group")]

def get_all_groups_enum(self, context):
    """Enum para todos los grupos (incluyendo DEFAULT)."""
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
    from bonsai.bim.module.sequence.prop import UnifiedColorTypeManager
    try:
        user_groups = UnifiedColorTypeManager.get_user_created_groups(context)
        if user_groups:
            return [(name, name, f"colortype group: {name}") for name in user_groups]
    except Exception:
        pass
    return [("NONE", "<no custom groups>", "Create custom groups in the Animation Color Schemes panel")]


def get_all_task_columns_enum(self, context):
    """
    Genera una lista EnumProperty con TODAS las columnas filtrables,
    incluyendo el tipo de dato en el identificador para uso interno.
    """
    if not SequenceData.is_loaded:
        SequenceData.load()

    items = []
    # 1. Special columns (manually defined)
    # The format is: "InternalName||data_type", "UI Label", "Description"
    items.append(("Special.OutputsCount||integer", "Element 3D", "Total number of 3D elements assigned to task (inputs + outputs)."))
    
    items.append(("Special.VarianceStatus||string", "Variance Status", "Task variance status (Delayed, Ahead, On Time)"))
    items.append(("Special.VarianceDays||integer", "Variance (Days)", "Task variance in days"))
    # --- END OF MODIFICATION ---

    # 2. Columnas de IfcTask
    for name_type, label, desc in SequenceData.data.get("task_columns_enum", []):
        try:
            name, data_type = name_type.split('/')
            identifier = f"IfcTask.{name}||{data_type}"
            items.append((identifier, f"Task: {label}", desc))
        except Exception:
            continue

    # 3. Columnas de IfcTaskTime
    for name_type, label, desc in SequenceData.data.get("task_time_columns_enum", []):
        try:
            name, data_type = name_type.split('/')
            # We correct so that dates are treated as 'date'
            final_data_type = 'date' if any(s in label.lower() for s in ['date', 'start', 'finish']) else data_type
            identifier = f"IfcTaskTime.{name}||{final_data_type}"
            items.append((identifier, f"Time: {label}", desc))
        except Exception:
            continue

    return sorted(items, key=lambda x: x[1])

def get_date_source_items(self, context):
    """Helper for EnumProperty items to select date sources."""
    return [
        ('SCHEDULE', "Schedule", "Use Schedule dates"),
        ('ACTUAL', "Actual", "Use Actual dates"),
        ('EARLY', "Early", "Use Early dates"),
        ('LATE', "Late", "Use Late dates"),
    ]








