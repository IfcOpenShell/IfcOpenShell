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
from bpy.types import Panel
import bonsai.tool as tool
from bonsai.bim.module.sequence.data import AnimationColorSchemeData



class BIM_PT_animation_tools(Panel):
    bl_label = "Animation Tools"
    bl_idname = "BIM_PT_animation_tools"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_sequence"

    @staticmethod
    def _label_from_iso(val, placeholder):
        """Helper to format ISO date for UI display"""
        try:
            if not val or val.strip() in ("", "-"):
                return placeholder
            return val.split("T")[0]
        except Exception:
            return placeholder
    bl_order = 3

    @classmethod
    def poll(cls, context):
        return True

    def draw_processing_options(self):
        layout = self.layout
        self.animation_props = tool.Sequence.get_animation_props()
        camera_props = self.animation_props.camera_orbit

        box = layout.box()
        col = box.column(align=True)

        row = col.row(align=True)
        # Changed to a toggle button for a more consistent UI style, as requested.
        row.prop(camera_props, "show_camera_orbit_settings", text="Camera & Orbit Settings", toggle=True, icon='CAMERA_DATA')

        if camera_props.show_camera_orbit_settings:
            self.draw_camera_orbit_ui()

    def draw_hud_settings_section(self, layout):
        """Draws the complete HUD section as an independent panel."""
        try:
            camera_props = self.animation_props.camera_orbit
            hud_box = layout.box()

            # Main HUD header with expandable arrow
            hud_header = hud_box.row(align=True)
            # Changed to a toggle button for a more consistent UI style, as requested.
            hud_header.prop(camera_props, "expand_hud_settings", text="Schedule HUD", toggle=True, icon='SCRIPTPLUGINS')

            # Complete HUD settings (only if expanded)
            if camera_props.expand_hud_settings:
                self.draw_camera_hud_settings(hud_box)

        except Exception as e:
            # Fallback if there are issues
            error_box = layout.box()
            error_box.label(text="Schedule HUD", icon="VIEW_CAMERA")
            error_box.label(text=f"Error: {str(e)}", icon='ERROR')

    def draw_visualisation_ui(self):
        # Appearance Groups (Animation): priority-ordered, selectable & re-orderable
        box = self.layout.box()
        col = box.column(align=True)
        col.label(text="Animation Groups (For Animation/Snapshot):")
        row = col.row()
        row.template_list("BIM_UL_animation_group_stack", "", self.animation_props, "animation_group_stack", self.animation_props, "animation_group_stack_index", rows=3)
        col2 = row.column(align=True)
        # Always enabled: Add
        col2.operator("bim.anim_group_stack_add", text="", icon="ADD")
        # Compute current selection and total for enabling logic
        idx = self.animation_props.animation_group_stack_index
        total = len(self.animation_props.animation_group_stack)
        # Remove: enabled only when a valid item is selected
        _row = col2.row(align=True)
        _row.enabled = (0 <= idx < total)
        _row.operator("bim.anim_group_stack_remove", text="", icon="REMOVE")
        col2.separator()
        # Move Up: enabled only when not the first item
        _row = col2.row(align=True)
        _row.enabled = (idx > 0)
        op = _row.operator("bim.anim_group_stack_move", text="", icon="TRIA_UP")
        op.direction = "UP"
        # Move Down: enabled only when not the last item
        _row = col2.row(align=True)
        _row.enabled = (0 <= idx < total - 1)
        op = _row.operator("bim.anim_group_stack_move", text="", icon="TRIA_DOWN")
        op.direction = "DOWN"

        if not AnimationColorSchemeData.is_loaded:
            AnimationColorSchemeData.load()

        row = self.layout.row(align=True)
        row.label(text="Start Date/ Date Range:", icon="CAMERA_DATA")

        row = self.layout.row(align=True)
        
        # Display schedule type selection without sync auto functionality
        row.prop(self.props, "date_source_type", expand=True)


        # Note: Using custom buttons above instead of expand=True to avoid duplication
        

        row = self.layout.row(align=True)
        row.alignment = "RIGHT"
        op = row.operator("bim.datepicker", text=self._label_from_iso(self.props.visualisation_start, "Start Date"), icon="REW")
        op.target_prop = "BIMWorkScheduleProperties.visualisation_start"
        op = row.operator("bim.datepicker", text=self._label_from_iso(self.props.visualisation_finish, "Finish Date"), icon="FF")
        op.target_prop = "BIMWorkScheduleProperties.visualisation_finish"
        op = row.operator("bim.guess_date_range", text="Guess", icon="FILE_REFRESH")
        op.work_schedule = self.props.active_work_schedule_id

        row = self.layout.row(align=True)
        row.label(text="Speed Settings")
        row = self.layout.row(align=True)
        row.alignment = "RIGHT"
        row.prop(self.props, "speed_types", text="")
        if self.props.speed_types == "FRAME_SPEED":
            row.prop(self.props, "speed_animation_frames", text="")
            row.prop(self.props, "speed_real_duration", text="")
        elif self.props.speed_types == "DURATION_SPEED":
            row.prop(self.props, "speed_animation_duration", text="")
            row.label(text="->")
            row.prop(self.props, "speed_real_duration", text="")
        elif self.props.speed_types == "MULTIPLIER_SPEED":
            row.prop(self.props, "speed_multiplier", text="")

        # --- Display Settings Section ---
        row.label(text="Display Settings")
        row = self.layout.row(align=True)
        row.prop(self.animation_props, "should_show_task_bar_options", text="Task Bars", toggle=True, icon="NLA_PUSHDOWN")
        row.label(text="", icon='INFO')

        if self.animation_props.should_show_task_bar_options:
            box = self.layout.box()
            row = box.row()
            row.label(text="Task Bar Options", icon="NLA_PUSHDOWN")

            # Show schedule information for Task Bars
            try:
                schedule_start, schedule_finish = tool.Sequence.get_schedule_date_range()
                if schedule_start and schedule_finish:
                    info_row = box.row()
                    info_row.label(text=f"📅 Schedule: {schedule_start.strftime('%Y-%m-%d')} to {schedule_finish.strftime('%Y-%m-%d')}", icon='TIME')
                    info_row = box.row()
                    info_row.label(text="[INFO] Task bars align with schedule dates (independent of animation settings)", icon='INFO')
                else:
                    info_row = box.row()
                    info_row.label(text="[WARNING] No schedule dates available", icon='ERROR')
            except Exception:
                pass


            # Enable task selection
            row = box.row(align=True)
            row.prop(self.props, "should_show_task_bar_selection", text="Enable Selection", icon="CHECKBOX_HLT")

            # Show selected task counter
            task_count = len(tool.Sequence.get_task_bar_list())
            if task_count > 0:
                row.label(text=f"({task_count} selected)")

            # Button to generate bars
            row = box.row(align=True)
            row.operator("bim.add_task_bars", text="Generate Bars", icon="VIEW3D")

            # If there are selected tasks, show option to clear
            if task_count > 0:
                row.operator("bim.clear_task_bars", text="Clear", icon="TRASH")

            # Bar colors
            grid = box.grid_flow(columns=2, even_columns=True)
            col = grid.column()
            row = col.row(align=True)
            row.prop(self.animation_props, "color_progress")

            col = grid.column()
            row = col.row(align=True) # This line is duplicated, but I will keep it as it is in the original file.
            row.prop(self.animation_props, "color_full") # This line is duplicated, but I will keep it as it is in the original file.

        self.layout.separator()  # Visual separator

        row = self.layout.row(align=True)
        row.alignment = "RIGHT"

        # Color scheme selector (optional, no longer used)
        if AnimationColorSchemeData.data.get("saved_color_schemes"):
            row.prop(
                self.animation_props,
                "saved_color_schemes",
                text="Color Scheme",
                icon=tool.Blender.SEQUENCE_COLOR_SCHEME_ICON,
            )

        
        # Color scheme selector (optional, no longer used)
        if AnimationColorSchemeData.data.get("saved_color_schemes"):
            row.prop(
                self.animation_props,
                "saved_color_schemes",
                text="Color Scheme",
                icon=tool.Blender.SEQUENCE_COLOR_SCHEME_ICON,
            )

        # === MAIN BUTTONS - Animation Settings ===
        main_actions_box = self.layout.box()
        main_actions_box.label(text="Animation Actions:", icon="OUTLINER_OB_CAMERA")

        # Main button with protection against crashes
        main_row = main_actions_box.row()

        # Check if animation is already active to prevent crashes
        try:
            anim_props = tool.Sequence.get_animation_props()
            is_animation_active = getattr(anim_props, 'is_animation_created', False)
            is_snapshot_active = bpy.context.scene.get("is_snapshot_mode", False)
        except Exception:
            is_animation_active = False
            is_snapshot_active = False

        # Check if work schedule tasks are opened/expanded
        tasks_opened = self.props.active_work_schedule_id and self.props.editing_type == "TASKS"

        # Disable if ANY state is active (animation or snapshot) OR tasks are not opened
        main_row.enabled = not (is_animation_active or is_snapshot_active) and tasks_opened

        # Dynamic button text based on state
        if is_animation_active:
            button_text = "Animation Active - Reset First"
        elif is_snapshot_active:
            button_text = "Snapshot Active - Reset Snapshot First"
        else:
            button_text = "Create Animation"

        op = main_row.operator(
            "bim.visualise_work_schedule_date_range",
            text=button_text,
            icon="OUTLINER_OB_CAMERA")

        op.work_schedule = self.props.active_work_schedule_id

        # Reset Button - only enabled if an animation is active
        reset_row = main_actions_box.row()
        reset_row.enabled = is_animation_active
        reset_row.operator("bim.clear_previous_animation", text="Reset", icon="TRASH")

        # --- Processing Tools (moved below main actions) ---
        self.draw_processing_options()
        
        # === Independent HUD Settings ===
        self.layout.separator()
        self.draw_hud_settings_section(self.layout)



    def draw_snapshot_ui(self):
        # Ensure animation properties are always available
        try:
            import bonsai.tool as tool
            self.animation_props = tool.Sequence.get_animation_props()
        except Exception:
            pass  # If it fails, we keep the previous value if it exists

        # Label and date selector
        row = self.layout.row(align=True)
        row.label(text="Date of Snapshot:", icon="CAMERA_STEREO")

        row = self.layout.row(align=True)
        row.alignment = "RIGHT"
        op = row.operator("bim.datepicker", text=self._label_from_iso(self.props.visualisation_start, "Date"), icon="PROP_PROJECTED")
        op.target_prop = "BIMWorkScheduleProperties.visualisation_start"

        # Active Profile Group information box (simplified)
        box = self.layout.box()
        row = box.row(align=True)
        
        # Get only the first active group
        active_group = None
        try:
            for stack_item in getattr(self.animation_props, "animation_group_stack", []):
                if getattr(stack_item, "enabled", False) and getattr(stack_item, "group", None):
                    active_group = stack_item.group
                    break
        except Exception:
            active_group = None

        # Simple layout: label on the left, group on the right
        row.label(text="Active colortype Group:", icon='PRESET')
        if active_group:
            row.label(text=active_group)
        else:
            row.label(text="DEFAULT")

        # === SNAPSHOT ACTIONS (moved above camera controls) ===
        actions_box = self.layout.box()
        actions_box.label(text="Snapshot Actions:", icon="RENDER_STILL")

        # Main button to create the snapshot with protection against crashes
        main_row = actions_box.row()

        # Check if snapshot is already active to prevent crashes
        try:
            import bpy
            import bonsai.tool as tool
            is_snapshot_active = bpy.context.scene.get("is_snapshot_mode", False)
            anim_props = tool.Sequence.get_animation_props()
            is_animation_active = getattr(anim_props, 'is_animation_created', False)
            print(f"🔍 SNAPSHOT UI DEBUG: is_snapshot_mode = {is_snapshot_active}, is_animation_active = {is_animation_active}")
        except Exception as e:
            print(f"🔍 SNAPSHOT UI DEBUG: Exception reading states: {e}")
            is_snapshot_active = False
            is_animation_active = False

        # Check if work schedule tasks are opened/expanded
        tasks_opened = self.props.active_work_schedule_id and self.props.editing_type == "TASKS"

        # Disable if ANY state is active (animation or snapshot) OR tasks are not opened
        main_row.enabled = not (is_snapshot_active or is_animation_active) and tasks_opened

        # Dynamic button text based on state
        if is_snapshot_active:
            button_text = "Snapshot Active - Reset First"
        elif is_animation_active:
            button_text = "Animation Active - Reset Animation First"
        else:
            button_text = "Create SnapShot"

        op = main_row.operator("bim.snapshot_with_colortypes_fixed",
                                text=button_text,
                                icon="CAMERA_STEREO")


        try:
            op.work_schedule = self.props.active_work_schedule_id
        except Exception:
            pass

        # Reset Button - only enabled if a snapshot is active
        reset_row = actions_box.row()
        reset_row.enabled = is_snapshot_active
        reset_row.operator("bim.clear_previous_snapshot", text="Reset", icon="TRASH")

        self.layout.separator()

        # === Snapshot Camera Controls (now below actions) ===
        try:
            import bpy  # Ensure local import in case of partial Blender contexts
            camera_box = self.layout.box()
            camera_header = camera_box.row()
            camera_header.label(text="Snapshot Camera Controls:", icon="CAMERA_DATA")
            camera_row = camera_box.row(align=True)
            camera_row.operator("bim.add_snapshot_camera", text="Add Camera", icon="OUTLINER_OB_CAMERA")
            camera_row.operator("bim.align_snapshot_camera_to_view", text="Align to View", icon="CAMERA_DATA")

            active_cam = bpy.context.scene.camera if bpy.context and bpy.context.scene else None
            info_row = camera_box.row()
            if active_cam:
                info_row.label(text=f"Active: {active_cam.name}", icon="CAMERA_DATA")
            else:
                info_row.label(text="No active camera", icon="ERROR")

            # --- Manage Snapshot Cameras ---
            camera_props = self.animation_props.camera_orbit
            col = camera_box.column(align=True)
            col.separator()
            col.label(text="Manage Snapshot Cameras:", icon="OUTLINER_OB_CAMERA")

            row = col.row(align=True)

            delete_col = row.split(factor=0.5, align=True)
            delete_col.operator("bim.delete_snapshot_camera", text="Delete Snapshot Camera", icon="TRASH")

            # ALLOW camera change during snapshots

            row.prop(camera_props, "active_snapshot_camera", text="")
            row.prop(camera_props, "hide_all_snapshot_cameras", text="", icon='HIDE_ON' if camera_props.hide_all_snapshot_cameras else 'HIDE_OFF')
        except Exception:
            pass

        # === HUD Settings for Snapshot ===
        self.layout.separator()
        self.draw_hud_settings_section(self.layout)

    def draw_camera_orbit_ui(self):
        self.animation_props = tool.Sequence.get_animation_props()
        camera_props = self.animation_props.camera_orbit

        # Camera Block
        box = self.layout.box()
        col = box.column(align=True)
        col.label(text="Camera", icon="CAMERA_DATA")
        row = col.row(align=True)
        row.prop(camera_props, "camera_focal_mm")
        row = col.row(align=True)
        row.prop(camera_props, "camera_clip_start")
        row.prop(camera_props, "camera_clip_end")

        # Orbit Block
        box = self.layout.box()
        col = box.column(align=True)
        col.label(text="Orbit", icon="ORIENTATION_GIMBAL")
        row = col.row(align=True)
        row.operator("bim.add_camera_by_mode", text="Add Camera", icon="OUTLINER_OB_CAMERA")
        row.prop(camera_props, "orbit_mode", expand=True)

        # Radius, Height, Angle and Direction options
        row = col.row(align=True)
        row.prop(camera_props, "orbit_radius_mode", text="")
        sub = row.row(align=True)
        sub.enabled = camera_props.orbit_radius_mode == "MANUAL"
        sub.prop(camera_props, "orbit_radius", text="")
        row = col.row(align=True)
        row.prop(camera_props, "orbit_height")
        row = col.row(align=True)
        row.prop(camera_props, "orbit_start_angle_deg")
        row.prop(camera_props, "orbit_direction", expand=True)

        # Look At
        col.separator()
        row = col.row(align=True)
        row.prop(camera_props, "look_at_mode", expand=True)
        if camera_props.look_at_mode == "OBJECT":
            col.prop(camera_props, "look_at_object")
        
        # Method and Path Section
        col.separator()
        col.label(text="Animation Method & Path:")
        
        row = col.row(align=True)
        row.prop(camera_props, "orbit_path_shape", expand=True)
        
        if camera_props.orbit_path_shape == 'CUSTOM':
            col.prop(camera_props, "custom_orbit_path")

        row = col.row(align=True)
        row.enabled = camera_props.orbit_path_shape == 'CIRCLE'
        row.prop(camera_props, "orbit_path_method", expand=True)

        # Hide interpolation options for CIRCLE_360 since it always uses LINEAR
        is_circle_360 = camera_props.orbit_path_method == 'CIRCLE_360'
        

        # Action Buttons
        col.separator()
        action_row = col.row(align=True)
        action_row.operator("bim.align_4d_camera_to_view", text="Align Cam to View", icon="CAMERA_DATA")
        action_row.operator("bim.update_camera_only", text="Update", icon="FILE_TICK")
        action_row.operator("bim.reset_camera_settings", text="Reset", icon="FILE_REFRESH")

        # --- NEW: 4D Camera Management ---
        col.separator()
        col.label(text="Manage Animation Cameras:", icon="OUTLINER_OB_CAMERA")
        
        # Create a single row for all new camera management controls
        row = col.row(align=True) # This line is duplicated, but I will keep it as it is in the original file.
        
        # Split the row to balance the controls: 50% for delete, 50% for the rest.
        delete_col = row.split(factor=0.5, align=True)
        
        # Column 1: Delete button
        delete_col.operator("bim.delete_animation_camera", text="Delete Animation Camera", icon="TRASH")
        
        # The selector now takes up most of the remaining space, pushing the hide button to the right.
        # Selecting a camera from the dropdown will now automatically make it the active scene camera.

        # ALLOW selector during animation to switch between static cameras
        # (The filter already handles showing only appropriate cameras)
        row.enabled = True

        row.prop(camera_props, "active_animation_camera", text="") # This line is duplicated, but I will keep it as it is in the original file.
        row.prop(camera_props, "hide_all_animation_cameras", text="", icon='HIDE_ON' if camera_props.hide_all_animation_cameras else 'HIDE_OFF') # This line is duplicated, but I will keep it as it is in the original file.

    def draw_camera_hud_settings(self, layout):
        """Draws the configuration panels for both HUDs."""
        camera_props = self.animation_props.camera_orbit

        # --- PANEL FOR THE TEXT HUD ---
        text_hud_box = layout.box()
        text_header = text_hud_box.row(align=True)
        text_header.prop(camera_props, "enable_text_hud", text="")
        icon = 'TRIA_DOWN' if camera_props.expand_schedule_hud else 'TRIA_RIGHT'
        text_header.prop(camera_props, "expand_schedule_hud", text="Text HUD", toggle=True, icon=icon)

        if camera_props.expand_schedule_hud:
            # Visibility Controls for Text HUD elements
            visibility_box = text_hud_box.box()
            visibility_box.label(text="Element Visibility", icon="HIDE_OFF")
            visibility_row1 = visibility_box.row(align=True)
            visibility_row1.prop(camera_props, "hud_show_date", text="Date")
            visibility_row1.prop(camera_props, "hud_show_week", text="Week")
            visibility_row2 = visibility_box.row(align=True)
            visibility_row2.prop(camera_props, "hud_show_day", text="Day")
            visibility_row2.prop(camera_props, "hud_show_progress", text="Progress")

            # ==========================================
            # === LAYOUT - COMPLETE SECTION ===
            # ==========================================
            layout_box = text_hud_box.box()
            layout_box.label(text="Layout", icon="SNAP_GRID")
            layout_box.prop(camera_props, "hud_position", text="Position")

            # Margins
            margin_row = layout_box.row(align=True)
            margin_row.prop(camera_props, "hud_margin_horizontal", text="H-Margin")
            margin_row.prop(camera_props, "hud_margin_vertical", text="V-Margin")

            # Scale and Line Spacing
            spacing_row = layout_box.row(align=True)
            spacing_row.prop(camera_props, "hud_scale_factor", text="Scale")
            if hasattr(camera_props, 'hud_text_spacing'):
                spacing_row.prop(camera_props, "hud_text_spacing", text="Line Spacing")

            # Padding
            if hasattr(camera_props, 'hud_padding_horizontal'):
                padding_row = layout_box.row(align=True)
                padding_row.prop(camera_props, "hud_padding_horizontal", text="H-Padding")
                padding_row.prop(camera_props, "hud_padding_vertical", text="V-Padding")

            # ==========================================
            # === COLORS - COMPLETE SECTION ===
            # ==========================================
            colors_box = text_hud_box.box()
            colors_box.label(text="Colors", icon="COLOR")

            # Basic colors
            if hasattr(camera_props, 'hud_text_color'):
                colors_box.prop(camera_props, "hud_text_color", text="Text")
            if hasattr(camera_props, 'hud_background_color'):
                colors_box.prop(camera_props, "hud_background_color", text="Background")

            # Gradient
            if hasattr(camera_props, 'hud_background_gradient_enabled'):
                gradient_row = colors_box.row()
                gradient_row.prop(camera_props, "hud_background_gradient_enabled", text="Gradient")

                if getattr(camera_props, "hud_background_gradient_enabled", False):
                    colors_box.prop(camera_props, "hud_background_gradient_color", text="Gradient Color")
                    if hasattr(camera_props, 'hud_gradient_direction'):
                        colors_box.prop(camera_props, "hud_gradient_direction", text="Direction")

            # ==========================================
            # === BORDERS & EFFECTS - COMPLETE SECTION ===
            # ==========================================
            effects_box = text_hud_box.box()
            effects_box.label(text="Borders & Effects", icon="MESH_PLANE")

            # Borders
            if hasattr(camera_props, 'hud_border_width'):
                border_row = effects_box.row(align=True)
                border_row.prop(camera_props, "hud_border_width", text="Border Width")
                if getattr(camera_props, "hud_border_width", 0) > 0 and hasattr(camera_props, 'hud_border_color'):
                    border_row.prop(camera_props, "hud_border_color", text="")

            if hasattr(camera_props, 'hud_border_radius'):
                effects_box.prop(camera_props, "hud_border_radius", text="Border Radius")

            # ==========================================
            # === SHADOWS - COMPLETE SECTION ===
            # ==========================================
            shadows_box = text_hud_box.box()
            shadows_box.label(text="Shadows", icon="LIGHT_SUN")

            # Text shadow
            if hasattr(camera_props, 'hud_text_shadow_enabled'):
                text_shadow_row = shadows_box.row()
                text_shadow_row.prop(camera_props, "hud_text_shadow_enabled", text="Text Shadow")

                if getattr(camera_props, "hud_text_shadow_enabled", False):
                    shadow_offset_row = shadows_box.row(align=True)
                    if hasattr(camera_props, 'hud_text_shadow_offset_x'):
                        shadow_offset_row.prop(camera_props, "hud_text_shadow_offset_x", text="X")
                    if hasattr(camera_props, 'hud_text_shadow_offset_y'):
                        shadow_offset_row.prop(camera_props, "hud_text_shadow_offset_y", text="Y")
                    if hasattr(camera_props, 'hud_text_shadow_color'):
                        shadows_box.prop(camera_props, "hud_text_shadow_color", text="Shadow Color")

            # Background shadow
            if hasattr(camera_props, 'hud_background_shadow_enabled'):
                bg_shadow_row = shadows_box.row()
                bg_shadow_row.prop(camera_props, "hud_background_shadow_enabled", text="Background Shadow")

                if getattr(camera_props, "hud_background_shadow_enabled", False):
                    if hasattr(camera_props, 'hud_background_shadow_offset_x'):
                        bg_shadow_offset_row = shadows_box.row(align=True)
                        bg_shadow_offset_row.prop(camera_props, "hud_background_shadow_offset_x", text="X")
                        bg_shadow_offset_row.prop(camera_props, "hud_background_shadow_offset_y", text="Y")
                    if hasattr(camera_props, 'hud_background_shadow_blur'):
                        shadows_box.prop(camera_props, "hud_background_shadow_blur", text="Blur")
                    if hasattr(camera_props, 'hud_background_shadow_color'):
                        shadows_box.prop(camera_props, "hud_background_shadow_color", text="Shadow Color")

            # ==========================================
            # === TYPOGRAPHY - COMPLETE SECTION ===
            # ==========================================
            if hasattr(camera_props, 'hud_font_weight'):
                typo_box = text_hud_box.box()
                typo_box.label(text="Typography", icon="FONT_DATA")

                typo_box.prop(camera_props, "hud_font_weight", text="Weight")
                if hasattr(camera_props, 'hud_letter_spacing'):
                    typo_box.prop(camera_props, "hud_letter_spacing", text="Letter Spacing")

        # ==========================================
        # === TIMELINE HUD - CONFIGURATION PANEL ===
        # ==========================================
        timeline_box = layout.box()
        timeline_header = timeline_box.row(align=True)
        timeline_header.prop(camera_props, "enable_timeline_hud", text="")
        icon = 'TRIA_DOWN' if camera_props.expand_timeline_hud else 'TRIA_RIGHT'
        timeline_header.prop(camera_props, "expand_timeline_hud", text="Timeline HUD", toggle=True, icon=icon)

        if camera_props.expand_timeline_hud:
            timeline_box.prop(camera_props, "timeline_hud_locked", text="Lock Position", icon="LOCKED" if getattr(camera_props, "timeline_hud_locked", True) else "UNLOCKED")
            # Layout & Position
            # Controls according to lock state
            if getattr(camera_props, "timeline_hud_locked", True):
                row = timeline_box.row() # This line is duplicated, but I will keep it as it is in the original file.
                row.prop(camera_props, "timeline_hud_position", text="Position")
                margin_row = timeline_box.row(align=True)
                margin_row.prop(camera_props, "timeline_hud_margin_horizontal", text="H-Margin")
                margin_row.prop(camera_props, "timeline_hud_margin_vertical", text="V-Margin")
                row = timeline_box.row(align=True)
                row.prop(camera_props, "timeline_hud_height", text="Height")
                row.prop(camera_props, "timeline_hud_width", text="Width")
            else: # This line is duplicated, but I will keep it as it is in the original file.
                manual_row = timeline_box.row(align=True)
                manual_row.label(text="Manual Position:", icon="TRANSFORM_ORIGINS")
                manual_pos_row = timeline_box.row(align=True)
                manual_pos_row.prop(camera_props, "timeline_hud_manual_x", text="X")
                manual_pos_row.prop(camera_props, "timeline_hud_manual_y", text="Y")
                timeline_box.prop(camera_props, "timeline_hud_height", text="Height")
                timeline_box.prop(camera_props, "timeline_hud_width", text="Width")

            # Colors - Simplified for Synchro 4D Style
            colors_box = timeline_box.box()
            colors_box.label(text="Colors", icon="COLOR")
            colors_box.prop(camera_props, "timeline_hud_color_inactive_range", text="Background")
            colors_box.prop(camera_props, "timeline_hud_color_text", text="Text & Lines")
            colors_box.prop(camera_props, "timeline_hud_color_indicator", text="Current Date Indicator")
            
            # Progress Bar Controls
            progress_row = colors_box.row()
            progress_row.prop(camera_props, "timeline_hud_show_progress_bar", text="Show Progress Bar")
            if getattr(camera_props, "timeline_hud_show_progress_bar", True):
                colors_box.prop(camera_props, "timeline_hud_color_progress", text="Progress Color")
            
            # Style
            style_box = timeline_box.box()
            style_box.label(text="Style", icon="MESH_PLANE")
            style_box.prop(camera_props, "timeline_hud_border_radius", text="Border Radius")

        # ==================== LEGEND HUD ====================
        legend_box = layout.box()
        legend_header = legend_box.row(align=True)
        legend_header.prop(camera_props, "enable_legend_hud", text="")
        icon = 'TRIA_DOWN' if camera_props.expand_legend_hud else 'TRIA_RIGHT'
        legend_header.prop(camera_props, "expand_legend_hud", text="Legend HUD", toggle=True, icon=icon)

        if camera_props.expand_legend_hud:
            # Position & Layout
            position_box = legend_box.box()
            position_box.label(text="Position & Layout", icon="SNAP_GRID")
            
            position_row = position_box.row(align=True)
            position_row.prop(camera_props, "legend_hud_position", text="Position")
            position_row.prop(camera_props, "legend_hud_orientation", text="")
            
            margins_row = position_box.row(align=True)
            margins_row.prop(camera_props, "legend_hud_margin_horizontal", text="Margin H")
            margins_row.prop(camera_props, "legend_hud_margin_vertical", text="Margin V")
            
            scaling_row = position_box.row(align=True)
            scaling_row.prop(camera_props, "legend_hud_scale", text="Scale")
            scaling_row.prop(camera_props, "legend_hud_auto_scale", text="Auto Scale")
            
            if not getattr(camera_props, "legend_hud_auto_scale", True):
                position_box.prop(camera_props, "legend_hud_max_width", text="Max Width")
            
            # Content Settings
            content_box = legend_box.box()
            content_box.label(text="Content", icon="TEXT")
            
            title_row = content_box.row(align=True)
            title_row.prop(camera_props, "legend_hud_show_title", text="Show Title")
            if getattr(camera_props, "legend_hud_show_title", True):
                title_row.prop(camera_props, "legend_hud_title_text", text="",)
                title_row.prop(camera_props, "legend_hud_title_font_size", text="Size")
            
            spacing_row = content_box.row(align=True)
            spacing_row.prop(camera_props, "legend_hud_item_spacing", text="Item Spacing")
            spacing_row.prop(camera_props, "legend_hud_color_indicator_size", text="Color Size")
            
            # colortype Selection with Scrollable List
            colortypes_box = content_box.box()
            colortypes_header = colortypes_box.row(align=True)
            colortypes_header.label(text="colortype Visibility", icon="RESTRICT_VIEW_OFF")
            
            # Get ALL colortypes from the active animation group (NEVER filtered)
            all_colortypes = []
            try:
                import bonsai.tool as tool
                anim_props = tool.Sequence.get_animation_props()
                if hasattr(anim_props, 'animation_group_stack') and anim_props.animation_group_stack:
                    # CORRECTION: Only get profiles from the first active group (enabled=True).
                    active_group = None
                    print("🔍 UI: Checking animation group stack for active group:")
                    for i, group_item in enumerate(anim_props.animation_group_stack):
                        enabled = getattr(group_item, 'enabled', False)
                        print(f"  {i}: Group '{group_item.group}' enabled={enabled}")
                        if enabled and active_group is None:
                            active_group = group_item.group
                            print(f"🎯 UI: Selected active group: {active_group}")
                            break
                    
                    # FALLBACK: If there are no active groups, use the first group as a fallback.
                    if active_group is None:
                        if anim_props.animation_group_stack:
                            active_group = anim_props.animation_group_stack[0].group
                            print(f"🔄 UI: Using FALLBACK to first group: {active_group}")
                        else:
                            print("[ERROR] UI: No groups available at all")
                    
                    if active_group:
                        print(f"🎯 UI: Getting colortypes from group: {active_group}")
                        
                        # Get colortypes directly from the active group JSON data
                        try:
                            import json
                            scene = bpy.context.scene
                            key = "BIM_AnimationColorSchemesSets"
                            raw_data = scene.get(key, "{}")
                            
                            if isinstance(raw_data, str):
                                colortype_sets = json.loads(raw_data)
                            else:
                                colortype_sets = raw_data or {}
                                
                            if active_group in colortype_sets and 'ColorTypes' in colortype_sets[active_group]:
                                # For the DEFAULT group, always use the hardcoded, predefined order
                                if active_group == "DEFAULT":
                                    default_order = [
                                        "CONSTRUCTION", "INSTALLATION", "DEMOLITION", "REMOVAL",
                                        "DISPOSAL", "DISMANTLE", "OPERATION", "MAINTENANCE",
                                        "ATTENDANCE", "RENOVATION", "LOGISTIC", "MOVE", "NOTDEFINED"
                                    ]
                                    for colortype_name in default_order:
                                        if colortype_name and colortype_name not in all_colortypes:
                                            all_colortypes.append(colortype_name)
                                            print(f"🎯 UI: Added DEFAULT colortype in predefined order: {colortype_name}")
                                else:
                                    # For custom groups, maintain the order from the JSON file
                                    for colortype in colortype_sets[active_group]['ColorTypes']:
                                        colortype_name = colortype.get('name', '')
                                        if colortype_name and colortype_name not in all_colortypes:
                                            all_colortypes.append(colortype_name)
                                            print(f"🎯 UI: Added custom colortype to list: {colortype_name}")
                        except Exception as e:
                            print(f"[ERROR] UI: Error getting colortypes from active group {active_group}: {e}")
                    else:
                        print("🎯 UI: No active group found (no enabled groups)")
                            
            except Exception as e:
                print(f"[ERROR] UI: Error getting animation props: {e}")
                all_colortypes = []
                
            print(f"🎯 UI: Total colortypes for settings list: {len(all_colortypes)} - {all_colortypes}")
            
            # Force refresh - make sure we always have the full list
            if not all_colortypes:
                print("[WARNING] UI: No colortypes found, trying alternative method...")
                try:
                    # Fallback: try to get from scene property directly
                    scene = bpy.context.scene
                    if hasattr(scene, 'BIMAnimationProperties') and scene.BIMAnimationProperties.ColorType_groups:
                        active_group = scene.BIMAnimationProperties.ColorType_groups
                        print(f"🎯 UI: Fallback - trying group: {active_group}")
                        
                        import json
                        key = "BIM_AnimationColorSchemesSets"
                        raw_data = scene.get(key, "{}")
                        colortype_sets = json.loads(raw_data) if isinstance(raw_data, str) else (raw_data or {})
                        
                        if active_group in colortype_sets and 'ColorTypes' in colortype_sets[active_group]:
                            all_colortypes = [colortype.get('name', '') for colortype in colortype_sets[active_group]['ColorTypes'] if colortype.get('name')]
                            print(f"🎯 UI: Fallback found {len(all_colortypes)} colortypes: {all_colortypes}")
                except Exception as e:
                    print(f"[ERROR] UI: Fallback failed: {e}")
            
            if all_colortypes:
                # Get current scroll position and hidden colortypes
                scroll_offset = getattr(camera_props, 'legend_hud_colortype_scroll_offset', 0)
                colortypes_per_page = 5  # Fixed to show 5 colortypes at a time
                
                # NOTE: legend_hud_visible_colortypes now stores HIDDEN colortypes (inverted logic)
                # By default all colortypes are visible, user unchecks to hide them
                hidden_colortypes_str = getattr(camera_props, 'legend_hud_visible_colortypes', '')
                hidden_colortypes = [p.strip() for p in hidden_colortypes_str.split(',') if p.strip()] if hidden_colortypes_str else []
                
                # Calculate pagination
                total_colortypes = len(all_colortypes)
                max_scroll = max(0, total_colortypes - colortypes_per_page)
                scroll_offset = max(0, min(scroll_offset, max_scroll))
                
                # Navigation controls (only arrows, no text)
                nav_row = colortypes_box.row(align=True)
                nav_row.operator("bim.legend_hud_colortype_scroll_up", text="", icon="TRIA_UP")
                # Spacer to center the arrows
                nav_row.separator()
                nav_row.operator("bim.legend_hud_colortype_scroll_down", text="", icon="TRIA_DOWN")
                
                # colortype checkboxes - All colortypes are always visible in the list
                # Checkbox controls if a colortype appears in the viewport HUD legend
                end_index = min(scroll_offset + colortypes_per_page, total_colortypes)
                print(f"🎯 UI: Displaying colortypes {scroll_offset} to {end_index} of {total_colortypes}")
                print(f"🎯 UI: Hidden colortypes: {hidden_colortypes}")
                
                for i in range(scroll_offset, end_index):
                    if i < len(all_colortypes):  # Safety check
                        colortype_name = all_colortypes[i]
                        colortype_row = colortypes_box.row(align=True)
                        
                        # Checkbox: checked = show in viewport HUD, unchecked = hide from viewport HUD
                        # colortype always remains visible in this settings list
                        is_visible_in_hud = colortype_name not in hidden_colortypes
                        
                        # Use checkbox icon with tilde when checked
                        icon = "CHECKBOX_HLT" if is_visible_in_hud else "CHECKBOX_DEHLT"
                        checkbox_op = colortype_row.operator(
                            "bim.legend_hud_toggle_colortype_visibility", 
                            text="", 
                            icon=icon,
                            depress=False  # Don't use depress, use icon state instead
                        )
                        checkbox_op.colortype_name = colortype_name
                        
                        # colortype name - always visible
                        colortype_row.label(text=colortype_name)
                        
                        print(f"🎯 UI: Showing colortype {i}: {colortype_name} (HUD visible: {is_visible_in_hud})")
                    else:
                        print(f"[ERROR] UI: Index {i} out of range for colortypes list (len: {len(all_colortypes)})")
                    
            else:
                colortypes_box.label(text="No colortypes available", icon="INFO")
            
            # Color Columns
            columns_box = content_box.box()
            columns_box.label(text="Color Columns", icon="COLORSET_01_VEC")
            
            columns_vis_row = columns_box.row(align=True)
            columns_vis_row.prop(camera_props, "legend_hud_show_start_column", text="Start")
            columns_vis_row.prop(camera_props, "legend_hud_show_active_column", text="Active") 
            columns_vis_row.prop(camera_props, "legend_hud_show_end_column", text="End")
            
            titles_vis_row = columns_box.row(align=True)
            titles_vis_row.label(text="Show Titles:")
            if getattr(camera_props, "legend_hud_show_start_column", True):
                titles_vis_row.prop(camera_props, "legend_hud_show_start_title", text="Start", toggle=True)
            if getattr(camera_props, "legend_hud_show_active_column", True):
                titles_vis_row.prop(camera_props, "legend_hud_show_active_title", text="Active", toggle=True)
            if getattr(camera_props, "legend_hud_show_end_column", True):
                titles_vis_row.prop(camera_props, "legend_hud_show_end_title", text="End", toggle=True)
            
            columns_box.prop(camera_props, "legend_hud_column_spacing", text="Column Spacing")
            
            # Styling
            style_box = legend_box.box()
            style_box.label(text="Styling", icon="BRUSH_DATA")
            
            # Background
            bg_row = style_box.row(align=True)
            bg_row.prop(camera_props, "legend_hud_background_color", text="Background")
            bg_row.prop(camera_props, "legend_hud_border_radius", text="Radius")
            
            # Padding
            padding_row = style_box.row(align=True)
            padding_row.prop(camera_props, "legend_hud_padding_horizontal", text="Padding H")
            padding_row.prop(camera_props, "legend_hud_padding_vertical", text="Padding V")
            
            # Text
            text_color_row = style_box.row(align=True)
            text_color_row.prop(camera_props, "legend_hud_text_color", text="Text Color")
            text_color_row.prop(camera_props, "legend_hud_title_color", text="Title Color")
            
            # Text Shadow
            shadow_row = style_box.row(align=True)
            shadow_row.prop(camera_props, "legend_hud_text_shadow_enabled", text="Text Shadow")
            if getattr(camera_props, "legend_hud_text_shadow_enabled", True):
                shadow_row.prop(camera_props, "legend_hud_text_shadow_color", text="")
                
                shadow_offset_row = style_box.row(align=True)
                shadow_offset_row.label(text="Shadow Offset:")
                shadow_offset_row.prop(camera_props, "legend_hud_text_shadow_offset_x", text="X")
                shadow_offset_row.prop(camera_props, "legend_hud_text_shadow_offset_y", text="Y")
        

        # --- 3D Scene Texts ---
        layout.separator()
        
        # 3D HUD Render expandable section
        schedule_box = layout.box()
        schedule_header = schedule_box.row(align=True)
        schedule_header.prop(camera_props, "show_3d_schedule_texts", text="")
        icon = 'TRIA_DOWN' if camera_props.expand_3d_hud_render else 'TRIA_RIGHT'
        schedule_header.prop(camera_props, "expand_3d_hud_render", text="3D HUD Render", toggle=True, icon=icon)

        if camera_props.expand_3d_hud_render:
            self.draw_3d_hud_render_settings(schedule_box) # This line is duplicated, but I will keep it as it is in the original file.

    def draw(self, context):
        self.props = tool.Sequence.get_work_schedule_props()
        self.animation_props = tool.Sequence.get_animation_props()
        
        row = self.layout.row(align=True)
        row.alignment = "RIGHT"
        row.prop(self.props, "should_show_visualisation_ui", text="Animation Settings", icon="SETTINGS")
        row.prop(self.props, "should_show_snapshot_ui", text="Snapshot Settings", icon="SETTINGS")

        if not (self.props.should_show_visualisation_ui or self.props.should_show_snapshot_ui):
            self.props.should_show_visualisation_ui = True

        if self.props.should_show_visualisation_ui:
            self.draw_visualisation_ui()
        if self.props.should_show_snapshot_ui:
            self.draw_snapshot_ui()


    def draw_3d_hud_render_settings(self, layout):
        """Draw 3D HUD Render settings (empty controls + individual text controls)"""
        import bpy
        import bonsai.tool as tool

        # ==================== 3D LEGEND HUD ====================
        try:
            anim_props = tool.Sequence.get_animation_props()
            camera_props = anim_props.camera_orbit
            
            # 3D Legend HUD simple checkbox - NO ICONS
            layout.prop(camera_props, "enable_3d_legend_hud", text="3D Legend HUD")
                    
        except Exception:
            pass # Fail silently if props aren't available

        # --- Parent Empty Controls (from original version) ---
        parent_empty = bpy.data.objects.get("Schedule_Display_Parent")
        if parent_empty:
            box = layout.box()
            row = box.row(align=True)
            row.label(text="Display Group Control", icon="EMPTY_DATA")
            row.prop(parent_empty, "hide_viewport", text="", icon='HIDE_OFF' if not parent_empty.hide_viewport else 'HIDE_ON', emboss=False)

            col = box.column(align=True)
            col.prop(parent_empty, "location", text="Group Position")
            col.prop(parent_empty, "rotation_euler", text="Group Rotation")
            col.prop(parent_empty, "scale", text="Group Scale")

            # --- Custom Rotation Constraint ---
            try:
                anim_props = tool.Sequence.get_animation_props()
                camera_props = anim_props.camera_orbit
                
                # --- Rotation Constraint ---
                col.separator()
                col.label(text="Rotation Constraint:")
                
                row = col.row(align=True)
                row.prop(camera_props, "use_custom_rotation_target", text="Use Custom Target")
                
                sub_row = col.row(align=True)
                sub_row.enabled = camera_props.use_custom_rotation_target
                sub_row.prop(camera_props, "schedule_display_rotation_target", text="")
                
                # --- Location Constraint ---
                col.separator()
                col.label(text="Location Constraint:")
                
                row = col.row(align=True)
                row.prop(camera_props, "use_custom_location_target", text="Use Custom Target")
                
                sub_row = col.row(align=True)
                sub_row.enabled = camera_props.use_custom_location_target
                sub_row.prop(camera_props, "schedule_display_location_target", text="")
            except Exception:
                pass # Fail silently if props aren't available

            info_row = box.row()
            info_row.label(text="Note: Rotation and Location follow the active camera by default.", icon='INFO')
            layout.separator()

        collection = bpy.data.collections.get("Schedule_Display_Texts")
        if not collection or not collection.objects:
            layout.label(text="No display texts found", icon='INFO')
            return
        
        # Define the desired order
        order = ["Schedule_Name", "Schedule_Date", "Schedule_Week", "Schedule_Day_Counter", "Schedule_Progress"]
        
        # Get objects in the desired order, and any others at the end
        sorted_objects = []
        existing_objects = {obj.name: obj for obj in collection.objects}
        
        for name in order:
            if name in existing_objects:
                sorted_objects.append(existing_objects.pop(name))
        
        # Add any remaining objects (e.g., if new ones are added in the future)
        sorted_objects.extend(existing_objects.values())

        for text_obj in sorted_objects:
            box = layout.box()
            row = box.row(align=True)
            text_type = text_obj.data.get("text_type", "unknown")
            icon_map = {"schedule_name": "TEXT", "date": "TIME","week": "COLLAPSEMENU","day_counter": "SORTTIME","progress": "STATUSBAR"}
            row.label(text=text_type.replace("_", " ").title(), icon=icon_map.get(text_type, "FONT_DATA"))
            row.prop(text_obj, "hide_viewport", text="", icon='HIDE_OFF', emboss=False)
            col = box.column(align=True)
            col.prop(text_obj, "location", text="Position")
            try:
                col.prop(text_obj.data, "size", text="Size")
            except Exception:
                pass
            if text_obj.data.materials:
                mat = text_obj.data.materials[0]
                if getattr(mat, "use_nodes", False) and mat.node_tree:
                    bsdf = mat.node_tree.nodes.get("Principled BSDF")
                    if bsdf:
                        col.prop(bsdf.inputs["Base Color"], "default_value", text="Color")
        row = layout.row(align=True)
        row.operator("bim.arrange_schedule_texts", text="Auto-Arrange", icon="ALIGN_TOP")



