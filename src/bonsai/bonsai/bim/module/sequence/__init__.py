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

from . import prop, ui, operators

# Classes tuple for main Bonsai registration - contains all UI classes
classes = ui.classes

# --- Optional registration: ClearAnimationAdvanced (guarded) ---
try:
    _ADV = operators.ClearAnimationAdvanced
except Exception:
    _ADV = None
if _ADV:
    try:
        classes = tuple(list(classes) + [_ADV])
    except Exception:
        pass


def menu_func_export(self, context):
    self.layout.operator(operators.ExportP6.bl_idname, text="P6 (.xml)")
    self.layout.operator(operators.ExportMSP.bl_idname, text="Microsoft Project (.xml)")


def menu_func_import(self, context):
    self.layout.operator(operators.ImportWorkScheduleCSV.bl_idname, text="Work Schedule (.csv)")
    self.layout.operator(operators.ImportP6.bl_idname, text="P6 (.xml)")
    self.layout.operator(operators.ImportP6XER.bl_idname, text="P6 (.xer)")
    self.layout.operator(operators.ImportPP.bl_idname, text="Powerproject (.pp)")
    self.layout.operator(operators.ImportMSP.bl_idname, text="Microsoft Project (.xml)")


def register():
    # 1. Register all properties by delegating to the 'prop' package
    prop.register()

    # 2. Register Scene properties immediately after prop registration
    bpy.types.Scene.show_saved_ColorTypes_section = bpy.props.BoolProperty(name="Show Saved ColorTypes", default=True)
    bpy.types.Scene.BIMWorkPlanProperties = bpy.props.PointerProperty(type=prop.BIMWorkPlanProperties)
    bpy.types.Scene.BIMWorkScheduleProperties = bpy.props.PointerProperty(type=prop.BIMWorkScheduleProperties)
    bpy.types.Scene.BIMTaskTreeProperties = bpy.props.PointerProperty(type=prop.BIMTaskTreeProperties)
    bpy.types.Scene.BIMWorkCalendarProperties = bpy.props.PointerProperty(type=prop.BIMWorkCalendarProperties)
    bpy.types.Scene.BIMStatusProperties = bpy.props.PointerProperty(type=prop.BIMStatusProperties)
    bpy.types.Scene.BIMAnimationProperties = bpy.props.PointerProperty(type=prop.BIMAnimationProperties)
    bpy.types.Scene.DatePickerProperties = bpy.props.PointerProperty(type=prop.DatePickerProperties)
    bpy.types.TextCurve.BIMDateTextProperties = bpy.props.PointerProperty(type=prop.BIMDateTextProperties)

    # 3. Register camera orbit property group and attach it dynamically
    try:
        bpy.utils.register_class(prop.BIMCameraOrbitProperties)
    except Exception:
        pass

    try:
        if not hasattr(prop.BIMAnimationProperties, 'camera_orbit'):
            prop.BIMAnimationProperties.camera_orbit = bpy.props.PointerProperty(type=prop.BIMCameraOrbitProperties)
    except Exception as _e:
        print("camera_orbit dynamic attach failed:", _e)

    # 4. UI classes are registered by main Bonsai system via 'classes' tuple
    # Do not call ui.register() here to avoid duplicates

    # 5. Register all operators
    operators.register()

    # 6. Register additional operators
    try:
        bpy.utils.register_class(operators.ResetCameraSettings)
    except Exception:
        pass

    # 7. Register menu functions
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

