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
from bpy.types import PropertyGroup
from bpy.props import (
    PointerProperty,
    StringProperty,
    EnumProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    CollectionProperty,
)
from typing import TYPE_CHECKING
from ..operators.camera_operators import _get_animation_cameras, _get_snapshot_cameras
# Import callback functions to avoid duplication
from . import callbacks_prop
# ============================================================================
# CAMERA AND HUD CALLBACK FUNCTIONS
# ============================================================================

# ============================================================================
# CAMERA AND HUD PROPERTY GROUP CLASSES
# ============================================================================

class BIMCameraOrbitProperties(PropertyGroup):
    # =====================
    # Camera settings
    # =====================
    camera_focal_mm: FloatProperty(
        name="Focal (mm)",
        default=35.0,
        min=1.0,
        max=300.0,
        description="Camera focal length in millimeters",
    )
    camera_clip_start: FloatProperty(
        name="Clip Start",
        default=0.1,
        min=0.0001,
        description="Camera near clipping distance",
    )
    camera_clip_end: FloatProperty(
        name="Clip End",
        default=10000.0,
        min=1.0,
        description="Camera far clipping distance",
    )

    # =====================
    # Orbit settings
    # =====================
    orbit_mode: EnumProperty(
        name="Orbit Mode",
        items=[
            ("NONE", "None (Static)", "The camera will not move or be animated."),
            ("CIRCLE_360", "360", "The camera performs a full 360-degree circular orbit."),
            ("PINGPONG", "Ping-Pong", "The camera moves back and forth along a 180-degree arc."),
        ],
        default="CIRCLE_360",
    )
    orbit_radius_mode: EnumProperty(
        name="Radius Mode",
        items=[
            ("AUTO", "Auto (from bbox)", "Compute radius from WorkSchedule bbox"),
            ("MANUAL", "Manual", "Use manual radius value"),
        ],
        default="AUTO",
    )
    orbit_radius: FloatProperty(
        name="Radius (m)",
        default=10.0,
        min=0.01,
        description="Manual orbit radius in meters",
    )
    orbit_height: FloatProperty(
        name="Height (Z offset)",
        default=8.0,
        description="Height offset from target center",
    )
    orbit_start_angle_deg: FloatProperty(
        name="Start Angle (deg)",
        default=0.0,
        description="Starting angle in degrees",
    )
    orbit_direction: EnumProperty(
        name="Direction",
        items=[("CCW", "CCW", "Counter-clockwise"), ("CW", "CW", "Clockwise")],
        default="CCW",
    )

    # =====================
    # Look At settings
    # =====================
    look_at_mode: EnumProperty(
        name="Look At",
        items=[
            ("AUTO", "Auto (active WorkSchedule area)", "Use bbox center of active WorkSchedule"),
            ("OBJECT", "Object", "Select object/Empty as target"),
        ],
        default="AUTO",
    )
    look_at_object: PointerProperty(
        name="Target",
        type=bpy.types.Object,
        description="Target object for camera to look at",
    )

    # =====================
    # Path & Interpolation
    # =====================
    orbit_path_shape: EnumProperty(
        name="Path Shape",
        items=[
            ("CIRCLE", "Circle (Generated)", "The add-on creates a perfect circle"),
            ("CUSTOM", "Custom Path", "Use your own curve object as the path"),
        ],
        default="CIRCLE",
        description="Choose between a generated circle or a custom curve for the orbit path",
    )
    custom_orbit_path: PointerProperty(
        name="Custom Path",
        type=bpy.types.Object,
        description="Select a Curve object for the camera to follow",
        poll=lambda self, object: getattr(object, "type", None) == "CURVE",
    )
    interpolation_mode: EnumProperty(
        name="Interpolation",
        items=[
            ("LINEAR", "Linear (Constant Speed)", "Constant, mechanical speed"),
            ("BEZIER", "Bezier (Smooth)", "Smooth ease-in and ease-out for a natural feel"),
        ],
        default="LINEAR",
        description="Controls the smoothness and speed changes of the camera motion",
    )
    bezier_smoothness_factor: FloatProperty(
        name="Smoothness Factor",
        description="Controls the intensity of the ease-in/ease-out. Higher values create a more gradual transition",
        default=0.35,
        min=0.0,
        max=2.0,
        soft_min=0.0,
        soft_max=1.0,
    )

    # =====================
    # Animation settings
    # =====================
    orbit_path_method: EnumProperty(
        name="Path Method",
        items=[
            ("FOLLOW_PATH", "Follow Path (editable)", "Bezier circle + Follow Path"),
            ("KEYFRAMES", "Keyframes (lightweight)", "Animate location directly"),
        ],
        default="FOLLOW_PATH",
    )
    orbit_use_4d_duration: BoolProperty(
        name="Use 4D total frames",
        default=True,
        description="If enabled, orbit spans the whole 4D animation range",
    )
    orbit_duration_frames: FloatProperty(
        name="Orbit Duration (frames)",
        default=250.0,
        min=1.0,
        description="Custom orbit duration in frames",
    )

    # =====================
    # UI toggles
    # =====================
    show_camera_orbit_settings: BoolProperty(
        name="Camera & Orbit",
        default=False,
        description="Toggle Camera & Orbit settings visibility",
    )
    hide_orbit_path: BoolProperty(
        name="Hide Orbit Path",
        default=False,
        description="Hide the visible orbit path (Bezier Circle) in the viewport and render",
    )

    # =====================
    # 3D Texts
    # =====================
    show_3d_schedule_texts: BoolProperty(
        name="Show 3D HUD Render",
        description="Toggle visibility of the 3D objects used as a Heads-Up Display (HUD) for rendering",
        default=False,
        update=lambda self, context: callbacks_prop.toggle_3d_text_visibility(self, context),
    )

    # =====================
    # HUD (GPU) - Base
    # =====================
    enable_text_hud: BoolProperty(
        name="Enable Viewport HUD",
        description="Enable GPU-based HUD overlay for real-time schedule information in the viewport",
        default=False,
        update=callbacks_prop.update_gpu_hud_visibility,
    )
    expand_hud_settings: BoolProperty(
        name="Expand HUD Settings",
        description="Show/hide detailed HUD configuration options",
        default=False,
    )
    expand_schedule_hud: BoolProperty(
        name="Expand Schedule HUD",
        default=False,
        description="Show/hide Schedule HUD settings"
    )
    expand_timeline_hud: BoolProperty(
        name="Expand Timeline HUD",
        default=False,
        description="Show/hide Timeline HUD settings"
    )
    expand_legend_hud: BoolProperty(
        name="Expand Legend HUD",
        default=False,
        description="Show/hide Legend HUD settings"
    )
    expand_3d_hud_render: BoolProperty(
        name="Expand 3D HUD Render",
        default=False,
        description="Show/hide 3D HUD Render settings"
    )

    hud_show_date: BoolProperty(name="Date", default=True, update=update_hud_gpu)
    hud_show_week: BoolProperty(name="Week", default=True, update=update_hud_gpu)
    hud_show_day: BoolProperty(name="Day", default=False, update=update_hud_gpu)
    hud_show_progress: BoolProperty(name="Progress", default=False, update=callbacks_prop.update_hud_gpu)

    hud_position: EnumProperty(
        name="Position",
        items=[
            ("TOP_RIGHT", "Top Right", ""),
            ("TOP_LEFT", "Top Left", ""),
            ("BOTTOM_RIGHT", "Bottom Right", ""),
            ("BOTTOM_LEFT", "Bottom Left", ""),
        ],
        default="BOTTOM_LEFT",
        update=callbacks_prop.force_hud_refresh,
    )
    hud_scale_factor: FloatProperty(
        name="Scale",
        default=1.0,
        min=0.1,
        max=5.0,
        precision=2,
        update=callbacks_prop.force_hud_refresh,
    )
    hud_margin_horizontal: FloatProperty(
        name="H-Margin",
        default=0.05,
        min=0.0,
        max=0.3,
        precision=3,
        update=callbacks_prop.force_hud_refresh,
    )
    hud_margin_vertical: FloatProperty(
        name="V-Margin",
        default=0.05,
        min=0.0,
        max=0.3,
        precision=3,
        update=callbacks_prop.force_hud_refresh,
    )

    # Base colors (RGBA)
    hud_text_color: FloatVectorProperty(
        name="Text Color",
        subtype="COLOR",
        size=4,
        default=(1.0, 1.0, 1.0, 1.0),
        min=0.0,
        max=1.0,
        update=callbacks_prop.force_hud_refresh,
    )
    hud_background_color: FloatVectorProperty(
        name="Background Color",
        subtype="COLOR",
        size=4,
        default=(0.09, 0.114, 0.102, 0.102),
        min=0.0,
        max=1.0,
        update=callbacks_prop.force_hud_refresh,
    )

    # =====================
    # HUD VISUAL ENHANCEMENTS
    # =====================
    # Spacing & alignment
    hud_text_spacing: FloatProperty(
        name="Line Spacing",
        description="Vertical spacing between HUD text lines",
        default=0.02,
        min=0.0,
        max=0.3,
        precision=3,
        update=callbacks_prop.force_hud_refresh,
    )
    hud_text_alignment: EnumProperty(
        name="Text Alignment",
        items=[
            ("LEFT", "Left", "Align text to the left"),
            ("CENTER", "Center", "Center align text"),
            ("RIGHT", "Right", "Align text to the right"),
        ],
        default="LEFT",
        update=callbacks_prop.force_hud_refresh,
    )

    # Panel padding
    hud_padding_horizontal: FloatProperty(
        name="H-Padding",
        description="Horizontal padding inside the HUD panel",
        default=10.0,
        min=0.0,
        max=50.0,
        update=callbacks_prop.force_hud_refresh,
    )
    hud_padding_vertical: FloatProperty(
        name="V-Padding",
        description="Vertical padding inside the HUD panel",
        default=8.0,
        min=0.0,
        max=50.0,
        update=callbacks_prop.force_hud_refresh,
    )

    # Borders
    hud_border_radius: FloatProperty(
        name="Border Radius",
        description="Corner rounding of the HUD background",
        default=20.0,
        min=0.0,
        max=50.0,
        update=callbacks_prop.force_hud_refresh,
    )
    hud_border_width: FloatProperty(
        name="Border Width",
        description="Width of the HUD border",
        default=0.0,
        min=0.0,
        max=5.0,
        update=callbacks_prop.force_hud_refresh,
    )
    hud_border_color: FloatVectorProperty(
        name="Border Color",
        subtype="COLOR",
        size=4,
        default=(1.0, 1.0, 1.0, 0.5),
        min=0.0,
        max=1.0,
        update=callbacks_prop.force_hud_refresh,
    )

    # Text shadow
    hud_text_shadow_enabled: BoolProperty(
        name="Text Shadow",
        description="Enable text shadow for better readability",
        default=True,
        update=callbacks_prop.force_hud_refresh,
    )
    hud_text_shadow_offset_x: FloatProperty(
        name="Shadow Offset X",
        description="Horizontal offset of text shadow",
        default=1.0,
        min=-10.0,
        max=10.0,
        update=callbacks_prop.force_hud_refresh,
    )
    hud_text_shadow_offset_y: FloatProperty(
        name="Shadow Offset Y",
        description="Vertical offset of text shadow",
        default=-1.0,
        min=-10.0,
        max=10.0,
        update=callbacks_prop.force_hud_refresh,
    )
    hud_text_shadow_color: FloatVectorProperty(
        name="Shadow Color",
        subtype="COLOR",
        size=4,
        default=(0.0, 0.0, 0.0, 0.8),
        min=0.0,
        max=1.0,
        update=callbacks_prop.force_hud_refresh,
    )

    # Background drop shadow
    hud_background_shadow_enabled: BoolProperty(
        name="Background Shadow",
        description="Enable drop shadow for the HUD background",
        default=False,
        update=callbacks_prop.force_hud_refresh,
    )
    hud_background_shadow_offset_x: FloatProperty(
        name="BG Shadow Offset X",
        default=3.0,
        min=-20.0,
        max=20.0,
        update=callbacks_prop.force_hud_refresh,
    )
    hud_background_shadow_offset_y: FloatProperty(
        name="BG Shadow Offset Y",
        default=-3.0,
        min=-20.0,
        max=20.0,
        update=callbacks_prop.force_hud_refresh,
    )
    hud_background_shadow_blur: FloatProperty(
        name="BG Shadow Blur",
        description="Blur radius of the background shadow",
        default=5.0,
        min=0.0,
        max=20.0,
        update=callbacks_prop.force_hud_refresh,
    )
    hud_background_shadow_color: FloatVectorProperty(
        name="BG Shadow Color",
        subtype="COLOR",
        size=4,
        default=(0.0, 0.0, 0.0, 0.6),
        min=0.0,
        max=1.0,
        update=callbacks_prop.force_hud_refresh,
    )

    # Typography
    hud_font_weight: EnumProperty(
        name="Font Weight",
        items=[
            ("NORMAL", "Normal", "Normal font weight"),
            ("BOLD", "Bold", "Bold font weight"),
        ],
        default="NORMAL",
        update=callbacks_prop.force_hud_refresh,
    )
    hud_letter_spacing: FloatProperty(
        name="Letter Spacing",
        description="Spacing between characters (tracking)",
        default=0.0,
        min=-2.0,
        max=5.0,
        precision=2,
        update=callbacks_prop.force_hud_refresh,
    )

    # Background gradient
    hud_background_gradient_enabled: BoolProperty(
        name="Background Gradient",
        description="Enable gradient background instead of solid color",
        default=False,
        update=callbacks_prop.force_hud_refresh,
    )
    hud_background_gradient_color: FloatVectorProperty(
        name="Gradient Color",
        subtype="COLOR",
        size=4,
        default=(0.1, 0.1, 0.1, 0.9),
        min=0.0,
        max=1.0,
        update=callbacks_prop.force_hud_refresh,
    )
    hud_gradient_direction: EnumProperty(
        name="Gradient Direction",
        items=[
            ("VERTICAL", "Vertical", "Top to bottom gradient"),
            ("HORIZONTAL", "Horizontal", "Left to right gradient"),
            ("DIAGONAL", "Diagonal", "Diagonal gradient"),
        ],
        default="VERTICAL",
        update=callbacks_prop.force_hud_refresh,
    )

