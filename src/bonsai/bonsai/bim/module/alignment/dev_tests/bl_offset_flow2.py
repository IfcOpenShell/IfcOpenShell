# This file was generated with the assistance of an AI coding tool.
# Development test script for the alignment authoring work -- remove before the final PR (see README.md).

import sys
import traceback

import bpy

import bonsai.bim.handler
import bonsai.tool as tool
import ifcopenshell.api.alignment

sys.path.insert(0, __import__("os").path.dirname(__file__))
from bl_panel_render_rec import Rec


def check(cond, msg):
    if not cond:
        raise AssertionError(msg)


def select(obj):
    for o in bpy.context.selected_objects:
        o.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def authoring_buttons():
    """The operators ALIGN_PT_alignment_authoring offers for the active alignment."""
    from bonsai.bim.module.alignment import ui as ui_mod

    out = []
    panel = type("P", (), {"layout": Rec(out)})()
    ui_mod.ALIGN_PT_alignment_authoring.draw(panel, bpy.context)
    return [l.split()[1] for l in out if l.strip().startswith("op:") and "add_alignment" not in l and "remove_alignment" not in l]


def definitions():
    from bonsai.bim.module.alignment import operator as op_mod

    return [i[0] for i in op_mod._alignment_definition_items(None, bpy.context)]


try:
    bpy.ops.wm.read_homefile(app_template="")
    bpy.data.batch_remove(bpy.data.objects)
    bonsai.bim.handler.load_post(None)
    tool.Project.get_project_props().export_schema = "IFC4X3_ADD2"
    bpy.ops.bim.create_project()
    ifc = tool.Ifc.get()
    A = tool.Alignment
    props = bpy.context.scene.CivilAlignmentProperties
    import bonsai.bim.module.alignment as align_mod

    # ---- 3rd issue: with no alignments, Offset Curve isn't offered
    print("definitions, empty project:", definitions())
    check(definitions() == ["LAYOUTS", "POLYLINE"], "offset offered with nothing to offset from")

    # a standard alignment (horizontal + vertical)
    main = ifcopenshell.api.alignment.create_by_pi_method(
        ifc, "Main", [(0.0, 0.0), (100.0, 0.0), (200.0, 100.0)], [50.0], [(0.0, 10.0), (80.0, 12.0), (200.0, 10.0)], [0.0]
    )
    A.create_object_for_alignment(main)
    A.refresh_alignment_representation_object(main)
    print("definitions, with Main:", definitions())
    check("OFFSET" in definitions(), "offset not offered once there's a basis")

    # ---- 1st issue: an offset alignment is created complete; only Edit Offsets applies
    grad = next(c for c, _, d in A.get_offset_basis_candidates(None) if d == 3)
    r = bpy.ops.align.add_alignment(alignment_name="Lane", definition="OFFSET", offset_from=str(grad.id()),
                                    offset_lateral=3.5, offset_vertical=0.2)
    check(r == {"FINISHED"}, "add offset")
    lane = next(x for x in ifc.by_type("IfcAlignment") if x.Name == "Lane")
    check(A.is_offset_alignment(lane), "offset alignment not created complete")
    basis, rows = A.get_offset_values(lane)
    check(basis == grad and rows[0][1] == 3.5, f"offset values {rows}")
    select(tool.Ifc.get_object(lane))
    print("buttons for an offset alignment:", authoring_buttons())
    check(authoring_buttons() == ["align.load_offset_table"], "more than Edit Offsets offered")
    check(not bpy.ops.align.draw_horizontal_alignment.poll() and not bpy.ops.align.draw_polyline_alignment.poll(), "draw polls")

    # ---- 2nd issue: an offset of the offset, chosen at creation; editable even with Lane's table left open
    bpy.ops.align.load_offset_table()  # Lane's table, left open
    lane_curve = A.get_offset_curve(lane)
    r = bpy.ops.align.add_alignment(alignment_name="Edge", definition="OFFSET", offset_from=str(lane_curve.id()),
                                    offset_lateral=2.0, define_stationing=False)
    check(r == {"FINISHED"}, "add offset of offset")
    edge = next(x for x in ifc.by_type("IfcAlignment") if x.Name == "Edge")
    check(A.get_offset_values(edge)[0] == lane_curve, "edge basis")
    # moving to Edge (the selection handler) closes the table left open for Lane
    align_mod._auto_finish_unrelated_tables(bpy.context.scene, tool.Ifc.get_object(edge), edge)
    check(not props.offset_value_rows, "Lane's table not closed when Edge was selected")
    select(tool.Ifc.get_object(edge))
    check(bpy.ops.align.load_offset_table() == {"FINISHED"}, "can't edit Edge's offsets")
    bpy.ops.align.add_offset_value_row()
    props.offset_value_rows[1].lateral = 4.0
    check(bpy.ops.align.apply_offset_table() == {"FINISHED"}, "apply Edge")
    print("Edge offsets:", A.get_offset_values(edge)[1])
    check(len(A.get_offset_values(edge)[1]) == 2, "Edge offsets not added")
    bpy.ops.align.finish_offset_table()

    # ---- a new polyline alignment offers only Draw Polyline
    r = bpy.ops.align.add_alignment(alignment_name="Survey", definition="POLYLINE")
    survey = next(x for x in ifc.by_type("IfcAlignment") if x.Name == "Survey")
    select(tool.Ifc.get_object(survey))
    print("buttons for a new polyline alignment:", authoring_buttons())
    check("align.draw_horizontal_alignment" not in authoring_buttons(), "PI draw offered for a polyline")
    check("align.draw_polyline_alignment" in authoring_buttons(), "Draw Polyline missing")
    check(not bpy.ops.align.draw_horizontal_alignment.poll() and bpy.ops.align.draw_polyline_alignment.poll(), "polls")

    # ---- a standard alignment still offers the PI tools only
    select(tool.Ifc.get_object(main))
    print("buttons for a layout alignment:", authoring_buttons())
    check("align.draw_horizontal_alignment" in authoring_buttons() and "align.load_offset_table" not in authoring_buttons(), "layout buttons")
    print("OFFSET_FLOW2_OK")
except Exception:
    traceback.print_exc()
    print("OFFSET_FLOW2_FAILED")
sys.stdout.flush()
