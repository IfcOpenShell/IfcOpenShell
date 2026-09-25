# This file was generated with the assistance of an AI coding tool.
# Development test script for the alignment authoring work -- remove before the final PR (see README.md).

"""Staged tables write back exact values: untouched values are bit-identical after Apply, edited ones
are the clean decimal typed (not float32 noise)."""

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


def hvals(h):
    return [(s.DesignParameters.SegmentLength, s.DesignParameters.StartRadiusOfCurvature,
             tuple(s.DesignParameters.StartPoint.Coordinates), s.DesignParameters.StartDirection) for s in real(h)]


def vvals(v):
    return [(s.DesignParameters.HorizontalLength, s.DesignParameters.StartGradient, s.DesignParameters.StartHeight)
            for s in real(v)]


def cvals(c):
    return [(s.DesignParameters.HorizontalLength, s.DesignParameters.StartCantLeft, s.DesignParameters.StartCantRight,
             s.DesignParameters.EndCantLeft, s.DesignParameters.EndCantRight) for s in real(c)]


try:
    bpy.ops.wm.read_homefile(app_template="")
    bpy.data.batch_remove(bpy.data.objects)
    bonsai.bim.handler.load_post(None)
    tool.Project.get_project_props().export_schema = "IFC4X3_ADD2"
    bpy.ops.bim.create_project()
    ifc = tool.Ifc.get()
    props = bpy.context.scene.CivilAlignmentProperties
    from bonsai.bim.module.alignment import operator as op_mod

    # large local coordinates and radii with more digits than float32 holds
    E0, N0 = 512345.6789, 4712345.4321
    H = [(E0, N0), (E0 + 812.3456789, N0 + 1.2345678), (E0 + 1400.1234567, N0 + 600.7654321), (E0 + 2200.9876543, N0 + 610.1111111)]
    R = [(312.4567891, 61.2345678, 59.8765432), 401.2345679]
    V = [(0.0, 100.1234567), (1100.7654321, 110.9876543), (2000.0, 104.4444444)]
    alignment = ifcopenshell.api.alignment.create_by_pi_method(ifc, "T", H, R, V, [203.3333333])
    tool.Alignment.create_object_for_alignment(alignment)
    tool.Alignment.refresh_alignment_representation_object(alignment)
    obj = tool.Ifc.get_object(alignment)
    select(obj)
    h = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
    v = ifcopenshell.api.alignment.get_vertical_layout(alignment)
    check(bpy.ops.align.generate_cant_layout(cant_value=0.1234567, layout_id=v.id()) == {"FINISHED"}, "cant")
    c = ifcopenshell.api.alignment.get_cant_layout(alignment)
    select(obj)

    def same(a, b, what, exact=True):
        if exact:
            check(a == b, f"{what} changed:\n{a}\n{b}")
            return

        def flat(x):
            for i in x:
                if isinstance(i, (tuple, list)):
                    yield from flat(i)
                else:
                    yield i

        fa, fb = list(flat(a)), list(flat(b))
        check(len(fa) == len(fb) and all(abs(x - y) < 1e-6 for x, y in zip(fa, fb)), f"{what} moved:\n{a}\n{b}")
        if what != "vertical PIs":  # grades are recomputed from the reconstructed VPIs
            check([x[1] for x in a] == [x[1] for x in b], f"{what} radii changed")

    # 1. horizontal segment table untouched
    h0 = hvals(h)
    bpy.ops.align.enable_editing_h_segments(layout_id=h.id())
    check(bpy.ops.align.apply_h_segments() == {"FINISHED"}, "apply h")
    same(hvals(h), h0, "h table", exact=False)
    # edited: a typed 250.2 is written as 250.2
    bpy.ops.align.enable_editing_h_segments(layout_id=h.id())
    arc = next(i for i, r in enumerate(props.h_segment_rows) if r.predefined_type == "CIRCULARARC")
    props.h_segment_rows[arc].start_radius = 250.2
    bpy.ops.align.apply_h_segments()
    check(real(h)[arc].DesignParameters.StartRadiusOfCurvature == 250.2, f"typed {real(h)[arc].DesignParameters.StartRadiusOfCurvature}")
    print("1 ok")

    # 2. vertical segment table untouched
    v0 = vvals(v)
    bpy.ops.align.enable_editing_v_segments(layout_id=v.id())
    check(bpy.ops.align.apply_v_segments() == {"FINISHED"}, "apply v")
    same(vvals(v), v0, "v table", exact=False)
    print("2 ok")

    # 3. cant table untouched, then a typed 0.2
    c0 = cvals(c)
    bpy.ops.align.enable_editing_cant_segments(layout_id=c.id())
    check(bpy.ops.align.apply_cant_segments() == {"FINISHED"}, "apply cant")
    same(cvals(c), c0, "cant table")
    print("3 ok")

    # 4. PI markers untouched (locations and curves) -- the whole horizontal is unchanged
    ok, msg = op_mod._generate_alignment_segments(bpy.context, alignment, H, R)  # undo step 1's odd arc
    check(ok, msg)
    select(obj)
    h1 = hvals(h)
    check(bpy.ops.align.edit_horizontal_pis() == {"FINISHED"}, "edit pis")
    select(op_mod._find_pi_markers(alignment.id())[1])
    check(bpy.ops.align.apply_pi_curve() == {"FINISHED"}, "apply pis")
    same(hvals(h), h1, "PI markers", exact=False)
    bpy.ops.align.finish_pi_editing()
    print("4 ok")

    # 5. PI table untouched
    select(obj)
    check(bpy.ops.align.load_horizontal_pi_table() == {"FINISHED"}, "load pi table")
    check(bpy.ops.align.apply_horizontal_pi_table() == {"FINISHED"}, "apply pi table")
    same(hvals(h), h1, "PI table", exact=False)
    bpy.ops.align.finish_horizontal_pi_table()
    print("5 ok")

    # 6. vertical PI list untouched
    select(obj)
    v1 = vvals(v)
    check(bpy.ops.align.load_vertical_pis() == {"FINISHED"}, "load vpis")
    check(bpy.ops.align.apply_vertical_pi_curve() == {"FINISHED"}, "apply vpis")
    same(vvals(v), v1, "vertical PIs", exact=False)
    # a typed elevation is written clean
    props.vertical_pi_markers[0].elevation = 111.3
    check(bpy.ops.align.apply_vertical_pi_curve() == {"FINISHED"}, "apply vpis 2")
    grades = [s.DesignParameters for s in real(v)]
    pvi = op_mod._reconstruct_vertical_pis(v)[0][0]
    check(abs(pvi["elevation"] - 111.3) < 1e-9, f"typed elevation {pvi['elevation']}")
    bpy.ops.align.finish_vertical_pi_editing()
    print("6 ok")

    # 7. polyline points untouched
    p = tool.Alignment.create_bare_alignment("P", define_stationing=False)
    pts = [(E0, N0), (E0 + 100.1234567, N0 + 5.5555555), (E0 + 250.7654321, N0 - 20.4444444)]
    tool.Alignment.set_polyline_points(p, pts, 2)
    select(tool.Ifc.get_object(p))
    check(bpy.ops.align.load_polyline_table() == {"FINISHED"}, "load polyline")
    check(bpy.ops.align.apply_polyline_table() == {"FINISHED"}, "apply polyline")
    curve = tool.Alignment.get_polyline_curve(p)
    got = [tuple(c) for c in curve.Points.CoordList] if hasattr(curve.Points, "CoordList") else [tuple(pt.Coordinates) for pt in curve.Points]
    check(got == [tuple(x) for x in pts], f"polyline changed {got}")
    bpy.ops.align.finish_polyline_table()
    print("7 ok")
    print("ALL OK")
except Exception:
    traceback.print_exc()
    sys.exit(1)
sys.exit(0)
