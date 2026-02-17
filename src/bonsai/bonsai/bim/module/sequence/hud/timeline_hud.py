# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021, 2022 Dion Moult <dion@thinkmoult.com>, Federico Eraso <feraso@svisuals.net
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


import blf
import gpu
from gpu_extras.batch import batch_for_shader
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class TimelineHUD:
    """Specialized component for displaying timeline and schedule bars"""
    
    def __init__(self, font_id):
        """Initialize TimelineHUD with shared font"""
        self.font_id = font_id
        print(f"📊 TimelineHUD initialized with font_id={font_id}")
    
    def draw(self, data, settings, viewport_width, viewport_height):
        """Timeline HUD estilo Synchro 4D Pro con una sola barra background"""
        """Synchro 4D Pro style Timeline HUD with a single background bar"""
        print(f"\n🎬 === TIMELINE HUD DRAW START ===")
        print(f"🎬 Viewport: {viewport_width}x{viewport_height}")
        print(f"🎬 Settings enabled: {settings.get('enabled', False)}")
        print(f"🎬 Data received: {list(data.keys()) if data else 'None'}")
        print(f"🎬 Is snapshot: {data.get('is_snapshot', False) if data else 'Unknown'}")
        print(f"🎬 Font ID at start: {self.font_id}")
        
        # Verificar datos necesarios - CORREGIDO: usar rangos seleccionados
        # Verify necessary data - CORRECTED: use selected ranges
        full_start = data.get('full_schedule_start')
        full_end = data.get('full_schedule_end')
        viz_start = data.get('viz_start') or data.get('start_date')
        viz_finish = data.get('viz_finish') or data.get('finish_date')
        current_date = data.get('current_date')
        
        print(f"🎬 Data keys: {list(data.keys())}")
        print(f"🎬 Timeline data valid: full_start={full_start is not None}, viz_start={viz_start is not None}, current_date={current_date is not None}")

        # DEBUG: Show ranges
        print(f"📅 Timeline HUD Ranges:")
        if full_start and full_end:
            print(f"   Full Schedule: {full_start.strftime('%Y-%m-%d')} → {full_end.strftime('%Y-%m-%d')}")
        if viz_start and viz_finish:
            print(f"   Selected Range: {viz_start.strftime('%Y-%m-%d')} → {viz_finish.strftime('%Y-%m-%d')}")
        if current_date:
            print(f"   Current Date: {current_date.strftime('%Y-%m-%d')}")

        # FIXED: Handle both animation mode (needs viz range) and snapshot mode (needs current_date)
        if data.get('is_snapshot', False):
            # Snapshot mode: only need current_date and schedule range
            if not (current_date and full_start and full_end):
                print("[ERROR] Timeline HUD (Snapshot): Missing current_date or schedule range")
                return
            # For snapshot, use full schedule range as display range
            viz_start = full_start
            viz_finish = full_end
            print(f"🎬 Timeline HUD: Using full schedule range for snapshot")
        else:
            # Animation mode: need viz range and current_date
            if not (viz_start and viz_finish and current_date):
                print("[ERROR] Timeline HUD (Animation): Missing required viz_start, viz_finish or current_date")
                return
        
        # Configuration
        color_background = settings.get('color_inactive_range', (0.2, 0.2, 0.2, 0.8)) # Renamed to color_background for clarity
        color_text = settings.get('color_text', (1.0, 1.0, 1.0, 1.0))
        color_indicator = settings.get('color_indicator', (1.0, 1.0, 1.0, 1.0))
        progress_color = settings.get('color_progress')
        bar_h = settings.get('height', 40.0)
        border_radius = settings.get('border_radius', 0.0)

        # Viewport geometry and positioning
        margin_v_px = int(viewport_height * settings.get('margin_v', 0.05))
        bar_h = settings.get('height', 40.0)
        bar_w = int(viewport_width * settings.get('width', 0.8))
        
        h_margin_offset = int(viewport_width * settings.get('margin_h', 0.0))
        x_start = ((viewport_width - bar_w) // 2) + h_margin_offset
        y_start = margin_v_px if settings.get('position') == 'BOTTOM' else viewport_height - margin_v_px - bar_h

        # The timeline display range is NOW the animation range.
        # This makes the background bar and the progress bar always occupy the widget's space.
        display_start = viz_start
        display_end = viz_finish

        duration = (display_end - display_start).total_seconds()
        if duration <= 0:
            return # Don't draw if the range is invalid

        def date_to_x(date):
            # Clamp date to the display window to avoid extreme values
            date = max(display_start, min(display_end, date))
            progress = (date - display_start).total_seconds() / duration
            return int(x_start + progress * bar_w)

        # Determine the zoom level for the timestamps
        selected_days = (viz_finish - viz_start).days if viz_finish and viz_start else 0
        if selected_days <= 14:  # <= 2 weeks
            zoom_level = 'DETAILED'
        elif selected_days <= 180:  # <= 6 months (approx)
            zoom_level = 'NORMAL'
        elif selected_days <= 730:  # <= 2 years
            zoom_level = 'WIDE'
        else:  # > 2 years
            zoom_level = 'FULL'

        # ====== DRAW ELEMENTS ======
        try:
            gpu.state.blend_set('ALPHA')
        except Exception:
            pass

        # 1. Draw background bar (now occupies the full width of the widget)
        if border_radius > 0:
            self.draw_rounded_rect(x_start, y_start, bar_w, int(bar_h), color_background, border_radius)
        else:
            self.draw_gpu_rect(x_start, y_start, bar_w, int(bar_h), color_background)

        # 1.5. Draw progress bar if enabled
        if settings.get('show_progress_bar', True):
            # FIXED: For snapshots, disable animated progress bar
            if data.get('is_snapshot', False):
                # For snapshots, show static progress bar only if date is within range
                if viz_start <= current_date <= viz_finish:
                    progress_x_end = date_to_x(current_date)
                    progress_width = progress_x_end - x_start
                    if progress_width > 0:
                        self.draw_gpu_rect(x_start, y_start, int(progress_width), int(bar_h), progress_color)
            else:
                # Normal animated behavior for non-snapshot mode
                if current_date > viz_start:
                    progress_x_end = date_to_x(current_date)
                    progress_width = progress_x_end - x_start
                    
                    if progress_width > 0:
                        self.draw_gpu_rect(x_start, y_start, int(progress_width), int(bar_h), progress_color)

        # 2. Draw indicator lines and texts
        self.draw_synchro_timeline_marks(x_start, y_start, bar_w, int(bar_h), 
                                       display_start, display_end, zoom_level, color_text, data)

        # 3. Draw current date indicator (vertical line with diamond)
        x_current = date_to_x(current_date)
        self.draw_current_date_indicator(x_current, y_start, int(bar_h), color_indicator)

        try:
            gpu.state.blend_set('NONE')
        except Exception:
            pass

    def draw_gpu_rect(self, x, y, w, h, color):
        """Draws a simple rectangle using the GPU module."""
        vertices = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
        indices = [(0, 1, 2), (2, 3, 0)]
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'TRIS', {"pos": vertices}, indices=indices)
        gpu.state.blend_set('ALPHA')
        shader.bind()
        shader.uniform_float("color", color)
        batch.draw(shader)
        gpu.state.blend_set('NONE')

    def draw_rounded_rect(self, x, y, w, h, color, radius):
        """Draws a rectangle with rounded corners using approximation with multiple triangles."""
        try:
            from math import cos, sin
            # Limit the radius to half the smaller dimension
            max_radius = min(w, h) / 2.0
            radius = min(radius, max_radius)
            
            if radius <= 0:
                # If the radius is 0 or negative, draw a normal rectangle
                self.draw_gpu_rect(x, y, w, h, color)
                return
            
            vertices = []
            indices = []
            
            # Number of segments for the rounded corners (more = smoother)
            segments = max(4, int(radius / 2))  # Adjust according to radius size
            
            # Center of the rectangle to facilitate calculations
            center_x = x + w / 2
            center_y = y + h / 2
            
            # Create vertices for a rounded rectangle
            # Lower left corner
            for i in range(segments + 1):
                angle = 3.14159 + i * (3.14159 / 2) / segments  # 180° to 270°
                vx = x + radius + radius * cos(angle)
                vy = y + radius + radius * sin(angle)
                vertices.append((vx, vy))
            
            # Lower right corner
            for i in range(segments + 1):
                angle = 3.14159 * 1.5 + i * (3.14159 / 2) / segments  # 270° to 360°
                vx = x + w - radius + radius * cos(angle)
                vy = y + radius + radius * sin(angle)
                vertices.append((vx, vy))
            
            # Upper right corner
            for i in range(segments + 1):
                angle = 0 + i * (3.14159 / 2) / segments  # 0° to 90°
                vx = x + w - radius + radius * cos(angle)
                vy = y + h - radius + radius * sin(angle)
                vertices.append((vx, vy))
            
            # Upper left corner
            for i in range(segments + 1):
                angle = 3.14159 / 2 + i * (3.14159 / 2) / segments  # 90° to 180°
                vx = x + radius + radius * cos(angle)
                vy = y + h - radius + radius * sin(angle)
                vertices.append((vx, vy))
            
            # Create triangles using the center as a common point
            center_vertex_index = len(vertices)
            vertices.append((center_x, center_y))
            
            # Connect all perimeter vertices with the center
            total_perimeter_vertices = len(vertices) - 1
            for i in range(total_perimeter_vertices):
                next_i = (i + 1) % total_perimeter_vertices
                indices.append((center_vertex_index, i, next_i))
            
            # Draw the rounded rectangle
            shader = gpu.shader.from_builtin('UNIFORM_COLOR')
            batch = batch_for_shader(shader, 'TRIS', {"pos": vertices}, indices=indices)
            gpu.state.blend_set('ALPHA')
            shader.bind()
            shader.uniform_float("color", color)
            batch.draw(shader)
            
        except Exception as e:
            print(f"Error drawing rounded rectangle: {e}")
            # Fallback to normal rectangle
            self.draw_gpu_rect(x, y, w, h, color)

    def draw_current_date_indicator(self, x, y_start, bar_h, color_indicator):
        """Draws the current date indicator as a vertical line with diamond"""
        try:
            # Vertical line
            line_vertices = [(x, y_start), (x, y_start + bar_h)]
            shader = gpu.shader.from_builtin('UNIFORM_COLOR')
            batch = batch_for_shader(shader, 'LINES', {"pos": line_vertices})
            
            gpu.state.blend_set('ALPHA')
            gpu.state.line_width_set(2.0)
            shader.bind()
            shader.uniform_float("color", color_indicator)
            batch.draw(shader)
            
            # Diamond at top
            diamond_size = 4
            diamond_y = y_start + bar_h + 2
            diamond_vertices = [
                (x, diamond_y + diamond_size),  # Top
                (x + diamond_size, diamond_y),  # Right
                (x, diamond_y - diamond_size),  # Bottom
                (x - diamond_size, diamond_y)   # Left
            ]
            diamond_indices = [(0, 1, 2), (2, 3, 0)]
            
            diamond_batch = batch_for_shader(shader, 'TRIS', {"pos": diamond_vertices}, indices=diamond_indices)
            shader.bind()
            shader.uniform_float("color", color_indicator)
            diamond_batch.draw(shader)
            
            gpu.state.line_width_set(1.0)
            gpu.state.blend_set('NONE')
            
        except Exception as e:
            print(f"[ERROR] Error drawing current date indicator: {e}")

    def draw_synchro_timeline_marks(self, x_start, y_start, bar_w, bar_h, start_date, end_date, zoom_level, color_text, data=None):
        """Draws Synchro 4D Pro style timestamps with lines and texts"""
        try:
            import os
            import locale
            import bpy
            
            duration_seconds = (end_date - start_date).total_seconds()
            if duration_seconds <= 0:
                return

            def date_to_x(date):
                progress = (date - start_date).total_seconds() / duration_seconds
                return int(x_start + progress * bar_w)

            # Configure font
            blf.size(self.font_id, 10)
            blf.color(self.font_id, *color_text)
            
            # Force locale to English for consistent month names
            original_locale = locale.getlocale(locale.LC_TIME)
            try:
                try:
                    locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
                except locale.Error:
                    locale.setlocale(locale.LC_TIME, 'C')

                # ====== DRAW YEARS WITH CHANGE INDICATORS ======
                current_year = start_date.year
                end_year = end_date.year
                
                print(f"🗺️ Drawing years from {current_year} to {end_year}")
                print(f"🗺️ Date range: {start_date.strftime('%Y-%m-%d')} → {end_date.strftime('%Y-%m-%d')}")
                print(f"🗺️ Timeline coordinates: x_start={x_start}, bar_w={bar_w}, y_start={y_start}, bar_h={bar_h}")
                
                years_drawn = 0
                # Extend the loop by one year to draw the final marker
                for year in range(current_year, end_year + 2):
                    # Calculate the effective start date of the year within the timeline
                    if year == current_year:
                        # For the first year, use the timeline start date
                        # Also normalize the first year for perfect alignment.
                        from datetime import time
                        year_effective_start = datetime.combine(start_date.date(), time.min)
                    else:
                        # For subsequent years, use January 1
                        year_effective_start = datetime(year, 1, 1)
                    
                    # Only process if the year appears in the timeline
                    if year_effective_start <= end_date:
                        year_x = date_to_x(year_effective_start)
                        print(f"🗺️ Year {year}: effective_date={year_effective_start.strftime('%Y-%m-%d')}, x={year_x}")
                        
                        # Check if it is within the visible area
                        if x_start <= year_x <= x_start + bar_w:
                            print(f"🗺️ [DEBUG] Drawing year {year} at x={year_x}")
                            
                            # Vertical year line (full height)
                            year_line_color = (color_text[0], color_text[1], color_text[2], 0.8)
                            self.draw_timeline_line(year_x, y_start, bar_h, year_line_color, 2.0)
                            
                            # YEAR TEXT with distinctive yellow color
                            year_text = str(year) # Using yellow for distinction
                            
                            # Configure font for years (white color like lines and texts)
                            blf.size(self.font_id, 12)
                            year_color = color_text  # Use the same color as other texts (white)
                            blf.color(self.font_id, *year_color)
                            
                            # Text position (just above the bar)
                            text_x = year_x + 4
                            text_y = y_start + bar_h + 4
                            
                            # Render year text
                            blf.position(self.font_id, text_x, text_y, 0)
                            blf.draw(self.font_id, year_text)
                            print(f"🗺️ [DEBUG] Year {year} drawn at ({text_x}, {text_y})")
                            years_drawn += 1
                            
                            # Restore original configuration
                            blf.size(self.font_id, 10)
                            blf.color(self.font_id, *color_text)
                            
                        else:
                            print(f"🗺️ [ERROR] Year {year} outside visible area (x={year_x})")
                    else:
                        print(f"🗺️ Year {year} outside time range")
                
                print(f"🗺️ Total years drawn: {years_drawn}")

                # ====== DRAW MONTHS ======
                current_month = datetime(start_date.year, start_date.month, 1)
                # Extend the loop by one month to ensure the final marker is drawn
                loop_end_month = end_date + relativedelta(months=1)
                
                # Loop until the marker is past the end date's extended boundary
                while current_month <= loop_end_month:
                    month_x = date_to_x(current_month)
                    
                    if x_start <= month_x <= x_start + bar_w:
                        # Vertical month line (3/4 height)
                        line_height = bar_h * 0.75
                        month_line_color = (color_text[0], color_text[1], color_text[2], 0.6)
                        self.draw_timeline_line(month_x, y_start, line_height, month_line_color, 1.5)
                        
                        # Month text (positioned at the top of the bar)
                        month_text = current_month.strftime('%b')  # Jan, Feb, etc.
                        text_dims = blf.dimensions(self.font_id, month_text)
                        text_x = month_x + 4
                        text_y = y_start + bar_h - 18  # Moved lower to avoid overlap
                        blf.color(self.font_id, color_text[0], color_text[1], color_text[2], color_text[3])
                        blf.position(self.font_id, text_x, text_y, 0)
                        blf.draw(self.font_id, month_text)
                    
                    # Advance to the next month
                    if current_month.month == 12:
                        current_month = datetime(current_month.year + 1, 1, 1)
                    else:
                        current_month = datetime(current_month.year, current_month.month + 1, 1)

                # ====== DRAW DAYS ======
                # Only show days if the zoom is very detailed (e.g., <= 2 weeks)
                if zoom_level == 'DETAILED':
                    # Normalize the start date to midnight to align the day marks.
                    from datetime import time
                    normalized_start_date = datetime.combine(start_date.date(), time.min)
                    current_day_date = normalized_start_date
                    day_counter = 0
                    # Extend the loop by one day to ensure the final marker is drawn
                    loop_end_day = end_date + timedelta(days=1)
                    
                    # Use the START date as a reference point for Day 0/1
                    reference_start = data.get('viz_start') or data.get('start_date') or start_date
                    full_start = data.get('full_schedule_start')
                    
                    # If there is a full schedule, use that as a reference for the day counter
                    if full_start and full_start <= reference_start:
                        actual_day_ref = full_start
                    else:
                        actual_day_ref = reference_start
                    # Loop until the marker is past the end date's extended boundary
                    while current_day_date <= loop_end_day:
                        day_x = date_to_x(current_day_date)
                        
                        if x_start <= day_x <= x_start + bar_w:
                            # Vertical day line (1/4 height)
                            line_height = bar_h * 0.25
                            day_line_color = (color_text[0], color_text[1], color_text[2], 0.2) # Lighter color
                            self.draw_timeline_line(day_x, y_start, line_height, day_line_color, 0.5) # Thinner line
                            
                            # Day text (D + number)
                            delta_days_from_ref = (current_day_date.date() - actual_day_ref.date()).days
                            day_number_display = max(1, delta_days_from_ref + 1) # Days start at 1
                            day_text = f"D{day_number_display}"
                            
                            text_x = day_x + 1
                            text_y = y_start + 2 # Very low on the bar, below the weeks
                            
                            blf.color(self.font_id, color_text[0], color_text[1], color_text[2], color_text[3])
                            blf.position(self.font_id, text_x, text_y, 0)
                            blf.draw(self.font_id, day_text)
                        
                        current_day_date += timedelta(days=1)
                        day_counter += 1

                # ====== DRAW WEEKS (always visible with adaptive logic) ======
                # Show weeks at all zoom levels but with different frequencies
                duration_days = (end_date - start_date).days
                if duration_days <= 365:  # <= 1 year: show all weeks
                    week_interval = 1
                    show_week_text = True
                elif duration_days <= 730:  # <= 2 years: show every 2 weeks
                    week_interval = 2 
                    show_week_text = True
                else:  # > 2 years: show every 4 weeks (only lines, no text)
                    week_interval = 4
                    show_week_text = False
                
                # Decide the height of the week text based on whether days are visible
                days_are_visible = (zoom_level == 'DETAILED')
                if days_are_visible:
                    y_pos_weeks = y_start + 15  # Elevated position to not overlap with days
                else:
                    y_pos_weeks = y_start + 5   # Original position, lower
                
                # Use the START date as a reference point for Week 0/1
                reference_start = data.get('viz_start') or data.get('start_date') or start_date
                full_start = data.get('full_schedule_start')
                
                # CRITICAL: Use full schedule as reference if it exists
                if full_start:
                    actual_start = full_start
                    print(f"🔄 Using full schedule as reference: {actual_start.strftime('%Y-%m-%d')}")
                else:
                    actual_start = reference_start
                    print(f"🔄 Using selected range as reference: {actual_start.strftime('%Y-%m-%d')}")
                
                # Start from the configured START date (not from ISO Monday)
                # Normalize the start date to midnight so that the week markers
                # align with the beginning of the day, eliminating offsets due to time.
                from datetime import time
                normalized_start_date = datetime.combine(actual_start.date(), time.min)
                week_start_date = normalized_start_date
                week_counter = 0
                
                print(f"🔄 Timeline weeks aligned from START date: {week_start_date.strftime('%Y-%m-%d')}")
                
                # Draw vertical lines every 7 days from the START date
                while week_start_date <= end_date:
                    week_x = date_to_x(week_start_date)
                    
                    if x_start <= week_x <= x_start + bar_w and week_counter % week_interval == 0:
                        if show_week_text:
                            # Vertical week line ALIGNED with the indicator
                            line_height = bar_h * 0.5
                            week_line_color = (color_text[0], color_text[1], color_text[2], 0.4)
                            self.draw_timeline_line(week_x, y_start, line_height, week_line_color, 1.0)
                            
                            # Week text PERFECTLY ALIGNED with the vertical line
                            try:
                                # IDENTICAL LOGIC to Viewport HUD to ensure perfect synchronization
                                if full_start:
                                    # With full schedule: use the EXACT SAME logic as get_schedule_data()
                                    week_date = week_start_date.date()
                                    fss_d = full_start.date()
                                    
                                    delta_days = (week_date - fss_d).days
                                    if week_date < fss_d:
                                        week_number_display = 0
                                    else:
                                        week_number_display = max(1, (delta_days // 7) + 1)
                                    
                                    week_text = f"W{week_number_display}"
                                    
                                else:
                                    # Without full schedule: use selected range
                                    ref_start_d = reference_start.date()
                                    week_date = week_start_date.date()
                                    
                                    delta_days = (week_date - ref_start_d).days
                                    if week_date < ref_start_d:
                                        week_number_display = 0
                                    else:
                                        week_number_display = max(1, (delta_days // 7) + 1)
                                    
                                    week_text = f"W{week_number_display}"
                                    
                            except Exception as e:
                                print(f"[ERROR] Error calculating synchronized week: {e}")
                                week_text = f"W{week_counter}"
                                
                            # POSITION EXACTLY ALIGNED with the vertical line
                            text_x = week_x + 1  # Very close to the line for perfect alignment
                            text_y = y_pos_weeks  # Positioned lower to avoid overlap with months
                            
                            blf.color(self.font_id, color_text[0], color_text[1], color_text[2], color_text[3])
                            blf.position(self.font_id, text_x, text_y, 0)
                            blf.draw(self.font_id, week_text)
                    
                    # Next week start date (every 7 days)
                    week_start_date += timedelta(days=7)
                    week_counter += 1

            finally:
                # Restore original locale
                try:
                    if original_locale[0]:
                        locale.setlocale(locale.LC_TIME, original_locale)
                except Exception:
                    pass
                    
        except Exception as e:
            print(f"[ERROR] Error drawing synchro timeline marks: {e}")

    def draw_timeline_line(self, x, y, height, color, width=1.0):
        """Draws a vertical line on the timeline"""
        try:
            vertices = [(x, y), (x, y + height)]
            shader = gpu.shader.from_builtin('UNIFORM_COLOR')
            batch = batch_for_shader(shader, 'LINES', {"pos": vertices})
            
            gpu.state.blend_set('ALPHA')
            gpu.state.line_width_set(width)
            shader.bind()
            shader.uniform_float("color", color)
            batch.draw(shader)
            gpu.state.line_width_set(1.0)
            gpu.state.blend_set('NONE')
            
        except Exception as e:
            print(f"[ERROR] Error drawing timeline line: {e}")
    
    def calculate_timeline_bounds(self, viewport_width, viewport_height, settings):
        """Calculate the bounds of the timeline HUD"""
        # Get position settings
        position = settings.get('position', 'BOTTOM')
        margin_h = int(viewport_width * settings.get('margin_h', 0.02))
        margin_v = int(viewport_height * settings.get('margin_v', 0.02))
        
        # Calculate timeline dimensions
        timeline_width = int(viewport_width * settings.get('width_ratio', 0.6))
        timeline_height = int(settings.get('height', 80))
        
        # Position timeline
        if position == 'BOTTOM':
            timeline_x = (viewport_width - timeline_width) // 2
            timeline_y = margin_v
        elif position == 'TOP':
            timeline_x = (viewport_width - timeline_width) // 2
            timeline_y = viewport_height - margin_v - timeline_height
        elif position == 'LEFT':
            timeline_x = margin_h
            timeline_y = (viewport_height - timeline_height) // 2
        else:  # RIGHT
            timeline_x = viewport_width - margin_h - timeline_width
            timeline_y = (viewport_height - timeline_height) // 2
        
        return timeline_x, timeline_y, timeline_width, timeline_height
    
    def draw_timeline_background(self, x, y, width, height, settings):
        """Draw the background of the timeline"""
        try:
            bg_enabled = settings.get('background_enabled', True)
            if not bg_enabled:
                return
            
            bg_color = settings.get('background_color', (0.1, 0.1, 0.1, 0.7))
            
            vertices = [
                (x, y), (x + width, y),
                (x + width, y + height), (x, y + height)
            ]
            indices = [(0, 1, 2), (2, 3, 0)]
            
            shader = gpu.shader.from_builtin('UNIFORM_COLOR')
            batch = batch_for_shader(shader, 'TRIS', {"pos": vertices}, indices=indices)
            
            gpu.state.blend_set('ALPHA')
            shader.bind()
            shader.uniform_float("color", bg_color)
            batch.draw(shader)
            gpu.state.blend_set('NONE')
            
            # Draw border if enabled
            border_enabled = settings.get('border_enabled', True)
            if border_enabled:
                border_color = settings.get('border_color', (0.5, 0.5, 0.5, 1.0))
                self.draw_timeline_border(x, y, width, height, border_color)
                
        except Exception as e:
            print(f"[ERROR] Error drawing timeline background: {e}")
    
    def draw_timeline_border(self, x, y, width, height, border_color):
        """Draw border around timeline"""
        try:
            vertices = [
                # Outer rectangle
                (x, y), (x + width, y),
                (x + width, y), (x + width, y + height),
                (x + width, y + height), (x, y + height),
                (x, y + height), (x, y)
            ]
            
            shader = gpu.shader.from_builtin('UNIFORM_COLOR')
            batch = batch_for_shader(shader, 'LINES', {"pos": vertices})
            
            gpu.state.blend_set('ALPHA')
            shader.bind()
            shader.uniform_float("color", border_color)
            batch.draw(shader)
            gpu.state.blend_set('NONE')
            
        except Exception as e:
            print(f"[ERROR] Error drawing timeline border: {e}")
    
    def draw_timeline_bars(self, data, x, y, width, height, settings):
        """Draw the timeline bars (years, months, weeks)"""
        try:
            # Get date range from data
            full_start = data.get('full_start')
            full_end = data.get('full_end')
            current_date = data.get('current_date')
            
            if not (full_start and full_end):
                print("[WARNING] Timeline: Missing date range data")
                return
            
            # Draw different timeline levels based on settings
            if settings.get('show_years', True):
                self.draw_year_bars(full_start, full_end, current_date, x, y, width, height, settings)
            
            if settings.get('show_months', True):
                self.draw_month_bars(full_start, full_end, current_date, x, y, width, height, settings)
            
            if settings.get('show_weeks', True):
                self.draw_week_bars(full_start, full_end, current_date, x, y, width, height, settings)
                
        except Exception as e:
            print(f"[ERROR] Error drawing timeline bars: {e}")
    
    def draw_year_bars(self, full_start, full_end, current_date, x, y, width, height, settings):
        """Draw year-level timeline bars"""
        try:
            total_days = (full_end - full_start).days
            if total_days <= 0:
                return
            
            year_height = height * settings.get('year_height_ratio', 0.3)
            year_y = y + height - year_height
            
            # Generate year boundaries
            current_year = full_start.year
            end_year = full_end.year
            
            while current_year <= end_year:
                try:
                    year_start = datetime(current_year, 1, 1)
                    year_end = datetime(current_year, 12, 31)
                    
                    # Calculate positions
                    if year_start < full_start:
                        bar_start = full_start
                    else:
                        bar_start = year_start
                        
                    if year_end > full_end:
                        bar_end = full_end
                    else:
                        bar_end = year_end
                    
                    # Calculate pixel positions
                    start_ratio = (bar_start - full_start).days / total_days
                    end_ratio = (bar_end - full_start).days / total_days
                    
                    bar_x = x + start_ratio * width
                    bar_width = (end_ratio - start_ratio) * width
                    
                    # Determine color based on current date
                    if current_date and bar_start <= current_date <= bar_end:
                        year_color = settings.get('year_current_color', (0.0, 0.8, 0.0, 0.8))
                    elif current_date and bar_end < current_date:
                        year_color = settings.get('year_past_color', (0.5, 0.5, 0.5, 0.6))
                    else:
                        year_color = settings.get('year_future_color', (0.2, 0.4, 0.8, 0.6))
                    
                    # Draw year bar
                    self.draw_bar(bar_x, year_y, bar_width, year_height, year_color)
                    
                    # Draw year label if enabled
                    if settings.get('show_year_labels', True) and bar_width > 30:
                        label_x = bar_x + 4
                        label_y = year_y + year_height + 4
                        self.draw_timeline_label(str(current_year), label_x, label_y, settings.get('year_text_color', (1.0, 1.0, 1.0, 1.0)))
                    
                    current_year += 1
                    
                except Exception as e:
                    print(f"[ERROR] Error drawing year {current_year}: {e}")
                    current_year += 1
                    continue
                    
        except Exception as e:
            print(f"[ERROR] Error in draw_year_bars: {e}")
    
    def draw_month_bars(self, full_start, full_end, current_date, x, y, width, height, settings):
        """Draw month-level timeline bars"""
        try:
            total_days = (full_end - full_start).days
            if total_days <= 0:
                return
            
            month_height = height * settings.get('month_height_ratio', 0.4)
            month_y = y + height * 0.3
            
            # Generate monthly boundaries
            current = full_start.replace(day=1)
            
            while current <= full_end:
                try:
                    # Get month boundaries
                    month_start = current
                    if current.month == 12:
                        month_end = datetime(current.year + 1, 1, 1) - timedelta(days=1)
                    else:
                        month_end = datetime(current.year, current.month + 1, 1) - timedelta(days=1)
                    
                    # Clip to full range
                    if month_start < full_start:
                        month_start = full_start
                    if month_end > full_end:
                        month_end = full_end
                    
                    # Calculate positions
                    start_ratio = (month_start - full_start).days / total_days
                    end_ratio = (month_end - full_start).days / total_days
                    
                    bar_x = x + start_ratio * width
                    bar_width = (end_ratio - start_ratio) * width
                    
                    # Determine color based on current date
                    if current_date and month_start <= current_date <= month_end:
                        month_color = settings.get('month_current_color', (0.0, 0.6, 0.8, 0.7))
                    elif current_date and month_end < current_date:
                        month_color = settings.get('month_past_color', (0.4, 0.4, 0.4, 0.5))
                    else:
                        month_color = settings.get('month_future_color', (0.1, 0.3, 0.6, 0.5))
                    
                    # Draw month bar
                    self.draw_bar(bar_x, month_y, bar_width, month_height, month_color)
                    
                    # Draw month label if enabled and bar is wide enough
                    if settings.get('show_month_labels', True) and bar_width > 20:
                        month_name = current.strftime('%b')
                        label_x = bar_x + 2
                        label_y = month_y + month_height / 2 - 6
                        self.draw_timeline_label(month_name, label_x, label_y, settings.get('month_text_color', (1.0, 1.0, 1.0, 0.9)))
                    
                    # Move to next month
                    if current.month == 12:
                        current = datetime(current.year + 1, 1, 1)
                    else:
                        current = datetime(current.year, current.month + 1, 1)
                        
                except Exception as e:
                    print(f"[ERROR] Error drawing month {current}: {e}")
                    break
                    
        except Exception as e:
            print(f"[ERROR] Error in draw_month_bars: {e}")
    
    def draw_week_bars(self, full_start, full_end, current_date, x, y, width, height, settings):
        """Draw week-level timeline bars"""
        try:
            total_days = (full_end - full_start).days
            if total_days <= 0:
                return
            
            week_height = height * settings.get('week_height_ratio', 0.3)
            week_y = y
            
            # Start from the first Monday on or before full_start
            current = full_start - timedelta(days=full_start.weekday())
            week_number = 1
            
            while current <= full_end:
                try:
                    week_start = current
                    week_end = current + timedelta(days=6)
                    
                    # Clip to full range
                    if week_start < full_start:
                        week_start = full_start
                    if week_end > full_end:
                        week_end = full_end
                    
                    # Skip if week is outside range
                    if week_end < full_start or week_start > full_end:
                        current += timedelta(days=7)
                        week_number += 1
                        continue
                    
                    # Calculate positions
                    start_ratio = (week_start - full_start).days / total_days
                    end_ratio = (week_end - full_start).days / total_days
                    
                    bar_x = x + start_ratio * width
                    bar_width = max(1, (end_ratio - start_ratio) * width)
                    
                    # Determine color based on current date
                    if current_date and week_start <= current_date <= week_end:
                        week_color = settings.get('week_current_color', (0.8, 0.8, 0.0, 0.8))
                    elif current_date and week_end < current_date:
                        week_color = settings.get('week_past_color', (0.3, 0.3, 0.3, 0.4))
                    else:
                        week_color = settings.get('week_future_color', (0.0, 0.2, 0.4, 0.4))
                    
                    # Draw week bar
                    self.draw_bar(bar_x, week_y, bar_width, week_height, week_color)
                    
                    # Draw week label if enabled and bar is wide enough
                    if settings.get('show_week_labels', True) and bar_width > 15:
                        label_x = bar_x + 1
                        label_y = week_y + week_height / 2 - 4
                        self.draw_timeline_label(f"W{week_number}", label_x, label_y, settings.get('week_text_color', (1.0, 1.0, 1.0, 0.8)), small=True)
                    
                    current += timedelta(days=7)
                    week_number += 1
                    
                except Exception as e:
                    print(f"[ERROR] Error drawing week {week_number}: {e}")
                    current += timedelta(days=7)
                    week_number += 1
                    continue
                    
        except Exception as e:
            print(f"[ERROR] Error in draw_week_bars: {e}")
    
    def draw_bar(self, x, y, width, height, color):
        """Draw a single timeline bar"""
        try:
            if width <= 0 or height <= 0:
                return
                
            vertices = [
                (x, y), (x + width, y),
                (x + width, y + height), (x, y + height)
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
            print(f"[ERROR] Error drawing bar: {e}")
    
    def draw_timeline_label(self, text, x, y, color, small=False):
        """Draw text label on timeline"""
        try:
            font_size = 10 if small else 12
            blf.size(self.font_id, font_size)
            blf.color(self.font_id, *color)
            blf.position(self.font_id, x, y, 0)
            blf.draw(self.font_id, text)
            
        except Exception as e:
            print(f"[ERROR] Error drawing timeline label '{text}': {e}")
    
    def draw_gpu_rect(self, x, y, w, h, color):
        """Draws a simple rectangle"""
        try:
            vertices = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
            indices = [(0, 1, 2), (2, 3, 0)]
            shader = gpu.shader.from_builtin('UNIFORM_COLOR')
            batch = batch_for_shader(shader, 'TRIS', {"pos": vertices}, indices=indices)
            gpu.state.blend_set('ALPHA')
            shader.bind()
            shader.uniform_float("color", color)
            batch.draw(shader)
            gpu.state.blend_set('NONE')
        except Exception as e:
            print(f"Error drawing GPU rect: {e}")

    def draw_rounded_rect(self, x, y, w, h, color, radius):
        """Draws a rectangle with rounded corners using approximation with multiple triangles."""
        try:
            from math import cos, sin
            # Limit the radius to half the smaller dimension
            max_radius = min(w, h) / 2.0
            radius = min(radius, max_radius)
            
            if radius <= 0:
                # If the radius is 0 or negative, draw a normal rectangle
                self.draw_gpu_rect(x, y, w, h, color)
                return
            
            vertices = []
            indices = []
            
            # Number of segments for the rounded corners (more = smoother)
            segments = max(4, int(radius / 2))  # Adjust according to radius size
            
            # Center of the rectangle to facilitate calculations
            center_x = x + w / 2
            center_y = y + h / 2
            
            # Create vertices for a rounded rectangle
            # Lower left corner
            for i in range(segments + 1):
                angle = 3.14159 + i * (3.14159 / 2) / segments  # 180° to 270°
                vx = x + radius + radius * cos(angle)
                vy = y + radius + radius * sin(angle)
                vertices.append((vx, vy))
            
            # Lower right corner
            for i in range(segments + 1):
                angle = 3.14159 * 1.5 + i * (3.14159 / 2) / segments  # 270° to 360°
                vx = x + w - radius + radius * cos(angle)
                vy = y + radius + radius * sin(angle)
                vertices.append((vx, vy))
            
            # Upper right corner
            for i in range(segments + 1):
                angle = 0 + i * (3.14159 / 2) / segments  # 0° to 90°
                vx = x + w - radius + radius * cos(angle)
                vy = y + h - radius + radius * sin(angle)
                vertices.append((vx, vy))
            
            # Upper left corner
            for i in range(segments + 1):
                angle = 3.14159 / 2 + i * (3.14159 / 2) / segments  # 90° to 180°
                vx = x + radius + radius * cos(angle)
                vy = y + h - radius + radius * sin(angle)
                vertices.append((vx, vy))
            
            # Create triangles using the center as a common point
            center_vertex_index = len(vertices)
            vertices.append((center_x, center_y))
            
            # Connect all perimeter vertices with the center
            total_perimeter_vertices = len(vertices) - 1
            for i in range(total_perimeter_vertices):
                next_i = (i + 1) % total_perimeter_vertices
                indices.append((center_vertex_index, i, next_i))
            
            # Draw the rounded rectangle
            shader = gpu.shader.from_builtin('UNIFORM_COLOR')
            batch = batch_for_shader(shader, 'TRIS', {"pos": vertices}, indices=indices)
            gpu.state.blend_set('ALPHA')
            shader.bind()
            shader.uniform_float("color", color)
            batch.draw(shader)
            
        except Exception as e:
            print(f"Error drawing rounded rectangle: {e}")
            # Fallback to normal rectangle
            self.draw_gpu_rect(x, y, w, h, color)