# --- Seed DEFAULT Animation Color Schemes group if none exists, and select it ---
try:
    import json
    scn = bpy.context.scene
    key = "BIM_AnimationColorSchemesSets"
    raw = scn.get(key, "{}")
    data = {}
    try:
        data = json.loads(raw) if isinstance(raw, str) else (raw or {})
    except Exception:
        data = {}
    # If the DEFAULT group doesn't exist or is empty, create it with full data.
    # This is more robust than just checking if `data` is empty.
    if not isinstance(data, dict) or not data.get("DEFAULT"):
        color_map = {
            "CONSTRUCTION": {"start": [1,1,1,0], "active": [0,1,0,1], "end": [0.3,1,0.3,1]},
            "INSTALLATION": {"start": [1,1,1,0], "active": [0,1,0,1], "end": [0.3,0.8,0.5,1]},
            "DEMOLITION": {"start": [1,1,1,1], "active": [1,0,0,1], "end": [0,0,0,0], "hide": True},
            "REMOVAL": {"start": [1,1,1,1], "active": [1,0,0,1], "end": [0,0,0,0], "hide": True},
            "DISPOSAL": {"start": [1,1,1,1], "active": [1,0,0,1], "end": [0,0,0,0], "hide": True},
            "DISMANTLE": {"start": [1,1,1,1], "active": [1,0,0,1], "end": [0,0,0,0], "hide": True},
            "OPERATION": {"start": [1,1,1,1], "active": [0,0,1,1], "end": [1,1,1,1]},
            "MAINTENANCE": {"start": [1,1,1,1], "active": [0,0,1,1], "end": [1,1,1,1]},
            "ATTENDANCE": {"start": [1,1,1,1], "active": [0,0,1,1], "end": [1,1,1,1]},
            "RENOVATION": {"start": [1,1,1,1], "active": [0,0,1,1], "end": [0.9,0.9,0.9,1]},
            "LOGISTIC": {"start": [1,1,1,1], "active": [1,1,0,1], "end": [1,0.8,0.3,1]},
            "MOVE": {"start": [1,1,1,1], "active": [1,1,0,1], "end": [0.8,0.6,0,1]},
            "NOTDEFINED": {"start": [0.7,0.7,0.7,1], "active": [0.5,0.5,0.5,1], "end": [0.3,0.3,0.3,1]},
            "USERDEFINED": {"start": [0.7,0.7,0.7,1], "active": [0.5,0.5,0.5,1], "end": [0.3,0.3,0.3,1]},
        }
        default_colortypes = []
        for name, colors in color_map.items():
            # Create the full profile data structure
            profile = {
                "name": name, "start_color": colors["start"], "in_progress_color": colors["active"], "end_color": colors["end"],
                "consider_start": False, "consider_active": True, "consider_end": True,
                "use_start_original_color": False, "use_active_original_color": False,
                "use_end_original_color": not colors.get("hide", False),
                "start_transparency": 0.0, "active_start_transparency": 0.0, "active_finish_transparency": 0.0,
                "active_transparency_interpol": 1.0, "end_transparency": 0.0,
                "hide_at_end": colors.get("hide", False)
            }
            default_colortypes.append(profile)
        data["DEFAULT"] = {"ColorTypes": default_colortypes}
        scn[key] = json.dumps(data)
    # try to select DEFAULT in the UI
    try:
        scn.BIMAnimationProperties.ColorType_groups = "DEFAULT"
    except Exception:
        pass
except Exception:
    pass

# === CACHE INVALIDATION HANDLER ===
# Solution to the persistent state bug between .blend files

def clear_animation_caches(*args):
    """Clears ALL animation caches when a new file is loaded"""
    print("[INFO] NEW FILE LOADED: Clearing all animation caches...")

    try:
        # 1. Invalidate IFC lookup cache
        from .utils import ifc_lookup
        ifc_lookup.invalidate_all_lookups()
        print("[INFO] IFC lookup cache cleared")
    except Exception as e:
        print(f"[ERROR] Could not clear IFC lookup cache: {e}")

    try:
        # 2. Invalidate performance cache
        from .utils import performance_cache
        performance_cache.invalidate_cache()
        print("[INFO] Performance cache cleared")
    except Exception as e:
        print(f"[ERROR] Could not clear performance cache: {e}")

    try:
        # 3. Invalidate global ColorType cache
        from .utils import colortype_cache
        colortype_cache.clear_global_cache()
        print("[INFO] ColorType cache cleared")
    except Exception as e:
        print(f"[ERROR] Could not clear ColorType cache: {e}")

    try:
        # 4. Invalidate HUD Legend cache
        from . import hud
        hud.invalidate_legend_hud_cache()
        print("[INFO] HUD Legend cache cleared")
    except Exception as e:
        print(f"[ERROR] Could not clear HUD Legend cache: {e}")

    try:
        # 5. Clear active animation flags
        import bpy
        if hasattr(bpy.context, 'scene'):
            if "is_snapshot_mode" in bpy.context.scene:
                del bpy.context.scene["is_snapshot_mode"]
                print("[INFO] Snapshot mode flag cleared")

            # Reset animation properties
            try:
                import bonsai.tool as tool
                anim_props = tool.Sequence.get_animation_props()
                anim_props.is_animation_created = False
                print("[INFO] Animation active flag cleared")
            except Exception:
                pass
    except Exception as e:
        print(f"[ERROR] Could not clear animation flags: {e}")

    print("[INFO] Cache invalidation complete - ready for new project!")

