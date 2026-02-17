# Bonsai - OpenBIM Blender Add-on
"""HUD Overlay System for 4D Animation - Refactored Architecture.

This module provides a comprehensive HUD system for displaying schedule information
during 4D animations, now split into specialized components for better maintainability.

Components:
- TextHUD: Displays schedule text information (date, progress, etc.)
- TimelineHUD: Shows timeline bars and date ranges
- LegendHUD: Displays colortype legend and task status

The ScheduleHUD class coordinates all components while maintaining backward compatibility
with the original single-file architecture.
"""

import bpy
import os
import blf
from .text_hud import TextHUD
from .timeline_hud import TimelineHUD  
from .legend_hud import LegendHUD

# Global handler reference - maintained for compatibility
_hud_draw_handler = None
_hud_enabled = False


class ScheduleHUD:
    """Enhanced HUD system coordinating specialized components"""
    
    def __init__(self):
        """Initialize the main HUD coordinator and its specialized components"""
        self.font_id = 0
        self.ensure_valid_font()
        
        # Initialize specialized HUD components
        self.text_hud = TextHUD(self.font_id)
        self.timeline_hud = TimelineHUD(self.font_id)
        self.legend_hud = LegendHUD(self.font_id)
        
        print(f"🎬 ScheduleHUD.__init__: Refactored architecture initialized with font_id={self.font_id}")
    
    def ensure_valid_font(self):
        """Ensures we have a valid font_id for text rendering"""
        try:
            # Try default font first
            test_font_id = 0
            blf.size(test_font_id, 12)
            test_dims = blf.dimensions(test_font_id, "TEST")
            if test_dims[0] > 0 and test_dims[1] > 0:
                self.font_id = test_font_id
                return
            
            # Try loading DroidSans
            try:
                datafiles_dir = bpy.utils.system_resource('DATAFILES')
                font_path = os.path.join(datafiles_dir, "fonts", "droidsans.ttf")
                if os.path.exists(font_path):
                    loaded_id = blf.load(font_path)
                    if loaded_id != -1:
                        blf.size(loaded_id, 12)
                        test_dims = blf.dimensions(loaded_id, "TEST")
                        if test_dims[0] > 0 and test_dims[1] > 0:
                            self.font_id = loaded_id
                            return
            except Exception:
                pass
                
            # Fallback to font ID 0
            self.font_id = 0
            
        except Exception as e:
            print(f"🔤 Error in ensure_valid_font: {e}")
            self.font_id = 0

    def get_active_colortype_legend_data(self, include_hidden=False):
        """Delegate to legend_hud for compatibility with 3D Legend HUD"""
        return self.legend_hud.get_active_colortype_legend_data(include_hidden)
    
    def invalidate_legend_cache(self):
        """Invalidates the legend data cache to force an update"""
        self.legend_hud.invalidate_legend_cache()
    
    def get_camera_props(self):
        """Helper to get camera properties"""
        try:
            import bonsai.tool as tool
            animation_props = tool.Sequence.get_animation_props()
            if hasattr(animation_props, 'camera_orbit') and animation_props.camera_orbit:
                return animation_props.camera_orbit
            return None
        except Exception as e:
            print(f"[ERROR] Error getting camera props: {e}")
            return None

    def get_schedule_data(self):
        """Extracts data from the current schedule"""
        return self._get_schedule_data()
    
    def draw(self):
        """Main drawing method coordinating all HUD components"""
        try:
            if not hasattr(bpy.context, 'region') or not bpy.context.region:
                return
            if bpy.context.space_data.type != 'VIEW_3D':
                return

            # Get settings and data - this is shared across all components
            text_settings, timeline_settings, legend_settings = self.get_hud_settings()

            # Check if any HUD components are enabled - exit early if all disabled
            if not any([text_settings.get('enabled', False),
                       timeline_settings.get('enabled', False),
                       legend_settings.get('enabled', False)]):
                # Don't spam the console - only log once per state change
                if not hasattr(self, '_last_disabled_logged') or not self._last_disabled_logged:
                    print("💤 All HUD components disabled - handler will remain quiet until enabled")
                    self._last_disabled_logged = True
                return

            # Reset the logging flag when HUD is enabled
            self._last_disabled_logged = False

            data = self._get_schedule_data()
            if not data:
                return

            viewport_width = bpy.context.region.width
            viewport_height = bpy.context.region.height

            # Delegate to specialized components
            if text_settings.get('enabled', False):
                self.text_hud.draw(data, text_settings, viewport_width, viewport_height)
            
            if timeline_settings.get('enabled', False):
                self.timeline_hud.draw(data, timeline_settings, viewport_width, viewport_height)
            
            if legend_settings.get('enabled', False):
                print(f"🎨 LEGEND HUD: Drawing with {len(self.legend_hud.get_active_colortype_legend_data())} legend items")
                self.legend_hud.draw(data, legend_settings, viewport_width, viewport_height)
            else:
                print(f"🙈 LEGEND HUD: Disabled - enable_legend_hud={getattr(self.get_camera_props(), 'enable_legend_hud', 'NOT_FOUND')}")

        except Exception as e:
            print(f"Bonsai HUD draw error: {e}")
            import traceback
            traceback.print_exc()

    
    def get_hud_settings(self):
        """Gets complete HUD configuration from properties"""
        try:
            import bonsai.tool as tool
            anim_props = tool.Sequence.get_animation_props()
            camera_props = anim_props.camera_orbit

            # --- TEXT HUD SETTINGS (EXISTING) ---
            text_hud_settings = {
                'enabled': getattr(camera_props, 'enable_text_hud', False),
                'position': getattr(camera_props, 'hud_position', 'TOP_RIGHT'),
                'margin_h': getattr(camera_props, 'hud_margin_horizontal', 0.05),
                'margin_v': getattr(camera_props, 'hud_margin_vertical', 0.05),
                'spacing': getattr(camera_props, 'hud_text_spacing', 0.08),
                'scale': getattr(camera_props, 'hud_scale_factor', 1.0),
                'text_color': getattr(camera_props, 'hud_text_color', (1.0, 1.0, 1.0, 1.0)),
                'background_color': getattr(camera_props, 'hud_background_color', (0.0, 0.0, 0.0, 0.8)),
                'text_alignment': getattr(camera_props, 'hud_text_alignment', 'LEFT'),
                'padding_h': getattr(camera_props, 'hud_padding_horizontal', 10.0),
                'padding_v': getattr(camera_props, 'hud_padding_vertical', 8.0),
                'border_radius': getattr(camera_props, 'hud_border_radius', 5.0),
                'border_width': getattr(camera_props, 'hud_border_width', 0.0),
                'border_color': getattr(camera_props, 'hud_border_color', (1.0, 1.0, 1.0, 0.5)),
                'text_shadow_enabled': getattr(camera_props, 'hud_text_shadow_enabled', True),
                'text_shadow_offset_x': getattr(camera_props, 'hud_text_shadow_offset_x', 1.0),
                'text_shadow_offset_y': getattr(camera_props, 'hud_text_shadow_offset_y', -1.0),
                'text_shadow_color': getattr(camera_props, 'hud_text_shadow_color', (0.0, 0.0, 0.0, 0.8)),
                'background_shadow_enabled': getattr(camera_props, 'hud_background_shadow_enabled', False),
                'background_shadow_offset_x': getattr(camera_props, 'hud_background_shadow_offset_x', 3.0),
                'background_shadow_offset_y': getattr(camera_props, 'hud_background_shadow_offset_y', -3.0),
                'background_shadow_blur': getattr(camera_props, 'hud_background_shadow_blur', 5.0),
                'background_shadow_color': getattr(camera_props, 'hud_background_shadow_color', (0.0, 0.0, 0.0, 0.6)),
                'font_weight': getattr(camera_props, 'hud_font_weight', 'NORMAL'),
                'letter_spacing': getattr(camera_props, 'hud_letter_spacing', 0.0),
                'background_gradient_enabled': getattr(camera_props, 'hud_background_gradient_enabled', False),
                'background_gradient_color': getattr(camera_props, 'hud_background_gradient_color', (0.1, 0.1, 0.1, 0.9)),
                'gradient_direction': getattr(camera_props, 'hud_gradient_direction', 'VERTICAL'),
                # Visibility flags
                'hud_show_date': getattr(camera_props, 'hud_show_date', True),
                'hud_show_week': getattr(camera_props, 'hud_show_week', True),
                'hud_show_day': getattr(camera_props, 'hud_show_day', True),
                'hud_show_progress': getattr(camera_props, 'hud_show_progress', True),
            }

            # --- CHECK FOR SNAPSHOT MODE ---
            # Detect snapshot mode to auto-enable Timeline HUD
            work_props = tool.Sequence.get_work_schedule_props()
            snapshot_date = getattr(work_props, 'visualisation_start', None)
            is_snapshot_ui_active = getattr(work_props, 'should_show_snapshot_ui', False)
            scene_snapshot_mode = hasattr(bpy.context.scene, 'get') and bpy.context.scene.get("is_snapshot_mode", False)
            
            is_snapshot_mode_active = (
                is_snapshot_ui_active and
                snapshot_date and snapshot_date.strip() not in ('', '-')
            ) or scene_snapshot_mode
            
            # Only log snapshot detection on state changes
            current_snapshot_state = (is_snapshot_ui_active, scene_snapshot_mode, is_snapshot_mode_active)
            if not hasattr(self, '_last_snapshot_state') or self._last_snapshot_state != current_snapshot_state:
                print(f"🔍 SNAPSHOT DETECTION: is_snapshot_ui_active={is_snapshot_ui_active}, scene_snapshot_mode={scene_snapshot_mode}")
                print(f"🔍 SNAPSHOT DETECTION: snapshot_date='{snapshot_date}', is_snapshot_mode_active={is_snapshot_mode_active}")
                self._last_snapshot_state = current_snapshot_state
            
            # --- TIMELINE HUD SETTINGS (NEW) ---
            # Enable Timeline HUD automatically for snapshots (following v90 behavior)
            timeline_enabled_setting = getattr(camera_props, 'enable_timeline_hud', False)
                
            timeline_hud_settings = {
                'enabled': timeline_enabled_setting,
                'locked': getattr(camera_props, 'timeline_hud_locked', True),
                'manual_x': getattr(camera_props, 'timeline_hud_manual_x', 0.0),
                'manual_y': getattr(camera_props, 'timeline_hud_manual_y', 0.0),
                'position': getattr(camera_props, 'timeline_hud_position', 'BOTTOM'),
                'margin_h': getattr(camera_props, 'timeline_hud_margin_horizontal', 0.0),
                'margin_v': getattr(camera_props, 'timeline_hud_margin_vertical', 0.05),
                'zoom_level': getattr(camera_props, 'timeline_hud_zoom_level', 'MONTHS'),
                'height': getattr(camera_props, 'timeline_hud_height', 30.0),
                'width': getattr(camera_props, 'timeline_hud_width', 0.8),
                'border_radius': getattr(camera_props, 'timeline_hud_border_radius', 10.0),
                'show_progress_bar': getattr(camera_props, 'timeline_hud_show_progress_bar', True),
                'color_inactive_range': getattr(camera_props, 'timeline_hud_color_inactive_range', (0.588, 0.953, 0.745, 0.3)),
                'color_active_range': getattr(camera_props, 'timeline_hud_color_active_range', (0.588, 0.953, 0.745, 0.5)),
                'color_progress': getattr(camera_props, 'timeline_hud_color_progress', (0.122, 0.663, 0.976, 0.102)),  # #1FA9F91A
            'color_indicator': getattr(camera_props, 'timeline_hud_color_indicator', (1.0, 0.906, 0.204, 1.0)), # #FFE734FF
                'color_text': getattr(camera_props, 'timeline_hud_color_text', (1.0, 1.0, 1.0, 1.0)),
            }
            
            # --- LEGEND HUD SETTINGS (NEW) ---
            legend_enabled = getattr(camera_props, 'enable_legend_hud', False)

            # Only log legend debug info on state changes
            if not hasattr(self, '_last_legend_enabled') or self._last_legend_enabled != legend_enabled:
                print(f"🔍 LEGEND DEBUG: enable_legend_hud property = {legend_enabled}")
                self._last_legend_enabled = legend_enabled
            
            legend_hud_settings = {
                'enabled': legend_enabled,
                'position': getattr(camera_props, 'legend_hud_position', 'TOP_LEFT'),
                'margin_h': getattr(camera_props, 'legend_hud_margin_horizontal', 0.05),
                'margin_v': getattr(camera_props, 'legend_hud_margin_vertical', 0.5),
                'orientation': getattr(camera_props, 'legend_hud_orientation', 'VERTICAL'),
                'scale': getattr(camera_props, 'legend_hud_scale', 1.0),
                'background_color': getattr(camera_props, 'legend_hud_background_color', (0.0, 0.0, 0.0, 0.8)),
                'border_radius': getattr(camera_props, 'legend_hud_border_radius', 5.0),
                'padding_h': getattr(camera_props, 'legend_hud_padding_horizontal', 12.0),
                'padding_v': getattr(camera_props, 'legend_hud_padding_vertical', 8.0),
                'item_spacing': getattr(camera_props, 'legend_hud_item_spacing', 8.0),
                'text_color': getattr(camera_props, 'legend_hud_text_color', (1.0, 1.0, 1.0, 1.0)),
                'show_title': getattr(camera_props, 'legend_hud_show_title', True),
                'title_text': getattr(camera_props, 'legend_hud_title_text', 'Legend'),
                'title_color': getattr(camera_props, 'legend_hud_title_color', (1.0, 1.0, 1.0, 1.0)),
                'color_indicator_size': getattr(camera_props, 'legend_hud_color_indicator_size', 12.0),
                'text_shadow_enabled': getattr(camera_props, 'legend_hud_text_shadow_enabled', True),
                'text_shadow_color': getattr(camera_props, 'legend_hud_text_shadow_color', (0.0, 0.0, 0.0, 0.8)),
                'text_shadow_offset_x': getattr(camera_props, 'legend_hud_text_shadow_offset_x', 1.0),
                'text_shadow_offset_y': getattr(camera_props, 'legend_hud_text_shadow_offset_y', -1.0),
                'selected_colortypes': getattr(camera_props, 'legend_hud_selected_colortypes', set()),
                'auto_scale': getattr(camera_props, 'legend_hud_auto_scale', True),
                'max_width': getattr(camera_props, 'legend_hud_max_width', 0.3),  # 30% of viewport width
                # Column visibility settings
                'show_start_column': getattr(camera_props, 'legend_hud_show_start_column', False),
                'show_active_column': getattr(camera_props, 'legend_hud_show_active_column', True),
                'show_end_column': getattr(camera_props, 'legend_hud_show_end_column', False),
                'show_start_title': getattr(camera_props, 'legend_hud_show_start_title', False),
                'show_active_title': getattr(camera_props, 'legend_hud_show_active_title', False),
                'show_end_title': getattr(camera_props, 'legend_hud_show_end_title', False),
                'column_spacing': getattr(camera_props, 'legend_hud_column_spacing', 16.0)
            }
            
            return text_hud_settings, timeline_hud_settings, legend_hud_settings

        except Exception as e:
            print(f"Error getting HUD settings: {e}")
            return {}, {}, {}

    def _get_schedule_data(self):
        """Extracts data from the current schedule - COMPLETE v60 IMPLEMENTATION"""
        try:
            import bonsai.tool as tool

            # Get properties
            work_props = tool.Sequence.get_work_schedule_props()
            anim_props = tool.Sequence.get_animation_props()

            # CRITICAL: Check if synchronization mode is enabled
            # Visualization dates (user-selected range)
            viz_start = tool.Sequence.get_start_date()
            viz_finish = tool.Sequence.get_finish_date()
            print(f"📅 HUD: Using visualization range: {viz_start} to {viz_finish}")
            
              # full_schedule_start and full_schedule_end will ALWAYS represent the complete unified range for the HUD background.
            full_schedule_start, full_schedule_end = None, None
            try:
                active_schedule = tool.Sequence.get_active_work_schedule()
                if active_schedule:
                    # We always get the unified range for the timeline background.
                    unified_start, unified_end = self._get_unified_schedule_range(active_schedule)
                    if unified_start and unified_end:
                        full_schedule_start, full_schedule_end = unified_start, unified_end
                        print(f"📊 HUD: Using unified range for the time bar: {full_schedule_start.strftime('%Y-%m-%d')} -> {full_schedule_end.strftime('%Y-%m-%d')}")

                # Fallback if the unified range could not be obtained.
                if not (full_schedule_start and full_schedule_end):
                    full_schedule_start, full_schedule_end = viz_start, viz_finish
                    if full_schedule_start:
                         print(f"[WARNING] HUD: Using visualization range as fallback for timeline bar.")

            except Exception as e:
                print(f"[WARNING] Error getting unified schedule range: {e}")
                # Final fallback if everything fails
                full_schedule_start, full_schedule_end = viz_start, viz_finish
          
           
            # Use multiple sources to reliably determine snapshot mode
            snapshot_date = getattr(work_props, 'visualisation_start', None)
            is_snapshot_ui_active = getattr(work_props, 'should_show_snapshot_ui', False)
            is_snapshot_flag_active = bpy.context.scene.get("is_snapshot_mode", False)
            
            is_snapshot_mode = (
                (is_snapshot_ui_active and snapshot_date and snapshot_date.strip() not in ('', '-')) or
                is_snapshot_flag_active
            )
            
            if is_snapshot_mode:
                print(f"🎬 SNAPSHOT MODE: Using date {snapshot_date}")
            else:
                print(f"🎞️ ANIMATION MODE: Range {viz_start} to {viz_finish}")
                
            # NEW: Snapshot support - use specific date
            if is_snapshot_mode:
                # In Snapshot mode, ALWAYS use the unified range for the Timeline HUD
                if snapshot_date and snapshot_date.strip() not in ('', '-'):
                    try:
                        from datetime import datetime
                        current_date = datetime.fromisoformat(snapshot_date.replace('Z', '+00:00'))
                        
                        # CRITICAL: For snapshots, ALWAYS use unified range for Timeline HUD
                        if active_schedule:
                            unified_start, unified_end = self._get_unified_schedule_range(active_schedule)
                            if unified_start and unified_end:
                                print(f"📊 SNAPSHOT: Using unified range {unified_start.strftime('%Y-%m-%d')} → {unified_end.strftime('%Y-%m-%d')}")
                                full_schedule_start, full_schedule_end = unified_start, unified_end
                            else:
                                print("[WARNING] SNAPSHOT: No unified range found, using fallback")
                        
                        if full_schedule_start and full_schedule_end:
                
                            # Convert to dates for precise calculations
                            cd_d = current_date.date()
                            fss_d = full_schedule_start.date()
                            fse_d = full_schedule_end.date()

                            delta_days = (cd_d - fss_d).days
                            
                            if cd_d < fss_d:
                                day_from_schedule = 0
                                week_number = 0
                                progress_pct = 0
                            else:
                                day_from_schedule = max(1, delta_days + 1)
                                week_number = max(1, (delta_days // 7) + 1)
                                total_schedule_days = (fse_d - fss_d).days
                                
                                if delta_days <= 0:
                                    progress_pct = 0
                                elif cd_d >= fse_d or total_schedule_days <= 0:
                                    progress_pct = 100
                                else:
                                    progress_pct = (delta_days / total_schedule_days) * 100
                                    progress_pct = round(progress_pct)

                            total_days_full_schedule = (fse_d - fss_d).days + 1

                            print("🎬 SNAPSHOT MODE: Metrics calculated directly.")
                            return {
                                'full_schedule_start': full_schedule_start,
                                'full_schedule_end': full_schedule_end,
                                'current_date': current_date,
                                'start_date': current_date,
                                'finish_date': current_date,
                                'current_frame': -1,
                                'total_days': total_days_full_schedule,
                                'elapsed_days': day_from_schedule,
                                'week_number': int(max(0, week_number)),
                                'progress_pct': progress_pct,
                                'day_of_week': current_date.strftime('%A'),
                                'schedule_name': active_schedule.Name if active_schedule else 'No Schedule',
                                'is_snapshot': True,
                            }
                        # Fallback: ensure unified range is always available for snapshots
                        if not full_schedule_start or not full_schedule_end:
                            print("[WARNING] SNAPSHOT: No unified range found, calculating fallback range")
                            # Use current snapshot date as both start and end if no range is available
                            full_schedule_start = current_date
                            full_schedule_end = current_date
                            
                        print("🎬 SNAPSHOT MODE: Animation disabled for HUD Schedule and Timeline (fallback)")
                        return {
                            'full_schedule_start': full_schedule_start,
                            'full_schedule_end': full_schedule_end,
                            'current_date': current_date,
                            'start_date': current_date,
                            'finish_date': current_date,
                            'current_frame': -1,  # FIXED: Disable frame animation for snapshots
                            'total_days': 1,
                            'elapsed_days': 1,
                            'week_number': 1,
                            'progress_pct': 100,
                            'day_of_week': current_date.strftime('%A'),
                            'schedule_name': active_schedule.Name if active_schedule else 'No Schedule',
                            'is_snapshot': True,
                        }
                    except Exception as e:
                        print(f"[ERROR] Error processing snapshot: {e}")
    
            # --- NORMAL ANIMATION LOGIC (if not snapshot) ---
            scene = bpy.context.scene
            current_frame = scene.frame_current
            start_frame = scene.frame_start
            end_frame = scene.frame_end

            # 1. CALCULATE THE CURRENT ANIMATION DATE (CURRENT_DATE)
            # It is based on the visualization range you manually selected (Start Date and Finish Date in the UI).
            if end_frame > start_frame and viz_start and viz_finish:
                progress = (current_frame - start_frame) / (end_frame - start_frame)
                progress = max(0.0, min(1.0, progress))
                duration = viz_finish - viz_start
                current_date = viz_start + (duration * progress)
            elif viz_start:
                current_date = viz_start
            else:
                from datetime import datetime
                current_date = datetime.now()
                print("[WARNING] No visualization dates configured, using current date")

            
            day_from_schedule = 0
            week_number = 0
            progress_pct = 0
            total_days_in_schedule = (full_schedule_end - full_schedule_start).days + 1 if full_schedule_start and full_schedule_end else 1

            if active_schedule:
                # 2. GET THE REAL DATE RANGE OF THE ACTIVE SCHEDULE TYPE (Schedule, Actual, etc.)
                #    This will be our absolute reference for the counters.
                date_range = tool.Sequence.guess_date_range(active_schedule)
                if date_range is not None:
                    reference_start, reference_finish = date_range
                else:
                    reference_start, reference_finish = None, None

                if reference_start and reference_finish:
                    print(f"🎯 HUD Counters: Using absolute reference range {reference_start.strftime('%Y-%m-%d')} to {reference_finish.strftime('%Y-%m-%d')}")
                    
                    cd_d = current_date.date()
                    ref_start_d = reference_start.date()
                    ref_finish_d = reference_finish.date()

                    # 3. CALCULATE PROGRESS, DAY, AND WEEK RELATIVE TO THE ABSOLUTE REFERENCE
                    delta_days = (cd_d - ref_start_d).days

                    if cd_d < ref_start_d:
                        # The animation is at a date before the start of the reference schedule.
                        day_from_schedule = 0
                        week_number = 0
                        progress_pct = 0
                    else:
                        # The animation has reached or passed the reference start date.
                        day_from_schedule = max(1, delta_days + 1)
                        week_number = max(1, (delta_days // 7) + 1)

                        total_reference_days = (ref_finish_d - ref_start_d).days
                        
                        if delta_days < 0:
                            progress_pct = 0
                        elif cd_d >= ref_finish_d or total_reference_days <= 0:
                            progress_pct = 100
                        else:
                            # PROGRESS IS CALCULATED OVER THE TOTAL DURATION OF THE REFERENCE SCHEDULE
                            progress_pct = (delta_days / total_reference_days) * 100
                            progress_pct = round(progress_pct)
                    
                    total_days_in_schedule = (ref_finish_d - ref_start_d).days + 1

                    return {
                        'full_schedule_start': full_schedule_start,
                        'full_schedule_end': full_schedule_end,
                        'current_date': current_date,
                        'start_date': viz_start,
                        'finish_date': viz_finish,
                        'current_frame': current_frame,
                        'total_days': total_days_in_schedule,
                        'elapsed_days': day_from_schedule,
                        'week_number': int(max(0, week_number)),
                        'progress_pct': progress_pct,
                        'day_of_week': current_date.strftime('%A'),
                        'schedule_name': active_schedule.Name if active_schedule else 'No Schedule',
                        'is_snapshot': False,
                    }
            else:
                print(f"[WARNING] Sin fechas de schedule completo, usando fallback")

                # FALLBACK: Use logic based only on selected range
                if viz_start and viz_finish:
                    viz_start_d = viz_start.date()
                    viz_finish_d = viz_finish.date()
                    
                    # Calculate total_days and elapsed_days consistently
                    total_days = (viz_finish_d - viz_start_d).days + 1
                    elapsed_days = (current_date - viz_start).days + 1
                    elapsed_days = max(1, min(total_days, elapsed_days))
                else:
                    # No range dates, use default values
                    total_days = 1
                    elapsed_days = 1
                    print("[WARNING] No selected range dates, using default values")

                # Calculate week_number and progress_pct
                if end_frame > start_frame:
                    frame_progress = (current_frame - start_frame) / (end_frame - start_frame)
                    frame_progress = max(0.0, min(1.0, frame_progress))
                    
                    # WEEK: from the start of the range (starting at W1)
                    # Use elapsed_days for consistency
                    week_number = max(1, ((elapsed_days - 1) // 7) + 1)
                    
                    # PROGRESS: based on frame progress
                    progress_pct = round(frame_progress * 100)
                    progress_pct = max(0, min(100, progress_pct))
                else:
                    # If there is no animation, we are on day 1, week 1, 0% progress
                    week_number = 1
                    progress_pct = 0
                
                return {
                    'full_schedule_start': full_schedule_start,
                    'full_schedule_end': full_schedule_end,
                    'current_date': current_date,
                    'start_date': viz_start,
                    'finish_date': viz_finish,
                    'current_frame': current_frame,
                    'total_days': total_days,
                    'elapsed_days': elapsed_days,
                    'week_number': int(max(0, week_number)),
                    'progress_pct': progress_pct,
                    'day_of_week': current_date.strftime('%A'),
                    'schedule_name': active_schedule.Name if active_schedule else 'No Schedule',
                    'is_snapshot': False, # Not a snapshot if we reach here
                }
        except Exception as e:
            print(f"Error getting schedule data: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _get_unified_schedule_range(self, work_schedule):
        """
        Calculate the unified date range by analyzing ALL 4 schedule types
        Returns the earliest start and latest finish across all types
        Used for Timeline HUD snapshots and unified timeline display
        """
        from datetime import datetime
        import ifcopenshell.util.sequence
        
        if not work_schedule:
            return None, None
        
        all_starts = []
        all_finishes = []
        
        # Check all schedule types: SCHEDULE, ACTUAL, EARLY, LATE
        for schedule_type in ["SCHEDULE", "ACTUAL", "EARLY", "LATE"]:
            start_attr = f"{schedule_type.capitalize()}Start"
            finish_attr = f"{schedule_type.capitalize()}Finish"
            
            print(f"🔍 UNIFIED HUD: Analyzing {schedule_type} -> {start_attr}/{finish_attr}")
            
            # Get all tasks from schedule
            root_tasks = ifcopenshell.util.sequence.get_root_tasks(work_schedule)
            
            def get_all_tasks_recursive(tasks):
                result = []
                for task in tasks:
                    result.append(task)
                    nested = ifcopenshell.util.sequence.get_nested_tasks(task)
                    if nested:
                        result.extend(get_all_tasks_recursive(nested))
                return result
            
            all_tasks = get_all_tasks_recursive(root_tasks)
            
            for task in all_tasks:
                start_date = ifcopenshell.util.sequence.derive_date(task, start_attr, is_earliest=True)
                if start_date:
                    all_starts.append(start_date)
                
                finish_date = ifcopenshell.util.sequence.derive_date(task, finish_attr, is_latest=True)
                if finish_date:
                    all_finishes.append(finish_date)
        
        if not all_starts or not all_finishes:
            print("[ERROR] UNIFIED HUD: No valid dates found across all schedule types")
            return None, None
        
        unified_start = min(all_starts)
        unified_finish = max(all_finishes)
        
        return unified_start, unified_finish
    
    def _is_unified_range(self, work_schedule, viz_start, viz_finish):
        """
        Check if the current visualization range spans multiple schedule types,
        which indicates it's a unified range set by Guess button.
        """
        try:
            # Get the unified range
            unified_start, unified_end = self._get_unified_schedule_range(work_schedule)
            
            if not unified_start or not unified_end:
                return False
            
            # Check if viz range is approximately the same as unified range
            # (allowing for small differences due to time formatting)
            start_match = abs((viz_start - unified_start).total_seconds()) < 86400  # 1 day tolerance
            end_match = abs((viz_finish - unified_end).total_seconds()) < 86400
            
            return start_match and end_match
            
        except Exception as e:
            print(f"[WARNING] Error checking unified range: {e}")
            return False

    def calculate_position(self, viewport_width, viewport_height, settings):
        """Calculates the HUD position in pixels"""
        margin_h = int(viewport_width * settings['margin_h'])
        margin_v = int(viewport_height * settings['margin_v'])

        position = settings['position']

        if position == 'TOP_RIGHT':
            x = viewport_width - margin_h
            y = viewport_height - margin_v
            align_x = 'RIGHT'
            align_y = 'TOP'
        elif position == 'TOP_LEFT':
            x = margin_h
            y = viewport_height - margin_v
            align_x = 'LEFT'
            align_y = 'TOP'
        elif position == 'BOTTOM_RIGHT':
            x = viewport_width - margin_h
            y = margin_v
            align_x = 'RIGHT'
            align_y = 'BOTTOM'
        else:  # BOTTOM_LEFT
            x = margin_h
            y = margin_v
            align_x = 'LEFT'
            align_y = 'BOTTOM'

        return x, y, align_x, align_y

    def format_text_lines(self, data):
        """Formats the HUD text lines"""
        if not data:
            return ["No Schedule Data"]

        lines = [
            f"{data['current_date'].strftime('%d %B %Y')}",
            f"Week {data['week_number']} - {data['day_of_week']}",
            f"Day {data['elapsed_days']} of {data['total_days']}",
            f"Progress: {data['progress_pct']}%",
        ]

        return lines

    def draw_background_with_effects(self, x, y, width, height, align_x, align_y, settings):
        """Draws background with enhanced effects and coordinates. `width` and `height` should be ONLY for the text block (without padding)."""
        """Draws background with enhanced effects and corrected coordinates. `width` and `height` should be ONLY for the text block (without padding)."""
        padding_h = settings.get('padding_h', 10.0)
        padding_v = settings.get('padding_v', 8.0)

        # Final width and height including padding
        final_width = width + (padding_h * 2)
        final_height = height + (padding_v * 2)

        # Calculate background position according to alignment
        if align_x == 'RIGHT':
            bg_x = x - final_width
        elif align_x == 'CENTER':
            bg_x = x - (final_width / 2)
        else:  # LEFT
            bg_x = x

        if align_y == 'TOP':
            bg_y = y - final_height
        else:  # BOTTOM
            bg_y = y

        # Draw background shadow if enabled
        if settings.get('background_shadow_enabled', False):
            shadow_offset_x = settings.get('background_shadow_offset_x', 3.0)
            shadow_offset_y = settings.get('background_shadow_offset_y', -3.0)
            shadow_color = settings.get('background_shadow_color', (0.0, 0.0, 0.0, 0.6))

            shadow_vertices = [
                (bg_x + shadow_offset_x, bg_y + shadow_offset_y),
                (bg_x + final_width + shadow_offset_x, bg_y + shadow_offset_y),
                (bg_x + final_width + shadow_offset_x, bg_y + final_height + shadow_offset_y),
                (bg_x + shadow_offset_x, bg_y + final_height + shadow_offset_y),
            ]

            shadow_indices = [(0, 1, 2), (2, 3, 0)]

            shader = gpu.shader.from_builtin('UNIFORM_COLOR')
            batch = batch_for_shader(shader, 'TRIS', {"pos": shadow_vertices}, indices=shadow_indices)

            gpu.state.blend_set('ALPHA')
            shader.bind()
            shader.uniform_float("color", shadow_color)
            batch.draw(shader)

        # Create main background vertices
        vertices = [
            (bg_x, bg_y),
            (bg_x + final_width, bg_y),
            (bg_x + final_width, bg_y + final_height),
            (bg_x, bg_y + final_height),
        ]

        indices = [(0, 1, 2), (2, 3, 0)]

        # Draw background with rounded corners if enabled
        border_radius = settings.get('border_radius', 0.0)
        background_color = settings.get('background_color', (0.0, 0.0, 0.0, 0.8))
        
        if border_radius > 0:
            # Use rounded rectangle
            if settings.get('background_gradient_enabled', False):
                # For gradients, use average color as an approximation
                gradient_color = settings.get('background_gradient_color', (0.1, 0.1, 0.1, 0.9))
                avg_color = tuple((c1 + c2) / 2 for c1, c2 in zip(background_color, gradient_color))
                self.draw_rounded_rect(bg_x, bg_y, final_width, final_height, avg_color, border_radius)
            else:
                self.draw_rounded_rect(bg_x, bg_y, final_width, final_height, background_color, border_radius)
        else:
            # Use original method
            if settings.get('background_gradient_enabled', False):
                self.draw_gradient_background(vertices, indices, settings)
            else:
                shader = gpu.shader.from_builtin('UNIFORM_COLOR')
                batch = batch_for_shader(shader, 'TRIS', {"pos": vertices}, indices=indices)

                gpu.state.blend_set('ALPHA')
                shader.bind()
                shader.uniform_float("color", background_color)
                batch.draw(shader)

        # Draw border if enabled
        border_width = settings.get('border_width', 0.0)
        if border_width > 0:
            self.draw_border(
                bg_x, bg_y, final_width, final_height, border_width,
                settings.get('border_color', (1.0, 1.0, 1.0, 0.5)),
            )

        gpu.state.blend_set('NONE')

    def draw_gradient_background(self, vertices, indices, settings):
        """Draws a background with a gradient (simplified)"""
        try:
            color1 = settings.get('background_color', (0.0, 0.0, 0.0, 0.8))
            color2 = settings.get('background_gradient_color', (0.1, 0.1, 0.1, 0.9))

            # To simplify, use average color
            avg_color = tuple((c1 + c2) / 2 for c1, c2 in zip(color1, color2))

            shader = gpu.shader.from_builtin('UNIFORM_COLOR')
            batch = batch_for_shader(shader, 'TRIS', {"pos": vertices}, indices=indices)

            gpu.state.blend_set('ALPHA')
            shader.bind()
            shader.uniform_float("color", avg_color)
            batch.draw(shader)
        except Exception as e:
            print(f"Error drawing gradient: {e}")
            # Fallback to solid color
            shader = gpu.shader.from_builtin('UNIFORM_COLOR')
            batch = batch_for_shader(shader, 'TRIS', {"pos": vertices}, indices=indices)
            gpu.state.blend_set('ALPHA')
            shader.bind()
            shader.uniform_float("color", settings.get('background_color', (0.0, 0.0, 0.0, 0.8)))
            batch.draw(shader)

    def draw_border(self, x, y, width, height, border_width, border_color):
        """Draws a border around the rectangle"""
        try:
            # Border lines
            border_lines = [
                # Top
                [(x, y + height), (x + width, y + height)],
                # Bottom
                [(x, y), (x + width, y)],
                # Left
                [(x, y), (x, y + height)],
                # Right
                [(x + width, y), (x + width, y + height)],
            ]

            gpu.state.blend_set('ALPHA')
            gpu.state.line_width_set(border_width)

            shader = gpu.shader.from_builtin('UNIFORM_COLOR')
            for line in border_lines:
                batch = batch_for_shader(shader, 'LINES', {"pos": line})
                shader.bind()
                shader.uniform_float("color", border_color)
                batch.draw(shader)

            gpu.state.line_width_set(1.0)  # Reset line width
        except Exception as e:
            print(f"Error drawing border: {e}")

    def draw_text_with_shadow(self, text, x, y, settings, align_x='LEFT'):
        """Draws text with shadow and improved alignment using the correct baseline"""
        """Draws text with shadow and improved alignment using the correct baseline"""
        # Configure font
        font_size = int(settings.get('scale', 1.0) * 16)
        blf.size(self.font_id, font_size)

        # Calculate text width for alignment
        text_width, text_height = blf.dimensions(self.font_id, text)

        # Adjust X position according to alignment
        text_alignment = settings.get('text_alignment', 'LEFT')
        if text_alignment == 'RIGHT' or align_x == 'RIGHT':
            text_x = x - text_width
        elif text_alignment == 'CENTER' or align_x == 'CENTER':
            text_x = x - (text_width / 2)
        else:  # LEFT
            text_x = x

        # Y comes as baseline
        text_y = y

        # Draw text shadow if enabled
        if settings.get('text_shadow_enabled', True):
            shadow_offset_x = settings.get('text_shadow_offset_x', 1.0)
            shadow_offset_y = settings.get('text_shadow_offset_y', -1.0)
            shadow_color = settings.get('text_shadow_color', (0.0, 0.0, 0.0, 0.8))

            blf.position(self.font_id, text_x + shadow_offset_x, text_y + shadow_offset_y, 0)
            blf.color(self.font_id, *shadow_color)
            blf.draw(self.font_id, text)

        # Draw main text
        text_color = settings.get('text_color', (1.0, 1.0, 1.0, 1.0))
        blf.position(self.font_id, text_x, text_y, 0)
        blf.color(self.font_id, *text_color)
        blf.draw(self.font_id, text)

        return text_width, text_height

    def draw_rounded_rect(self, x, y, width, height, color, radius):
        """Draw a rounded rectangle using GPU primitives"""
        try:
            import math
            # Simplified rounded rectangle - just draw regular rectangle for now
            # Full implementation would require complex geometry generation
            vertices = [
                (x, y),
                (x + width, y),
                (x + width, y + height),
                (x, y + height),
            ]
            indices = [(0, 1, 2), (2, 3, 0)]
            
            shader = gpu.shader.from_builtin('UNIFORM_COLOR')
            batch = batch_for_shader(shader, 'TRIS', {"pos": vertices}, indices=indices)

            gpu.state.blend_set('ALPHA')
            shader.bind()
            shader.uniform_float("color", color)
            batch.draw(shader)
            
        except Exception as e:
            print(f"Error drawing rounded rect: {e}")

    def _get_unified_schedule_range(self, work_schedule):
        """
        Calculates the unified date range by analyzing ALL 4 schedule types. Returns the earliest start and latest end among them.
        """
        from datetime import datetime
        import ifcopenshell.util.sequence

        if not work_schedule:
            return None, None

        all_starts = []
        all_finishes = []

        # Analyze all schedule types: SCHEDULE, ACTUAL, EARLY, LATE
        for schedule_type in ["SCHEDULE", "ACTUAL", "EARLY", "LATE"]:
            start_attr = f"{schedule_type.capitalize()}Start"
            finish_attr = f"{schedule_type.capitalize()}Finish"

            root_tasks = ifcopenshell.util.sequence.get_root_tasks(work_schedule)

            def get_all_tasks_recursive(tasks):
                result = []
                for task in tasks:
                    result.append(task)
                    nested = ifcopenshell.util.sequence.get_nested_tasks(task)
                    if nested:
                        result.extend(get_all_tasks_recursive(nested))
                return result

            all_tasks = get_all_tasks_recursive(root_tasks)

            for task in all_tasks:
                start_date = ifcopenshell.util.sequence.derive_date(task, start_attr, is_earliest=True)
                if start_date:
                    all_starts.append(start_date)

                finish_date = ifcopenshell.util.sequence.derive_date(task, finish_attr, is_latest=True)
                if finish_date:
                    all_finishes.append(finish_date)

        if not all_starts or not all_finishes:
            return None, None

        unified_start = min(all_starts)
        unified_finish = max(all_finishes)

        return unified_start, unified_finish
        


def draw_hud_callback():
    """Callback that runs every frame to draw the HUD"""
    try:
        # Quick performance check - if no HUD components were enabled for several frames,
        # temporarily reduce the frequency of checks to save performance
        if hasattr(schedule_hud, '_consecutive_disabled_calls'):
            schedule_hud._consecutive_disabled_calls += 1

            # Skip every 10 calls if HUD has been disabled for a while
            if schedule_hud._consecutive_disabled_calls > 30 and schedule_hud._consecutive_disabled_calls % 10 != 0:
                return
        else:
            schedule_hud._consecutive_disabled_calls = 0

        schedule_hud.draw()

        # Reset counter if HUD is active
        if hasattr(schedule_hud, '_last_disabled_logged') and not schedule_hud._last_disabled_logged:
            schedule_hud._consecutive_disabled_calls = 0

        # Periodically check if handler should be cleaned up
        if hasattr(schedule_hud, '_consecutive_disabled_calls') and schedule_hud._consecutive_disabled_calls % 100 == 0:
            cleanup_idle_hud_handler()

    except Exception as e:
        print(f"🔴 HUD callback error: {e}")
        import traceback
        traceback.print_exc()


# Global instance of the HUD
schedule_hud = ScheduleHUD()


def register_hud_handler():
    """Registers the HUD drawing handler"""
    global _hud_draw_handler, _hud_enabled

    if _hud_draw_handler is not None:
        unregister_hud_handler()

    try:
        _hud_draw_handler = bpy.types.SpaceView3D.draw_handler_add(
            draw_hud_callback, (), 'WINDOW', 'POST_PIXEL'
        )
        _hud_enabled = True

        # Force immediate redraw
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()

    except Exception as e:
        print(f"🔴 Error registering HUD handler: {e}")
        _hud_enabled = False


def unregister_hud_handler():
    """Unregisters the HUD drawing handler"""
    global _hud_draw_handler, _hud_enabled

    if _hud_draw_handler is not None:
        try:
            bpy.types.SpaceView3D.draw_handler_remove(_hud_draw_handler, 'WINDOW')
        except Exception as e:
            print(f"🔴 Error removing HUD handler: {e}")
        _hud_draw_handler = None

    _hud_enabled = False


def is_hud_enabled():
    """Checks if the HUD is active"""
    return _hud_enabled


def ensure_hud_handlers():
    """Ensures that all handlers are registered correctly"""
    global _hud_enabled
    if not _hud_enabled:
        register_hud_handler()

def cleanup_idle_hud_handler():
    """Clean up HUD handler if it's been idle for too long to save performance"""
    global schedule_hud, _hud_enabled

    if hasattr(schedule_hud, '_consecutive_disabled_calls'):
        # If HUD has been disabled for more than 300 calls (~10 seconds at 30fps), unregister it
        if schedule_hud._consecutive_disabled_calls > 300:
            print("💤 HUD handler has been idle for too long, unregistering to save performance")
            unregister_hud_handler()
            schedule_hud._consecutive_disabled_calls = 0

def auto_manage_hud_handler():
    """Automatically manage HUD handler based on whether any components are enabled"""
    try:
        import bonsai.tool as tool
        anim_props = tool.Sequence.get_animation_props()
        camera_props = anim_props.camera_orbit

        any_hud_enabled = (
            getattr(camera_props, 'enable_text_hud', False) or
            getattr(camera_props, 'enable_timeline_hud', False) or
            getattr(camera_props, 'enable_legend_hud', False)
        )

        if any_hud_enabled and not _hud_enabled:
            print("🔄 HUD components enabled, registering handler")
            register_hud_handler()
        elif not any_hud_enabled and _hud_enabled:
            # Don't immediately unregister - let cleanup_idle_hud_handler handle it
            pass

    except Exception as e:
        print(f"[WARNING] Error in auto HUD management: {e}")



def refresh_hud():
    """Forces a viewport refresh to update the HUD"""
    try:
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()
        print("🔄 HUD refresh requested")
    except Exception as e:
        print(f"🔴 HUD refresh error: {e}")


def debug_hud_state():
    """Diagnostic function to debug the HUD state"""
    print("\\n🔍 === HUD DEBUG STATE ===")
    print(f"Handler enabled: {_hud_enabled}")
    print(f"Handler object: {_hud_draw_handler}")

    try:
        import bonsai.tool as tool
        anim_props = tool.Sequence.get_animation_props()
        camera_props = anim_props.camera_orbit
        hud_enabled = getattr(camera_props, 'enable_text_hud', False)
        print(f"Property enable_text_hud: {hud_enabled}")

    except Exception as e:
        print(f"Error in debug: {e}")

    print("=== END DEBUG ===\\n")


# Compatibility functions for the original single-file API
def draw_current_date_indicator(x, y, height, color):
    """Draws a current date indicator line"""
    try:
        import gpu
        from gpu_extras.batch import batch_for_shader
        
        vertices = [(x, y), (x, y + height)]
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'LINES', {"pos": vertices})
        
        gpu.state.blend_set('ALPHA')
        shader.bind()
        shader.uniform_float("color", color)
        batch.draw(shader)
        gpu.state.blend_set('NONE')
        
    except Exception as e:
        print(f"[ERROR] Error drawing current date indicator: {e}")


def draw_color_indicator(x, y, size, color):
    """Draws a color indicator square"""
    try:
        import gpu
        from gpu_extras.batch import batch_for_shader
        
        vertices = [
            (x, y), (x + size, y), (x + size, y + size), (x, y + size)
        ]
        indices = [(0, 1, 2), (2, 3, 0)]
        
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'TRIS', {"pos": vertices}, indices=indices)
        
        gpu.state.blend_set('ALPHA')
        shader.bind()
        shader.uniform_float("color", color)
        batch.draw(shader)
        gpu.state.blend_set('NONE')
        
    except Exception as e:
        print(f"[ERROR] Error drawing color indicator: {e}")


def draw_hud_callback():
    """Callback that runs every frame to draw the HUD"""
    try:
        # Always use regular draw - snapshot detection is now handled inside get_schedule_data()
        # This ensures proper data flow while preventing animation for snapshots
        schedule_hud.draw()
    except Exception as e:
        print(f"🔴 HUD callback error: {e}")
        import traceback
        traceback.print_exc()

# Global instance of the HUD
schedule_hud = ScheduleHUD()

def register_hud_handler():
    """Registers the HUD drawing handler"""
    global _hud_draw_handler, _hud_enabled
    if _hud_draw_handler is not None:
        unregister_hud_handler()
    try:
        _hud_draw_handler = bpy.types.SpaceView3D.draw_handler_add(
            draw_hud_callback, (), 'WINDOW', 'POST_PIXEL'
        )
        _hud_enabled = True
        # Force immediate redraw
        wm = bpy.context.window_manager
        for window in wm.windows:
            screen = window.screen
            for area in screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()
    except Exception as e:
        print(f"🔴 Error registering HUD handler: {e}")
        _hud_enabled = False

def unregister_hud_handler():
    """Unregisters the HUD drawing handler"""
    global _hud_draw_handler, _hud_enabled
    if _hud_draw_handler is not None:
        try:
            bpy.types.SpaceView3D.draw_handler_remove(_hud_draw_handler, 'WINDOW')
        except Exception as e:
            print(f"🔴 Error removing HUD handler: {e}")
        _hud_draw_handler = None
    _hud_enabled = False

def is_hud_enabled():
    """Checks if the HUD is active"""
    return _hud_enabled

def invalidate_legend_hud_cache():
    """Global function to invalidate Legend HUD cache when animation groups change"""
    global schedule_hud
    if 'schedule_hud' in globals() and schedule_hud and hasattr(schedule_hud, 'invalidate_legend_cache'):
        schedule_hud.invalidate_legend_cache()
        print("🔄 Legend HUD cache invalidated globally")
    
    # Also update 3D Legend HUD if it exists and is enabled
    try:
        import bonsai.tool as tool
        anim_props = tool.Sequence.get_animation_props()
        camera_props = anim_props.camera_orbit
        
        if getattr(camera_props, 'enable_3d_legend_hud', False):
            # Check if 3D Legend HUD exists
            hud_exists = False
            for obj in bpy.data.objects:
                if obj.get("is_3d_legend_hud", False):
                    hud_exists = True
                    break
            
            if hud_exists:
                print("🔄 Updating 3D Legend HUD due to ColorType change")
                bpy.ops.bim.update_3d_legend_hud()
    except Exception as e:
        print(f"[WARNING] Failed to auto-update 3D Legend HUD: {e}")
    
    print(f"🔍 Estado actual: _hud_enabled={_hud_enabled}")
    if not _hud_enabled:
        print("🔧 Registering HUD handlers automatically...")
        register_hud_handler()
    else:
        print("🔧 HUD handlers already registered or not needed")

def refresh_hud():
    """Forces a viewport refresh to update the HUD"""
    try:
        wm = bpy.context.window_manager
        for window in wm.windows:
            screen = window.screen
            for area in screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()
        print("🔄 HUD refresh requested")
    except Exception as e:
        print(f"🔴 HUD refresh error: {e}")

# 🔧 ADDITIONAL DIAGNOSTIC FUNCTION
def debug_hud_state():
    """Diagnostic function to debug the HUD state"""
    print("\n🔍 === HUD DEBUG STATE ===")
    print(f"Handler enabled: {_hud_enabled}")
    print(f"Handler object: {_hud_draw_handler}")
    try:
        import bonsai.tool as tool
        anim_props = tool.Sequence.get_animation_props()
        camera_props = anim_props.camera_orbit
        hud_enabled = getattr(camera_props, 'enable_text_hud', False)
        print(f"Property enable_text_hud: {hud_enabled}")
        # Check schedule data
        data = schedule_hud.get_schedule_data()
        print(f"Schedule data available: {data is not None}")
        if data:
            print(f"  Current date: {data.get('current_date')}")
            print(f"  Frame: {data.get('current_frame')}")
    except Exception as e:
        print(f"Error in debug: {e}")
    print("=== END DEBUG ===\n")