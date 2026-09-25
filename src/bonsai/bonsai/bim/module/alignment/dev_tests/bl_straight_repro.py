# This file was generated with the assistance of an AI coding tool.
# Development test script for the alignment authoring work -- remove before the final PR (see README.md).

import sys, traceback, bpy
import bonsai.bim.handler, bonsai.tool as tool, ifcopenshell.api.alignment
try:
    bpy.ops.wm.read_homefile(app_template="")
    bpy.data.batch_remove(bpy.data.objects)
    bonsai.bim.handler.load_post(None)
    tool.Project.get_project_props().export_schema = "IFC4X3_ADD2"
    bpy.ops.bim.create_project()
    ifc = tool.Ifc.get()
    from bonsai.bim.module.alignment import operator as op_mod
    # path 1: built via the PI method with no interior PIs
    a = ifcopenshell.api.alignment.create_by_pi_method(ifc, "Straight", [(0.0, 0.0), (500.0, 100.0)], [], [], [])
    tool.Alignment.create_object_for_alignment(a)
    tool.Alignment.refresh_alignment_representation_object(a)
    o = tool.Ifc.get_object(a); o.select_set(True); bpy.context.view_layer.objects.active = o
    h = ifcopenshell.api.alignment.get_horizontal_layout(a)
    print("segments:", [s.DesignParameters.PredefinedType for s in tool.Alignment.get_real_layout_segments(h)])
    print("reconstruct:", op_mod._reconstruct_horizontal_pis(h))
    print("poll:", op_mod.ALIGN_OT_edit_horizontal_pis.poll(bpy.context))
    try:
        print("edit_horizontal_pis:", bpy.ops.align.edit_horizontal_pis())
    except Exception as e:
        print("edit_horizontal_pis raised:", e)
    print("markers:", [m.name for m in op_mod._find_pi_markers(a.id())])
except Exception:
    traceback.print_exc()
sys.stdout.flush()

# ---- after the fix: drag End, Apply, check the line followed; table path doesn't error either
try:
    ms = op_mod._find_pi_markers(a.id())
    assert [m.bonsai_pi_curve_marker.role for m in ms] == ["START", "END"], [m.name for m in ms]
    end = ms[-1]
    end.location = (400.0, 300.0, end.location.z)
    for x in bpy.context.selected_objects:
        x.select_set(False)
    end.select_set(True); bpy.context.view_layer.objects.active = end
    print("apply:", bpy.ops.align.apply_pi_curve())
    segs = tool.Alignment.get_real_layout_segments(ifcopenshell.api.alignment.get_horizontal_layout(a))
    dp = segs[0].DesignParameters
    import math
    end_pt = (dp.StartPoint.Coordinates[0] + dp.SegmentLength * math.cos(dp.StartDirection),
              dp.StartPoint.Coordinates[1] + dp.SegmentLength * math.sin(dp.StartDirection))
    print("segments:", [s.DesignParameters.PredefinedType for s in segs], "end:", tuple(round(v, 3) for v in end_pt))
    assert len(segs) == 1 and abs(end_pt[0] - 400) < 1e-3 and abs(end_pt[1] - 300) < 1e-3
    print("finish:", bpy.ops.align.finish_pi_editing())
    o = tool.Ifc.get_object(a)
    for x in bpy.context.selected_objects:
        x.select_set(False)
    o.select_set(True); bpy.context.view_layer.objects.active = o
    print("table:", bpy.ops.align.load_horizontal_pi_table(), "rows:", len(bpy.context.scene.CivilAlignmentProperties.horizontal_pi_rows))
    print("STRAIGHT_TEST_OK")
except Exception:
    traceback.print_exc()
    print("STRAIGHT_TEST_FAILED")
sys.stdout.flush()
