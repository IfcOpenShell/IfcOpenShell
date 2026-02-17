

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


import bpy
import blf
import gpu
import json
import time
from gpu_extras.batch import batch_for_shader


class LegendHUD:
    """Specialized component for displaying colortype legend and task status"""
    
    def __init__(self, font_id):
        """Initialize LegendHUD with shared font"""
        self.font_id = font_id
        
        # Cache for legend data with invalidation
        self._legend_data_cache = None
        self._cached_animation_groups = None
        self._cache_timestamp = 0
        self._last_active_group = None
        
        print(f"[INFO] LegendHUD initialized with font_id={font_id}")
    
    def invalidate_legend_cache(self):
        """Invalidates the legend data cache to force an update"""
        print("[INFO] Invalidating legend cache")
        self._legend_data_cache = None
        self._cached_animation_groups = None
        self._cache_timestamp = 0
        self._last_active_group = None  # Reset group tracking to force detection
    
    def draw(self, data, settings, viewport_width, viewport_height):
        """Draws the Legend HUD with active animation profiles and their dynamic colors"""
        print(f"\n[INFO] === LEGEND HUD DRAW START ===")
        print(f"[INFO] Viewport: {viewport_width}x{viewport_height}")
        print(f"[INFO] Settings enabled: {settings.get('enabled', False)}")
        
        try:
            # Get active profiles from animation system
            legend_data = self.get_active_colortype_legend_data()
            if not legend_data:
                print("[ERROR] Legend HUD: No active colortype data available")
                return
            
            print(f"[INFO] Legend data: {len(legend_data)} ColorTypes found")
            
            # Configuration
            position = settings.get('position', 'BOTTOM_LEFT')
            margin_h = settings.get('margin_h', 0.05)
            margin_v = settings.get('margin_v', 0.05)
            
            # Calculate base position
            base_x, base_y, align_x, align_y = self.calculate_position(viewport_width, viewport_height, settings)
            
            # Draw legend elements
            self.draw_legend_elements(
                legend_data, settings, base_x, base_y, align_x, align_y, viewport_width, viewport_height
            )
            
            print("[INFO] Legend HUD drawn successfully")
            
        except Exception as e:
            print(f"[ERROR] Error drawing legend HUD: {e}")
            import traceback
            traceback.print_exc()
    
    def calculate_position(self, viewport_width, viewport_height, settings):
        """Calculate HUD position in pixels"""
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
        elif position == 'BOTTOM_LEFT':
            x = margin_h
            y = margin_v
            align_x = 'LEFT'
            align_y = 'BOTTOM'
        else:  # CENTER
            x = viewport_width // 2
            y = viewport_height // 2
            align_x = 'CENTER'
            align_y = 'CENTER'
        
        return x, y, align_x, align_y
    
    def draw_legend_elements(self, legend_data: list, settings: dict, base_x: float, base_y: float, align_x: str, align_y: str, viewport_width: int, viewport_height: int):
        """Draws the individual legend elements with support for 3 color columns"""
        try:
            if not legend_data:
                return
            
            camera_props = self.get_camera_props()
            if not camera_props:
                return
            
            # --- 2. GET VISIBILITY AND STYLE SETTINGS ---
            show_start = settings.get('show_start_column', False)
            show_active = settings.get('show_active_column', True)
            show_end = settings.get('show_end_column', False)
            
            show_start_title = settings.get('show_start_title', False)
            show_active_title = settings.get('show_active_title', False)
            show_end_title = settings.get('show_end_title', False)
            
            print(f"[INFO] COLUMN VISIBILITY: start={show_start}, active={show_active}, end={show_end}")
            print(f"[INFO] TITLE VISIBILITY: start_title={show_start_title}, active_title={show_active_title}, end_title={show_end_title}")
            
            scale = settings.get('scale', 1.0)
            font_size = int(14 * scale)
            color_indicator_size = settings.get('color_indicator_size', 12.0) * scale
            item_spacing = settings.get('item_spacing', 8.0) * scale
            column_spacing = settings.get('column_spacing', 16.0) * scale
            padding_h = settings.get('padding_h', 12.0) * scale
            padding_v = settings.get('padding_v', 8.0) * scale
            text_gap = 8 * scale
            orientation = settings.get('orientation', 'VERTICAL')
            auto_scale = getattr(camera_props, 'legend_hud_auto_scale', True)
            
            # Configure font
            blf.size(self.font_id, font_size)
            
            # --- 3. CALCULATE CONTENT DIMENSIONS ---
            colors_width = 0
            num_visible_cols = sum([show_start, show_active, show_end])
            if num_visible_cols > 0:
                colors_width = (num_visible_cols * color_indicator_size) + max(0, num_visible_cols - 1) * column_spacing
            
            _, row_height = blf.dimensions(self.font_id, "X")
            
            item_widths = []
            for item in legend_data:
                text_width, _ = blf.dimensions(self.font_id, item['name'])
                item_width = colors_width + text_gap + text_width
                item_widths.append(item_width)
            
            rows_of_indices = []
            total_content_width = 0
            
            if orientation == 'VERTICAL':
                rows_of_indices = [[i] for i in range(len(legend_data))]
                if item_widths:
                    total_content_width = max(item_widths)
            else:  # HORIZONTAL
                max_width_prop = getattr(camera_props, 'legend_hud_max_width', 0.3)
                max_width_px = viewport_width * max_width_prop
                
                if legend_data:
                    if auto_scale:
                        rows_of_indices.append(list(range(len(legend_data))))
                    else:
                        current_row_indices = []
                        current_row_width = 0
                        
                        for i, item_width in enumerate(item_widths):
                            if not current_row_indices or (current_row_width + item_spacing + item_width <= max_width_px):
                                current_row_indices.append(i)
                                current_row_width += item_width
                                if len(current_row_indices) > 1:
                                    current_row_width += item_spacing
                            else:
                                rows_of_indices.append(current_row_indices)
                                current_row_indices = [i]
                                current_row_width = item_width
                        
                        if current_row_indices:
                            rows_of_indices.append(current_row_indices)
                
                if auto_scale:
                    total_content_width = sum(item_widths) + max(0, len(item_widths) - 1) * item_spacing
                else:
                    max_row_width = 0
                    for row in rows_of_indices:
                        row_width = sum(item_widths[i] for i in row) + max(0, len(row) - 1) * item_spacing
                        max_row_width = max(max_row_width, row_width)
                    total_content_width = max_row_width
            
            total_content_height = 0
            if settings.get('show_title', True):
                original_font_size = font_size
                title_font_size = getattr(camera_props, 'legend_hud_title_font_size', 16.0) * scale
                blf.size(self.font_id, int(title_font_size))
                _, title_h = blf.dimensions(self.font_id, settings.get('title_text', 'Legend'))
                blf.size(self.font_id, original_font_size)  # Restore
                total_content_height += title_h + item_spacing
            
            if any([show_start_title and show_start, show_active_title and show_active, show_end_title and show_end]):
                total_content_height += row_height + item_spacing
            
            total_content_height += len(rows_of_indices) * (row_height + item_spacing)
            if rows_of_indices:
                total_content_height -= item_spacing
            
            # --- 4. CALCULATE BACKGROUND GEOMETRY AND DRAW ---
            bg_width = total_content_width + 2 * padding_h
            bg_height = total_content_height + 2 * padding_v
            
            if align_x == 'RIGHT':
                bg_x = base_x - bg_width
            elif align_x == 'CENTER':
                bg_x = base_x - bg_width / 2
            else:  # LEFT
                bg_x = base_x
            
            if align_y == 'TOP':
                bg_y = base_y - bg_height
            elif align_y == 'CENTER':
                bg_y = base_y - bg_height / 2
            else:  # BOTTOM
                bg_y = base_y
            
            self.draw_legend_background(bg_x, bg_y, bg_width, bg_height, settings)
            
            # --- 5. DRAW CONTENT ---
            content_x = bg_x + padding_h
            current_y = bg_y + bg_height - padding_v
            
            if settings.get('show_title', True):
                title_font_size = getattr(camera_props, 'legend_hud_title_font_size', 16.0) * scale
                blf.size(self.font_id, int(title_font_size))
                
                title_text = settings.get('title_text', 'Legend')
                title_color = settings.get('title_color', (1.0, 1.0, 1.0, 1.0))
                
                if settings.get('text_shadow_enabled', True):
                    shadow_color = settings.get('text_shadow_color', (0.0, 0.0, 0.0, 0.8))
                    shadow_offset_x = settings.get('text_shadow_offset_x', 1.0)
                    shadow_offset_y = settings.get('text_shadow_offset_y', -1.0)
                    
                    blf.color(self.font_id, *shadow_color)
                    blf.position(self.font_id, content_x + shadow_offset_x, current_y - row_height + shadow_offset_y, 0)
                    blf.draw(self.font_id, title_text)
                
                blf.color(self.font_id, *title_color)
                blf.position(self.font_id, content_x, current_y - row_height, 0)
                blf.draw(self.font_id, title_text)
                
                current_y -= row_height + item_spacing
                blf.size(self.font_id, font_size)  # Restore original font size
            
            if any([show_start_title and show_start, show_active_title and show_active, show_end_title and show_end]):
                self.draw_column_titles(content_x, current_y, color_indicator_size, column_spacing,
                                        show_start, show_active, show_end,
                                        show_start_title, show_active_title, show_end_title,
                                        settings)
                current_y -= item_spacing
            
            # --- 6. DRAW PROFILE ROWS (UNIFIED LOGIC) ---
            if rows_of_indices:
                for row_indices in rows_of_indices:
                    current_y -= row_height
                    current_x = content_x
                    
                    for item_index in row_indices:
                        self.draw_colortype_row(legend_data[item_index], current_x, current_y, color_indicator_size, column_spacing, show_start, show_active, show_end, settings)
                        if orientation == 'HORIZONTAL': 
                            current_x += item_widths[item_index] + item_spacing
                    
                    current_y -= item_spacing
            
        except Exception as e:
            print(f"[ERROR] Error drawing legend elements: {e}")
            import traceback
            traceback.print_exc()
    
    def draw_column_titles(self, base_x: float, y: float, indicator_size: float, column_spacing: float,
                           show_start: bool, show_active: bool, show_end: bool, 
                           show_start_title: bool, show_active_title: bool, show_end_title: bool, settings: dict):
        """Draws the titles of the Start/Active/End columns"""
        try:
            title_color = settings.get('title_color', (1.0, 1.0, 1.0, 1.0))
            current_x = base_x
            
            if show_start and show_start_title:
                text_width, _ = blf.dimensions(self.font_id, "S")
                title_x = current_x + (indicator_size - text_width) / 2
                blf.color(self.font_id, *title_color)
                blf.position(self.font_id, title_x, y, 0)
                blf.draw(self.font_id, "S")
                current_x += indicator_size + column_spacing
            
            if show_active and show_active_title:
                text_width, _ = blf.dimensions(self.font_id, "A")
                title_x = current_x + (indicator_size - text_width) / 2
                blf.color(self.font_id, *title_color)
                blf.position(self.font_id, title_x, y, 0)
                blf.draw(self.font_id, "A")
                current_x += indicator_size + column_spacing
            
            if show_end and show_end_title:
                text_width, _ = blf.dimensions(self.font_id, "E")
                title_x = current_x + (indicator_size - text_width) / 2
                blf.color(self.font_id, *title_color)
                blf.position(self.font_id, title_x, y, 0)
                blf.draw(self.font_id, "E")
                
        except Exception as e:
            print(f"[ERROR] Error drawing column titles: {e}")
    
    def draw_colortype_row(self, legend_item: dict, base_x: float, y: float, indicator_size: float, column_spacing: float,
                         show_start: bool, show_active: bool, show_end: bool, settings: dict):
        """Draws a profile row with its corresponding colors"""
        try:
            current_x = base_x
            text_color = settings.get('text_color', (1.0, 1.0, 1.0, 1.0))
            _, row_height = blf.dimensions(self.font_id, "X")
            
            # Draw color indicators
            if show_start:
                self.draw_color_indicator(current_x, y, indicator_size, legend_item['start_color'])
                current_x += indicator_size + column_spacing
            
            if show_active:
                self.draw_color_indicator(current_x, y, indicator_size, legend_item['active_color'])
                current_x += indicator_size + column_spacing
            
            if show_end:
                self.draw_color_indicator(current_x, y, indicator_size, legend_item['end_color'])
                current_x += indicator_size + column_spacing
            
            # Draw text with shadow if enabled
            text_x = current_x - column_spacing + 8  # Small gap after last color
            
            if settings.get('text_shadow_enabled', True):
                shadow_color = settings.get('text_shadow_color', (0.0, 0.0, 0.0, 0.8))
                shadow_offset_x = settings.get('text_shadow_offset_x', 1.0)
                shadow_offset_y = settings.get('text_shadow_offset_y', -1.0)
                
                blf.color(self.font_id, *shadow_color)
                blf.position(self.font_id, text_x + shadow_offset_x, y + shadow_offset_y, 0)
                blf.draw(self.font_id, legend_item['name'])
            
            blf.color(self.font_id, *text_color)
            blf.position(self.font_id, text_x, y, 0)
            blf.draw(self.font_id, legend_item['name'])
            
        except Exception as e:
            print(f"[ERROR] Error drawing colortype row: {e}")
    
    def draw_color_indicator(self, x: float, y: float, size: float, color: tuple):
        """Draws a color indicator circle"""
        try:
            import math
            radius = size / 2.0
            center_x = x + radius
            center_y = y + radius
            segments = 32

            vertices = [(center_x, center_y)]  # Center vertex
            for i in range(segments + 1):
                angle = 2 * math.pi * i / segments
                vx = center_x + radius * math.cos(angle)
                vy = center_y + radius * math.sin(angle)
                vertices.append((vx, vy))

            shader = gpu.shader.from_builtin('UNIFORM_COLOR')
            batch = batch_for_shader(shader, 'TRI_FAN', {"pos": vertices})

            gpu.state.blend_set('ALPHA')
            shader.bind()
            shader.uniform_float("color", color)
            batch.draw(shader)
            gpu.state.blend_set('NONE')

        except Exception as e:
            print(f"[ERROR] Error drawing color indicator: {e}")
    
    def draw_legend_background(self, x: float, y: float, width: float, height: float, settings: dict):
        """Draws the legend background with configurable effects"""
        try:
            background_color = settings.get('background_color', (0.0, 0.0, 0.0, 0.8))
            border_radius = settings.get('border_radius', 5.0)
            
            if border_radius > 0:
                self.draw_rounded_rect(x, y, width, height, background_color, border_radius)
            else:
                self.draw_gpu_rect(x, y, width, height, background_color)
                
        except Exception as e:
            print(f"[ERROR] Error drawing legend background: {e}")

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
    
    def get_camera_props(self):
        """Get camera properties for Legend HUD settings"""
        try:
            import bonsai.tool as tool
            animation_props = tool.Sequence.get_animation_props()
            if hasattr(animation_props, 'camera_orbit') and animation_props.camera_orbit:
                return animation_props.camera_orbit
            return None
        except Exception as e:
            print(f"[ERROR] Error getting camera props: {e}")
            return None
    
    def get_active_colortype_legend_data(self, include_hidden=False):
        """Get colortype legend data with caching and visibility filtering"""
        try:
            import bonsai.tool as tool
            
            # Get animation properties
            anim_props = tool.Sequence.get_animation_props()
            if not hasattr(anim_props, 'animation_group_stack') or not anim_props.animation_group_stack:
                print("[INFO] No animation group stack found")
                self._legend_data_cache = []
                return []
            
            # Find the first enabled group (active group)
            current_active_group = None
            print("[INFO] HUD: Checking animation group stack for the active group:")
            for i, group_item in enumerate(anim_props.animation_group_stack):
                enabled = getattr(group_item, 'enabled', False)
                group_name = getattr(group_item, 'group', '')
                print(f"  {i}: Group '{group_name}' enabled={enabled}") # This line is fine
                if enabled and current_active_group is None:
                    current_active_group = group_name
                    print(f"[INFO] HUD: Selected active group: {current_active_group}")
                    break
                    
            # FALLBACK: If no group is enabled, default to "DEFAULT"
            if current_active_group is None:
                print("[ERROR] HUD: No active group found (no groups enabled)")
                current_active_group = "DEFAULT"
                print("[INFO] HUD: Falling back to 'DEFAULT' group.")
            
            # AUTOMATIC DETECTION: If the active group changed, clear hidden profiles
            if self._last_active_group != current_active_group:
                print(f"[INFO] AUTO-DETECTION: Active group changed from '{self._last_active_group}' to '{current_active_group}'")
                self._last_active_group = current_active_group
                
                # Auto-clear hidden profiles to show the new active group
                try:
                    camera_props = self.get_camera_props()
                    if camera_props:
                        camera_props.legend_hud_visible_colortypes = ""
                        print("[INFO] AUTO-CLEARED: legend_hud_visible_colortypes (showing all colortypes from new active group)")
                except Exception as e:
                    print(f"[WARNING] Could not auto-clear visible colortypes: {e}")
            
            current_timestamp = time.time()
            
            # Get visibility settings to include in the cache comparison
            camera_props = self.get_camera_props()
            visible_colortypes_str = getattr(camera_props, 'legend_hud_visible_colortypes', '') if camera_props else ''
            
            # The cache depends on the active group, visible profiles and whether we include hidden ones
            cache_key = (current_active_group, visible_colortypes_str, include_hidden)
            
            if (self._legend_data_cache is not None and 
                self._cached_animation_groups == cache_key and 
                current_timestamp - self._cache_timestamp < 1.0):
                return self._legend_data_cache
            
            print(f"[INFO] Refreshing legend data cache for active group: {current_active_group} (include_hidden={include_hidden})")
            
            hidden_colortypes = set()
            if not include_hidden:
                if visible_colortypes_str.strip():
                    hidden_colortypes = {p.strip() for p in visible_colortypes_str.split(',') if p.strip()}
            
            legend_data = []
            
            # The active group should never be None at this point due to FALLBACK
            if not current_active_group:
                print("[ERROR] CRITICAL: No active group after FALLBACK - this should not happen")
                self._legend_data_cache = []
                return []
            
            active_group = current_active_group
            print(f"[INFO] Found active group (first enabled): {active_group}")
            
            # Get colortype data with visibility filtering
            legend_data = self._extract_colortype_data(active_group, include_hidden, hidden_colortypes)
            
            # Update cache
            self._legend_data_cache = legend_data
            self._cached_animation_groups = cache_key
            self._cache_timestamp = current_timestamp
            
            print(f"[INFO] Legend cache updated for group '{active_group}': {len(legend_data)} items")
            return legend_data
            
        except Exception as e:
            print(f"[ERROR] Error getting legend data: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _extract_colortype_data(self, active_group, include_hidden=False, hidden_colortypes=None):
        """Extract colortype data from the active group with visibility filtering"""
        try:
            import bonsai.tool as tool
            
            if hidden_colortypes is None:
                hidden_colortypes = set()
            
            # CRITICAL: Import UnifiedColorTypeManager from the correct location
            try:
                from ..prop.color_manager_prop import UnifiedColorTypeManager
            except ImportError:
                from ..prop import UnifiedColorTypeManager
            
            context = bpy.context
            
            # SPECIAL CASE: For DEFAULT group, ensure ALL colortypes are loaded
            if active_group == "DEFAULT":
                print(f"[INFO] Processing DEFAULT group - ensuring all colortypes loaded")
                try:
                    UnifiedColorTypeManager.ensure_default_colortypes(context)
                    # Force reload to get complete list
                    UnifiedColorTypeManager._invalidate_cache(context)
                except Exception as e:
                    print(f"[WARNING] Could not ensure DEFAULT colortypes: {e}")
            
            # Get colortypes for the active group
            group_colortypes = UnifiedColorTypeManager.get_group_colortypes(context, active_group)
            
            if not group_colortypes:
                print(f"[ERROR] No colortypes found for group '{active_group}'")
                self._legend_data_cache = []
                return []
            
            legend_data = []
            
            # Process each profile of the active group
            for colortype_name, colortype_data in group_colortypes.items():
                if colortype_name in hidden_colortypes:
                    continue
                
                # Get the 3 colors: start, active, end
                start_color = self.get_colortype_color_for_state(colortype_data, 'start')
                active_color = self.get_colortype_color_for_state(colortype_data, 'in_progress') 
                end_color = self.get_colortype_color_for_state(colortype_data, 'end')
                
                legend_entry = {
                    'name': colortype_name,
                    'start_color': start_color,
                    'active_color': active_color,
                    'end_color': end_color,
                    'group': active_group,  # Use active_group instead of group_name
                    'active': True,  # It's in the active stack
                }
                
                legend_data.append(legend_entry)
            
            # Sort alphabetically for consistent display
            legend_data.sort(key=lambda x: x['name'])
            
            print(f"[INFO] Processed {len(legend_data)} colortypes from active group '{active_group}'")
            if hidden_colortypes:
                print(f"🙈 Hidden colortypes: {list(hidden_colortypes)}")
            
            return legend_data
            
        except Exception as e:
            print(f"[ERROR] Error extracting colortype data: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_colortype_color_for_state(self, colortype_data: dict, state: str) -> tuple:
        """Gets the color of a profile for a specific state (start/in_progress/end)"""
        try:
            # Mapping of states to color fields
            color_field_mapping = {
                'start': 'start_color',
                'in_progress': 'in_progress_color',
                'active': 'in_progress_color',  # Alias
                'end': 'end_color',
                'finished': 'end_color',  # Alias
            }
            
            color_field = color_field_mapping.get(state, 'in_progress_color')
            
            # Get the profile color
            if color_field in colortype_data:
                color = colortype_data[color_field]
                
                # Ensure valid RGBA format
                if isinstance(color, (list, tuple)) and len(color) >= 3:
                    if len(color) == 3:
                        return (*color, 1.0)  # Add alpha
                    else:
                        return tuple(color[:4])  # Limit to RGBA
            
            # Fallback colors
            fallback_colors = {
                'start': (1.0, 1.0, 1.0, 1.0),      # White
                'in_progress': (0.0, 1.0, 0.0, 1.0), # Green
                'end': (0.0, 0.8, 0.0, 1.0)          # Dark green
            }
            
            return fallback_colors.get(state, (0.5, 0.5, 0.5, 1.0))  # Gray fallback
            
        except Exception as e:
            print(f"[ERROR] Error getting colortype color for state '{state}': {e}")
            return (0.5, 0.5, 0.5, 1.0)  # Gray fallback