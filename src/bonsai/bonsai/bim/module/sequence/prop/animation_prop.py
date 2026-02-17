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
from bpy.types import PropertyGroup
from bpy.props import (
    PointerProperty, StringProperty, EnumProperty,
    BoolProperty, IntProperty, FloatProperty, FloatVectorProperty, CollectionProperty
)
from typing import TYPE_CHECKING
from . import callbacks_prop as callbacks
from . import enums_prop as enums


class BIMTaskTypeColor(PropertyGroup):
    """Color by task type (legacy - maintain for compatibility)"""
    name: StringProperty(name="Name")
    animation_type: StringProperty(name="Type")
    color: FloatVectorProperty(
        name="Color",
        subtype="COLOR", size=4,
        default=(1.0, 0.0, 0.0, 1.0),
        min=0.0,
        max=1.0,
    )
    if TYPE_CHECKING:
        name: str
        animation_type: str
        color: tuple[float, float, float, float]

class AnimationColorSchemes(PropertyGroup):
    """Animation Color Scheme for 4D animation"""
    name: StringProperty(name="Color Type Name", default="New Color Type")
    
    # Considered States
    consider_start: BoolProperty(
        name="Start state", 
        default=False,
        description="When enabled, elements use start appearance throughout the entire animation, "
                    "useful for existing elements, demolition context, or persistent visibility",
        update=callbacks.update_colortype_considerations)
    consider_active: BoolProperty(
        name="Active state", 
        default=True,
        description="Apply appearance during task execution period",
        update=callbacks.update_colortype_considerations)
    consider_end: BoolProperty(
        name="End state", 
        default=True,
        description="Apply appearance after task completion",
        update=callbacks.update_colortype_considerations)
    
    # Colors by State
    start_color: FloatVectorProperty(
        name="Start Color",
        subtype="COLOR",
        size=4, min=0.0, max=1.0,
        default=(1.0, 1.0, 1.0, 1.0),
    )
    in_progress_color: FloatVectorProperty(
        name="In Progress Color",
        subtype="COLOR",
        size=4, min=0.0, max=1.0,
        default=(0.8, 0.8, 0.0, 1.0),
    )
    end_color: FloatVectorProperty(
        name="End Color",
        subtype="COLOR",
        size=4, min=0.0, max=1.0,
        default=(0.0, 1.0, 0.0, 1.0),
    )
    
    # Option to keep original color
    use_start_original_color: BoolProperty(name="Start: Use Original Color", default=False)
    use_active_original_color: BoolProperty(name="Active: Use Original Color", default=False)
    use_end_original_color: BoolProperty(name="End: Use Original Color", default=True)
    
    # Transparency Control
    start_transparency: FloatProperty(name="Start Transparency", min=0.0, max=1.0, default=0.0)
    active_start_transparency: FloatProperty(name="Active Start Transparency", min=0.0, max=1.0, default=0.0)
    active_finish_transparency: FloatProperty(name="Active Finish Transparency", min=0.0, max=1.0, default=0.0)
    active_transparency_interpol: FloatProperty(name="Transparency Interpol.", min=0.0, max=1.0, default=1.0)
    end_transparency: FloatProperty(name="End Transparency", min=0.0, max=1.0, default=0.0)

    hide_at_end: BoolProperty(name="Hide When Finished", description="If enabled, the object will become invisible in the End phase", default=False)
    
    if TYPE_CHECKING:
        name: str
        start_color: tuple[float, float, float, float]
        in_progress_color: tuple[float, float, float, float]
        end_color: tuple[float, float, float, float]
        use_start_original_color: bool
        use_active_original_color: bool
        use_end_original_color: bool
        start_transparency: float
        active_start_transparency: float
        active_finish_transparency: float
        active_transparency_interpol: float
        end_transparency: float
        hide_at_end: bool

class AnimationColorTypeGroupItem(PropertyGroup):
    """Item for animation group stack"""
    group: EnumProperty(name="Group", items=enums.get_internal_ColorType_sets_enum)
    enabled: BoolProperty(name="Use", default=True, update=callbacks.update_legend_hud_on_group_change)


