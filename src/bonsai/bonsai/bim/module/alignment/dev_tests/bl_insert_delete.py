# This file was generated with the assistance of an AI coding tool.
# Development test script for the alignment authoring work -- remove before the final PR (see README.md).

"""Insert/Delete PI (viewport markers, horizontal PI table, vertical PI list) + Apply keep the other
PIs' segment GlobalIds."""

import sys
import traceback

import bpy

import bonsai.bim.handler
import bonsai.tool as tool
import ifcopenshell.api.alignment


def check(cond, msg):
    if not cond:
        raise AssertionError(msg)


def guids(layout):
    return [s.GlobalId for s in tool.Alignment.get_real_layout_segments(layout)]


def types(layout):
    return [s.DesignParameters.PredefinedType for s in tool.Alignment.get_real_layout_segments(layout)]


def select(obj):
    for o in bpy.context.selected_objects:
        o.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


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
    R = [(300.0, 60.0, 60.0), (400.0, 80.0, 80.0), 350.0]
    V = [(0.0, 100.0), (900.0, 110.0), (2000.0, 104.0), (3000.0, 108.0)]
    alignment = ifcopenshell.api.alignment.create_by_pi_method(ifc, "T", H, R, V, [200.0, 150.0])
    tool.Alignment.create_object_for_alignment(alignment)
    tool.Alignment.refresh_alignment_representation_object(alignment)
    obj = tool.Ifc.get_object(alignment)
    select(obj)
    h = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
    v = ifcopenshell.api.alignment.get_vertical_layout(alignment)
    g0 = guids(h)
    print("h:", types(h))

    # ---- viewport markers: delete PI 2, Apply
    check(bpy.ops.align.edit_horizontal_pis() == {"FINISHED"}, "edit pis")
    markers = op_mod._find_pi_markers(alignment.id())
    print("markers:", [m.name for m in markers])
    select(markers[2])
    check(bpy.ops.align.delete_pi_marker() == {"FINISHED"}, "delete marker")
    markers = op_mod._find_pi_markers(alignment.id())
    check([m.bonsai_pi_curve_marker.pi_index for m in markers] == [0, 1, 2, 3], "renumber")
    check(bpy.context.view_layer.objects.active == markers[1], "previous selected")
    check(bpy.ops.align.apply_pi_curve() == {"FINISHED"}, "apply")
    g1 = guids(h)
    print("after delete:", types(h))
    check(g1 == g0[:4] + g0[8:], "delete kept the others")

    # ---- insert after PI 1, move it off the line, give it a curve, Apply
    select(markers[1])
    check(bpy.ops.align.insert_pi_marker() == {"FINISHED"}, "insert marker")
    markers = op_mod._find_pi_markers(alignment.id())
    check(len(markers) == 5 and [m.bonsai_pi_curve_marker.pi_index for m in markers] == [0, 1, 2, 3, 4], "insert renumber")
    new = bpy.context.view_layer.objects.active
    check(new == markers[2] and new.bonsai_pi_curve_marker.role == "PI", "new marker active")
    new.location.y += 150.0
    new.bonsai_pi_curve_marker.curve_type = "CIRCULAR"
    new.bonsai_pi_curve_marker.radius = 250.0
    check(bpy.ops.align.apply_pi_curve() == {"FINISHED"}, "apply insert")
    g2 = guids(h)
    print("after insert:", types(h))
    check(g2[:4] == g1[:4] and g2[-3:] == g1[-3:], f"insert kept the others")
    check(not set(g2[4:-3]) & set(g1), "insert made new ones")
    check(bpy.ops.align.finish_pi_editing() == {"FINISHED"}, "finish")

    # ---- horizontal PI table: delete the new PI again
    select(obj)
    check(bpy.ops.align.load_horizontal_pi_table() == {"FINISHED"}, "load table")
    check(len(props.horizontal_pi_rows) == 3, "3 rows")
    props.active_horizontal_pi_row_index = 1
    check(bpy.ops.align.delete_pi_row(kind="HORIZONTAL") == {"FINISHED"}, "delete row")
    check(bpy.ops.align.apply_horizontal_pi_table() == {"FINISHED"}, "apply table")
    g3 = guids(h)
    check(g3 == g2[:4] + g2[-3:], "table delete kept others")
    # insert before the first row: halfway along the first leg
    props.active_horizontal_pi_row_index = 0
    check(bpy.ops.align.insert_pi_row(kind="HORIZONTAL", after=False) == {"FINISHED"}, "insert row")
    check(props.active_horizontal_pi_row_index == 0 and abs(props.horizontal_pi_rows[0].x - 400.0) < 1e-6, "row midpoint")
    props.horizontal_pi_rows[0].y = 100.0
    check(bpy.ops.align.apply_horizontal_pi_table() == {"FINISHED"}, "apply table insert")
    print("after table insert:", types(h))
    rows = props.horizontal_pi_rows
    start, end = tool.Alignment.get_alignment_start_end_points(alignment)
    hp = [start] + [(r.x, r.y) for r in rows] + [end]
    print("hpoints", hp)
    radii = [op_mod._pi_curve_radii_entry(r, None) for r in rows]
    try:
        ifcopenshell.api.alignment.solve_horizontal_alignment_by_pi_method(hp, radii)
    except Exception as e:
        print("solver:", e)
    g4 = guids(h)
    check(len(g4) == 8 and g4[0] not in g3 and g4[1] == g3[0] and g4[2:] == g3[1:], f"table insert {types(h)}")
    check(bpy.ops.align.finish_horizontal_pi_table() == {"FINISHED"}, "finish table")

    # ---- vertical PI list: delete VPI 1, then insert one after the remaining VPI
    vg0 = guids(v)
    check(bpy.ops.align.load_vertical_pis() == {"FINISHED"}, "load vpis")
    props.active_vertical_pi_marker_index = 0
    check(bpy.ops.align.delete_pi_row(kind="VERTICAL") == {"FINISHED"}, "delete vpi")
    check(bpy.ops.align.apply_vertical_pi_curve() == {"FINISHED"}, "apply v")
    check(guids(v) == vg0[2:], f"v delete {types(v)}")
    check(bpy.ops.align.insert_pi_row(kind="VERTICAL", after=True) == {"FINISHED"}, "insert vpi")
    m = props.vertical_pi_markers[1]
    check(abs(m.dist_along - 2500.0) < 1e-6, f"vpi midpoint {m.dist_along}")
    m.elevation += 3.0
    check(bpy.ops.align.apply_vertical_pi_curve() == {"FINISHED"}, "apply v insert")
    vg = guids(v)
    print("v after insert:", types(v))
    check(vg[:2] == vg0[2:4] and vg[-1] == vg0[-1], "v insert kept the others")
    print("ALL OK")
except Exception:
    traceback.print_exc()
    sys.exit(1)
sys.exit(0)
