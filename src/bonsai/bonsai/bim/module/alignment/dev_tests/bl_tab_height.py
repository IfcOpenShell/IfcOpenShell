# This file was generated with the assistance of an AI coding tool.
# Development test script for the alignment authoring work -- remove before the final PR (see README.md).
"""Typed Distance and Angle stay as typed on every Tab when the anchor point isn't at Z = 0: the polyline
tool measures in 3D, and a marker 10 m up turned a typed 1000 into 1000.05, then 1000.10."""

import sys
import traceback

import bpy

import bonsai.bim.handler
import bonsai.tool as tool


def check(cond, msg):
    if not cond:
        raise AssertionError(msg)


try:
    bpy.ops.wm.read_homefile(app_template="")
    bonsai.bim.handler.load_post(None)
    tool.Project.get_project_props().export_schema = "IFC4X3_ADD2"
    bpy.ops.bim.create_project()
    import bonsai.bim.module.model.polyline as polyline_module
    from bonsai.bim.module.alignment import operator as op_mod
    from bonsai.bim.module.model.polyline import PolylineOperator

    polyline_module.PolylineDecorator.update = staticmethod(lambda *a, **k: None)  # no viewport in background
    tool.Blender.update_viewport = staticmethod(lambda *a, **k: None)

    bpy.ops.align.add_alignment(alignment_name="T", definition="LAYOUTS")
    alignment = tool.Alignment.get_active_alignment()
    hpoints = [(0.0, 0.0), (1000.0, 0.0), (1707.1067811865476, 707.1067811865476)]
    op_mod._generate_alignment_segments(bpy.context, alignment, hpoints, [0.0])
    ifc = tool.Ifc.get()
    world = [op_mod._local_ifc_to_world_point(ifc, 1.0, p) for p in hpoints]
    markers = op_mod._create_pi_markers(bpy.context, alignment.id(), [(w[0], w[1], 10.0) for w in world])

    class Op(op_mod._CivilAngleInput, PolylineOperator):
        def report(self, *a):
            print("REPORT", a)

    op = Op()
    PolylineOperator.__init__(op)
    op.tool_state.use_default_container = False
    op.tool_state.plane_method = "XY"
    op.snapping_points = [{"type": "Plane", "point": None}]
    props = tool.Model.get_polyline_props()
    if not props.snap_mouse_point:
        props.snap_mouse_point.add()
    op_mod.ALIGN_OT_move_pi_marker._seed_anchor_points(op, bpy.context, op_mod._move_marker_anchors(markers, 1))
    props.insertion_polyline[0].polyline_points[-1].z = 10.0
    print("anchor z", props.insertion_polyline[0].polyline_points[-1].z)
    mp = props.snap_mouse_point[0]
    mp.x, mp.y, mp.z = 600.0, 500.0, 10.0
    tool.Polyline.calculate_distance_and_angle(bpy.context, op.input_ui, op.tool_state)
    print("input options:", op.input_options)

    class Event:
        def __init__(self, type, value, ascii=""):
            self.type, self.value, self.ascii = type, value, ascii

    def press(type, ascii=""):
        # a character arrives with the PRESS only; Tab acts on PRESS while typing, on RELEASE to start
        op.handle_keyboard_input(bpy.context, Event(type, "PRESS", ascii))
        op.handle_keyboard_input(bpy.context, Event(type, "RELEASE", ""))

    def show(label):
        f = {k: op.input_ui.get_text_value(k) for k in ("D", "A", "X", "Y")}
        print("   snapshot:", getattr(op, "field_values", None), "is_typing:", getattr(op, "is_typing", None))
        print(
            f"{label:14s} field={op.input_type}  D={f['D']}  A={f['A']}  X={f['X']}  Y={f['Y']}  typing={op.number_output!r}"
        )

    press("TAB")
    show("Tab (start)")
    for ch in "1000":
        press(ch.upper() if not ch.isdigit() else {"0": "ZERO", "1": "ONE"}[ch], ch)
    show("typed 1000")
    press("TAB")
    show("Tab")
    for ch in "45":
        press({"4": "FOUR", "5": "FIVE"}[ch], ch)
    show("typed 45")
    for i in range(6):
        press("TAB")
        show(f"Tab {i + 1}")
        if op.input_type != "D":
            check(op.input_ui.get_number_value("D") == 1000.0, f"Distance changed: {op.input_ui.get_text_value('D')}")
    check(abs(op.input_ui.get_number_value("A") - 45.0) < 1e-9, "Angle changed")
    # the Bearing readout's direction (counter-clockwise from east): N 45 E, not 3D-measured (N 44 59 49.7 E)
    world = op.input_ui.get_number_value("WORLD_ANGLE")
    print("WORLD_ANGLE", world)
    check(abs(world - 45.0) < 1e-6, f"Bearing direction {world}")
    print("TAB_HEIGHT_TEST_OK")
except Exception:
    traceback.print_exc()
    print("TAB_HEIGHT_TEST_FAILED")
    sys.exit(1)
