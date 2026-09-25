# This file was generated with the assistance of an AI coding tool.
# Development test script for the alignment authoring work -- remove before the final PR (see README.md).

"""Cant follows horizontal edits: one cant segment per horizontal segment, kept GlobalIds, kept
per-arc cant values."""

import sys
import traceback

import bpy

import bonsai.bim.handler
import bonsai.tool as tool
import ifcopenshell.api.alignment


def check(cond, msg):
    if not cond:
        raise AssertionError(msg)


def real(layout):
    return tool.Alignment.get_real_layout_segments(layout)


def select(obj):
    for o in bpy.context.selected_objects:
        o.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def in_step(h, c):
    hs, cs = real(h), real(c)
    check(len(hs) == len(cs), f"counts {len(hs)} vs {len(cs)}")
    dist = 0.0
    for hseg, cseg in zip(hs, cs):
        hdp, cdp = hseg.DesignParameters, cseg.DesignParameters
        check(abs(hdp.SegmentLength - cdp.HorizontalLength) < 1e-9, "length")
        check(abs(cdp.StartDistAlong - dist) < 1e-6, "dist along")
        check(cdp.PredefinedType == tool.Alignment.CANT_TYPE_FOR_HORIZONTAL_TYPE[hdp.PredefinedType], "type")
        dist += cdp.HorizontalLength
    # continuous: each segment starts where the previous one ended
    prev_end = None
    for cseg in cs:
        dp = cseg.DesignParameters
        start = (dp.StartCantLeft, dp.StartCantRight)
        if prev_end is not None:
            check(all(abs(a - b) < 1e-9 for a, b in zip(start, prev_end)), f"cant jump {prev_end} -> {start}")
        prev_end = (
            dp.EndCantLeft if dp.EndCantLeft is not None else dp.StartCantLeft,
            dp.EndCantRight if dp.EndCantRight is not None else dp.StartCantRight,
        )


def arcs(c):
    return [(s.GlobalId, s.DesignParameters.StartCantLeft, s.DesignParameters.StartCantRight) for s in real(c)
            if s.DesignParameters.StartCantLeft or s.DesignParameters.StartCantRight]


