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
import ifcopenshell
import bonsai.tool as tool
from .props_sequence import PropsSequence

class UiHelpersSequence:
    """Mixin class for UI helper functions like column and stack management."""

    @classmethod
    def add_task_column(cls, column_type: str, name: str, data_type: str) -> None:
        props = tool.Sequence.get_work_schedule_props()
        new = props.columns.add()
        new.name = f"{column_type}.{name}"
        new.data_type = data_type

    @classmethod
    def setup_default_task_columns(cls) -> None:
        props = tool.Sequence.get_work_schedule_props()
        props.columns.clear()
        default_columns = ["ScheduleStart", "ScheduleFinish", "ScheduleDuration"]
        for item in default_columns:
            new = props.columns.add()
            new.name = f"IfcTaskTime.{item}"
            new.data_type = "string"

    @classmethod
    def remove_task_column(cls, name: str) -> None:
        props = tool.Sequence.get_work_schedule_props()
        props.columns.remove(props.columns.find(name))
        if props.sort_column == name:
            props.sort_column = ""

    @classmethod
    def set_task_sort_column(cls, column: str) -> None:
        props = tool.Sequence.get_work_schedule_props()
        props.sort_column = column

    @staticmethod
    def add_group_to_animation_stack():
        """Add a new group to the animation group stack"""
        try:
            anim_props = tool.Sequence.get_animation_props()
            if not hasattr(anim_props, 'animation_group_stack'):
                print("[ERROR] animation_group_stack not found in animation properties")
                return

            # Check if DEFAULT group already exists
            for existing_item in anim_props.animation_group_stack:
                if existing_item.group == "DEFAULT":
                    print("[WARNING] DEFAULT group already exists in animation stack. Cannot create multiple DEFAULT groups.")
                    return

            # Add a new item to the stack
            item = anim_props.animation_group_stack.add()
            item.group = "DEFAULT"  # Default group name
            item.enabled = True

            # Set as the active item
            anim_props.animation_group_stack_index = len(anim_props.animation_group_stack) - 1

            print(f"[OK] Added group '{item.group}' to animation stack")

        except Exception as e:
            print(f"[ERROR] Error adding group to animation stack: {e}")
            import traceback
            traceback.print_exc()

    @staticmethod
    def remove_group_from_animation_stack():
        """Remove the selected group from the animation group stack"""
        try:
            anim_props = tool.Sequence.get_animation_props()
            if not hasattr(anim_props, 'animation_group_stack'):
                print("[ERROR] animation_group_stack not found in animation properties")
                return
            
            idx = anim_props.animation_group_stack_index
            if 0 <= idx < len(anim_props.animation_group_stack):
                removed_group = anim_props.animation_group_stack[idx].group
                anim_props.animation_group_stack.remove(idx)
                
                # Adjust the index if needed
                if anim_props.animation_group_stack_index >= len(anim_props.animation_group_stack):
                    anim_props.animation_group_stack_index = len(anim_props.animation_group_stack) - 1
                    
                print(f"[OK] Removed group '{removed_group}' from animation stack")
            else:
                print("[ERROR] No valid group selected to remove")
                
        except Exception as e:
            print(f"[ERROR] Error removing group from animation stack: {e}")
            import traceback
            traceback.print_exc()

    @staticmethod
    def move_group_in_animation_stack(direction):
        """Move the selected group up or down in the animation group stack"""
        try:
            anim_props = tool.Sequence.get_animation_props()
            if not hasattr(anim_props, 'animation_group_stack'):
                print("[ERROR] animation_group_stack not found in animation properties")
                return
            
            idx = anim_props.animation_group_stack_index
            stack_len = len(anim_props.animation_group_stack)
            
            if not (0 <= idx < stack_len):
                print("[ERROR] No valid group selected to move")
                return
                
            new_idx = idx
            if direction == "UP" and idx > 0:
                new_idx = idx - 1
            elif direction == "DOWN" and idx < stack_len - 1:
                new_idx = idx + 1
            else:
                print(f"[ERROR] Cannot move {direction} from position {idx}")
                return
                
            # Move the item by removing and re-inserting it
            item = anim_props.animation_group_stack[idx]
            group_name = item.group
            enabled = item.enabled
            
            # Remove the old item
            anim_props.animation_group_stack.remove(idx)
            
            # Add at the new position
            new_item = anim_props.animation_group_stack.add()
            anim_props.animation_group_stack.move(len(anim_props.animation_group_stack) - 1, new_idx)
            
            # Restore the properties
            anim_props.animation_group_stack[new_idx].group = group_name
            anim_props.animation_group_stack[new_idx].enabled = enabled
            
            # Update index
            anim_props.animation_group_stack_index = new_idx
            
            print(f"[OK] Moved group '{group_name}' {direction} to position {new_idx}")
            
        except Exception as e:
            print(f"[ERROR] Error moving group in animation stack: {e}")
            import traceback
            traceback.print_exc()

    @classmethod
    def enable_editing_task_calendar(cls, task: ifcopenshell.entity_instance) -> None:
        props = tool.Sequence.get_work_schedule_props()
        props.active_task_id = task.id()
        props.editing_task_type = "CALENDAR"