class BIMAnimationProperties(PropertyGroup):
    """Animation properties with improved colortype system"""
    
    # Unified colortype system
    active_ColorType_system: EnumProperty(
        name="ColorType System",
        items=[
            ("ColorTypeS", "Animation Color Schemes", "Use advanced ColorType system"),
        ],
        default="ColorTypeS"
    )
    
    # Animation group stack
    animation_group_stack: CollectionProperty(name="Animation Group Stack", type=AnimationColorTypeGroupItem)
    animation_group_stack_index: IntProperty(name="Animation Group Stack Index", default=-1)
    
    # State and configuration
    is_editing: BoolProperty(name="Is Loaded", default=False)
    saved_colortype_name: StringProperty(name="colortype Set Name", default="Default")
    
    # Animation Color Scheme
    ColorTypes: CollectionProperty(name="Animation Color Scheme", type=AnimationColorSchemes)
    active_ColorType_index: IntProperty(name="Active ColorType Index")
    ColorType_groups: EnumProperty(name="ColorType Group", items=enums.get_internal_ColorType_sets_enum, update=callbacks.update_ColorType_group)

    # Bandera para controlar si la animation ha sido creada al menos una vez.
    is_animation_created: BoolProperty(
        name="Is Animation Created",
        description="Internal flag to check if the main animation has been created at least once",
        default=False
    )

    # New property, only for the Tasks panel UI, which excludes 'DEFAULT'
    task_colortype_group_selector: EnumProperty(
        name="Custom colortype Group",
        items=enums.get_user_created_groups_enum,
        update=callbacks.update_task_colortype_group_selector
    )
   
    # UI toggles
    show_saved_task_colortypes_panel: BoolProperty(name="Show Saved colortypes", default=False)
    should_show_task_bar_options: BoolProperty(name="Show Task Bar Options", default=False)

    
    
    # Task bar colors
    color_full: FloatVectorProperty(
        name="Full Bar",
        subtype="COLOR", size=4,
        default=(1.0, 0.0, 0.0, 1.0),
        min=0.0, max=1.0,
        description="Color for full task bar",
        update=callbacks.update_color_full,
    )
    color_progress: FloatVectorProperty(
        name="Progress Bar",
        subtype="COLOR", size=4,
        default=(0.0, 1.0, 0.0, 1.0),
        min=0.0, max=1.0,
        description="Color for progress task bar",
        update=callbacks.update_color_progress,
    )
    
    # Legacy properties (maintain for compatibility)
    saved_color_schemes: EnumProperty(items=enums.get_saved_color_schemes, name="Saved Colour Schemes")
    active_color_component_outputs_index: IntProperty(name="Active Color Component Index")
    active_color_component_inputs_index: IntProperty(name="Active Color Component Index")
    if TYPE_CHECKING:
        active_ColorType_system: str
        animation_group_stack: bpy.types.bpy_prop_collection_idprop[AnimationColorTypeGroupItem]
        animation_group_stack_index: int
        is_editing: bool
        saved_colortype_name: str
        ColorTypes: bpy.types.bpy_prop_collection_idprop[AnimationColorSchemes]
        active_ColorType_index: int
        ColorType_groups: str
        task_colortype_group_selector: str
        show_saved_task_colortypes_panel: bool
        should_show_task_bar_options: bool
        color_full: Color
        color_progress: Color
        saved_color_schemes: str
        active_color_component_outputs_index: int
        active_color_component_inputs_index: int


# === Camera & Orbit Settings (safe-inject) ===================================
# We attach properties dynamically to BIMAnimationProperties so we don't depend
# on the exact class body location. This works as long as registration happens
# after these attributes exist.

