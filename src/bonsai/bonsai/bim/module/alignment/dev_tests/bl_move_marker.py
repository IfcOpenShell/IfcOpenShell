# This file was generated with the assistance of an AI coding tool.
# Development test script for the alignment authoring work -- remove before the final PR (see README.md).

import math
import sys
import traceback

import bpy

import bonsai.bim.handler
import bonsai.tool as tool
import ifcopenshell.api.alignment


def check(cond, msg):
    if not cond:
        raise AssertionError(msg)


def near(a, b, tol=1e-3):
    return abs(a[0] - b[0]) < tol and abs(a[1] - b[1]) < tol


try:
    bpy.ops.wm.read_homefile(app_template="")
    bpy.data.batch_remove(bpy.data.objects)
    bonsai.bim.handler.load_post(None)
    tool.Project.get_project_props().export_schema = "IFC4X3_ADD2"
    bpy.ops.bim.create_project()
    ifc = tool.Ifc.get()

    alignment = ifcopenshell.api.alignment.create_by_pi_method(
        ifc, "MV", [(0.0, 0.0), (1000.0, 0.0), (1000.0, 1000.0)], [0.0], [], []
    )
    tool.Alignment.create_object_for_alignment(alignment)
    tool.Alignment.refresh_alignment_representation_object(alignment)
    obj = tool.Ifc.get_object(alignment)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    check(bpy.ops.align.edit_horizontal_pis() == {"FINISHED"}, "edit_horizontal_pis failed")

    from bonsai.bim.module.alignment import operator as op_mod
    from bonsai.bim.module.model.polyline import PolylineOperator

    markers = op_mod._find_pi_markers(alignment.id())
    print("markers:", [(m.name, tuple(round(v, 3) for v in m.location[:2])) for m in markers])
    check(len(markers) == 3, "expected Start, PI 1, End")

    # anchors: PI 1 from Start; End from Start->PI 1; Start backwards from End->PI 1
    anchors = lambda i: [tuple(v[:2]) for v in op_mod._move_marker_anchors(markers, i)]
    check(anchors(1) == [(0.0, 0.0)], f"PI 1 anchors {anchors(1)}")
    check(anchors(2) == [(0.0, 0.0), (1000.0, 0.0)], f"End anchors {anchors(2)}")
    check(anchors(0) == [(1000.0, 1000.0), (1000.0, 0.0)], f"Start anchors {anchors(0)}")

    Op = op_mod.ALIGN_OT_move_pi_marker
    attrs = {}
    for klass in reversed(Op.__mro__):
        if klass is PolylineOperator or klass.__module__.startswith("bonsai.bim.module.alignment"):
            attrs.update({n: m for n, m in vars(klass).items() if callable(m) and not n.startswith("__")})
    Fake = type("Fake", (), attrs)

    polyline_props = tool.Model.get_polyline_props()
    if not polyline_props.snap_mouse_point:
        polyline_props.snap_mouse_point.add()

    def move(marker_obj, d, a, mouse_side):
        """Seed from the marker's neighbours, type D and A (mouse picks the side), place."""
        op = Fake()
        PolylineOperator.__init__(op)
        op._seeded = 0
        op._bearing_handle = None
        op._last_mouse_pos = (0, 0)
        op.report = lambda level, msg: print("report:", msg)
        op.tool_state.use_default_container = False
        op.tool_state.plane_method = "XY"
        op.tool_state.is_input_on = False
        ms = op_mod._find_pi_markers(alignment.id())
        op._marker_name = marker_obj.name
        op._seeded = op._seed_anchor_points(bpy.context, op_mod._move_marker_anchors(ms, ms.index(marker_obj)))
        check(len(op._polyline_points()) == op._seeded, "seeding failed")
        mp = polyline_props.snap_mouse_point[0]
        mp.x, mp.y, mp.z = mouse_side
        op.tool_state.is_input_on = True
        op.input_ui.set_value("D", d)
        op.input_ui.set_value("A", a)
        tool.Polyline.calculate_x_y_and_z(bpy.context, op.input_ui, op.tool_state)
        tool.Polyline.insert_polyline_point(op.input_ui, op.tool_state)
        return op._finish(bpy.context, moved=True)

    pi1, end, start = markers[1], markers[2], markers[0]

    # PI 1: 800 at 45 degrees from Start (one anchor -> angle against the +X axis, like the first drawn leg)
    r = move(pi1, 800.0, 45.0, (0.0, 500.0, 0.0))
    print("PI 1 ->", tuple(pi1.location[:2]), r)
    check(r == {"FINISHED"} and near(pi1.location[:2], (800 * math.cos(math.radians(45)), 800 * math.sin(math.radians(45)))),
          "PI 1 not moved to D=800, A=45")
    check(not tool.Model.get_polyline_props().insertion_polyline, "polyline not cleaned up")

    def check_placed(moved, anchor_back, anchor, d, a, mouse):
        """The draw tool's convention: moved is d from anchor, at angle a measured counter-clockwise
        from the back leg (anchor -> anchor_back); a negative a turns the other way."""
        bx, by = anchor_back[0] - anchor[0], anchor_back[1] - anchor[1]
        n = math.hypot(bx, by)
        t = math.radians(a)
        ux, uy = (bx * math.cos(t) - by * math.sin(t)) / n, (bx * math.sin(t) + by * math.cos(t)) / n
        want = (anchor[0] + d * ux, anchor[1] + d * uy)
        print(f"  got {tuple(round(v, 4) for v in moved)} want {tuple(round(v, 4) for v in want)}")
        check(near(moved, want), "placement wrong")

    # End: interior angle 150 at PI 1 against the Start->PI 1 leg, mouse below the leg
    p1 = tuple(pi1.location[:2])
    s0 = tuple(start.location[:2])
    move(end, 500.0, 150.0, (2000.0, 0.0, 0.0))
    print("End ->", tuple(end.location[:2]))
    check_placed(tuple(end.location[:2]), s0, p1, 500.0, 150.0, (2000.0, 0.0))

    # Start: measured backwards -- interior angle 120 at PI 1 against the End->PI 1 leg
    e0 = tuple(end.location[:2])
    move(start, 300.0, 120.0, (0.0, 0.0, 0.0))
    print("Start ->", tuple(start.location[:2]))
    check_placed(tuple(start.location[:2]), e0, p1, 300.0, 120.0, (0.0, 0.0))
    # exactly 180 = straight on from the End->PI 1 leg (used to go the wrong way for a non-+X leg)
    move(start, 400.0, 180.0, (0.0, 0.0, 0.0))
    print("Start (A=180) ->", tuple(start.location[:2]))
    check_placed(tuple(start.location[:2]), e0, p1, 400.0, 180.0, (0.0, 0.0))
    move(start, 250.0, -100.0, (0.0, 0.0, 0.0))
    print("Start (A=-100) ->", tuple(start.location[:2]))
    check_placed(tuple(start.location[:2]), e0, p1, 250.0, -100.0, (0.0, 0.0))

    # nothing placed -> marker stays, operator cancels
    before = tuple(pi1.location[:2])
    op = Fake()
    PolylineOperator.__init__(op)
    op._marker_name, op._seeded, op._bearing_handle = pi1.name, 1, None
    op.report = lambda *a: None
    tool.Polyline.clear_polyline()
    check(op._finish(bpy.context, moved=False) == {"CANCELLED"} and tuple(pi1.location[:2]) == before, "cancel moved it")

    # Apply Curve uses the moved markers
    for o in bpy.context.selected_objects:
        o.select_set(False)
    pi1.select_set(True)
    bpy.context.view_layer.objects.active = pi1
    check(bpy.ops.align.apply_pi_curve() == {"FINISHED"}, "apply failed")
    h = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
    segs = tool.Alignment.get_real_layout_segments(h)
    first = segs[0].DesignParameters
    print("first segment start/direction:", first.StartPoint.Coordinates, math.degrees(first.StartDirection))
    check(near(first.StartPoint.Coordinates, tuple(start.location[:2])), "Start not applied")
    want = math.degrees(math.atan2(p1[1] - start.location.y, p1[0] - start.location.x))
    check(abs(math.degrees(first.StartDirection) - want) < 1e-3, "first direction wrong")

    print("MOVE_MARKER_TEST_OK")
except Exception:
    traceback.print_exc()
    print("MOVE_MARKER_TEST_FAILED")
sys.stdout.flush()
