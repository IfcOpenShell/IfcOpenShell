# This file was generated with the assistance of an AI coding tool.
# Development test script for the alignment authoring work -- remove before the final PR (see README.md).

import math
import sys
import traceback
from types import SimpleNamespace

import bpy

import bonsai.bim.handler
import bonsai.tool as tool
import ifcopenshell.api.alignment


def check(cond, msg):
    if not cond:
        raise AssertionError(msg)


def select(obj):
    for o in bpy.context.selected_objects:
        o.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def fake(op_cls, *bases):
    attrs = {}
    for klass in reversed(op_cls.__mro__):
        if klass.__module__.startswith("bonsai.bim.module.alignment"):
            attrs.update({n: m for n, m in vars(klass).items() if (callable(m) or isinstance(m, property)) and not n.startswith("__")})
    cls = type("Fake", bases, attrs)
    op = cls()
    op.report = lambda level, msg: print("  report:", msg)
    return op


try:
    bpy.ops.wm.read_homefile(app_template="")
    bpy.data.batch_remove(bpy.data.objects)
    bonsai.bim.handler.load_post(None)
    tool.Project.get_project_props().export_schema = "IFC4X3_ADD2"
    bpy.ops.bim.create_project()
    ifc = tool.Ifc.get()
    A = tool.Alignment
    from bonsai.bim.module.alignment import operator as op_mod
    from bonsai.bim.module.model.polyline import PolylineOperator

    # horizontal: a spiral curve at PI 1; vertical with a parabolic curve, ending at the horizontal's end
    a = ifcopenshell.api.alignment.create_by_pi_method(
        ifc, "EX", [(0.0, 0.0), (500.0, 0.0), (900.0, 300.0)], [(200.0, 60.0, 60.0)], [(0.0, 100.0)], []
    )
    h = ifcopenshell.api.alignment.get_horizontal_layout(a)
    h_len = A.get_horizontal_alignment_length(h)
    v = ifcopenshell.api.alignment.add_vertical_layout(ifc, a)
    ok, msg, v = op_mod._generate_vertical_alignment_segments(
        bpy.context, a, [(0.0, 100.0), (400.0, 108.0), (h_len, 104.0)], [150.0], v_layout=v
    )
    check(ok, msg)
    tool.Alignment.create_object_for_alignment(a)
    tool.Alignment.refresh_alignment_representation_object(a)
    select(tool.Ifc.get_object(a))
    bpy.ops.align.generate_cant_layout(cant_value=0.1)
    cant = A.get_all_cant_layouts(a)[0]
    print("before: h", round(h_len, 3), "| v end", A.get_layout_end_distance(v), "| cant end", A.get_layout_end_distance(cant))
    check(A.get_length_mismatch(v) is None and A.get_length_mismatch(cant) is None, "should start matched")

    # ---- extend the horizontal (the draw tool's pieces, driven directly)
    op = fake(op_mod.ALIGN_OT_extend_horizontal_alignment, op_mod._CivilAngleInput, PolylineOperator)
    PolylineOperator.__init__(op)
    op.tool_state.use_default_container = False
    op.tool_state.plane_method = "XY"
    op.tool_state.is_input_on = False
    props_poly = tool.Model.get_polyline_props()
    if not props_poly.snap_mouse_point:
        props_poly.snap_mouse_point.add()
    check(op._load_existing(a) is None, "load existing")
    print("existing hpoints:", [tuple(round(c, 3) for c in p) for p in op._existing_hpoints], "radii:", op._existing_radii)
    ifc_unit = ifcopenshell.util.unit.calculate_unit_scale(ifc)
    anchors = [op_mod._local_ifc_to_world_point(ifc, ifc_unit, p) for p in op._existing_hpoints[-2:]]
    op._seeded = op_mod._seed_polyline_tool(op, bpy.context, anchors)
    check(op._seeded == 2, "seeded")
    check(op_mod._swallow_seed_backspace(op, SimpleNamespace(type="BACK_SPACE")), "backspace would delete an existing point")
    data = props_poly.insertion_polyline[0]
    for x, y in ((1300.0, 300.0), (1700.0, 600.0)):
        p = data.polyline_points.add()
        p.x, p.y, p.z = x, y, 0.0
    check(not op_mod._swallow_seed_backspace(op, SimpleNamespace(type="BACK_SPACE")), "backspace blocked on a new point")
    op._finish(bpy.context)
    tool.Polyline.clear_polyline()
    specs, skipped = op_mod._reconstruct_horizontal_pis(h)
    print("after extend PIs:", [(tuple(round(c, 3) for c in s["pi_local"]), s["curve_type"], s["radius"]) for s in specs])
    check(not skipped and len(specs) == 3, "wrong PI count after extend")
    check(specs[0]["curve_type"] == "SPIRAL_CIRCULAR_SPIRAL" and abs(specs[0]["radius"] - 200.0) < 1e-6, "PI 1 curve lost")
    check(specs[1]["curve_type"] == "TANGENT" and math.dist(specs[1]["pi_local"], (900.0, 300.0)) < 1e-3, "old end not a PI")
    end = A.get_alignment_start_end_points(a)[1]
    check(math.dist(end, (1700.0, 600.0)) < 1e-2, f"new end {end}")
    h_len2 = A.get_horizontal_alignment_length(h)
    print("h length", round(h_len, 3), "->", round(h_len2, 3))
    bpy.ops.align.finish_pi_editing()

    # ---- vertical and cant were left alone -> now short of the horizontal
    dv, dc = A.get_length_mismatch(v), A.get_length_mismatch(cant)
    print("mismatch: vertical", round(dv, 3), "| cant", round(dc, 3))
    check(dv < 0 and dc < 0 and abs(dv - (h_len - h_len2)) < 1e-3, "mismatch not detected")

    # ---- Match Horizontal Length on the vertical: only its last segment changes
    before = [(s.DesignParameters.PredefinedType, round(s.DesignParameters.HorizontalLength, 6))
              for s in A.get_real_layout_segments(v)]
    check(bpy.ops.align.match_horizontal_length(layout_id=v.id()) == {"FINISHED"}, "match vertical")
    after = [(s.DesignParameters.PredefinedType, round(s.DesignParameters.HorizontalLength, 6))
             for s in A.get_real_layout_segments(v)]
    print("vertical segments:", before, "->", after)
    check(after[:-1] == before[:-1] and after[-1][1] > before[-1][1], "vertical match changed the wrong segments")
    check(A.get_length_mismatch(v) is None and abs(A.get_layout_end_distance(v) - h_len2) < 1e-6, "vertical not matched")
    cant = A.get_all_cant_layouts(a)[0]
    check(bpy.ops.align.match_horizontal_length(layout_id=cant.id()) == {"FINISHED"}, "match cant")
    check(A.get_length_mismatch(cant) is None, "cant not matched")

    # ---- a layout too short to trim is refused, nothing changed
    #      (shorten the horizontal a lot by redrawing it short, then try to trim the vertical)
    ok, msg = op_mod._generate_alignment_segments(bpy.context, a, [(0.0, 0.0), (100.0, 0.0)], [])
    check(ok, msg)
    try:
        r = bpy.ops.align.match_horizontal_length(layout_id=v.id())
    except RuntimeError as e:
        r = str(e)
    print("trim too far:", r)
    check("too short" in str(r) and A.get_length_mismatch(v) > 0, "over-trim not refused")

    # ---- extend a vertical: redraw the horizontal long again, then continue the vertical to its end
    ok, msg = op_mod._generate_alignment_segments(bpy.context, a, [(0.0, 0.0), (3000.0, 0.0)], [])
    check(ok, msg)
    select(tool.Ifc.get_object(a))
    vop = fake(op_mod.ALIGN_OT_extend_vertical_alignment, op_mod._VerticalTypedInput)
    vop.layout_id = v.id()
    vop._points = []
    vop._init_typed_input()
    check(vop._load_existing(a) is None, "load vertical")
    vop._points.extend(vop._existing_vpoints)
    vop._seeded = len(vop._points)
    vop._alignment_id = a.id()
    old_end = vop._points[-1]
    vop._points.append((3000.0, 99.0))
    vop._finish(bpy.context)
    specs, skipped = op_mod._reconstruct_vertical_pis(v)
    print("vertical PIs after extend:", [(round(s["dist_along"], 3), round(s["elevation"], 3), s["curve_type"], s["curve_length"]) for s in specs])
    check(not skipped and specs[0]["curve_type"] == "PARABOLIC" and abs(specs[0]["curve_length"] - 150.0) < 1e-6, "vertical curve lost")
    check(specs[-1]["curve_type"] == "TANGENT" and abs(specs[-1]["dist_along"] - old_end[0]) < 1e-3, "old vertical end not a PI")
    check(abs(A.get_layout_end_distance(v) - 3000.0) < 1e-6, "vertical not extended to 3000")

    # ---- extend a 3D polyline alignment
    p = A.create_bare_alignment("PL", define_stationing=False)
    A.set_polyline_points(p, [(0.0, 0.0, 1.0), (100.0, 0.0, 2.0)], 3)
    select(tool.Ifc.get_object(p))
    pop = fake(op_mod.ALIGN_OT_extend_polyline_alignment, op_mod._CivilAngleInput, PolylineOperator)
    PolylineOperator.__init__(pop)
    pop.tool_state.use_default_container = False
    pop.tool_state.plane_method = None
    pop.tool_state.is_input_on = False
    check(pop._load_existing(p) is None, "load polyline")
    anchors = [op_mod._local_ifc_to_world_point_3d(ifc, ifc_unit, q) for q in pop._existing_points[-2:]]
    pop._seeded = op_mod._seed_polyline_tool(pop, bpy.context, anchors)
    pt = props_poly.insertion_polyline[0].polyline_points.add()
    pt.x, pt.y, pt.z = 150.0, 60.0, 4.0
    pop._finish(bpy.context)
    tool.Polyline.clear_polyline()
    pts, dim = A.get_polyline_points(p)
    print("polyline after extend:", pts, dim)
    check(dim == 3 and pts == [(0.0, 0.0, 1.0), (100.0, 0.0, 2.0), (150.0, 60.0, 4.0)], "polyline extend")
    print("EXTEND_TEST_OK")
except Exception:
    traceback.print_exc()
    print("EXTEND_TEST_FAILED")
sys.stdout.flush()
