# This file was generated with the assistance of an AI coding tool.
# Development test script for the alignment authoring work -- remove before the final PR (see README.md).
#
# Selects a circular curve with align.select_h_segment in a real 3D viewport and saves screenshots
# of the highlight, point labels and curve data block at a few zoom levels, for visual checks:
#
#     set CURVE_DATA_SHOTS=C:\some\dir
#     blender --window-geometry 0 0 1400 900 --python ui_curve_data.py

import os
import traceback

import bpy
import mathutils

OUT = os.environ.get("CURVE_DATA_SHOTS", bpy.app.tempdir)
VIEWS = [("framed", (750.0, 250.0), 1800.0), ("zoomed", (900.0, 120.0), 500.0), ("far", (750.0, 250.0), 4000.0)]
state = {"step": 0}


def log(msg):
    with open(os.path.join(OUT, "ui_curve_data.txt"), "a", encoding="utf-8") as f:
        f.write(msg + "\n")


def viewport():
    window = bpy.context.window_manager.windows[0]
    area = next(a for a in window.screen.areas if a.type == "VIEW_3D")
    region = next(r for r in area.regions if r.type == "WINDOW")
    return window, area, region


def setup():
    import bonsai.tool as tool
    import ifcopenshell.api.alignment

    tool.Project.get_project_props().export_schema = "IFC4X3_ADD2"
    bpy.ops.bim.create_project()
    ifc = tool.Ifc.get()
    alignment = ifcopenshell.api.alignment.create_by_pi_method(
        ifc, "Main", [(0.0, 0.0), (1000.0, 0.0), (1000.0, 1000.0)], [500.0]
    )
    ifcopenshell.api.alignment.add_stationing_referent(ifc, "start", alignment, 0.0, 0.0)
    tool.Alignment.create_object_for_alignment(alignment)
    tool.Alignment.refresh_alignment_representation_object(alignment)
    horizontal = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
    arc = ifcopenshell.api.alignment.get_alignment_segment_nest(horizontal).RelatedObjects[1]

    window, area, region = viewport()
    area.spaces.active.overlay.show_floor = False
    with bpy.context.temp_override(window=window, area=area, region=region):
        log(f"select_h_segment -> {sorted(bpy.ops.align.select_h_segment(segment_id=arc.id()))}")


def set_view(location, distance):
    window, area, region = viewport()
    r3d = area.spaces.active.region_3d
    r3d.view_perspective = "ORTHO"
    r3d.view_rotation = mathutils.Quaternion()
    r3d.view_location = (location[0], location[1], 0.0)
    r3d.view_distance = distance
    area.tag_redraw()


def step():
    try:
        i = state["step"]
        if i == 0:
            setup()
        if 0 < i <= len(VIEWS):
            window, area, region = viewport()
            path = os.path.join(OUT, f"curve_data_{VIEWS[i - 1][0]}.png")
            with bpy.context.temp_override(window=window, area=area, region=region):
                bpy.ops.screen.screenshot_area(filepath=path)
            log(f"saved {path}")
        if i < len(VIEWS):
            set_view(*VIEWS[i][1:])
        if i == len(VIEWS):
            bpy.app.timers.register(lambda: bpy.ops.wm.quit_blender() and None, first_interval=0.5)
            return None
        state["step"] = i + 1
        return 1.0
    except Exception:
        log(f"EXCEPTION\n{traceback.format_exc()}")
        bpy.app.timers.register(lambda: bpy.ops.wm.quit_blender() and None, first_interval=0.5)
        return None


bpy.app.timers.register(step, first_interval=1.0)