# --- START OF CORRECTED CODE ---

    # ==========================================
    # === TIMELINE HUD (GPU) - NEW PROPERTIES ===
    # ==========================================
    enable_timeline_hud: BoolProperty(
        name="Enable Timeline HUD",
        description="Show a graphical timeline at the bottom/top of the viewport",
        default=False,
        update=callbacks_prop.update_gpu_hud_visibility,
    )
    timeline_hud_position: EnumProperty(
        name="Timeline Position",
        items=[
            ('BOTTOM', "Bottom", "Place the timeline at the bottom"),
            ('TOP', "Top", "Place the timeline at the top"),
        ],
        default='BOTTOM',
        update=callbacks_prop.force_hud_refresh,
    )
    timeline_hud_margin_vertical: FloatProperty(
        name="V-Margin",
        description="Vertical margin from the viewport edge, as a percentage of viewport height",
        default=0.05,
        min=0.0,
        max=0.45,
        subtype='FACTOR',
        precision=3,
        update=callbacks_prop.force_hud_refresh,
    )
    timeline_hud_margin_horizontal: FloatProperty(
        name="H-Margin",
        description="Horizontal offset from the center, as a percentage of viewport width. 0 is center.",
        default=0.055,
        min=-0.4,
        max=0.4,
        subtype='FACTOR',
        precision=3,
        update=callbacks_prop.force_hud_refresh,
    )
    timeline_hud_zoom_level: EnumProperty(
        name="Timeline Zoom",
        items=[
            ('MONTHS', "Months", "Show years and months"),
            ('WEEKS', "Weeks", "Show weeks and days"),
            ('DAYS', "Days", "Show individual days"),
        ],
        default='MONTHS',
        update=callbacks_prop.force_hud_refresh,
    )
    timeline_hud_height: FloatProperty(
        name="Height (px)",
        description="Height of the timeline bar in pixels",
        default=40.0,
        min=20.0,
        max=100.0,
        update=callbacks_prop.force_hud_refresh,
    )
    timeline_hud_color_inactive_range: FloatVectorProperty(
        name="Inactive Range Color",
        subtype='COLOR', size=4, min=0.0, max=1.0,
        default=(0.588, 0.953, 0.745, 0.1),
        update=callbacks_prop.force_hud_refresh,
    )
    timeline_hud_color_active_range: FloatVectorProperty(
        name="Active Range Color",
        subtype='COLOR', size=4, min=0.0, max=1.0,
        default=(0.588, 0.953, 0.745, 0.1),
        update=callbacks_prop.force_hud_refresh,
    )
    timeline_hud_color_progress: FloatVectorProperty(
        name="Progress Bar Color",
        subtype='COLOR', size=4, min=0.0, max=1.0,
        default=(0.122, 0.663, 0.976, 0.102),  # #1FA9F91A
        update=callbacks_prop.force_hud_refresh,
    )
    timeline_hud_color_text: FloatVectorProperty(
        name="Timeline Text Color",
        subtype='COLOR', size=4, min=0.0, max=1.0,
        default=(1.0, 1.0, 1.0, 1.0),
        update=callbacks_prop.force_hud_refresh,
    )
    timeline_hud_border_radius: FloatProperty(
        name="Timeline Border Radius",
        description="Round corner radius for timeline HUD",
        default=10.0, min=0.0, max=50.0,
        update=callbacks_prop.force_hud_refresh,
    )
    timeline_hud_show_progress_bar: BoolProperty(
        name="Show Progress Bar",
        description="Display progress bar in timeline HUD",
        default=True,
        update=callbacks_prop.force_hud_refresh,
    )

    # ==================== LEGEND HUD PROPERTIES ====================
    # Note: All legend_hud_* properties are defined in camera_prop.py to avoid duplication
    
    # ==================== 3D LEGEND HUD PROPERTIES ====================
    
    enable_3d_legend_hud: BoolProperty(
        name="Enable 3D Legend HUD",
        description="Display 3D Legend HUD with current active ColorTypes as 3D objects",
        default=False,
        update=callbacks_prop.update_gpu_hud_visibility,
    )
    
    expand_3d_legend_hud: BoolProperty(
        name="Expand 3D Legend HUD Settings",
        description="Show/hide 3D Legend HUD settings",
        default=False,
    )
    
    # Position and Layout
    legend_3d_hud_distance: FloatProperty(
        name="HUD Distance",
        description="Distance from camera in camera space",
        default=2.2,
        min=0.5,
        max=10.0,
        step=1,
        precision=2,
    )
    
    legend_3d_hud_pos_x: FloatProperty(
        name="HUD Position X",
        description="Horizontal position in camera space",
        default=-3.6,
        min=-10.0,
        max=10.0,
        step=1,
        precision=2,
    )
    
    legend_3d_hud_pos_y: FloatProperty(
        name="HUD Position Y", 
        description="Vertical position in camera space",
        default=1.4,
        min=-10.0,
        max=10.0,
        step=1,
        precision=2,
    )
    
    legend_3d_hud_scale: FloatProperty(
        name="HUD Scale",
        description="Overall scale of the 3D Legend HUD",
        default=1.0,
        min=0.1,
        max=5.0,
        step=1,
        precision=2,
    )
    
    # Panel Settings
    legend_3d_panel_width: FloatProperty(
        name="Panel Width",
        description="Width of the legend panel",
        default=2.2,
        min=0.5,
        max=10.0,
        step=1,
        precision=2,
    )
    
    legend_3d_panel_radius: FloatProperty(
        name="Panel Corner Radius",
        description="Corner radius for rounded panel",
        default=0.12,
        min=0.0,
        max=1.0,
        step=1,
        precision=3,
    )
    
    legend_3d_panel_alpha: FloatProperty(
        name="Panel Alpha",
        description="Panel background transparency",
        default=0.85,
        min=0.0,
        max=1.0,
        step=1,
        precision=2,
    )
    
    # Font Settings
    legend_3d_font_size_title: FloatProperty(
        name="Title Font Size",
        description="Font size for legend title",
        default=0.18,
        min=0.05,
        max=1.0,
        step=1,
        precision=3,
    )
    
    legend_3d_font_size_item: FloatProperty(
        name="Item Font Size",
        description="Font size for legend items",
        default=0.15,
        min=0.05,
        max=1.0,
        step=1,
        precision=3,
    )
    
    # Layout Settings
    legend_3d_padding_x: FloatProperty(
        name="Padding X",
        description="Horizontal padding inside panel",
        default=0.18,
        min=0.0,
        max=1.0,
        step=1,
        precision=3,
    )
    
    legend_3d_padding_top: FloatProperty(
        name="Padding Top",
        description="Top padding inside panel",
        default=0.20,
        min=0.0,
        max=1.0,
        step=1,
        precision=3,
    )
    
    legend_3d_padding_bottom: FloatProperty(
        name="Padding Bottom", 
        description="Bottom padding inside panel",
        default=0.20,
        min=0.0,
        max=1.0,
        step=1,
        precision=3,
    )
    
    legend_3d_row_height: FloatProperty(
        name="Row Height",
        description="Height of each legend item row",
        default=0.20,
        min=0.05,
        max=1.0,
        step=1,
        precision=3,
    )
    
    legend_3d_dot_diameter: FloatProperty(
        name="Color Dot Diameter",
        description="Diameter of color indicator dots",
        default=0.10,
        min=0.02,
        max=0.5,
        step=1,
        precision=3,
    )
    
    legend_3d_dot_text_gap: FloatProperty(
        name="Dot to Text Gap",
        description="Gap between color dot and text",
        default=0.12,
        min=0.01,
        max=0.5,
        step=1,
        precision=3,
    )
    
    legend_3d_title_text: StringProperty(
        name="Legend Title",
        description="Text to display as legend title",
        default="Legend",
    )
    
    timeline_hud_width: FloatProperty(
        name="Timeline Width",
        description="Width of the timeline HUD as percentage of viewport width",
        default=0.8, min=0.1, max=1.0, subtype='PERCENTAGE',
        update=callbacks_prop.force_hud_refresh,
    )
    timeline_hud_color_indicator: FloatVectorProperty(
        name="Current Date Indicator Color",
        subtype='COLOR', size=4, min=0.0, max=1.0,
        default=(1.0, 0.906, 0.204, 1.0),  # #FFE734FF
        update=callbacks_prop.force_hud_refresh,
    )
    
    # LOCK/UNLOCK controls for manual positioning
    text_hud_locked: BoolProperty(
        name="Lock Text HUD",
        description="When locked, text HUD position is automatic. When unlocked, allows manual positioning",
        default=True,
        update=callbacks_prop.force_hud_refresh,
    )
    # Manual positioning coordinates (stored when unlocked)
    text_hud_manual_x: FloatProperty(
        name="Manual X Position",
        description="Manual X position for text HUD when unlocked",
        default=0.0,
        update=callbacks_prop.force_hud_refresh,
    )
    text_hud_manual_y: FloatProperty(
        name="Manual Y Position", 
        description="Manual Y position for text HUD when unlocked",
        default=0.0,
        update=callbacks_prop.force_hud_refresh,
    )
    timeline_hud_manual_x: FloatProperty(
        name="Manual X Position",
        description="Manual X position for timeline HUD when unlocked", 
        default=0.0,
        update=callbacks_prop.force_hud_refresh,
    )
    timeline_hud_manual_y: FloatProperty(
        name="Manual Y Position",
        description="Manual Y position for timeline HUD when unlocked",
        default=0.0,
        update=callbacks_prop.force_hud_refresh,
    )

    # =====================
