# This file was generated with the assistance of an AI coding tool.
# Development test script for the alignment authoring work -- remove before the final PR (see README.md).

"""The cant (for a Viennese bend) each PI gets on Apply follows that PI through an insert or a delete:
PIs are matched as update_layout_segments' segments are (map_segments_by_pi), not by their index."""

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
    from bonsai.bim.module.alignment import operator as op_mod

    A, B, C = (800.0, 0.0), (1400.0, 600.0), (2200.0, 600.0)
    # the alignment's current PIs: only B carries cant
    specs = [
        {"pi_local": A, "cant": 0.0, "rail_head_distance": 1.5},
        {"pi_local": B, "cant": 0.15, "rail_head_distance": 1.5},
        {"pi_local": C, "cant": 0.0, "rail_head_distance": 1.5},
    ]
    op_mod._reconstruct_horizontal_pis = lambda h_layout: (specs, [])
    alignment = tool.Ifc.get().createIfcAlignment(GlobalId="0" * 22)
    tool.Alignment.add_horizontal_layout_to_alignment(alignment)

    def lookup(pis):
        return [cant for cant, _ in op_mod._cant_lookup_for_pi_markers(alignment, pis)]

    default = (0.0, 1.0)
    # unchanged, and moved (same count: each PI keeps its own)
    check(lookup([A, B, C]) == [0.0, 0.15, 0.0], f"unchanged {lookup([A, B, C])}")
    check(lookup([A, (1500.0, 650.0), C]) == [0.0, 0.15, 0.0], "moved PI lost its cant")
    # a PI inserted before B: B keeps its cant, the new PI gets the default
    got = op_mod._cant_lookup_for_pi_markers(alignment, [A, (1100.0, 300.0), B, C])
    check([c for c, _ in got] == [0.0, 0.0, 0.15, 0.0], f"insert {got}")
    check(got[1] == default, f"inserted PI {got[1]}")
    # A deleted: B keeps its cant
    check(lookup([B, C]) == [0.15, 0.0], f"delete {lookup([B, C])}")
    print("CANT_LOOKUP_TEST_OK")
except Exception:
    traceback.print_exc()
    print("CANT_LOOKUP_TEST_FAILED")
    sys.exit(1)
