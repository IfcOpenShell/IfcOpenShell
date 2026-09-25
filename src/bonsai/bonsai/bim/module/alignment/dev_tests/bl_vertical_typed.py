# This file was generated with the assistance of an AI coding tool.
# Development test script for the alignment authoring work -- remove before the final PR (see README.md).

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


def near(a, b, tol=1e-6):
    return abs(a[0] - b[0]) < tol and abs(a[1] - b[1]) < tol


try:
    bpy.ops.wm.read_homefile(app_template="")
    bpy.data.batch_remove(bpy.data.objects)
    bonsai.bim.handler.load_post(None)
    tool.Project.get_project_props().export_schema = "IFC4X3_ADD2"
    bpy.ops.bim.create_project()
    ifc = tool.Ifc.get()

    alignment = ifcopenshell.api.alignment.create(ifc, "VT", include_vertical=False)
    h_layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
    ifcopenshell.api.alignment.layout_horizontal_alignment_by_pi_method(
        ifc, h_layout, [(0.0, 0.0), (500.0, 0.0), (1000.0, 300.0)], [200.0]
    )
    ifcopenshell.api.alignment.create_representation(ifc, alignment)
    tool.Alignment.create_object_for_alignment(alignment)
    tool.Alignment.refresh_alignment_representation_object(alignment)
    obj = tool.Ifc.get_object(alignment)
    for o in bpy.context.selected_objects:
        o.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    length = sum(s.DesignParameters.SegmentLength for s in tool.Alignment.get_real_layout_segments(h_layout))
    print("horizontal length:", length)

    from bonsai.bim.module.alignment import decorator as dec_mod
    from bonsai.bim.module.alignment import operator as op_mod

    Op = op_mod.ALIGN_OT_draw_vertical_alignment
    dec_mod.VerticalProfileDecorator.dist_min = 0.0
    dec_mod.VerticalProfileDecorator.dist_max = length

    class Fake:
        pass

    for klass in reversed(Op.__mro__):
        if not klass.__module__.startswith("bonsai"):
            continue
        for name, member in vars(klass).items():
            if (callable(member) or isinstance(member, property)) and name.startswith("_") and not name.startswith("__"):
                setattr(Fake, name, member)
    op = Fake()
    reports = []
    op.report = lambda level, msg: reports.append((set(level), msg))
    op._points = []
    op._area_ptr = 1
    op._alignment_id = alignment.id()
    op._mouse = None
    op._init_typed_input()
    # keyboard events never touch the region -- a zero-size area keeps the mouse "outside" it
    area = SimpleNamespace(x=0, y=0, width=0, height=0)
    op._locate_profile_view = lambda context: (area, SimpleNamespace(x=0, y=0), None)
    dec_mod.VerticalDrawDecorator.install(bpy.context, op._points)

    def ev(type_, value="PRESS", ascii=""):
        return SimpleNamespace(type=type_, value=value, ascii=ascii, ctrl=False, alt=False, shift=False,
                               mouse_x=-10, mouse_y=-10)

    def key(type_, ascii=""):
        results = [op._modal(bpy.context, ev(type_, "PRESS", ascii)), op._modal(bpy.context, ev(type_, "RELEASE"))]
        check(all(r == {"RUNNING_MODAL"} for r in results), f"{type_} ended the command: {results}")

    def type_text(text):
        for ch in text:
            name = {".": "PERIOD", "-": "MINUS"}.get(ch, ch)
            key(name, ch)

    # PI 1: first point only takes elevation; typing starts in Elevation directly
    key("S")
    check(op._active_field is None and any("only takes an elevation" in m for _, m in reports), "S allowed on PI 1")
    type_text("100")
    check(op._active_field == "ELEVATION", "typing didn't start in Elevation")
    key("RET")
    check(op._points == [(0.0, 100.0)], f"PI 1 wrong: {op._points}")

    # PI 2: Elevation + Slope -> distance derived (Tab order E -> S)
    key("TAB"); type_text("102"); key("TAB"); type_text("2")
    check(op._active_field == "SLOPE", "Tab didn't move to Slope")
    lines = dec_mod.VerticalDrawDecorator.input_lines
    print("cursor lines while typing:", lines)
    check(lines[0] == (f"Station: {tool.Alignment.format_station(100.0)}", "VALUE"), f"station line {lines[0]}")
    check(lines[1] == ("Elevation: 102.000  (locked)", "VALUE"), f"elevation line {lines[1]}")
    check(lines[2] == ("Slope: 2%", "ACTIVE"), f"slope line {lines[2]}")
    check(lines[3] == ("Distance Along: 100.000", "VALUE"), f"derived distance line {lines[3]}")
    key("RET")
    check(near(op._points[-1], (100.0, 102.0)), f"E+S wrong: {op._points[-1]}")
    op._mouse = (150.0, 103.0)
    op._refresh_input_display()
    print("cursor lines, mouse only:", dec_mod.VerticalDrawDecorator.input_lines)
    check([t for t, _ in dec_mod.VerticalDrawDecorator.input_lines][1:] == [
        "Elevation: 103.000", "Slope: 2.00%", "Distance Along: 150.000"], "mouse-only readout wrong")
    op._mouse = None

    # PI 3: Slope + Distance -> elevation derived
    key("S"); type_text("-1"); key("D"); type_text("300"); key("RET")
    check(near(op._points[-1], (300.0, 100.0)), f"S+D wrong: {op._points[-1]}")

    # PI 4: third typed value unlocks the oldest (Elevation)
    key("E"); type_text("90"); key("TAB"); type_text("1"); key("TAB"); type_text("500")
    key("TAB")  # commits Distance -> Elevation (oldest) is released
    print("locks after 3 values:", op._locks, op._lock_order)
    check(set(op._locks) == {"SLOPE", "DISTANCE"}, f"oldest not unlocked: {op._locks}")
    check(op._active_field == "ELEVATION", "Tab didn't wrap to Elevation")
    key("RET")
    check(near(op._points[-1], (500.0, 102.0)), f"S+D after unlock wrong: {op._points[-1]}")

    # Backspace on an empty field unlocks it; Backspace never removes a PI while typing
    n = len(op._points)
    key("E"); type_text("1"); key("BACK_SPACE"); key("BACK_SPACE")
    check(len(op._points) == n and "ELEVATION" not in op._locks, "Backspace misbehaved")
    key("ESC")
    check(not op._locks and op._active_field is None, "Esc didn't clear typed values")

    # refused: behind the previous PI, past the end, flat slope to a different elevation
    for keys, why in (
        (("D", "450"), "not past the previous PI"),
        (("D", str(int(length) + 50)), "past the end"),
    ):
        reports.clear()
        key(keys[0]); type_text(keys[1]); key("RET")
        check(len(op._points) == n and any(why in m for _, m in reports), f"not refused: {why} {reports}")
        key("ESC")
    reports.clear()
    key("E"); type_text("110"); key("S"); type_text("0"); key("RET")
    check(len(op._points) == n and any("0% slope" in m for _, m in reports), f"flat slope not refused {reports}")
    key("ESC")

    # one lock + mouse: Slope locked, distance from the mouse
    op._mouse = (700.0, 999.0)
    key("S"); type_text("-2"); key("RET")
    check(near(op._points[-1], (700.0, 98.0)), f"slope + mouse wrong: {op._points[-1]}")

    # last PI at the end station, then Enter with nothing typed finishes and builds the vertical
    key("E"); type_text("95"); key("D"); type_text(f"{length:.6f}"); key("RET")
    print("typed PIs:", op._points)
    r = [op._modal(bpy.context, ev("RET", "PRESS")), op._modal(bpy.context, ev("RET", "RELEASE"))]
    check(r[-1] == {"FINISHED"}, f"Enter with nothing typed didn't finish: {r}")

    v_layout = tool.Alignment.get_all_vertical_layouts(alignment)[0]
    segs = tool.Alignment.get_real_layout_segments(v_layout)
    got = [(round(s.DesignParameters.StartDistAlong, 6), round(s.DesignParameters.StartHeight, 6),
            round(s.DesignParameters.StartGradient * 100, 6)) for s in segs]
    print("vertical segments (dist, height, grade%):", got)
    expected_starts = [p for p in op._points[:-1]]
    check(len(segs) == len(op._points) - 1, "wrong segment count")
    for s, p in zip(segs, expected_starts):
        check(near((s.DesignParameters.StartDistAlong, s.DesignParameters.StartHeight), p, 1e-6), f"segment {s} != {p}")
    check(abs(segs[0].DesignParameters.StartGradient - 0.02) < 1e-9, "grade 2% not preserved")

    print("VERTICAL_TYPED_TEST_OK")
except Exception:
    traceback.print_exc()
    print("VERTICAL_TYPED_TEST_FAILED")
sys.stdout.flush()