# 4D Camera Management - Animation Context
# =====================
active_animation_camera: EnumProperty(
    name="Active Animation Camera",
    description="Select or activate a 4D Animation camera",
    items=_get_animation_cameras,  # <- CORRECTED! Use the function that filters the list
    update=callbacks_prop.update_active_animation_camera,
)
hide_all_animation_cameras: BoolProperty(
    name="Hide All Animation Cameras",
    description="Toggles the visibility of all 4D animation cameras in the viewport",
    default=False,
    update=callbacks_prop.update_animation_camera_visibility,
)

# =====================
# 4D Camera Management - Snapshot Context
# =====================
active_snapshot_camera: EnumProperty(
    name="Active Snapshot Camera",
    description="Select or activate a 4D Snapshot camera",
    items=_get_snapshot_cameras,  # <- CORRECTED! Use the function that filters the list
    update=callbacks_prop.update_active_snapshot_camera,
)
hide_all_snapshot_cameras: BoolProperty(
    name="Hide All Snapshot Cameras",
    description="Alterna la visibilidad de todas las cámaras de snapshot 4D en la vista",
    default=False,
    update=callbacks.update_snapshot_camera_visibility,
)
    
# Legacy property for backward compatibility - will be deprecated
active_4d_camera: PointerProperty(
    name="Active 4D Camera (Legacy)",
    type=bpy.types.Object,
    description="Legacy camera selector - use context-specific selectors instead",
    poll=lambda self, obj: (obj and obj.type == 'CAMERA' and 
                            (obj.get('is_4d_camera') or 
                            '4D_Animation_Camera' in obj.name or 
                            'Snapshot_Camera' in obj.name)),
    update=callbacks_prop.update_active_4d_camera,
)

