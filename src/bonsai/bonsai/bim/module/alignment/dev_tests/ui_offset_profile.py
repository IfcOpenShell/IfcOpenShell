# This file was generated with the assistance of an AI coding tool.
# Development test script for the alignment authoring work -- remove before the final PR (see README.md).

"""Run in Blender's normal UI mode (not --background): open the vertical profile view for a 3D offset
curve alignment the way its Show Profile button does, let it draw, and save a screenshot to
%TEMP%\\align_ui_offset_profile.png. The result is written to %TEMP%\\align_ui_offset_profile.txt.
Quits Blender afterwards."""

import os
import traceback

import bpy

TEMP = os.environ.get("TEMP", ".")
RESULT = os.path.join(TEMP, "align_ui_offset_profile.txt")
SHOT = os.path.join(TEMP, "align_ui_offset_profile.png")


def log(msg):
    with open(RESULT, "a", encoding="utf-8") as f:
        f.write(msg + "\n")


def select(obj):
    for o in bpy.context.selected_objects:
        o.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def view3d():
    window = bpy.context.window_manager.windows[0]
    area = next(a for a in window.screen.areas if a.type == "VIEW_3D")
    region = next(r for r in area.regions if r.type == "WINDOW")
    return window, area, region


def open_profile():
    try:
        import bonsai.tool as tool
        import ifcopenshell.api.alignment

        tool.Project.get_project_props().export_schema = "IFC4X3_ADD2"
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()
        A = tool.Alignment
        main = ifcopenshell.api.alignment.create_by_pi_method(
            ifc, "Main", [(0.0, 0.0), (100.0, 0.0), (200.0, 100.0)], [50.0],
            [(0.0, 10.0), (80.0, 12.0), (200.0, 10.0)], [40.0],
        )
        A.create_object_for_alignment(main)
        A.refresh_alignment_representation_object(main)
        gradient = next(c for c, _, d in A.get_offset_basis_candidates(None) if d == 3)
        bpy.ops.align.add_alignment(
            alignment_name="Lane", definition="OFFSET", offset_from=str(gradient.id()),
            offset_lateral=3.0, offset_vertical=0.5,
        )
        lane = next(x for x in ifc.by_type("IfcAlignment") if x.Name == "Lane")
        select(tool.Ifc.get_object(lane))
        A.set_offset_values(lane, gradient, [(0.0, 3.0, 0.5, None), (150.0, 6.0, -1.0, None)])
        window, area, region = view3d()
        with bpy.context.temp_override(window=window, area=area, region=region):
            result = bpy.ops.align.show_vertical_profile()
        log(f"show_vertical_profile: {result}")
    except Exception:
        log("ERROR\n" + traceback.format_exc())
    bpy.app.timers.register(screenshot, first_interval=2.0)


def screenshot():
    try:
        from bonsai.bim.module.alignment.decorator import VerticalProfileDecorator as dec

        log(f"installed: {dec.is_installed} verticals: {dec.available_verticals} spans: {len(dec.segments_info)}")
        window = bpy.context.window_manager.windows[0]
        area = next(a for a in window.screen.areas if a.type == "VIEW_3D")
        with bpy.context.temp_override(window=window, area=area):
            bpy.ops.screen.screenshot(filepath=SHOT)
        log(f"screenshot: {SHOT}")
    except Exception:
        log("ERROR\n" + traceback.format_exc())
    bpy.app.timers.register(lambda: bpy.ops.wm.quit_blender() and None, first_interval=0.5)


if os.path.exists(RESULT):
    os.remove(RESULT)
bpy.app.timers.register(open_profile, first_interval=1.0)
