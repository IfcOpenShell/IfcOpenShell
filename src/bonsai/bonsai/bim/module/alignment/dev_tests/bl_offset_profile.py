# This file was generated with the assistance of an AI coding tool.
# Development test script for the alignment authoring work -- remove before the final PR (see README.md).
#
# The profile view for a 3D offset curve alignment (REQUIREMENTS.md §5.2): its actual elevations,
# split at its offsets; a 2D offset curve has none.

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


def offset_section(alignment):
    from bonsai.bim.module.alignment import ui as ui_mod

    out = []
    panel = type("P", (), {})()
    ui_mod.ALIGN_PT_alignment_segments._draw_offset(panel, Rec(out), bpy.context.scene.CivilAlignmentProperties, alignment)
    return out


def elevation_at(spans, d):
    for start, end, pts in spans:
        for (d0, e0), (d1, e1) in zip(pts[:-1], pts[1:]):
            if d0 - 1e-9 <= d <= d1 + 1e-9:
                return e0 + (e1 - e0) * (d - d0) / (d1 - d0)
    raise AssertionError(f"{d} not in the profile")


try:
    bpy.ops.wm.read_homefile(app_template="")
    bpy.data.batch_remove(bpy.data.objects)
    bonsai.bim.handler.load_post(None)
    tool.Project.get_project_props().export_schema = "IFC4X3_ADD2"
    bpy.ops.bim.create_project()
    ifc = tool.Ifc.get()
    A = tool.Alignment
    from bonsai.bim.module.alignment import operator as op_mod
    from bonsai.bim.module.alignment.decorator import VerticalProfileDecorator as dec

    main = ifcopenshell.api.alignment.create_by_pi_method(
        ifc, "Main", [(0.0, 0.0), (100.0, 0.0), (200.0, 100.0)], [50.0], [(0.0, 10.0), (80.0, 12.0), (200.0, 10.0)], [40.0]
    )
    A.create_object_for_alignment(main)
    A.refresh_alignment_representation_object(main)
    gradient = next(c for c, _, d in A.get_offset_basis_candidates(None) if d == 3)
    horizontal = next(c for c, _, d in A.get_offset_basis_candidates(None) if d == 2)

    # ---- a 3D offset: 3 left / 0.5 up at the start, easing to 6 left / 1 down at 150
    bpy.ops.align.add_alignment(
        alignment_name="Lane", definition="OFFSET", offset_from=str(gradient.id()), offset_lateral=3.0, offset_vertical=0.5
    )
    lane = next(x for x in ifc.by_type("IfcAlignment") if x.Name == "Lane")
    select(tool.Ifc.get_object(lane))
    bpy.ops.align.load_offset_table()
    bpy.ops.align.add_offset_value_row()
    rows = bpy.context.scene.CivilAlignmentProperties.offset_value_rows
    rows[1].distance_along, rows[1].lateral, rows[1].vertical = 150.0, 6.0, -1.0
    check(bpy.ops.align.apply_offset_table() == {"FINISHED"}, "apply offsets")
    bpy.ops.align.finish_offset_table()
    print("offsets:", A.get_offset_values(lane)[1])

    spans = A.get_offset_profile(lane)
    print("spans:", [(round(s, 3), round(e, 3), len(p)) for s, e, p in spans])
    check([(round(s, 3), round(e, 3)) for s, e, _ in spans] == [(0.0, 150.0), (150.0, 200.0)], "spans not split at the offsets")
    # the geometry kernel's own values for this curve (checked independently of Bonsai)
    for d, expected in ((0.0, 10.4998), (40.0, 11.1), (80.0, 11.4917), (150.0, 9.8335)):
        e = elevation_at(spans, d)
        print(f"  elevation at {d}: {e:.4f} (kernel {expected})")
        check(abs(e - expected) < 2e-3, f"elevation at {d}")
    check(all(len(p) >= 50 for _, _, p in spans), "profile sampled too coarsely")

    dec._compute_profile(lane)
    print("verticals:", dec.available_verticals)
    check(len(dec.available_verticals) == 1 and dec.available_verticals[0][1] == "Lane", "one profile, named for the alignment")
    labels = [(i["start_label"], i["end_label"]) for i in dec.segments_info]
    print("labels:", labels, "| P.V.I.s:", [i["pvi"] for i in dec.segments_info])
    check(labels == [("Start", "Offset 2"), ("Offset 2", "End")], "labels")
    check(all(i["pvi"] is None for i in dec.segments_info), "an offset span got a P.V.I.")
    # the curve itself ends where Main's vertical does (200), but the canvas runs out to the end of
    # Main's horizontal (239.27), as Main's own profile view does -- showing where the offset stops short
    check(abs(dec.segments_info[-1]["dist"] + dec.segments_info[-1]["h_len"] - 200.0) < 1e-3, "offset curve's end")
    main_length = A.get_horizontal_alignment_length(ifcopenshell.api.alignment.get_horizontal_layout(main))
    check(abs(dec.dist_min) < 1e-6 and abs(dec.dist_max - main_length) < 1e-6, f"distance range {dec.dist_min}..{dec.dist_max}")
    # the reference's 2.5% grade, less the vertical offset easing from +0.5 to -1.0 over 150 (-1%)
    check(abs(dec.segments_info[0]["g_start"] - 0.015) < 1e-3, f"start grade {dec.segments_info[0]['g_start']}")

    panel = offset_section(lane)
    check(any("show_vertical_profile" in l for l in panel), "no Show Profile for a 3D offset")

    # ---- an offset of it follows it, 0.3 further up (square to the slope)
    lane_curve = A.get_offset_curve(lane)
    bpy.ops.align.add_alignment(
        alignment_name="Edge", definition="OFFSET", offset_from=str(lane_curve.id()), offset_lateral=2.0, offset_vertical=0.3
    )
    edge = next(x for x in ifc.by_type("IfcAlignment") if x.Name == "Edge")
    edge_spans = A.get_offset_profile(edge)
    for d in (0.0, 80.0, 199.0):
        diff = elevation_at(edge_spans, d) - elevation_at(spans, d)
        print(f"  edge - lane at {d}: {diff:.4f}")
        check(abs(diff - 0.3) < 1e-3, f"offset of offset at {d}")

    # ---- a 2D offset: nothing to profile, and the view doesn't choke on it
    bpy.ops.align.add_alignment(
        alignment_name="Flat", definition="OFFSET", offset_from=str(horizontal.id()), offset_lateral=-4.0
    )
    flat = next(x for x in ifc.by_type("IfcAlignment") if x.Name == "Flat")
    check(A.get_offset_profile(flat) == [], "2D offset has a profile")
    dec._compute_profile(flat)
    check(not dec.available_verticals and not dec.segments_info, "2D offset profile not empty")

    # ---- every offset chain ends on the reference's horizontal: from the vertical (3D), through
    #      another offset, or straight from the horizontal (2D)
    main_h = ifcopenshell.api.alignment.get_horizontal_layout(main)
    check(A.get_reference_horizontal_layout(main) == main_h, "a layout alignment's own horizontal")
    for x in (lane, edge, flat):
        check(A.get_reference_horizontal_layout(x) == main_h, f"{x.Name} doesn't resolve to Main's horizontal")
        check(ifcopenshell.api.alignment.get_horizontal_layout(x) is None, f"{x.Name} got a layout of its own")
    main_length = A.get_horizontal_alignment_length(main_h)
    print("2D offset canvas:", dec.dist_min, "..", dec.dist_max, "| Main's horizontal:", main_length)
    check(abs(dec.dist_max - main_length) < 1e-6, "2D offset's canvas not framed to the reference's horizontal")
    panel = offset_section(flat)
    check(any("no elevations" in l for l in panel) and not any("show_vertical_profile" in l for l in panel), "2D panel")

    # ---- the reference's own profile is unchanged
    dec._compute_profile(main)
    check(all(i["type"] != "OFFSET" for i in dec.segments_info) and len(dec.available_verticals) == 1, "reference profile")

    print("ALL OK")
except Exception:
    traceback.print_exc()
    print("OFFSET_PROFILE_FAILED")
    sys.stdout.flush()
    sys.exit(1)
sys.stdout.flush()
