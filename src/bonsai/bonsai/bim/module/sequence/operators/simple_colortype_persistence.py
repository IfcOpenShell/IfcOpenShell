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

# saves/restores animation_color_schemes 

import bpy
import bonsai.tool as tool

# Simple dictionary to store colortype values
_simple_colortype_backup = {}

def save_colortypes_simple():
    """Save ONLY animation_color_schemes - SIMPLE like v60"""
    global _simple_colortype_backup
    _simple_colortype_backup.clear()
    
    try:
        context = bpy.context
        tprops = getattr(context.scene, 'BIMTaskTreeProperties', None)
        if not tprops:
            return
        
        # Save ONLY animation_color_schemes for each visible task
        for task in tprops.tasks:
            task_id = str(task.ifc_definition_id)
            if task_id != "0":
                colortype_value = getattr(task, 'animation_color_schemes', '')
                if colortype_value:  # Only save if not empty
                    _simple_colortype_backup[task_id] = colortype_value
        
        print(f"[DEBUG] Simple: Saved {len(_simple_colortype_backup)} ColorTypes")
        
    except Exception as e:
        print(f"[ERROR] Simple save failed: {e}")

def restore_colortypes_simple():
    """Restore ONLY animation_color_schemes - SIMPLE like v60"""
    global _simple_colortype_backup
    
    try:
        context = bpy.context
        tprops = getattr(context.scene, 'BIMTaskTreeProperties', None)
        if not tprops or not _simple_colortype_backup:
            return
        
        restored_count = 0
        # Restore ONLY animation_color_schemes for each visible task
        for task in tprops.tasks:
            task_id = str(task.ifc_definition_id)
            if task_id in _simple_colortype_backup:
                try:
                    # Use safe setter to handle enum validation
                    from ..prop.animation import safe_set_animation_color_schemes
                    safe_set_animation_color_schemes(task, _simple_colortype_backup[task_id])
                    restored_count += 1
                except ImportError:
                    # Fallback to direct assignment if import fails
                    try:
                        task.animation_color_schemes = _simple_colortype_backup[task_id]
                        restored_count += 1
                    except Exception as e:
                        print(f"[ERROR] Failed to restore task {task_id}: {e}")
                except Exception as e:
                    print(f"[ERROR] Failed to restore task {task_id}: {e}")
        
        print(f"[DEBUG] Simple: Restored {restored_count} ColorTypes")
        
    except Exception as e:
        print(f"[ERROR] Simple restore failed: {e}")