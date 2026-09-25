# This file was generated with the assistance of an AI coding tool.
# Development test script for the alignment authoring work -- remove before the final PR (see README.md).

import sys, traceback, bpy
sys.path.insert(0, r"F:\ifcopenshell\src\bonsai")
try:
    import bonsai.tool as tool
    from test.tool.test_polyline import TestCalculateXYAndZStraightOn
    for name in ("test_180_degrees_continues_a_diagonal_leg_straight_on",
                 "test_180_degrees_from_a_single_point_still_goes_along_negative_x"):
        props = tool.Model.get_polyline_props()
        props.insertion_polyline.clear()
        props.snap_mouse_point.clear()
        getattr(TestCalculateXYAndZStraightOn(), name)()
        print("passed:", name)
    print("POLYLINE_180_TEST_OK")
except Exception:
    traceback.print_exc()
    print("POLYLINE_180_TEST_FAILED")
sys.stdout.flush()
