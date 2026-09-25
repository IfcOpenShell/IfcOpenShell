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


try:
    from bonsai.bim.module.alignment import operator as op_mod
    from bonsai.bim.module.model.polyline import PolylineOperator

    parse = op_mod._parse_civil_angle

    # ---- parser
    cases = {
        "30": None,
        "-45.5": None,
        "N 30 15 24 E": ("BEARING", 30 + 15 / 60 + 24 / 3600),
        "n30e": ("BEARING", 30.0),
        "S 45 W": ("BEARING", 225.0),
        "S 10 E": ("BEARING", 170.0),
        "N 10 W": ("BEARING", 350.0),
        "N 30°15'24.00\" E": ("BEARING", 30 + 15 / 60 + 24 / 3600),
        "Due W": ("BEARING", 270.0),
        "12 30 Rt": ("DEFLECTION", -12.5),
        "12.5 L": ("DEFLECTION", 12.5),
        "LT 12 30": ("DEFLECTION", 12.5),
        "r 90": ("DEFLECTION", -90.0),
    }
    for text, want in cases.items():
        got = parse(text)
        ok = got == want if want is None or got is None else (got[0] == want[0] and abs(got[1] - want[1]) < 1e-9)
        check(ok, f"parse({text!r}) = {got}, want {want}")
    for bad in ("N 95 E", "N 30 70 E", "E 30 N", "190 R", "N E"):
        try:
            parse(bad)
            raise AssertionError(f"parse({bad!r}) should have failed")
        except ValueError as e:
            pass
    # the Bearing readout's own output parses back to the same direction, all the way round
    for world in range(-179, 181, 7):
        text = op_mod._bearing_string(float(world))
        kind, azimuth = parse(text)
        back = (90.0 - azimuth) % 360.0
        check(kind == "BEARING" and abs(((back - world) + 180) % 360 - 180) < 0.01, f"round trip {world} -> {text}")
    print("parser OK")

    # ---- keyboard -> polyline tool -> placement
    bpy.ops.wm.read_homefile(app_template="")
    bonsai.bim.handler.load_post(None)

    Op = op_mod.ALIGN_OT_move_pi_marker

    class Fake(op_mod._CivilAngleInput, PolylineOperator):
        pass

    op = Fake()
    PolylineOperator.__init__(op)
    reports = []
    op.report = lambda level, msg: reports.append(msg)
    op.snapping_points = [{"type": "Mouse"}]
    props = tool.Model.get_polyline_props()
    if not props.snap_mouse_point:
        props.snap_mouse_point.add()

    def run(anchors, typed, mouse=(3.0, -7.0)):
        """Seed the anchors, type D=100 then `typed` into the Angle field, recalc, place."""
        reports.clear()
        op.tool_state.use_default_container = False
        op.tool_state.plane_method = "XY"
        op.tool_state.is_input_on = False
        from mathutils import Vector

        Op._seed_anchor_points(op, bpy.context, [Vector((x, y, 0.0)) for x, y in anchors])
        mp = props.snap_mouse_point[0]
        mp.x, mp.y, mp.z = mouse[0], mouse[1], 0.0
        tool.Polyline.calculate_distance_and_angle(bpy.context, op.input_ui, op.tool_state)
        op.tool_state.is_input_on = True
        op.tool_state.mode = "Select"
        op.input_ui.set_value("D", 100)
        op.input_type = op.tool_state.input_type = "A"
        op.number_input = list(op.input_ui.get_formatted_value("A") or "")
        for ch in typed:
            op.handle_keyboard_input(bpy.context, SimpleNamespace(value="PRESS", type=ch.upper(), ascii=ch))
        shown = op.input_ui.get_text_value("A")
        ok = op.recalculate_inputs(bpy.context)
        if not ok:
            return shown, None
        tool.Polyline.insert_polyline_point(op.input_ui, op.tool_state)
        p = Op._polyline_points(op)[-1]
        return shown, (p.x, p.y)

    def expect(start, direction_deg):
        t = math.radians(direction_deg)
        return (start[0] + 100 * math.cos(t), start[1] + 100 * math.sin(t))

    def close(a, b):
        return a is not None and abs(a[0] - b[0]) < 1e-3 and abs(a[1] - b[1]) < 1e-3

    # one anchor (a first leg): bearing N 45 E -> world direction 45
    shown, got = run([(10.0, 20.0)], "N 45 E")
    print("typed shows:", shown, "->", got)
    check(shown == "N 45 E", f"letters not shown as typed: {shown!r}")
    check(close(got, expect((10.0, 20.0), 45.0)), f"N 45 E placed at {got}")
    # a deflection on a first leg is refused (nothing to deflect from)
    shown, got = run([(10.0, 20.0)], "10 R")
    check(got is None and any("previous leg" in r for r in reports), f"first-leg deflection not refused {reports}")

    # two anchors, previous leg heading due east (0 -> 100, 0)
    leg = [(0.0, 0.0), (100.0, 0.0)]
    for typed, direction in (
        ("S 30 E", -60.0),  # azimuth 150
        ("N 10 W", 100.0),  # azimuth 350
        ("30 Rt", -30.0),
        ("30 L", 30.0),
        ("12 30 LT", 12.5),
        ("0 R", 0.0),  # straight on
        ("135", 135.0),  # a plain Angle is untouched: 135 CCW from the back leg (pointing west)
    ):
        shown, got = run(leg, typed)
        want = expect(leg[-1], direction if typed != "135" else 180.0 + 135.0)
        print(f"  {typed!r:12} -> {tuple(round(v, 3) for v in got)} want {tuple(round(v, 3) for v in want)}")
        check(close(got, want), f"{typed} placed wrongly")

    # a diagonal previous leg (heading NE): 90 Rt -> heading SE; a bearing ignores the leg
    diag = [(0.0, 0.0), (50.0, 50.0)]
    shown, got = run(diag, "90 R")
    check(close(got, expect(diag[-1], -45.0)), f"90 R on diagonal: {got}")
    shown, got = run(diag, "S 0 E")
    check(close(got, expect(diag[-1], -90.0)), f"due south on diagonal: {got}")

    # malformed text is refused with the parser's message, nothing placed
    shown, got = run(leg, "N 95 E")
    check(got is None and any("exceed 90" in r for r in reports), f"bad bearing not refused {reports}")
    shown, got = run(leg, "N 30 N")
    check(got is None and reports, "nonsense not refused")

    # letters only act in the Angle field: in Distance they're ignored by this mixin
    op.tool_state.is_input_on = True
    op.input_type = op.tool_state.input_type = "D"
    op.number_input = []
    op.handle_keyboard_input(bpy.context, SimpleNamespace(value="PRESS", type="N", ascii="n"))
    check("N" not in op.number_input, "letter accepted in Distance field")

    print("CIVIL_ANGLE_TEST_OK")
except Exception:
    traceback.print_exc()
    print("CIVIL_ANGLE_TEST_FAILED")
sys.stdout.flush()
