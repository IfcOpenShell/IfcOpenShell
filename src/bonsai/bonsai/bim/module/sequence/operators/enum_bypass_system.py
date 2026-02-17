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

class EnumBypassSystem:
    """
    Sistema de bypass para propiedades enum corruptas.
    Cuando las propiedades enum están corruptas con valor '0',
    este sistema mantiene los valores reales en propiedades de escena.
    """
    
    @staticmethod
    def store_colortype_value(task_id, property_name, value):
        """Store a ColorType value in scene bypass storage"""
        scene = bpy.context.scene
        key = f"_enum_bypass_{property_name}"
        
        try:
            # Get existing data or create new
            if key in scene:
                data = json.loads(scene[key])
            else:
                data = {}
            
            # Store the value
            data[str(task_id)] = value
            scene[key] = json.dumps(data)
            
            print(f"🔄 BYPASS: Stored {property_name}='{value}' for task {task_id}")
            
        except Exception as e:
            print(f"[ERROR] BYPASS: Error storing {property_name}: {e}")
    
    @staticmethod
    def get_colortype_value(task_id, property_name, default=""):
        """Get a ColorType value from scene bypass storage"""
        scene = bpy.context.scene
        key = f"_enum_bypass_{property_name}"
        
        try:
            if key in scene:
                data = json.loads(scene[key])
                value = data.get(str(task_id), default)
                if value != default:
                    print(f"📥 BYPASS: Retrieved {property_name}='{value}' for task {task_id}")
                return value
        except Exception as e:
            print(f"[ERROR] BYPASS: Error retrieving {property_name}: {e}")
        
        return default
    
    @staticmethod
    def is_enum_corrupted(task_item, property_name):
        """Check if an enum property is corrupted"""
        try:
            # Try to get current value
            current = getattr(task_item, property_name)
            
            # Try to get enum items
            prop_def = task_item.bl_rna.properties[property_name]
            items = prop_def.enum_items
            
            # If no items available or value is '0', it's corrupted
            if not items or str(current) == '0':
                return True
                
            return False
        except:
            return True
    
    @staticmethod
    def safe_get_colortype_value(task_item, property_name, default=""):
        """Safely get a ColorType value, using bypass if enum is corrupted"""
        task_id = getattr(task_item, 'ifc_definition_id', 0)
        
        # Check if enum is corrupted
        if EnumBypassSystem.is_enum_corrupted(task_item, property_name):
            # Use bypass system
            return EnumBypassSystem.get_colortype_value(task_id, property_name, default)
        else:
            # Use normal property
            try:
                return getattr(task_item, property_name, default)
            except:
                return EnumBypassSystem.get_colortype_value(task_id, property_name, default)
    
    @staticmethod
    def safe_set_colortype_value(task_item, property_name, value):
        """Safely set a ColorType value, using bypass if enum is corrupted"""
        task_id = getattr(task_item, 'ifc_definition_id', 0)
        
        # Always store in bypass system as backup
        EnumBypassSystem.store_colortype_value(task_id, property_name, value)
        
        # Try to set the actual property
        try:
            if not EnumBypassSystem.is_enum_corrupted(task_item, property_name):
                setattr(task_item, property_name, value)
                print(f"[DEBUG] DIRECT: Set {property_name}='{value}' for task {task_id}")
                return True
        except Exception as e:
            print(f"[WARNING] DIRECT FAILED: {property_name}='{value}' for task {task_id}: {e}")
        
        print(f"🔄 BYPASS ONLY: {property_name}='{value}' for task {task_id}")
        return False
    
    @staticmethod
    def repair_all_corrupted_enums():
        """Try to repair all corrupted enums and sync with bypass system"""
        try:
            task_props = tool.Sequence.get_task_tree_props()
            tasks = getattr(task_props, 'tasks', [])
            
            repaired_count = 0
            bypass_count = 0
            
            for task in tasks:
                task_id = getattr(task, 'ifc_definition_id', 0)
                
                # Check selected_colortype_in_active_group
                if EnumBypassSystem.is_enum_corrupted(task, 'selected_colortype_in_active_group'):
                    # Get value from bypass
                    bypass_value = EnumBypassSystem.get_colortype_value(task_id, 'selected_colortype_in_active_group')
                    if bypass_value:
                        # Try to repair and set
                        try:
                            # Force refresh by toggling use_active_colortype_group
                            original = task.use_active_colortype_group
                            task.use_active_colortype_group = not original
                            task.use_active_colortype_group = original
                            
                            # Try to set the value
                            if not EnumBypassSystem.is_enum_corrupted(task, 'selected_colortype_in_active_group'):
                                task.selected_colortype_in_active_group = bypass_value
                                repaired_count += 1
                                print(f"[DEBUG] REPAIRED: selected_colortype_in_active_group={bypass_value} for task {task_id}")
                            else:
                                bypass_count += 1
                        except Exception as e:
                            print(f"[ERROR] REPAIR FAILED: selected_colortype_in_active_group for task {task_id}: {e}")
                            bypass_count += 1
                
                # Check animation_color_schemes
                if EnumBypassSystem.is_enum_corrupted(task, 'animation_color_schemes'):
                    bypass_value = EnumBypassSystem.get_colortype_value(task_id, 'animation_color_schemes')
                    if bypass_value:
                        try:
                            # Force refresh
                            original = task.use_active_colortype_group
                            task.use_active_colortype_group = not original
                            task.use_active_colortype_group = original
                            
                            if not EnumBypassSystem.is_enum_corrupted(task, 'animation_color_schemes'):
                                task.animation_color_schemes = bypass_value
                                repaired_count += 1
                                print(f"[DEBUG] REPAIRED: animation_color_schemes={bypass_value} for task {task_id}")
                            else:
                                bypass_count += 1
                        except Exception as e:
                            print(f"[ERROR] REPAIR FAILED: animation_color_schemes for task {task_id}: {e}")
                            bypass_count += 1
            
            print(f"🔧 REPAIR SUMMARY: {repaired_count} repaired, {bypass_count} using bypass")
            return repaired_count, bypass_count
            
        except Exception as e:
            print(f"[ERROR] Error in repair_all_corrupted_enums: {e}")
            return 0, 0


class TestEnumBypass(bpy.types.Operator):
    bl_idname = "bim.test_enum_bypass"
    bl_label = "Test Enum Bypass System"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        print("\n" + "🧪"*50)
        print("🧪 TESTING ENUM BYPASS SYSTEM")
        print("🧪"*50)
        
        repaired, bypass = EnumBypassSystem.repair_all_corrupted_enums()
        
        print("🧪"*50 + "\n")
        
        self.report({'INFO'}, f"Repaired: {repaired}, Using Bypass: {bypass}")
        return {'FINISHED'}


def register():
    bpy.utils.register_class(TestEnumBypass)

def unregister():
    bpy.utils.unregister_class(TestEnumBypass)

if __name__ == "__main__":
    register()