# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>, 2022 Yassine Oualid <yassine@sigmadimensions.com>, 2025 Federico Eraso <feraso@svisuals.net>
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
from .operator import snapshot_all_ui_state
from .schedule_task_operators import restore_all_ui_state

try:
    # Updated imports for refactored sequence module
    from ..tool.sequence.ui.task_properties import TaskProperties as props_sequence
    from ..tool.sequence.core.color_manager import ColorManager as colortype_sequence
except ImportError:
    # Fallback definitions
    class props_sequence:
        @staticmethod
        def get_animation_props(): return None
        @staticmethod
        def get_task_tree_props(): return None
        @staticmethod
        def get_work_schedule_props(): return None
    
    class colortype_sequence:
        @staticmethod
        def load_ColorType_group_data(group_name): return {"ColorTypes": []}

try:
    from ..prop.animation import get_user_created_groups_enum
    from ..prop.color_manager_prop import UnifiedColorTypeManager
except ImportError:
    def get_user_created_groups_enum(self, context): return [("NONE", "None", "")]
    class UnifiedColorTypeManager: pass


class SearchCustomColorTypeGroup(bpy.types.Operator):
    bl_idname = "bim.search_custom_colortype_group"
    bl_label = "Search Custom ColorType Group"
    bl_description = "Search and filter custom ColorType groups"
    bl_options = {"REGISTER", "UNDO"}

    search_term: bpy.props.StringProperty(name="Search", default="")

    def execute(self, context):
        props = props_sequence.get_animation_props()
        if not self.search_term:
            self.report({'INFO'}, "Enter search term")
            return {'CANCELLED'}
        items = get_user_created_groups_enum(None, context)
        matches = [item for item in items if self.search_term.lower() in item[1].lower()]
        if matches:
            props.task_ColorType_group_selector = matches[0][0]
            self.report({'INFO'}, f"Found and selected: {matches[0][1]}")
        else:
            self.report({'WARNING'}, f"No groups found matching: {self.search_term}")
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "search_term")


class CopyCustomColorTypeGroup(bpy.types.Operator):
    bl_idname = "bim.copy_custom_colortype_group"
    bl_label = "Copy Custom ColorType Group"
    bl_description = "Copy current custom ColorType group to clipboard"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = props_sequence.get_animation_props()
        current_value = getattr(props, "task_ColorType_group_selector", "")
        if current_value:
            context.window_manager.clipboard = current_value
            self.report({'INFO'}, f"Copied to clipboard: {current_value}")
        else:
            self.report({'WARNING'}, "No custom ColorType group selected to copy")
        return {'FINISHED'}


class PasteCustomColorTypeGroup(bpy.types.Operator):
    bl_idname = "bim.paste_custom_colortype_group"
    bl_label = "Paste Custom ColorType Group"
    bl_description = "Paste custom ColorType group from clipboard"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = props_sequence.get_animation_props()
        clipboard_value = context.window_manager.clipboard.strip()
        if not clipboard_value:
            self.report({'WARNING'}, "Clipboard is empty")
            return {'CANCELLED'}
        items = get_user_created_groups_enum(None, context)
        valid_values = [item[0] for item in items]
        if clipboard_value in valid_values:
            props.task_ColorType_group_selector = clipboard_value
            self.report({'INFO'}, f"Pasted from clipboard: {clipboard_value}")
        else:
            self.report({'WARNING'}, f"Invalid group in clipboard: {clipboard_value}")
        return {'FINISHED'}


class SetCustomColorTypeGroupNull(bpy.types.Operator):
    bl_idname = "bim.set_custom_colortype_group_null"
    bl_label = "Set Custom ColorType Group to Null"
    bl_description = "Clear custom ColorType group selection (set to null)"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = props_sequence.get_animation_props()
        props.task_ColorType_group_selector = ""
        try:
            tprops = props_sequence.get_task_tree_props()
            wprops = props_sequence.get_work_schedule_props()
            if tprops.tasks and wprops.active_task_index < len(tprops.tasks):
                task = tprops.tasks[wprops.active_task_index]
                task.selected_ColorType_in_active_group = ""
                task.use_active_ColorType_group = False
        except Exception:
            pass
        self.report({'INFO'}, "Custom ColorType group cleared (set to null)")
        return {'FINISHED'}