# Type checking
if TYPE_CHECKING:
    camera_focal_mm: float
    camera_clip_start: float
    camera_clip_end: float
    active_animation_camera: bpy.types.Object
    active_snapshot_camera: bpy.types.Object
    show_animation_cameras: bool
    show_snapshot_cameras: bool
    show_camera_orbit_settings: bool
    enable_text_hud: bool
    expand_hud_settings: bool
    expand_schedule_hud: bool
    expand_timeline_hud: bool
    expand_legend_hud: bool
    hud_position: str
    hud_scale_factor: float
    hud_margin_horizontal: float
    hud_margin_vertical: float
    hud_text_color: tuple[float, float, float, float]
    hud_background_color: tuple[float, float, float, float]
    hud_text_spacing: float
    hud_text_alignment: str
    hud_padding_horizontal: float
    hud_padding_vertical: float
    hud_border_radius: float
    hud_border_width: float
    hud_border_color: tuple[float, float, float, float]
    hud_text_shadow_enabled: bool
    hud_text_shadow_offset_x: float
    hud_text_shadow_offset_y: float
    hud_text_shadow_color: tuple[float, float, float, float]
    hud_background_shadow_enabled: bool
    hud_background_shadow_offset_x: float
    hud_background_shadow_offset_y: float
    hud_background_shadow_blur: float
    hud_background_shadow_color: tuple[float, float, float, float]
    hud_font_weight: str
    hud_letter_spacing: float
    hud_background_gradient_enabled: bool
    hud_background_gradient_color: tuple[float, float, float, float]
    hud_gradient_direction: str
    enable_timeline_hud: bool
    timeline_hud_position: str
    timeline_hud_margin_vertical: float
    timeline_hud_margin_horizontal: float
    timeline_hud_zoom_level: str
    timeline_hud_height: float
    timeline_hud_color_inactive_range: tuple[float, float, float, float]
    timeline_hud_color_active_range: tuple[float, float, float, float]
    timeline_hud_color_progress: tuple[float, float, float, float]
    timeline_hud_color_text: tuple[float, float, float, float]
    timeline_hud_border_radius: float
    timeline_hud_show_progress_bar: bool
    enable_legend_hud: bool
    legend_hud_position: str
    legend_hud_margin_horizontal: float
    legend_hud_margin_vertical: float
    legend_hud_scale_factor: float
    legend_hud_background_color: tuple[float, float, float, float]
    legend_hud_text_color: tuple[float, float, float, float]
    legend_hud_padding: float
    legend_hud_border_radius: float
    legend_hud_item_spacing: float
    legend_hud_color_box_size: float
    legend_hud_show_task_count: bool
    legend_hud_show_inactive_types: bool
    legend_hud_max_items: int
    enable_3d_legend_hud: bool
    legend_3d_location: tuple[float, float, float]
    legend_3d_scale: float
    legend_3d_spacing: float
    legend_3d_always_face_camera: bool
    force_world_origin_anchor: bool
    orbit_speed: float
    orbit_radius: float 