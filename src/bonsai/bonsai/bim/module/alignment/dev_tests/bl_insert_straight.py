# This file was generated with the assistance of an AI coding tool.
# Development test script for the alignment authoring work -- remove before the final PR (see README.md).

"""Insert a PI on a straight leg and Apply without moving it: the straight is split there (it used to
divide by zero in the PI solver). Edit PIs then sees one straight with a split point, and keeps it."""

import sys
import traceback

import bpy
import ifcopenshell.api.alignment as A

import bonsai.bim.handler
import bonsai.tool as tool


def select(obj):
    for o in bpy.context.selected_objects:
        o.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def check(cond, msg):
    if not cond:
        raise AssertionError(msg)


def types(layout):
    return [s.DesignParameters.PredefinedType for s in tool.Alignment.get_real_layout_segments(layout)]


try:
    bpy.ops.wm.read_homefile(app_template="")
    bpy.data.batch_remove(bpy.data.objects)
    bonsai.bim.handler.load_post(None)
    tool.Project.get_project_props().export_schema = "IFC4X3_ADD2"
    bpy.ops.bim.create_project()
    ifc = tool.Ifc.get()
    from bonsai.bim.module.alignment import operator as op_mod

    alignment = A.create_by_pi_method(ifc, "T", [(0.0, 0.0), (800.0, 0.0), (1400.0, 600.0)], [300.0], [], [])
    tool.Alignment.create_object_for_alignment(alignment)
    tool.Alignment.refresh_alignment_representation_object(alignment)
    obj = tool.Ifc.get_object(alignment)
    h = A.get_horizontal_layout(alignment)
    print("before:", types(h))

    select(obj)
    print("edit:", bpy.ops.align.edit_horizontal_pis())
    markers = op_mod._find_pi_markers(alignment.id())
    print("markers:", [m.name for m in markers])

    # insert a PI after Start: on the straight leg, zero deflection
    select(markers[0])
    print("insert:", bpy.ops.align.insert_pi_marker())
    markers = op_mod._find_pi_markers(alignment.id())
    print("markers:", [(m.name, tuple(round(v, 3) for v in m.location[:2])) for m in markers])

    select(markers[1])
    check(bpy.ops.align.apply_pi_curve() == {"FINISHED"}, "apply failed")
    print("after apply:", types(h))
    check(types(h) == ["LINE", "LINE", "CIRCULARARC", "LINE"], "straight not split at the inserted PI")
    check(op_mod._split_tangent_stations(tool.Alignment.get_real_layout_segments(h)) == [400.0], "split point")

    select(markers[1])
    print("finish:", bpy.ops.align.finish_pi_editing())
    select(obj)
    print("edit again:", bpy.ops.align.edit_horizontal_pis())
    markers = op_mod._find_pi_markers(alignment.id())
    print("markers again:", [(m.name, tuple(round(v, 3) for v in m.location[:2])) for m in markers])
    check(len(markers) == 3, "the split straight should be one tangent to Edit PIs")
    check(tuple(markers[1].location[:2]) == (800.0, 0.0), "PI moved")

    # applying again keeps the split
    select(markers[1])
    check(bpy.ops.align.apply_pi_curve() == {"FINISHED"}, "second apply failed")
    check(types(h) == ["LINE", "LINE", "CIRCULARARC", "LINE"], f"split lost: {types(h)}")
    print("INSERT_STRAIGHT_TEST_OK")
except Exception:
    traceback.print_exc()
    print("INSERT_STRAIGHT_TEST_FAILED")
    sys.exit(1)
