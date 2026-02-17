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

"""
Task Column Persistence System - Maintains Task Column Values
============================================================

PROBLEM SOLVED:
When adding task columns with ADD TASK COLUMN functionality, the values
for colorType assignments and colorType groups used for filters get lost
during UI refreshes and column operations.

SOLUTION:
Implement the same snapshot/restore pattern used for colorType persistence
but adapted for task column values, ensuring they maintain their state
through column additions and filtering operations.

BENEFIT:
- Preserves task column values during ADD TASK COLUMN operations
- Maintains colorType assignments for filtering
- Preserves colorType group associations
- Works seamlessly with existing snapshot system

USAGE:
    save_task_column_values()
    # Perform ADD TASK COLUMN operations
    restore_task_column_values()
"""

import bpy
import bonsai.tool as tool
from typing import Dict, Any, Optional

# Global storage for task column values
_task_column_backup = {}

def save_task_column_values():
    """Save task column values including colorType and group assignments"""
    global _task_column_backup
    _task_column_backup.clear()

    try:
        context = bpy.context
        tprops = getattr(context.scene, 'BIMTaskTreeProperties', None)
        if not tprops:
            return

        # Get current work schedule for context
        ws_props = tool.Sequence.get_work_schedule_props()
        ws_id = int(getattr(ws_props, "active_work_schedule_id", 0))

        # Save task column values for each visible task
        for task in tprops.tasks:
            task_id = str(task.ifc_definition_id)
            if task_id != "0":
                task_data = {}

                # Save colorType related values (similar to colorType persistence)
                colortype_value = getattr(task, 'animation_color_schemes', '')
                if colortype_value:
                    task_data['animation_color_schemes'] = colortype_value

                # Save selected colorType in active group
                selected_colortype = getattr(task, 'selected_colortype_in_active_group', '')
                if selected_colortype:
                    task_data['selected_colortype_in_active_group'] = selected_colortype

                # Save use_active_colortype_group checkbox
                use_active = getattr(task, 'use_active_colortype_group', False)
                task_data['use_active_colortype_group'] = use_active

                # Save colortype_group_choices (the assignments summary)
                if hasattr(task, 'colortype_group_choices'):
                    group_choices = []
                    for group_choice in task.colortype_group_choices:
                        choice_data = {
                            'group_name': getattr(group_choice, 'group_name', ''),
                            'enabled': getattr(group_choice, 'enabled', False),
                        }
                        # Try to get selected_colortype (may have different attribute names)
                        for attr in ['selected_colortype', 'selected', 'active_colortype', 'colortype']:
                            if hasattr(group_choice, attr):
                                choice_data['selected_colortype'] = getattr(group_choice, attr, '')
                                break
                        group_choices.append(choice_data)

                    if group_choices:
                        task_data['colortype_group_choices'] = group_choices

                # Save task column values from work schedule properties
                if hasattr(ws_props, 'columns'):
                    column_values = {}
                    for column in ws_props.columns:
                        column_name = column.name
                        # Try to get the value from the task
                        if hasattr(task, column_name.replace('.', '_')):
                            value = getattr(task, column_name.replace('.', '_'), '')
                            if value:
                                column_values[column_name] = value

                    if column_values:
                        task_data['column_values'] = column_values

                # Save filter-related values
                predefined_type = getattr(task, 'PredefinedType', '')
                if predefined_type:
                    task_data['PredefinedType'] = predefined_type

                # Save any custom properties that might be used for filtering
                if hasattr(task, 'custom_properties'):
                    custom_props = getattr(task, 'custom_properties', {})
                    if custom_props:
                        task_data['custom_properties'] = custom_props

                # Only save if we have data
                if task_data:
                    _task_column_backup[task_id] = task_data

        print(f"[DEBUG] Task Column Snapshot: Saved data for {len(_task_column_backup)} tasks")

    except Exception as e:
        print(f"[ERROR] Task column save failed: {e}")
        import traceback
        traceback.print_exc()

def restore_task_column_values():
    """Restore task column values including colorType and group assignments"""
    global _task_column_backup

    try:
        context = bpy.context
        tprops = getattr(context.scene, 'BIMTaskTreeProperties', None)
        if not tprops or not _task_column_backup:
            return

        restored_count = 0

        # Restore task column values for each visible task
        for task in tprops.tasks:
            task_id = str(task.ifc_definition_id)
            if task_id in _task_column_backup:
                try:
                    task_data = _task_column_backup[task_id]

                    # Restore colorType related values using safe setters
                    if 'animation_color_schemes' in task_data:
                        value = task_data['animation_color_schemes']
                        try:
                            from ..prop.animation import safe_set_animation_color_schemes
                            safe_set_animation_color_schemes(task, value)
                        except:
                            try:
                                task.animation_color_schemes = value
                            except:
                                pass

                    if 'selected_colortype_in_active_group' in task_data:
                        value = task_data['selected_colortype_in_active_group']
                        try:
                            from ..prop.callbacks_prop import safe_set_selected_colortype_in_active_group
                            safe_set_selected_colortype_in_active_group(task, value, skip_validation=True)
                        except:
                            try:
                                setattr(task, 'selected_colortype_in_active_group', value)
                            except:
                                pass

                    # Restore use_active_colortype_group checkbox
                    if 'use_active_colortype_group' in task_data:
                        try:
                            task.use_active_colortype_group = task_data['use_active_colortype_group']
                        except:
                            pass

                    # Restore colortype_group_choices (the assignments summary)
                    if 'colortype_group_choices' in task_data:
                        try:
                            task.colortype_group_choices.clear()
                            for choice_data in task_data['colortype_group_choices']:
                                new_choice = task.colortype_group_choices.add()
                                new_choice.group_name = choice_data.get('group_name', '')
                                if hasattr(new_choice, 'enabled'):
                                    new_choice.enabled = choice_data.get('enabled', False)

                                selected = choice_data.get('selected_colortype', '')
                                if selected:
                                    for attr in ['selected_colortype', 'selected', 'active_colortype', 'colortype']:
                                        if hasattr(new_choice, attr):
                                            try:
                                                setattr(new_choice, attr, selected)
                                                break
                                            except:
                                                pass
                        except:
                            pass

                    # Restore task column values
                    if 'column_values' in task_data:
                        for column_name, value in task_data['column_values'].items():
                            attr_name = column_name.replace('.', '_')
                            if hasattr(task, attr_name):
                                setattr(task, attr_name, value)

                    # Restore PredefinedType
                    if 'PredefinedType' in task_data:
                        task.PredefinedType = task_data['PredefinedType']

                    # Restore custom properties
                    if 'custom_properties' in task_data:
                        if hasattr(task, 'custom_properties'):
                            task.custom_properties = task_data['custom_properties']

                    restored_count += 1

                except Exception as e:
                    print(f"[ERROR] Failed to restore task {task_id}: {e}")

        print(f"[DEBUG] Task Column Snapshot: Restored data for {restored_count} tasks")

    except Exception as e:
        print(f"[ERROR] Task column restore failed: {e}")
        import traceback
        traceback.print_exc()

