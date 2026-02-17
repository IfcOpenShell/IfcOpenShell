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


class TextHUD:
    """Specialized component for displaying text-based schedule information"""
    
    def __init__(self, font_id):
        """Initialize TextHUD with shared font"""
        self.font_id = font_id
        print(f"📝 TextHUD initialized with font_id={font_id}")
    
    def draw(self, data, settings, viewport_width, viewport_height):
        """Draw text HUD elements"""
        try:
            # Calculate position for text HUD
            text_x, text_y, align_x, align_y = self.calculate_position(
                viewport_width, viewport_height, settings
            )
            
            # Format text lines to display
            lines_to_draw = self.format_text_lines(data, settings)
            
            if not lines_to_draw:
                return
            
            # Set font size
            font_size = int(settings.get('scale', 1.0) * 16)
            blf.size(self.font_id, font_size)
            
            # Calculate dimensions for background
            line_dims = [blf.dimensions(self.font_id, line) for line in lines_to_draw]
            max_width = max(w for w, h in line_dims) if line_dims else 0
            total_text_height = sum(h for w, h in line_dims) + max(0, len(lines_to_draw) - 1) * (settings.get('spacing', 0.02) * viewport_height)
            
            # Draw background with effects
            self.draw_background_with_effects(
                text_x, text_y, max_width, total_text_height, 
                align_x, align_y, settings
            )
            
            # Draw text lines
            self.draw_text_lines(
                lines_to_draw, line_dims, text_x, text_y, 
                align_x, align_y, settings, viewport_height
            )
            
        except Exception as e:
            print(f"[ERROR] Error in TextHUD.draw: {e}")
            import traceback
            traceback.print_exc()
    
    def calculate_position(self, viewport_width, viewport_height, settings):
        """Calculate position of the HUD in pixels"""
        margin_h = int(viewport_width * settings.get('margin_h', 0.02))
        margin_v = int(viewport_height * settings.get('margin_v', 0.02))
        
        position = settings.get('position', 'TOP_RIGHT')
        
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
    
    def format_text_lines(self, data, settings):
        """Format the text lines to be displayed"""
        if not data:
            return ["No Schedule Data"]
        
        lines = []
        
        # Add schedule name
        lines.append(f"Schedule: {data.get('schedule_name', 'Unknown')}")
        
        # Add date if enabled
        if settings.get('hud_show_date', True):
            current_date = data.get('current_date')
            if current_date:
                lines.append(f"{current_date.strftime('%d/%m/%Y')}")
        
        # Add week if enabled
        if settings.get('hud_show_week', True):
            week_number = data.get('week_number')
            if week_number is not None:
                lines.append(f"Week {week_number}")
        
        # Add day if enabled
        if settings.get('hud_show_day', True):
            elapsed_days = data.get('elapsed_days')
            if elapsed_days is not None:
                lines.append(f"Day {elapsed_days}")
        
        # Add progress if enabled
        if settings.get('hud_show_progress', True):
            progress_pct = data.get('progress_pct')
            if progress_pct is not None:
                lines.append(f"Progress: {progress_pct}%")
        
        return lines
    
    def draw_background_with_effects(self, x, y, width, height, align_x, align_y, settings):
        """Draw background with effects (shadow, border, gradient, etc.)"""
        try:
            # Get background settings
            bg_enabled = settings.get('background_enabled', True)
            if not bg_enabled:
                return
            
            padding_h = settings.get('padding_h', 10.0)
            padding_v = settings.get('padding_v', 8.0)
            
            # Calculate background rectangle
            if align_x == 'RIGHT':
                bg_x = x - width - padding_h * 2
            else:
                bg_x = x - padding_h
            
            if align_y == 'TOP':
                bg_y = y - height - padding_v * 2
            else:
                bg_y = y - padding_v
            
            bg_width = width + padding_h * 2
            bg_height = height + padding_v * 2
            
            # Draw shadow if enabled
            shadow_enabled = settings.get('shadow_enabled', False)
            if shadow_enabled:
                self.draw_shadow(bg_x, bg_y, bg_width, bg_height, settings)
            
            # Draw main background
            bg_color = settings.get('background_color', (0.0, 0.0, 0.0, 0.5))
            gradient_enabled = settings.get('gradient_enabled', False)
            
            if gradient_enabled:
                self.draw_gradient_background(bg_x, bg_y, bg_width, bg_height, settings)
            else:
                self.draw_solid_background(bg_x, bg_y, bg_width, bg_height, bg_color)
            
            # Draw border if enabled
            border_enabled = settings.get('border_enabled', False)
            if border_enabled:
                border_width = settings.get('border_width', 1.0)
                border_color = settings.get('border_color', (1.0, 1.0, 1.0, 1.0))
                self.draw_border(bg_x, bg_y, bg_width, bg_height, border_width, border_color)
                
        except Exception as e:
            print(f"[ERROR] Error drawing background: {e}")
    
    def draw_text_lines(self, lines, line_dims, base_x, base_y, align_x, align_y, settings, viewport_height):
        """Draw the actual text lines"""
        try:
            padding_h = settings.get('padding_h', 10.0)
            padding_v = settings.get('padding_v', 8.0)
            
            # Calculate starting Y position
            if align_y == 'TOP':
                current_y = base_y - padding_v
                if line_dims:
                    current_y -= line_dims[0][1]
            else:
                total_height = sum(h for w, h in line_dims) + max(0, len(lines) - 1) * (settings.get('spacing', 0.02) * viewport_height)
                current_y = base_y + padding_v + total_height
                if line_dims:
                    current_y -= line_dims[0][1]
            
            # Draw each line
            for i, line in enumerate(lines):
                if align_x == 'RIGHT':
                    text_x = base_x - padding_h
                    self.draw_text_with_shadow(line, text_x, current_y, settings, 'RIGHT')
                else:
                    text_x = base_x + padding_h
                    self.draw_text_with_shadow(line, text_x, current_y, settings, 'LEFT')
                
                # Move to next line position
                if i < len(lines) - 1:
                    spacing = settings.get('spacing', 0.02) * viewport_height
                    current_y -= (spacing + line_dims[i + 1][1])
                    
        except Exception as e:
            print(f"[ERROR] Error drawing text lines: {e}")
    
    def draw_text_with_shadow(self, text, x, y, settings, alignment='LEFT'):
        """Draw text with optional shadow effect"""
        try:
            # Get text settings
            text_color = settings.get('text_color', (1.0, 1.0, 1.0, 1.0))
            shadow_enabled = settings.get('text_shadow_enabled', False)
            
            # Draw shadow if enabled
            if shadow_enabled:
                shadow_offset = settings.get('text_shadow_offset', (1.0, -1.0))
                shadow_color = settings.get('text_shadow_color', (0.0, 0.0, 0.0, 0.8))
                
                # Set shadow position
                shadow_x = x + shadow_offset[0]
                shadow_y = y + shadow_offset[1]
                
                # Draw shadow text
                blf.color(self.font_id, *shadow_color)
                if alignment == 'RIGHT':
                    # Calculate text width for right alignment
                    text_width = blf.dimensions(self.font_id, text)[0]
                    blf.position(self.font_id, shadow_x - text_width, shadow_y, 0)
                else:
                    blf.position(self.font_id, shadow_x, shadow_y, 0)
                blf.draw(self.font_id, text)
            
            # Draw main text
            blf.color(self.font_id, *text_color)
            if alignment == 'RIGHT':
                # Calculate text width for right alignment
                text_width = blf.dimensions(self.font_id, text)[0]
                blf.position(self.font_id, x - text_width, y, 0)
            else:
                blf.position(self.font_id, x, y, 0)
            blf.draw(self.font_id, text)
            
        except Exception as e:
            print(f"[ERROR] Error drawing text with shadow: {e}")
    
    def draw_solid_background(self, x, y, width, height, color):
        """Draw solid colored background"""
        try:
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
            print(f"[ERROR] Error drawing solid background: {e}")
    
    def draw_gradient_background(self, x, y, width, height, settings):
        """Draw gradient background"""
        try:
            # Get gradient colors
            gradient_top = settings.get('gradient_top_color', (0.2, 0.2, 0.2, 0.8))
            gradient_bottom = settings.get('gradient_bottom_color', (0.0, 0.0, 0.0, 0.8))
            
            # Create gradient effect by drawing multiple rectangles
            steps = 20
            step_height = height / steps
            
            for i in range(steps):
                # Interpolate color
                factor = i / (steps - 1)
                color = (
                    gradient_bottom[0] + (gradient_top[0] - gradient_bottom[0]) * factor,
                    gradient_bottom[1] + (gradient_top[1] - gradient_bottom[1]) * factor,
                    gradient_bottom[2] + (gradient_top[2] - gradient_bottom[2]) * factor,
                    gradient_bottom[3] + (gradient_top[3] - gradient_bottom[3]) * factor,
                )
                
                # Draw step
                step_y = y + i * step_height
                self.draw_solid_background(x, step_y, width, step_height, color)
                
        except Exception as e:
            print(f"[ERROR] Error drawing gradient background: {e}")
    
    def draw_shadow(self, x, y, width, height, settings):
        """Draw drop shadow for background"""
        try:
            shadow_offset = settings.get('shadow_offset', (2.0, -2.0))
            shadow_color = settings.get('shadow_color', (0.0, 0.0, 0.0, 0.3))
            shadow_blur = settings.get('shadow_blur', 0)  # Simple shadow for now
            
            shadow_x = x + shadow_offset[0]
            shadow_y = y + shadow_offset[1]
            
            # Draw simple shadow (no blur for performance)
            self.draw_solid_background(shadow_x, shadow_y, width, height, shadow_color)
            
        except Exception as e:
            print(f"[ERROR] Error drawing shadow: {e}")
    
    def draw_border(self, x, y, width, height, border_width, border_color):
        """Draw border around background"""
        try:
            # Draw border as four lines
            vertices = [
                # Top line
                (x, y + height), (x + width, y + height),
                # Right line  
                (x + width, y + height), (x + width, y),
                # Bottom line
                (x + width, y), (x, y),
                # Left line
                (x, y), (x, y + height)
            ]
            
            shader = gpu.shader.from_builtin('UNIFORM_COLOR')
            batch = batch_for_shader(shader, 'LINES', {"pos": vertices})
            
            gpu.state.blend_set('ALPHA')
            gpu.state.line_width_set(border_width)
            shader.bind()
            shader.uniform_float("color", border_color)
            batch.draw(shader)
            gpu.state.line_width_set(1.0)  # Reset line width
            gpu.state.blend_set('NONE')
            
        except Exception as e:
            print(f"[ERROR] Error drawing border: {e}")