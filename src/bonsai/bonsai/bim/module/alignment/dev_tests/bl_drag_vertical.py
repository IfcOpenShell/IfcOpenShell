# This file was generated with the assistance of an AI coding tool.
# Development test script for the alignment authoring work -- remove before the final PR (see README.md).

import sys
import traceback
from types import SimpleNamespace

import bpy
from mathutils import Vector

import bonsai.bim.handler
import bonsai.tool as tool
import ifcopenshell.api.alignment


def check(cond, msg):
    if not cond:
        raise AssertionError(msg)


def near(a, b, tol=1e-4):
    return abs(a[0] - b[0]) < tol and abs(a[1] - b[1]) < tol


try:
    bpy.ops.wm.read_homefile(app_template="")
    bpy.data.batch_remove(bpy.data.objects)
    bonsai.bim.handler.load_post(None)
    tool.Project.get_project_props().export_schema = "IFC4X3_ADD2"
    bpy.ops.bim.create_project()
    ifc = tool.Ifc.get()

    alignment = ifcopenshell.api.alignment.create_by_pi_method(
        ifc, "DV",
        [(0.0, 0.0), (1000.0, 0.0), (1000.0, 1000.0)], [300.0],
        [(0.0, 100.0), (600.0, 106.0), (1200.0, 100.0), (1800.0, 103.0)], [0.0, 0.0],
    )
    tool.Alignment.create_object_for_alignment(alignment)
    tool.Alignment.refresh_alignment_representation_object(alignment)
    obj = tool.Ifc.get_object(alignment)
    for o in bpy.context.selected_objects:
        o.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    props = bpy.context.scene.CivilAlignmentProperties
    check(bpy.ops.align.load_vertical_pis() == {"FINISHED"}, "load_vertical_pis failed")

    from bonsai.bim.module.alignment import decorator as dec_mod
    from bonsai.bim.module.alignment import operator as op_mod

    points = op_mod._staged_vertical_points(props)
    print("staged:", points)
    check(props.vertical_endpoints_staged and len(points) == 4, "endpoints not staged")
    check(near(points[0], (0.0, 100.0)) and near(points[1], (600.0, 106.0)), f"staged points wrong {points}")
    end_d = points[-1][0]

    # --- fake profile view: pixel = (dist_along, elevation * 10), region at the window origin
    area = SimpleNamespace(x=0, y=0, width=100000, height=100000)
    region = SimpleNamespace(x=0, y=0)
    op_mod._find_profile_view = lambda context: (area, region, "rv3d")
    op_mod._vertical_point_to_px = lambda region, rv3d, d, e: Vector((d, e * 10.0))
    dec_mod.VerticalProfileDecorator.screen_to_data = classmethod(lambda cls, region, rv3d, x, y: (x, y / 10.0))

    Op = op_mod.ALIGN_OT_drag_vertical_pis
    attrs = {}
    for klass in reversed(Op.__mro__):
        if klass.__module__.startswith("bonsai"):
            attrs.update({n: m for n, m in vars(klass).items()
                          if (callable(m) or isinstance(m, property)) and not n.startswith("__")})
    attrs.update(HIT_RADIUS_PX=Op.HIT_RADIUS_PX, is_running=True, _generation=1)
    Fake = type("Fake", (), attrs)
    op = Fake()
    op._generation_id = 1
    op._init_drag_state()
    reports = []
    op.report = lambda level, msg: reports.append(msg)
    dec_mod.VerticalPIMarkerDecorator.install(bpy.context)

    def ev(type_, value, x, y, ascii=""):
        return SimpleNamespace(type=type_, value=value, mouse_x=x, mouse_y=y, ascii=ascii,
                               ctrl=False, alt=False, shift=False)

    def key(type_, ascii="", x=0, y=0):
        for value in ("PRESS", "RELEASE"):
            r = op.modal(bpy.context, ev(type_, value, x, y, ascii))
            check(r == {"RUNNING_MODAL"}, f"{type_} {value} not consumed: {r}")

    def type_text(text):
        for ch in text:
            key({".": "PERIOD", "-": "MINUS"}.get(ch, ch), ch)

    def hud():
        return [t for t, _ in dec_mod.VerticalPIMarkerDecorator.input_lines or []]

    def px(p):
        return p[0], p[1] * 10.0

    # hover + press on empty space passes through
    check(op.modal(bpy.context, ev("MOUSEMOVE", "NOTHING", 300, 0)) == {"PASS_THROUGH"}, "empty move")
    check(dec_mod.VerticalPIMarkerDecorator.hover is None, "hover on empty space")
    check(op.modal(bpy.context, ev("LEFTMOUSE", "PRESS", 300, 0)) == {"PASS_THROUGH"}, "empty press consumed")

    # drag PI 1 from (600, 106) to (700, 110)
    x, y = px(points[1])
    op.modal(bpy.context, ev("MOUSEMOVE", "NOTHING", x + 3, y - 2))
    check(dec_mod.VerticalPIMarkerDecorator.hover == 1, "hover not detected")
    print("hover readout:", hud())
    check(hud() == [f"Station: {tool.Alignment.format_station(600.0)}", "Elevation: 106.000", "Slope In: 1.00%",
                    "Distance Along: 600.000", "Slope Out: -1.00%"], "hover readout wrong")
    check(op.modal(bpy.context, ev("LEFTMOUSE", "PRESS", x + 3, y - 2)) == {"RUNNING_MODAL"}, "press not consumed")
    check(op._drag == 1, "drag not started")
    op.modal(bpy.context, ev("MOUSEMOVE", "NOTHING", 700, 1100))
    print("drag readout:", hud())
    check(hud()[1:4] == ["Elevation: 110.000", "Slope In: 1.43%", "Distance Along: 700.000"], "drag readout wrong")
    op.modal(bpy.context, ev("LEFTMOUSE", "RELEASE", 700, 1100))
    m = props.vertical_pi_markers[0]
    print("PI 1 after drag:", (m.dist_along, m.elevation))
    check(near((m.dist_along, m.elevation), (700.0, 110.0)), "PI 1 not moved")
    check(op._drag is None and props.active_vertical_pi_marker_index == 0, "drop failed")

    # dragging PI 1 past PI 2 is held just before it
    x, y = px(op_mod._staged_vertical_points(props)[1])
    op.modal(bpy.context, ev("LEFTMOUSE", "PRESS", x, y))
    op.modal(bpy.context, ev("MOUSEMOVE", "NOTHING", 5000, 1000))
    op.modal(bpy.context, ev("LEFTMOUSE", "RELEASE", 5000, 1000))
    pts = op_mod._staged_vertical_points(props)
    print("PI 1 pushed past PI 2:", pts[1])
    check(pts[0][0] < pts[1][0] < pts[2][0], f"order broken {pts}")

    # Esc while dragging puts it back
    before = pts[1]
    x, y = px(before)
    op.modal(bpy.context, ev("LEFTMOUSE", "PRESS", x, y))
    op.modal(bpy.context, ev("MOUSEMOVE", "NOTHING", 800, 500))
    check(op.modal(bpy.context, ev("ESC", "PRESS", 800, 500)) == {"RUNNING_MODAL"}, "esc consumed")
    check(near(op_mod._staged_vertical_points(props)[1], before), "Esc didn't restore")

    # put PI 1 somewhere sensible, then drag Start and End: elevation only
    x, y = px(op_mod._staged_vertical_points(props)[1])
    op.modal(bpy.context, ev("LEFTMOUSE", "PRESS", x, y))
    op.modal(bpy.context, ev("MOUSEMOVE", "NOTHING", 700, 1100))
    op.modal(bpy.context, ev("LEFTMOUSE", "RELEASE", 700, 1100))
    for idx, target in ((0, (400.0, 980.0)), (3, (100.0, 1050.0))):
        x, y = px(op_mod._staged_vertical_points(props)[idx])
        op.modal(bpy.context, ev("LEFTMOUSE", "PRESS", x, y))
        op.modal(bpy.context, ev("MOUSEMOVE", "NOTHING", *target))
        op.modal(bpy.context, ev("LEFTMOUSE", "RELEASE", *target))
    pts = op_mod._staged_vertical_points(props)
    print("after endpoint drags:", pts)
    check(near(pts[0], (0.0, 98.0)) and near(pts[-1], (end_d, 105.0)), "endpoints moved wrongly")

    # ---- typed input on a selected PI (clicked, not dragged): PI 2 at (1200, 100)
    x, y = px(op_mod._staged_vertical_points(props)[2])
    op.modal(bpy.context, ev("MOUSEMOVE", "NOTHING", x, y))
    op.modal(bpy.context, ev("LEFTMOUSE", "PRESS", x, y))
    op.modal(bpy.context, ev("LEFTMOUSE", "RELEASE", x, y))
    check(op._active == 2 and op._drag is None, "click didn't select PI 2")
    key("E", x=x, y=y); type_text("104"); key("TAB"); type_text("-2")
    print("typing readout:", hud())
    check("Elevation: 104.000  (locked)" in hud() and "Slope In: -2%" in hud(), "typed readout wrong")
    key("RET")
    pts = op_mod._staged_vertical_points(props)
    # from PI 1 (700, 110): 104 = 110 - 0.02 * (d - 700) -> d = 1000
    print("PI 2 typed E=104, S=-2:", pts[2])
    check(near(pts[2], (1000.0, 104.0)), f"typed E+S wrong {pts[2]}")
    # a typed distance past the next point (End) is refused and the PI stays put
    reports.clear()
    key("D", x=x, y=y); type_text("2000"); key("RET")
    check(near(op_mod._staged_vertical_points(props)[2], (1000.0, 104.0)), "refused value moved the PI")
    check(any("past the End" in r for r in reports), f"no refusal message {reports}")
    key("ESC")  # clear the typed values (PI stays where it was)
    check(near(op_mod._staged_vertical_points(props)[2], (1000.0, 104.0)) and not op._is_typing, "Esc restore wrong")
    # End: only Elevation / Slope In -- Slope In from PI 2 at 1%: 104 + 0.01 * (1800 - 1000) = 112
    x, y = px(op_mod._staged_vertical_points(props)[3])
    op.modal(bpy.context, ev("LEFTMOUSE", "PRESS", x, y))
    op.modal(bpy.context, ev("LEFTMOUSE", "RELEASE", x, y))
    reports.clear()
    check(op.modal(bpy.context, ev("D", "PRESS", x, y, "d")) == {"RUNNING_MODAL"}, "refused D not consumed")
    check(any("only move up and down" in r for r in reports), "D allowed on End")
    key("S", x=x, y=y); type_text("1"); key("RET")
    check(near(op_mod._staged_vertical_points(props)[3], (end_d, 112.0)), "End slope-in wrong")
    # typing while dragging: mouse gives distance, typed elevation wins
    x, y = px(op_mod._staged_vertical_points(props)[1])
    op.modal(bpy.context, ev("LEFTMOUSE", "PRESS", x, y))
    op.modal(bpy.context, ev("MOUSEMOVE", "NOTHING", 650, 900))
    type_text("108")
    op.modal(bpy.context, ev("LEFTMOUSE", "RELEASE", 650, 900))
    check(near(op_mod._staged_vertical_points(props)[1], (650.0, 108.0)), "typed-while-dragging wrong")
    # typing does nothing (passes through) while the mouse is outside the profile view
    key("ESC")  # deselect
    area.width = 10
    check(op.modal(bpy.context, ev("S", "PRESS", 5000, 5000, "s")) == {"PASS_THROUGH"}, "S stolen outside profile")
    area.width = 100000

    # navigation passes through while idle and while dragging
    check(op.modal(bpy.context, ev("WHEELUPMOUSE", "PRESS", 0, 0)) == {"PASS_THROUGH"}, "wheel idle")

    # Apply -> IFC matches the dragged PIs
    staged = op_mod._staged_vertical_points(props)
    check(bpy.ops.align.apply_vertical_pi_curve() == {"FINISHED"}, "apply failed")
    v_layout = ifcopenshell.api.alignment.get_vertical_layout(alignment)
    segs = tool.Alignment.get_real_layout_segments(v_layout)
    starts = [(s.DesignParameters.StartDistAlong, s.DesignParameters.StartHeight) for s in segs]
    start, end = tool.Alignment.get_vertical_alignment_start_end_points(alignment)
    print("IFC starts:", starts, "end:", end)
    for got, want in zip(starts + [end], staged):
        check(near(got, want), f"IFC {got} != staged {want}")

    # Finish ends the drag session by itself
    check(bpy.ops.align.finish_vertical_pi_editing() == {"FINISHED"}, "finish failed")
    check(op.modal(bpy.context, ev("MOUSEMOVE", "NOTHING", 0, 0)) == {"FINISHED"}, "session didn't end")
    check(not Fake.is_running and not dec_mod.VerticalPIMarkerDecorator.is_installed, "cleanup incomplete")

    print("DRAG_VERTICAL_TEST_OK")
except Exception:
    traceback.print_exc()
    print("DRAG_VERTICAL_TEST_FAILED")
sys.stdout.flush()
