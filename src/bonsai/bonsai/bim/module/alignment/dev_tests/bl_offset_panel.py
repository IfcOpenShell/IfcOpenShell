# This file was generated with the assistance of an AI coding tool.
# Development test script for the alignment authoring work -- remove before the final PR (see README.md).

import sys, traceback, bpy
import bonsai.bim.handler, bonsai.tool as tool, ifcopenshell.api.alignment
sys.path.insert(0, __import__("os").path.dirname(__file__))
from bl_panel_render_rec import Rec
try:
    bpy.ops.wm.read_homefile(app_template=""); bpy.data.batch_remove(bpy.data.objects); bonsai.bim.handler.load_post(None)
    tool.Project.get_project_props().export_schema = "IFC4X3_ADD2"; bpy.ops.bim.create_project()
    ifc = tool.Ifc.get(); A = tool.Alignment
    base = ifcopenshell.api.alignment.create_by_pi_method(ifc, "Main", [(0.0, 0.0), (100.0, 0.0), (200.0, 100.0)], [50.0], [(0.0, 10.0), (80.0, 12.0), (200.0, 10.0)], [0.0])
    A.create_object_for_alignment(base); A.refresh_alignment_representation_object(base)
    lane = A.create_bare_alignment("Lane", define_stationing=False)
    grad = next(c for c, _, d in A.get_offset_basis_candidates(lane) if d == 3)
    A.set_offset_values(lane, grad, [(0.0, 3.5, 0.2, None), (100.0, 5.0, 0.2, None)])
    o = tool.Ifc.get_object(lane)
    for x in bpy.context.selected_objects: x.select_set(False)
    o.select_set(True); bpy.context.view_layer.objects.active = o
    from bonsai.bim.module.alignment import ui as ui_mod
    props = bpy.context.scene.CivilAlignmentProperties
    for title in ("listed", "editing"):
        if title == "editing":
            bpy.ops.align.load_offset_table()
        out = []
        ui_mod.ALIGN_PT_alignment_segments._draw_offset(None, Rec(out), props, lane)
        print("====", title); print(chr(10).join(out))
    print("PANEL_DONE")
except Exception:
    traceback.print_exc()
sys.stdout.flush()
