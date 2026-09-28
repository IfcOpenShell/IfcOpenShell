# This file was generated with the assistance of an AI coding tool.
# Development test script for the alignment authoring work -- remove before the final PR (see README.md).
#
# Stationing on offset curve alignments (REQUIREMENTS.md §5.2): none by default, added afterwards on
# the offset curve itself (not at the origin), and kept on it through offset and reference edits.

import inspect
import sys
import traceback
from types import SimpleNamespace

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


def stationing_panel():
    from bonsai.bim.module.alignment import ui as ui_mod

    out = []
    panel = type("P", (), {"layout": Rec(out)})()
    ui_mod.ALIGN_PT_alignment_stationing_authoring.draw(panel, bpy.context)
    return out


def fallback(referent):
    placement = referent.ObjectPlacement
    check(placement.is_a("IfcLinearPlacement"), f"{referent.Name} not linearly placed: {placement}")
    return tuple(placement.CartesianPosition.Location.Coordinates)


def close(a, b, tol=1e-3):
    return all(abs(x - y) < tol for x, y in zip(a, b))


try:
    print("add_stationing_referent from", inspect.getsourcefile(ifcopenshell.api.alignment.add_stationing_referent))
    bpy.ops.wm.read_homefile(app_template="")
    bpy.data.batch_remove(bpy.data.objects)
    bonsai.bim.handler.load_post(None)
    tool.Project.get_project_props().export_schema = "IFC4X3_ADD2"
    bpy.ops.bim.create_project()
    ifc = tool.Ifc.get()
    A = tool.Alignment
    from bonsai.bim.module.alignment import operator as op_mod

    # ---- the dialog's default: no stationing for an offset curve, stationing for the other kinds
    for definition, expected in (("OFFSET", False), ("LAYOUTS", True), ("POLYLINE", True)):
        dialog = SimpleNamespace(definition=definition, define_stationing=not expected, in_dialog=True)
        op_mod._on_add_alignment_definition_update(dialog, bpy.context)
        check(dialog.define_stationing is expected, f"{definition} defaults define_stationing to {not expected}")
        # outside the dialog (a script's own arguments) define_stationing is left as given
        script = SimpleNamespace(definition=definition, define_stationing=not expected, in_dialog=False)
        op_mod._on_add_alignment_definition_update(script, bpy.context)
        check(script.define_stationing is (not expected), f"{definition} overrode a script's define_stationing")

    main = ifcopenshell.api.alignment.create_by_pi_method(
        ifc, "Main", [(0.0, 0.0), (100.0, 0.0), (200.0, 100.0)], [50.0], [(0.0, 10.0), (80.0, 12.0), (200.0, 10.0)], [0.0]
    )
    A.create_object_for_alignment(main)
    A.refresh_alignment_representation_object(main)
    horizontal = next(c for c, _, d in A.get_offset_basis_candidates(None) if d == 2)

    # ---- created without stationing; the panel says so and offers to add it
    r = bpy.ops.align.add_alignment(
        alignment_name="Lane", definition="OFFSET", offset_from=str(horizontal.id()), offset_lateral=3.5,
        define_stationing=False,
    )
    check(r == {"FINISHED"}, "add offset")
    lane = next(x for x in ifc.by_type("IfcAlignment") if x.Name == "Lane")
    check(not A.get_stationing_referents(lane), "offset alignment created with stationing")
    select(tool.Ifc.get_object(lane))
    panel = stationing_panel()
    print("\n".join(panel))
    check(any("Add Stationing" in l for l in panel), "panel doesn't offer Add Stationing")
    check(not any("add_station_equation" in l for l in panel), "station equations offered with no stationing")

    # ---- added afterwards, on the offset curve (3.5 left of Main's start), not at the origin
    check(bpy.ops.align.set_start_station(station="1+000") == {"FINISHED"}, "add stationing")
    start = A.find_stationing_referent_at(lane, 0.0)
    check(start is not None, "no start referent added")
    check(start.ObjectPlacement.RelativePlacement.Location.BasisCurve == A.get_offset_curve(lane), "not on the offset curve")
    print("start referent at", fallback(start))
    check(close(fallback(start), (0.0, 3.5, 0.0)), "start referent not on the offset curve")
    obj = tool.Ifc.get_object(start)
    check(obj is not None and obj.matrix_world.translation.length > 1e-6, "start referent object left at the origin")
    panel = stationing_panel()
    check(any("Start: 1+000" in l for l in panel) and any("add_station_equation" in l for l in panel), "panel after adding")

    # a station equation on the offset curve too -- 50 along Main's straight, 3.5 left
    r = bpy.ops.align.add_station_equation(distance_along=50.0, station="2+000", incoming_station="1+050")
    check(r == {"FINISHED"}, "add station equation")
    equation = A.get_stationing_referents(lane)[1][0]
    print("equation at", fallback(equation))
    check(close(fallback(equation), (50.0, 3.5, 0.0)), "equation not on the offset curve")

    # ---- editing the offsets moves the referents with the curve
    check(bpy.ops.align.load_offset_table() == {"FINISHED"}, "load offsets")
    bpy.context.scene.CivilAlignmentProperties.offset_value_rows[0].lateral = 5.0
    check(bpy.ops.align.apply_offset_table() == {"FINISHED"}, "apply offsets")
    bpy.ops.align.finish_offset_table()
    print("after lateral 5:", fallback(start), fallback(equation))
    check(close(fallback(start), (0.0, 5.0, 0.0)) and close(fallback(equation), (50.0, 5.0, 0.0)), "referents didn't follow the offsets")

    # ---- editing the reference moves them too (the offset curve follows it)
    before = tool.Ifc.get_object(start).matrix_world.translation.copy()
    ok, msg = op_mod._generate_alignment_segments(bpy.context, main, [(0.0, 20.0), (100.0, 20.0), (200.0, 120.0)], [50.0])
    check(ok, msg)
    print("after moving Main 20 north:", fallback(start), fallback(equation))
    check(close(fallback(start), (0.0, 25.0, 0.0)) and close(fallback(equation), (50.0, 25.0, 0.0)), "referents didn't follow the reference")
    after = tool.Ifc.get_object(start).matrix_world.translation
    check((after - before).length > 1e-6, "start referent object didn't move with the reference")

    # ---- asked for at creation, stationing lands on the curve straight away (3D: offset from the vertical)
    gradient = next(c for c, _, d in A.get_offset_basis_candidates(None) if d == 3)
    r = bpy.ops.align.add_alignment(
        alignment_name="Barrier", definition="OFFSET", offset_from=str(gradient.id()), offset_lateral=-4.0,
        offset_vertical=0.5, define_stationing=True, start_station="0+500",
    )
    check(r == {"FINISHED"}, "add offset with stationing")
    barrier = next(x for x in ifc.by_type("IfcAlignment") if x.Name == "Barrier")
    b_start = A.find_stationing_referent_at(barrier, 0.0)
    print("Barrier start referent at", fallback(b_start))
    # Main starts on a 2.5% grade, and the vertical offset is square to the sloped tangent, not plumb
    import math

    grade = math.atan(2.0 / 80.0)
    expected = (-0.5 * math.sin(grade), 16.0, 10.0 + 0.5 * math.cos(grade))
    check(close(fallback(b_start), expected, 1e-6), f"3D offset start referent not on the curve (expected {expected})")

    print("ALL OK")
except Exception:
    traceback.print_exc()
    print("OFFSET_STATIONING_FAILED")
    sys.stdout.flush()
    sys.exit(1)
sys.stdout.flush()