def save_task_column_filters():
    """Save current filter state for task columns"""
    global _task_column_backup

    try:
        ws_props = tool.Sequence.get_work_schedule_props()
        if not hasattr(ws_props, 'filters') or not hasattr(ws_props.filters, 'rules'):
            return

        # Save filter rules state
        filter_data = {
            'active_rule_index': getattr(ws_props.filters, 'active_rule_index', 0),
            'rules': []
        }

        for rule in ws_props.filters.rules:
            rule_data = {
                'column': getattr(rule, 'column', ''),
                'operator': getattr(rule, 'operator', ''),
                'value': getattr(rule, 'value', ''),
                'enabled': getattr(rule, 'enabled', True)
            }
            filter_data['rules'].append(rule_data)

        # Store in global backup with special key
        _task_column_backup['_FILTER_STATE_'] = filter_data

        print(f"[DEBUG] Task Column Snapshot: Saved {len(filter_data['rules'])} filter rules")

    except Exception as e:
        print(f"[ERROR] Filter state save failed: {e}")

def restore_task_column_filters():
    """Restore filter state for task columns"""
    global _task_column_backup

    try:
        if '_FILTER_STATE_' not in _task_column_backup:
            return

        ws_props = tool.Sequence.get_work_schedule_props()
        if not hasattr(ws_props, 'filters'):
            return

        filter_data = _task_column_backup['_FILTER_STATE_']

        # Restore active rule index
        if hasattr(ws_props.filters, 'active_rule_index'):
            ws_props.filters.active_rule_index = filter_data.get('active_rule_index', 0)

        # Restore filter rules (if the collection supports it)
        if hasattr(ws_props.filters, 'rules') and 'rules' in filter_data:
            # Clear existing rules if possible
            try:
                ws_props.filters.rules.clear()
            except:
                pass

            # Add restored rules
            for rule_data in filter_data['rules']:
                try:
                    new_rule = ws_props.filters.rules.add()
                    new_rule.column = rule_data.get('column', '')
                    new_rule.operator = rule_data.get('operator', '')
                    new_rule.value = rule_data.get('value', '')
                    new_rule.enabled = rule_data.get('enabled', True)
                except:
                    pass

        print(f"[DEBUG] Task Column Snapshot: Restored filter state")

    except Exception as e:
        print(f"[ERROR] Filter state restore failed: {e}")

def clear_task_column_backup():
    """Clear the task column backup"""
    global _task_column_backup
    _task_column_backup.clear()
    print("[DEBUG] Task Column Snapshot: Backup cleared")

def get_backup_stats() -> Dict[str, Any]:
    """Get statistics about the current backup"""
    global _task_column_backup

    task_count = len([k for k in _task_column_backup.keys() if k != '_FILTER_STATE_'])
    has_filters = '_FILTER_STATE_' in _task_column_backup

    return {
        'task_count': task_count,
        'has_filters': has_filters,
        'total_size': len(_task_column_backup),
        'is_empty': len(_task_column_backup) == 0
    }

# Convenience functions for integration with ADD TASK COLUMN operations
def snapshot_before_add_column():
    """Complete snapshot before ADD TASK COLUMN operation"""
    save_task_column_values()
    save_task_column_filters()

def restore_after_add_column():
    """Complete restore after ADD TASK COLUMN operation"""
    restore_task_column_values()
    restore_task_column_filters()

# Integration with existing colorType system
def save_combined_state():
    """Save both colorType and task column state"""
    try:
        # Use existing colorType persistence
        from .simple_colortype_persistence import save_colortypes_simple
        save_colortypes_simple()
    except ImportError:
        print("[WARNING] Could not import colorType persistence")

    # Save task column state
    snapshot_before_add_column()

def restore_combined_state():
    """Restore both colorType and task column state"""
    try:
        # Use existing colorType persistence
        from .simple_colortype_persistence import restore_colortypes_simple
        restore_colortypes_simple()
    except ImportError:
        print("[WARNING] Could not import colorType persistence")

    # Restore task column state
    restore_after_add_column()