class BIM_PT_animation_color_schemes(Panel):
    bl_label = "Animation Color Scheme"
    bl_idname = "BIM_PT_animation_color_scheme"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_sequence"

    bl_order = 4
    @classmethod
    def poll(cls, context):
        file = tool.Ifc.get()
        return file and hasattr(file, "schema") and file.schema != "IFC2X3"

    def draw(self, context):
        layout = self.layout
        props = tool.Sequence.get_animation_props()
        row = layout.row()
        row.template_list(
            "UI_UL_list", "animation_color_schemes_list",
            props, "ColorTypes",
            props, "active_ColorType_index"
        )

        col = row.column(align=True)
        col.operator("bim.add_animation_color_schemes", icon='ADD', text="")
        col.operator("bim.remove_animation_color_schemes", icon='REMOVE', text="")
        col.separator()  # Add visual separator
        col.operator("bim.load_animation_color_schemes_set_internal", icon='FILE_TICK', text="")

        if props.ColorTypes and props.active_ColorType_index < len(props.ColorTypes):
            p = props.ColorTypes[props.active_ColorType_index]
            # --- Saved Sets (Internal) ---
            box = layout.box()
            row = box.row(align=True)
            row.operator("bim.save_animation_color_schemes_set_internal", icon='ADD', text="Save Group")
            row.operator("bim.update_active_colortype_group", icon='FILE_REFRESH', text="Update Group")
            row.operator("bim.cleanup_task_colortype_mappings", icon='BRUSH_DATA', text="Clean")
            # REMOVED: Load Set (now it's above, next to the - button)
            row.operator("bim.remove_animation_color_schemes_set_internal", icon='TRASH', text="Remove Group")
            row.operator("bim.import_animation_color_schemes_set_from_file", icon='IMPORT', text="")
            row.operator("bim.export_animation_color_schemes_set_to_file", icon='EXPORT', text="")
            box = layout.box()
            box.prop(p, "name")
            
            # === States to consider with improved documentation === #
            row = layout.row(align=True)
            row.label(text="States to consider:")
            
            # Add explanatory tooltips
            start_row = row.row(align=True)
            start_row.prop(p, "consider_start", text="Start", toggle=True)
            if p.consider_start:
                start_row.label(text="", icon='INFO')

            row.prop(p, "consider_active", text="Active", toggle=True)
            row.prop(p, "consider_end", text="End", toggle=True)
            
            # NEW: Information about consider_start
            if p.consider_start:
                info_box = layout.box()
                info_box.label(text="[INFO]  Start Mode: Elements will maintain start appearance", icon='INFO')
                info_box.label(text="   throughout the entire animation, ignoring task dates.")
                info_box.label(text="   Useful for: existing elements, demolition context.")

            # --- Start Appearance --- #
            start_box = layout.box()
            header = start_box.row(align=True)
            header.label(text="Start Appearance", icon='PLAY')
            col = start_box.column()
            col.enabled = bool(getattr(p, "consider_start", True))
            row = col.row(align=True)
            row.prop(p, "use_start_original_color")
            if not p.use_start_original_color:
                col.prop(p, "start_color")
            col.prop(p, "start_transparency")

            # --- Active / In Progress Appearance --- #
            active_box = layout.box()
            header = active_box.row(align=True)
            header.label(text="Active Appearance", icon='SEQUENCE')
            col = active_box.column()
            col.enabled = bool(getattr(p, "consider_active", True))
            row = col.row(align=True)
            row.prop(p, "use_active_original_color")
            if not p.use_active_original_color:
                if hasattr(p, "in_progress_color"):
                    col.prop(p, "in_progress_color")
                elif hasattr(p, "active_color"):
                    col.prop(p, "active_color")
            col.prop(p, "active_start_transparency")
            col.prop(p, "active_finish_transparency")
            col.prop(p, "active_transparency_interpol")

            # --- End Appearance --- #
            end_box = layout.box()
            header = end_box.row(align=True)
            header.label(text="End Appearance", icon='FF')
            col = end_box.column()
            col.enabled = bool(getattr(p, "consider_end", True))

          
            # Add the new switch to hide at the end
            col.prop(p, "hide_at_end")
            
            # Disable the following options if "Hide When Finished" is enabled
            row_original = col.row(align=True)
            row_original.enabled = not p.hide_at_end
            row_original.prop(p, "use_end_original_color")

            if not p.use_end_original_color:
                row_color = col.row(align=True)
                row_color.enabled = not p.hide_at_end
                row_color.prop(p, "end_color")

            row_transparency = col.row(align=True)
            row_transparency.enabled = not p.hide_at_end
            row_transparency.prop(p, "end_transparency")