# Register handler to clear caches on file load
if clear_animation_caches not in bpy.app.handlers.load_post:
    bpy.app.handlers.load_post.append(clear_animation_caches)
    print("[INFO] Animation cache invalidation handler registered")


def unregister():
    # === REMOVE CACHE INVALIDATION HANDLERS ===
    try:
        if clear_animation_caches in bpy.app.handlers.load_post:
            bpy.app.handlers.load_post.remove(clear_animation_caches)
            print("[INFO] Animation cache invalidation handler removed")
        if detect_file_change in bpy.app.handlers.depsgraph_update_post:
            bpy.app.handlers.depsgraph_update_post.remove(detect_file_change)
            print("[INFO] File change detector removed")
    except Exception as e:
        print(f"[WARNING] Could not remove cache handlers: {e}")

    # Unregister in reverse order of registration
    # 7. Remove menu functions
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

    # 6. Unregister additional operators
    try:
        bpy.utils.unregister_class(operators.ResetCameraSettings)
    except Exception:
        pass

    # 5. Unregister operators from operators module
    operators.unregister()

    # 4. UI classes are unregistered by main Bonsai system via 'classes' tuple
    # Do not call ui.unregister() here to avoid duplicates

    # 3. Remove dynamic camera_orbit pointer and unregister camera orbit PG
    try:
        if hasattr(prop.BIMAnimationProperties, 'camera_orbit'):
            delattr(prop.BIMAnimationProperties, 'camera_orbit')
    except Exception:
        pass
    try:
        bpy.utils.unregister_class(prop.BIMCameraOrbitProperties)
    except Exception:
        pass

    # 2. Remove Scene properties
    if hasattr(bpy.types.Scene, 'show_saved_ColorTypes_section'):
        del bpy.types.Scene.show_saved_ColorTypes_section
    if hasattr(bpy.types.Scene, 'BIMWorkPlanProperties'):
        del bpy.types.Scene.BIMWorkPlanProperties
    if hasattr(bpy.types.Scene, 'BIMWorkScheduleProperties'):
        del bpy.types.Scene.BIMWorkScheduleProperties
    if hasattr(bpy.types.Scene, 'BIMTaskTreeProperties'):
        del bpy.types.Scene.BIMTaskTreeProperties
    if hasattr(bpy.types.Scene, 'BIMWorkCalendarProperties'):
        del bpy.types.Scene.BIMWorkCalendarProperties
    if hasattr(bpy.types.Scene, 'BIMStatusProperties'):
        del bpy.types.Scene.BIMStatusProperties
    if hasattr(bpy.types.Scene, 'DatePickerProperties'):
        del bpy.types.Scene.DatePickerProperties
    if hasattr(bpy.types.Scene, 'BIMAnimationProperties'):
        del bpy.types.Scene.BIMAnimationProperties
    if hasattr(bpy.types.TextCurve, 'BIMDateTextProperties'):
        del bpy.types.TextCurve.BIMDateTextProperties

    # 1. Unregister properties from prop module last
    prop.unregister()