class ShowCustomColorTypeGroupInfo(bpy.types.Operator):
    bl_idname = "bim.show_custom_colortype_group_info"
    bl_label = "Custom ColorType Group Info"
    bl_description = "Show information about the current custom ColorType group"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = props_sequence.get_animation_props()
        current_value = getattr(props, "task_ColorType_group_selector", "")
        if current_value:
            group_data = colortype_sequence.load_ColorType_group_data(current_value)
            ColorTypes = group_data.get("ColorTypes", [])
            info_text = f"Group: {current_value}\nColorTypes: {len(ColorTypes)}\n"
            if ColorTypes:
                info_text += f"Available: {', '.join(c.get('name', '') for c in ColorTypes)}"
            self.report({'INFO'}, info_text)
        else:
            self.report({'INFO'}, "No custom ColorType group selected")
        return {'FINISHED'}


class BIM_OT_RefreshAnimationView(bpy.types.Operator):
    """The new Orchestra Director. Refreshes the entire 4D animation view."""
    bl_idname = "bim.refresh_animation_view"
    bl_label = "Refresh 4D Animation View"
    bl_description = "Refresh the entire 4D schedule animation view"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        # Always use tool.Sequence for compatibility
        import bonsai.tool as tool

        # SNAPSHOT before any destructive reload
        try:
            snapshot_all_ui_state(context)
        except Exception as e:
            print(f"Bonsai WARNING: snapshot_all_ui_state failed: {e}")

        try:
            # 1. Clear old animation and visuals to start fresh
            try:
                tool.Sequence.clear_objects_animation()
            except (AttributeError, TypeError):
                pass
            
            try:
                tool.Sequence.clear_task_bars()
            except (AttributeError, TypeError):
                pass

            # 2. Reload task properties from IFC
            try:
                tool.Sequence.load_task_properties()
            except (AttributeError, TypeError):
                pass

            # 3. Calculate new animation configuration (frames, dates, etc.)
            work_schedule = tool.Sequence.get_active_work_schedule()
            if not work_schedule:
                # Try to refresh UI properties even without work schedule
                try:
                    tool.Sequence.load_task_properties()
                except:
                    pass
                self.report({'WARNING'}, "No active work schedule - refreshing UI only.")
                # Force UI redraw
                for area in context.screen.areas:
                    area.tag_redraw()
                return {'FINISHED'}
            
            # Validate work schedule is valid IFC entity
            if not hasattr(work_schedule, 'id') or not work_schedule.id():
                self.report({'ERROR'}, "Invalid work schedule entity.")
                return {'CANCELLED'}
            
            # 4. Force a simple refresh by reloading task tree and properties
            try:
                tool.Sequence.load_task_tree(work_schedule)
                tool.Sequence.load_task_properties()
            except (AttributeError, TypeError) as e:
                self.report({'WARNING'}, f"Failed to reload tasks: {str(e)}")
            except Exception as e:
                # Handle any other errors gracefully
                self.report({'WARNING'}, f"Task loading error: {str(e)}")

            # 5. Try to refresh any visual elements
            try:
                tool.Sequence.refresh_task_bars()
            except (AttributeError, TypeError):
                pass
            
            # 6. RESTORE state after reload
            try:
                restore_all_ui_state(context)
            except Exception as e:
                print(f"Bonsai WARNING: restore_all_ui_state failed: {e}")

            # 7. Force Blender to redraw the entire interface
            for area in context.screen.areas:
                area.tag_redraw()

            self.report({'INFO'}, "4D Sequence Refreshed.")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to refresh animation view: {str(e)}")
            return {'CANCELLED'}