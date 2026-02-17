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

class FixCorruptedEnums(bpy.types.Operator):
    bl_idname = "bim.fix_corrupted_enums"
    bl_label = "Fix Corrupted Enum Properties"
    bl_description = "Reset corrupted enum properties that show '0' values"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        print("\n" + "🔧"*50)
        print("🔧 FIXING CORRUPTED ENUM PROPERTIES")
        print("🔧"*50)
        
        fixed_count = 0
        
        try:
            # Get task tree properties
            task_props = tool.Sequence.get_task_tree_props()
            tasks = getattr(task_props, 'tasks', [])
            
            print(f"🔍 Checking {len(tasks)} tasks for corrupted enums...")
            
            for i, task in enumerate(tasks):
                task_id = getattr(task, 'ifc_definition_id', 'N/A')
                task_name = getattr(task, 'name', 'N/A')
                
                # Check and fix selected_colortype_in_active_group
                try:
                    # Try to access current value
                    current = task.selected_colortype_in_active_group
                    
                    # Check if we can get enum items
                    prop_def = task.bl_rna.properties['selected_colortype_in_active_group']
                    items = prop_def.enum_items
                    
                    if not items:
                        print(f"🔧 Task {task_id} ({task_name}): No enum items for selected_colortype_in_active_group")
                        # Force property refresh by clearing and re-evaluating
                        try:
                            task.property_unset("selected_colortype_in_active_group")
                            # Try to trigger enum callback to reload items
                            task.use_active_colortype_group = task.use_active_colortype_group
                            fixed_count += 1
                        except Exception as reset_e:
                            print(f"[ERROR] Failed to reset selected_colortype_in_active_group: {reset_e}")
                    
                except Exception as e:
                    print(f"🔧 Task {task_id} ({task_name}): Error accessing selected_colortype_in_active_group: {e}")
                    try:
                        task.property_unset("selected_colortype_in_active_group")
                        task.use_active_colortype_group = task.use_active_colortype_group
                        fixed_count += 1
                    except:
                        print(f"[ERROR] Failed to reset selected_colortype_in_active_group for task {task_id}")
                
                # Check and fix animation_color_schemes
                try:
                    current = task.animation_color_schemes
                    prop_def = task.bl_rna.properties['animation_color_schemes'] 
                    items = prop_def.enum_items
                    
                    if not items:
                        print(f"🔧 Task {task_id} ({task_name}): No enum items for animation_color_schemes")
                        try:
                            task.property_unset("animation_color_schemes")
                            task.use_active_colortype_group = task.use_active_colortype_group
                            fixed_count += 1
                        except Exception as reset_e:
                            print(f"[ERROR] Failed to reset animation_color_schemes: {reset_e}")
                    
                except Exception as e:
                    print(f"🔧 Task {task_id} ({task_name}): Error accessing animation_color_schemes: {e}")
                    try:
                        task.property_unset("animation_color_schemes")
                        task.use_active_colortype_group = task.use_active_colortype_group
                        fixed_count += 1
                    except:
                        print(f"[ERROR] Failed to reset animation_color_schemes for task {task_id}")
                
                # Check groups
                groups = getattr(task, 'colortype_group_choices', [])
                for j, group in enumerate(groups):
                    group_name = getattr(group, 'group_name', f'Group_{j}')
                    try:
                        current = group.selected_colortype
                        prop_def = group.bl_rna.properties['selected_colortype']
                        items = prop_def.enum_items
                        
                        if not items:
                            print(f"🔧 Task {task_id}, Group '{group_name}': No enum items for selected_colortype")
                            try:
                                group.property_unset("selected_colortype")
                                group.enabled = group.enabled  # Trigger refresh
                                fixed_count += 1
                            except Exception as reset_e:
                                print(f"[ERROR] Failed to reset selected_colortype: {reset_e}")
                    except Exception as e:
                        print(f"🔧 Task {task_id}, Group '{group_name}': Error accessing selected_colortype: {e}")
                        try:
                            group.property_unset("selected_colortype") 
                            group.enabled = group.enabled
                            fixed_count += 1
                        except:
                            print(f"[ERROR] Failed to reset selected_colortype for group '{group_name}' in task {task_id}")
            
            
        except Exception as e:
            print(f"[ERROR] Error in fix_corrupted_enums: {e}")
            import traceback
            traceback.print_exc()
        
        print("🔧"*50 + "\n")
        
        self.report({'INFO'}, f"Fixed {fixed_count} corrupted enum properties")
        return {'FINISHED'}


def register():
    bpy.utils.register_class(FixCorruptedEnums)

def unregister():
    bpy.utils.unregister_class(FixCorruptedEnums)

if __name__ == "__main__":
    register()