try:
    from bpy.props import FloatProperty, BoolProperty, EnumProperty, PointerProperty
    import bpy
    from bpy.types import Object as _BpyObject

    _C = BIMAnimationProperties  # type: ignore[name-defined]

    def _add_prop(cls, name, pdef):
        # Ensure annotation slot exists for Blender 2.8+ registration
        try:
            ann = getattr(cls, "__annotations__", None)
            if ann is None:
                cls.__annotations__ = {}
            if name not in cls.__annotations__:
                cls.__annotations__[name] = pdef
        except Exception:
            pass
        # Attach descriptor if missing
        if not hasattr(cls, name):
            setattr(cls, name, pdef)

    # --- Camera ---
    _add_prop(_C, "camera_focal_mm", FloatProperty(name="Focal (mm)", default=35.0, min=1.0, max=300.0))
    _add_prop(_C, "camera_clip_start", FloatProperty(name="Clip Start", default=0.1, min=0.0001))
    _add_prop(_C, "camera_clip_end", FloatProperty(name="Clip End", default=10000.0, min=1.0))

    # --- Orbit ---
    _add_prop(_C, "orbit_mode", EnumProperty(
        name="Orbit Mode",
        items=[
            ("NONE", "None (Static)", "No orbit animation"),
            ("CIRCLE_360", "360", "Full circular orbit"),
            ("PINGPONG", "Ping-Pong", "Back and forth over an arc"),
        ],
        default="CIRCLE_360"
    ))

    _add_prop(_C, "orbit_radius_mode", EnumProperty(
        name="Radius Mode",
        items=[("AUTO", "Auto (from bbox)", "Compute radius from WorkSchedule bbox"),
                ("MANUAL", "Manual", "Use manual radius value")],
        default="AUTO"
    ))
    _add_prop(_C, "orbit_radius", FloatProperty(name="Radius (m)", default=10.0, min=0.01))
    _add_prop(_C, "orbit_height", FloatProperty(name="Height (Z offset)", default=8.0))
    _add_prop(_C, "orbit_start_angle_deg", FloatProperty(name="Start Angle (deg)", default=0.0))
    _add_prop(_C, "orbit_direction", EnumProperty(
        name="Direction",
        items=[("CCW", "CCW", "Counter-clockwise"), ("CW", "CW", "Clockwise")],
        default="CCW"
    ))

    # --- Look At ---
    _add_prop(_C, "look_at_mode", EnumProperty(
        name="Look At",
        items=[("AUTO", "Auto (active WorkSchedule area)", "Use bbox center of active WorkSchedule"),
                ("OBJECT", "Object", "Select object/Empty as target")],
        default="AUTO"
    ))
    _add_prop(_C, "look_at_object", PointerProperty(name="Target", type=_BpyObject))

    # --- NEW: Path Shape & Custom Path ---
    _add_prop(_C, "orbit_path_shape", EnumProperty(
        name="Path Shape",
        items=[
            ('CIRCLE', "Circle (Generated)", "The add-on creates a perfect circle"),
            ('CUSTOM', "Custom Path", "Use your own curve object as the path"),
        ],
        default='CIRCLE',
    ))
    _add_prop(_C, "custom_orbit_path", PointerProperty(
        name="Custom Path",
        type=_BpyObject,
        poll=lambda self, object: getattr(object, "type", None) == 'CURVE'
    ))

    # --- NEW: Interpolation ---
    _add_prop(_C, "interpolation_mode", EnumProperty(
        name="Interpolation",
        items=[
            ('LINEAR', "Linear (Constant Speed)", "Constant, mechanical speed"),
            ('BEZIER', "Bezier (Smooth)", "Smooth ease-in and ease-out for a natural feel"),
        ],
        default='LINEAR',
    ))


    _add_prop(_C, "bezier_smoothness_factor", FloatProperty(
        name="Smoothness Factor",
        description="Controls the intensity of the ease-in/ease-out. Higher values create a more gradual transition",
        default=0.35,
        min=0.0,
        max=2.0,
        soft_min=0.0,
        soft_max=1.0
    ))
    # --- Animation method & duration ---
    _add_prop(_C, "orbit_path_method", EnumProperty(
        name="Path Method",
        items=[("FOLLOW_PATH", "Follow Path (editable)", "Bezier circle + Follow Path"),
                ("KEYFRAMES", "Keyframes (lightweight)", "Animate location directly")],
        default="FOLLOW_PATH"
    ))
    _add_prop(_C, "orbit_use_4d_duration", BoolProperty(
        name="Use 4D total frames", default=True,
        description="If enabled, orbit spans the whole 4D animation range"))
    _add_prop(_C, "orbit_duration_frames", FloatProperty(
        name="Orbit Duration (frames)", default=250.0, min=1.0))

    # --- UI toggles ---
    _add_prop(_C, "show_camera_orbit_settings", BoolProperty(
        name="Camera & Orbit", default=False, description="Toggle Camera & Orbit settings visibility"))
    

    _add_prop(_C, "hide_orbit_path", BoolProperty(
        name="Hide Orbit Path", default=False,
        description="Hide the visible orbit path (Bezier Circle) in the viewport and render"))

    # --- HUD (Heads-Up Display) properties mirrored on BIMAnimationProperties ---
    _add_prop(_C, "enable_text_hud", BoolProperty(
        name="Enable Text HUD",
        description="Attach schedule texts as HUD elements to the active camera",
        default=False, update=callbacks.update_gpu_hud_visibility))
    _add_prop(_C, "hud_margin_horizontal", FloatProperty(
        name="Horizontal Margin",
        description="Distance from camera edge (percentage of camera width)",
        default=0.05, min=0.0, max=0.3, precision=3,
        update=callbacks.update_hud_gpu))
    _add_prop(_C, "hud_margin_vertical", FloatProperty(
        name="Vertical Margin",
        description="Distance from camera edge (percentage of camera height)",
        default=0.05, min=0.0, max=0.3, precision=3,
        update=callbacks.update_hud_gpu))
    _add_prop(_C, "hud_text_spacing", FloatProperty(
        name="Text Spacing",
        description="Vertical spacing between HUD text elements",
        default=0.02, min=0.0, max=0.2, precision=3,
        update=callbacks.update_hud_gpu))
    _add_prop(_C, "hud_scale_factor", FloatProperty(
        name="HUD Scale Factor",
        description="Scale multiplier for HUD elements relative to camera distance",
        default=1.0, min=0.1, max=5.0, precision=2,
        update=callbacks.update_hud_gpu))
    _add_prop(_C, "hud_distance", FloatProperty(
        name="Distance",
        description="Distance from camera to place HUD elements",
        default=3.0, min=0.5, max=50.0, precision=1,
        update=callbacks.update_hud_gpu))

    _add_prop(_C, "hud_position", EnumProperty(
        name="HUD Position",
        description="Position of HUD elements on screen",
        items=[
            ('TOP_LEFT', "Top Left", "Position HUD at top-left corner"),
            ('TOP_RIGHT', "Top Right", "Position HUD at top-right corner"),
            ('BOTTOM_LEFT', "Bottom Left", "Position HUD at bottom-left corner"),
            ('BOTTOM_RIGHT', "Bottom Right", "Position HUD at bottom-right corner"),
        ],
        default='TOP_RIGHT',
        update=callbacks.update_hud_gpu))



except Exception as _e:
    # Failsafe: leave file importable if Bonsai internals are not present here
    pass




