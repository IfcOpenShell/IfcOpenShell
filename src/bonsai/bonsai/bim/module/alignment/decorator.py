# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2025, 2026 Michael Yoder <myoder@desertspringscivil.com>
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

"""Alignment module decorators for GPU visualization.

This module contains decorators for rendering visual feedback during
alignment-related operations, such as PI editing.
"""

import bpy
import blf
import gpu
import bonsai.tool as tool
from bpy.types import SpaceView3D
from gpu_extras.batch import batch_for_shader


class PIEditDecorator:
    """Decorator for visualizing PI edit mode.

    This decorator provides visual feedback while the user is editing
    PI (Point of Intersection) positions with standard Blender transform tools:
    - Yellow lines connecting PI empties (tangent preview)
    - HUD text showing instructions

    The decorator reads positions directly from the PI empty objects,
    which are updated by Blender's transform operators (G key).
    """

    # Class-level state (cleared on uninstall)
    is_installed = False
    handlers = []

    # References to PI empty objects
    pi_empties = []

    # Colors
    COLOR_TANGENT_LINE = (1.0, 0.9, 0.2, 1.0)  # Yellow for tangent lines
    COLOR_HUD_TEXT = (1.0, 1.0, 1.0, 1.0)  # White for HUD text
    COLOR_EDIT_MODE_BG = (0.2, 0.4, 0.8, 0.8)  # Blue tint for edit mode indicator

    # Drawing parameters
    LINE_WIDTH = 2.5

    @classmethod
    def install(cls, context, pi_empties):
        """Install decorator handlers for PI edit mode visualization.

        Args:
            context: Blender context
            pi_empties: List of PI EMPTY objects to visualize
        """
        if cls.is_installed:
            cls.uninstall()

        cls.pi_empties = pi_empties

        handler = cls()
        # POST_VIEW for 3D world-space drawing (tangent lines in 3D)
        cls.handlers.append(
            SpaceView3D.draw_handler_add(handler.draw_tangent_lines_3d, (context,), "WINDOW", "POST_VIEW")
        )
        # POST_PIXEL for 2D screen-space drawing (HUD)
        cls.handlers.append(
            SpaceView3D.draw_handler_add(handler.draw_hud, (context,), "WINDOW", "POST_PIXEL")
        )
        cls.is_installed = True

    @classmethod
    def uninstall(cls):
        """Remove all handlers and clear state."""
        for handler in cls.handlers:
            try:
                SpaceView3D.draw_handler_remove(handler, "WINDOW")
            except ValueError:
                pass
        cls.handlers = []
        cls.is_installed = False
        cls.pi_empties = []

    @classmethod
    def update_positions(cls, pi_empties):
        """Update the list of PI empties (called when positions change).

        Args:
            pi_empties: Updated list of PI EMPTY objects
        """
        cls.pi_empties = pi_empties

    def draw_batch_3d(self, shader_type, content_pos, color, indices=None):
        """Draw a batch of 3D primitives using GPU shader.

        Args:
            shader_type: Type of primitive ("LINES", "POINTS", etc.)
            content_pos: List of 3D vertex positions
            color: RGBA color tuple
            indices: Optional list of index pairs for lines
        """
        if not tool.Blender.validate_shader_batch_data(content_pos, indices):
            return
        shader = gpu.shader.from_builtin("POLYLINE_UNIFORM_COLOR")
        shader.bind()

        # Get viewport size from active region
        region = bpy.context.region
        shader.uniform_float("viewportSize", (region.width, region.height))
        shader.uniform_float("lineWidth", self.LINE_WIDTH)

        batch = batch_for_shader(shader, shader_type, {"pos": content_pos}, indices=indices)
        shader.uniform_float("color", color)
        batch.draw(shader)

    def draw_tangent_lines_3d(self, context):
        """Draw yellow tangent lines connecting PI empties in 3D space."""
        if not self.pi_empties or len(self.pi_empties) < 2:
            return

        # Collect 3D positions from empties
        positions = []
        for empty in self.pi_empties:
            if empty and empty.name in bpy.data.objects:
                positions.append(tuple(empty.location))

        if len(positions) < 2:
            return

        # Setup blending for line drawing
        gpu.state.blend_set("ALPHA")
        gpu.state.depth_test_set("LESS_EQUAL")
        gpu.state.depth_mask_set(False)

        # Build edges list
        edges = [[i, i + 1] for i in range(len(positions) - 1)]

        # Draw lines
        self.draw_batch_3d("LINES", positions, self.COLOR_TANGENT_LINE, edges)

        # Restore state
        gpu.state.blend_set("NONE")
        gpu.state.depth_test_set("NONE")
        gpu.state.depth_mask_set(True)

    def draw_hud(self, context):
        """Draw HUD text with edit mode instructions."""
        region = context.region
        if not region:
            return

        font_id = 0
        font_size = tool.Blender.scale_font_size(14)
        blf.size(font_id, font_size)
        blf.enable(font_id, blf.SHADOW)
        blf.shadow(font_id, 6, 0, 0, 0, 1)  # Black shadow for readability
        blf.color(font_id, *self.COLOR_HUD_TEXT)

        # Position in top-left of viewport
        margin = 20
        line_height = 22
        y_pos = region.height - margin

        # Count valid empties
        valid_count = sum(1 for e in self.pi_empties if e and e.name in bpy.data.objects)

        # Instructions
        instructions = [
            "PI Edit Mode",
            f"PIs: {valid_count}",
            "",
            "G: Move selected PI",
            "ENTER: Apply changes",
            "ESC: Cancel",
        ]

        for i, line in enumerate(instructions):
            blf.position(font_id, margin, y_pos - (i * line_height), 0)
            blf.draw(font_id, line)

        blf.disable(font_id, blf.SHADOW)
