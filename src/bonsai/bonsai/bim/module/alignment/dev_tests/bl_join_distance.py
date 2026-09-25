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


def select_only(obj):
    for o in bpy.context.selected_objects:
        o.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def seg_summary(alignment):
    h_layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
    segs = tool.Alignment.get_real_layout_segments(h_layout)
    return [(s.DesignParameters.PredefinedType, s.DesignParameters) for s in segs]


try:
    bpy.ops.wm.read_homefile(app_template="")
    bpy.data.batch_remove(bpy.data.objects)
    bonsai.bim.handler.load_post(None)
    tool.Project.get_project_props().export_schema = "IFC4X3_ADD2"
    bpy.ops.bim.create_project()
    ifc = tool.Ifc.get()

    d1, d2 = math.radians(60.0), math.radians(40.0)
    leg = 450.0
    pi1 = (1000.0, 0.0)
    pi2 = (pi1[0] + leg * math.cos(d1), pi1[1] + leg * math.sin(d1))
    poe = (pi2[0] + 800.0 * math.cos(d1 + d2), pi2[1] + 800.0 * math.sin(d1 + d2))
    alignment = ifcopenshell.api.alignment.create_by_pi_method(
        ifc, "JoinDist", [(0.0, 0.0), pi1, pi2, poe], [200.0, 150.0],
        [(0.0, 0.0), (1000.0, 5.0), (2000.0, 0.0)], [400.0],
    )
    tool.Alignment.create_object_for_alignment(alignment)
    tool.Alignment.refresh_alignment_representation_object(alignment)
    select_only(tool.Ifc.get_object(alignment))

    from bonsai.bim.module.alignment.operator import _find_pi_markers, _is_interior_pi_marker
    from bonsai.bim.module.alignment.decorator import PIMarkerDecorator

    # ---------- viewport markers, CIRCULAR, distance mode (PCC) ----------
    check(bpy.ops.align.edit_horizontal_pis() == {"FINISHED"}, "edit_horizontal_pis failed")
    all_markers = _find_pi_markers(alignment.id())
    interior = [m for m in all_markers if _is_interior_pi_marker(m)]
    check(len(interior) == 2, f"expected 2 PIs, got {len(interior)}")
    m1, m2 = interior[0].bonsai_pi_curve_marker, interior[1].bonsai_pi_curve_marker
    m1.curve_type = "CIRCULAR"
    m1.join_next = True
    m1.join_mode = "DISTANCE"
    m1.join_distance = 300.0

    # decorator junction point (pure math, no GPU)
    idx = all_markers.index(interior[0])
    jp = PIMarkerDecorator._join_distance_point(all_markers[idx], all_markers[idx + 1])
    expected_world = (pi1[0] + 300.0 * math.cos(d1), pi1[1] + 300.0 * math.sin(d1))
    print("decorator junction:", tuple(jp), "expected ~", expected_world)
    check(abs(jp.x - expected_world[0]) < 1e-2 and abs(jp.y - expected_world[1]) < 1e-2, "decorator junction off")

    select_only(interior[0])
    check(bpy.ops.align.apply_pi_curve() == {"FINISHED"}, "apply failed")
    segs = seg_summary(alignment)
    types = [t for t, _ in segs]
    print("PCC by distance types:", types, "R1", m1.radius, "R2", m2.radius)
    check(types == ["LINE", "CIRCULARARC", "CIRCULARARC", "LINE"], f"unexpected types {types}")
    check(abs(m1.radius - 300.0 / math.tan(d1 / 2)) < 1e-2, f"R1 wrong: {m1.radius}")
    check(abs(m2.radius - 150.0 / math.tan(d2 / 2)) < 1e-2, f"R2 wrong: {m2.radius}")
    junction = segs[2][1].StartPoint.Coordinates
    print("junction:", junction, "expected", expected_world)
    check(math.hypot(junction[0] - expected_world[0], junction[1] - expected_world[1]) < 1e-2, "junction misplaced")
    check("R=" in interior[1].name, f"joined marker not relabeled: {interior[1].name}")

    # ---------- radius mode writes back join_distance ----------
    m1.join_mode = "RADIUS"
    m1.radius = 400.0
    check(bpy.ops.align.apply_pi_curve() == {"FINISHED"}, "radius-mode apply failed")
    print("radius mode join_distance:", m1.join_distance)
    check(abs(m1.join_distance - 400.0 * math.tan(d1 / 2)) < 1e-2, "join_distance not written back")

    # ---------- out-of-range distance is refused, segments untouched ----------
    before = [t for t, _ in seg_summary(alignment)]
    m1.join_mode = "DISTANCE"
    m1.join_distance = 500.0  # > leg
    check(bpy.ops.align.apply_pi_curve() == {"FINISHED"}, "refusal should still finish")
    check([t for t, _ in seg_summary(alignment)] == before, "segments changed on refused apply")

    # ---------- SPIRAL_CIRCULAR distance mode (mirrors onto CIRCULAR_SPIRAL) ----------
    m1.curve_type = "SPIRAL_CIRCULAR"
    m1.spiral_in_length = 80.0
    m1.spiral_family = "BLOSSCURVE"
    m1.join_distance = 280.0
    check(bpy.ops.align.apply_pi_curve() == {"FINISHED"}, "spiral apply failed")
    segs = seg_summary(alignment)
    types = [t for t, _ in segs]
    print("spiral by distance types:", types, "R1", m1.radius, "R2", m2.radius, m2.curve_type)
    check(types == ["LINE", "BLOSSCURVE", "CIRCULARARC", "CIRCULARARC", "BLOSSCURVE", "LINE"], f"types {types}")
    junction = segs[3][1].StartPoint.Coordinates
    exp = (pi1[0] + 280.0 * math.cos(d1), pi1[1] + 280.0 * math.sin(d1))
    print("spiral junction:", junction, "expected", exp)
    check(math.hypot(junction[0] - exp[0], junction[1] - exp[1]) < 1e-2, "spiral junction misplaced")

    check(bpy.ops.align.finish_pi_editing() == {"FINISHED"}, "finish failed")

    # ---------- reload via Edit PIs prefills join_distance ----------
    select_only(tool.Ifc.get_object(alignment))
    check(bpy.ops.align.edit_horizontal_pis() == {"FINISHED"}, "re-edit failed")
    interior = [m for m in _find_pi_markers(alignment.id()) if _is_interior_pi_marker(m)]
    r1 = interior[0].bonsai_pi_curve_marker
    print("reloaded:", r1.curve_type, r1.join_next, r1.join_mode, r1.join_distance)
    check(r1.join_next and abs(r1.join_distance - 280.0) < 1e-2, "join_distance not prefilled on reload")
    select_only(interior[0])
    check(bpy.ops.align.finish_pi_editing() == {"FINISHED"}, "finish failed")

    # ---------- table path, PRC-free CIRCULAR, distance mode ----------
    select_only(tool.Ifc.get_object(alignment))
    check(bpy.ops.align.load_horizontal_pi_table() == {"FINISHED"}, "load table failed")
    rows = bpy.context.scene.CivilAlignmentProperties.horizontal_pi_rows
    print("table row prefill distance:", rows[0].join_distance)
    check(abs(rows[0].join_distance - 280.0) < 1e-2, "table join_distance not prefilled")
    rows[0].curve_type = "CIRCULAR"
    rows[0].join_mode = "DISTANCE"
    rows[0].join_distance = 200.0
    check(bpy.ops.align.apply_horizontal_pi_table() == {"FINISHED"}, "table apply failed")
    types = [t for t, _ in seg_summary(alignment)]
    print("table types:", types, "R1", rows[0].radius, "R2", rows[1].radius)
    check(types == ["LINE", "CIRCULARARC", "CIRCULARARC", "LINE"], f"table types {types}")
    check(abs(rows[0].radius - 200.0 / math.tan(d1 / 2)) < 1e-2, "table R1 wrong")

    # ---------- distance mode on a joined-into PI is refused ----------
    from types import SimpleNamespace
    from bonsai.bim.module.alignment.operator import _apply_join_next_radii

    def pi(**kw):
        base = dict(curve_type="CIRCULAR", radius=200.0, spiral_in_length=0.0, spiral_out_length=0.0,
                    spiral_family="CLOTHOID", gravity_centerline_height=0.0, join_next=False,
                    join_mode="RADIUS", join_distance=100.0)
        base.update(kw)
        return SimpleNamespace(**base)

    pi3 = (pi2[0] + 400.0 * math.cos(d1 + d2), pi2[1] + 400.0 * math.sin(d1 + d2))
    poe3 = (pi3[0] + 500.0, pi3[1])
    hp = [(0.0, 0.0), pi1, pi2, pi3, poe3]
    items = [pi(join_next=True), pi(join_next=True, join_mode="DISTANCE"), pi()]
    ok, msg = _apply_join_next_radii(items, hp, [(0.0, 1.0)] * 3)
    print("chain refusal:", ok, msg)
    check(not ok and "already fixed" in msg, "chain distance mode not refused")

    print("JOIN_DISTANCE_TEST_OK")
except Exception:
    traceback.print_exc()
    print("JOIN_DISTANCE_TEST_FAILED")
sys.stdout.flush()