try:
    bpy.ops.wm.read_homefile(app_template="")
    bpy.data.batch_remove(bpy.data.objects)
    bonsai.bim.handler.load_post(None)
    tool.Project.get_project_props().export_schema = "IFC4X3_ADD2"
    bpy.ops.bim.create_project()
    ifc = tool.Ifc.get()
    props = bpy.context.scene.CivilAlignmentProperties
    from bonsai.bim.module.alignment import operator as op_mod

    H = [(0.0, 0.0), (800.0, 0.0), (1400.0, 600.0), (2200.0, 600.0), (3000.0, 0.0)]
    R = [(300.0, 60.0, 60.0), (400.0, 80.0, 80.0), (350.0, 70.0, 70.0)]
    V = [(0.0, 100.0), (1500.0, 110.0), (3000.0, 108.0)]
    alignment = ifcopenshell.api.alignment.create_by_pi_method(ifc, "T", H, R, V, [200.0])
    tool.Alignment.create_object_for_alignment(alignment)
    tool.Alignment.refresh_alignment_representation_object(alignment)
    obj = tool.Ifc.get_object(alignment)
    select(obj)
    h = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
    v = ifcopenshell.api.alignment.get_vertical_layout(alignment)
    check(bpy.ops.align.generate_cant_layout(cant_value=0.1, layout_id=v.id()) == {"FINISHED"}, "gen cant")
    c = ifcopenshell.api.alignment.get_cant_layout(alignment)
    in_step(h, c)

    # hand-tune the second arc's cant (both rails, symmetric) through the cant table
    check(bpy.ops.align.enable_editing_cant_segments(layout_id=c.id()) == {"FINISHED"}, "enable cant")
    arc_rows = [i for i, s in enumerate(real(h)) if s.DesignParameters.PredefinedType == "CIRCULARARC"]
    k = arc_rows[1]
    rows = props.cant_segment_rows
    rows[k].start_cant_left, rows[k].start_cant_right = -0.04, 0.03  # a right turn... raised left below
    rows[k - 1].end_cant_left, rows[k - 1].end_cant_right = -0.04, 0.03
    rows[k + 1].start_cant_left, rows[k + 1].start_cant_right = -0.04, 0.03
    check(bpy.ops.align.apply_cant_segments() == {"FINISHED"}, "apply cant")
    tuned = real(c)[k].DesignParameters
    tuned_values = (tuned.StartCantLeft, tuned.StartCantRight)
    print("tuned arc", tuned_values, "radius", real(h)[k].DesignParameters.StartRadiusOfCurvature)
    c0 = [s.GlobalId for s in real(c)]

    # 1. radius change: every cant GlobalId kept, lengths follow, tuned arc kept
    R1 = [(250.0, 60.0, 60.0), R[1], R[2]]
    ok, msg = op_mod._generate_alignment_segments(bpy.context, alignment, H, R1)
    check(ok, msg)
    in_step(h, c)
    check([s.GlobalId for s in real(c)] == c0, "radius change cant guids")
    dp = real(c)[k].DesignParameters
    check((dp.StartCantLeft, dp.StartCantRight) == tuned_values, f"tuned arc lost {(dp.StartCantLeft, dp.StartCantRight)}")
    print("1 ok")

    # 2. delete PI 1: its 4 cant segments go, the rest are kept, the tuned arc too
    ok, msg = op_mod._generate_alignment_segments(bpy.context, alignment, [H[0], H[2], H[3], H[4]], [R[1], R[2]])
    check(ok, msg)
    in_step(h, c)
    c2 = [s.GlobalId for s in real(c)]
    check(c2 == c0[4:], f"delete cant guids")
    print("2 ok", arcs(c))

    # 3. insert a spiralled PI back: 4 new cant segments, its arc at the design cant (0.1)
    ok, msg = op_mod._generate_alignment_segments(bpy.context, alignment, H, R)
    check(ok, msg)
    in_step(h, c)
    c3 = [s.GlobalId for s in real(c)]
    check(c3[4:] == c2 and not set(c3[:4]) & set(c0 + c2), "insert cant guids")
    new_arc = real(c)[2].DesignParameters
    check(abs(max(abs(new_arc.StartCantLeft), abs(new_arc.StartCantRight)) - 0.1) < 1e-6, f"new arc cant {new_arc}")
    print("3 ok", arcs(c))

    # 4. spiral family change through the segment table: cant type follows, guids kept
    check(bpy.ops.align.enable_editing_h_segments(layout_id=h.id()) == {"FINISHED"}, "enable h")
    props.h_segment_rows[1].predefined_type = "BLOSSCURVE"
    check(bpy.ops.align.apply_h_segments() == {"FINISHED"}, "apply h")
    in_step(h, c)
    check([s.GlobalId for s in real(c)] == c3, "type change guids")
    check(real(c)[1].DesignParameters.PredefinedType == "BLOSSCURVE", "bloss")
    print("4 ok")

    # 5. a table row added to the horizontal: a new cant segment for it
    check(bpy.ops.align.enable_editing_h_segments(layout_id=h.id()) == {"FINISHED"}, "enable h 2")
    props.active_h_segment_row_index = len(props.h_segment_rows) - 1
    bpy.ops.align.add_segment_row(kind="HORIZONTAL")
    check(bpy.ops.align.apply_h_segments() == {"FINISHED"}, "apply h 2")
    in_step(h, c)
    check([s.GlobalId for s in real(c)][:-1] == c3, "added row")
    print("5 ok")
    print("ALL OK")
except Exception:
    traceback.print_exc()
    sys.exit(1)
sys.exit(0)
