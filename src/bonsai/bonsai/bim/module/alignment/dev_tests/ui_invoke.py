# This file was generated with the assistance of an AI coding tool.
# Development test script for the alignment authoring work -- remove before the final PR (see README.md).

"""Run in Blender's normal UI mode (not --background): invoke one alignment draw/extend operator the
way its button does, on a real 3D viewport, and report whether it started cleanly. The operator to
test is given by the ALIGN_UI_TEST environment variable. Quits Blender afterwards."""

import os
import sys
import traceback

import bpy

RESULT = os.path.join(os.environ.get("TEMP", "."), "align_ui_invoke_result.txt")


def log(msg):
    with open(RESULT, "a", encoding="utf-8") as f:
        f.write(msg + "\n")


def select(obj):
    for o in bpy.context.selected_objects:
        o.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def run():
    which = os.environ.get("ALIGN_UI_TEST", "draw_horizontal_alignment")
    try:
        import bonsai.tool as tool
        import ifcopenshell.api.alignment

        tool.Project.get_project_props().export_schema = "IFC4X3_ADD2"
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()
        A = tool.Alignment
        from bonsai.bim.module.alignment import operator as op_mod

        kwargs = {}
        if which == "add_alignment":
            a = ifcopenshell.api.alignment.create_by_pi_method(
                ifc, "Main", [(0.0, 0.0), (100.0, 0.0), (200.0, 100.0)], [50.0],
                [(0.0, 10.0), (80.0, 12.0), (200.0, 10.0)], [0.0],
            )
            A.create_object_for_alignment(a)
            A.refresh_alignment_representation_object(a)
            kwargs["definition"] = "OFFSET"
        elif which in ("draw_horizontal_alignment",):
            bpy.ops.align.add_alignment(alignment_name="New", definition="LAYOUTS")
        elif which in ("draw_polyline_alignment",):
            bpy.ops.align.add_alignment(alignment_name="Poly", definition="POLYLINE")
        elif which == "extend_polyline_alignment":
            a = A.create_bare_alignment("Poly", define_stationing=False)
            A.set_polyline_points(a, [(0.0, 0.0), (100.0, 0.0)], 2)
            select(tool.Ifc.get_object(a))
        else:
            a = ifcopenshell.api.alignment.create_by_pi_method(
                ifc, "Main", [(0.0, 0.0), (100.0, 0.0), (200.0, 100.0)], [50.0],
                [(0.0, 10.0), (80.0, 12.0), (200.0, 10.0)], [0.0],
            )
            A.create_object_for_alignment(a)
            A.refresh_alignment_representation_object(a)
            select(tool.Ifc.get_object(a))
            if which == "extend_vertical_alignment":
                kwargs["layout_id"] = ifcopenshell.api.alignment.get_vertical_layout(a).id()
            if which == "move_pi_marker":
                bpy.ops.align.edit_horizontal_pis()
                select(op_mod._find_pi_markers(a.id())[1])

        window = bpy.context.window_manager.windows[0]
        area = next(a for a in window.screen.areas if a.type == "VIEW_3D")
        region = next(r for r in area.regions if r.type == "WINDOW")
        with bpy.context.temp_override(window=window, area=area, region=region):
            op = getattr(bpy.ops.align, which)
            log(f"{which}: poll={op.poll()}")
            result = op("INVOKE_DEFAULT", **kwargs)
        log(f"{which}: invoke -> {sorted(result)}")
    except Exception:
        log(f"{which}: EXCEPTION\n{traceback.format_exc()}")
    bpy.app.timers.register(lambda: bpy.ops.wm.quit_blender() and None, first_interval=1.0)
    return None


bpy.app.timers.register(run, first_interval=1.0)
