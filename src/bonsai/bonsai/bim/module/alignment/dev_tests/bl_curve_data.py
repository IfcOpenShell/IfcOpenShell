# This file was generated with the assistance of an AI coding tool.
# Development test script for the alignment authoring work -- remove before the final PR (see README.md).
#
# Computes the selected-segment highlight data (AlignmentSegmentDecorator.tangent_data) for every
# horizontal segment of a simple curve and a spiral-curve-spiral alignment, checks the curve data
# lines, and dumps the key points to CURVE_DATA_OUT (if set) so two versions can be diffed.

import json
import math
import os
import traceback

import bpy

import bonsai.bim.handler
import bonsai.tool as tool
import ifcopenshell.api.alignment
from bonsai.bim.module.alignment.decorator import AlignmentSegmentDecorator, _place_label_block


def check(cond, msg):
    if not cond:
        raise AssertionError(msg)


def rounded(value):
    if isinstance(value, (tuple, list)):
        return [rounded(v) for v in value]
    if isinstance(value, float):
        return round(value, 4)
    return value


def segment_data(alignment):
    horizontal = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
    result = []
    for segment in ifcopenshell.api.alignment.get_alignment_segment_nest(horizontal).RelatedObjects:
        if segment.DesignParameters.SegmentLength == 0.0:
            continue
        AlignmentSegmentDecorator._compute_segment_geometry(segment.id())
        td = AlignmentSegmentDecorator.tangent_data
        check(td is not None, f"no tangent data for {segment.DesignParameters.PredefinedType}")
        keys = ("start_world", "end_world", "pi_world", "center_world", "pc_perp", "pt_perp", "has_pi", "pc_station")
        result.append(
            {
                "type": segment.DesignParameters.PredefinedType,
                **{k: rounded(td.get(k)) for k in keys},
                "curve_props": td.get("curve_props"),
                "pi_station": td.get("pi_station"),
            }
        )
    return result


try:
    bpy.ops.wm.read_homefile(app_template="")
    bpy.data.batch_remove(bpy.data.objects)
    bonsai.bim.handler.load_post(None)
    tool.Project.get_project_props().export_schema = "IFC4X3_ADD2"
    bpy.ops.bim.create_project()
    ifc = tool.Ifc.get()

    dump = {}
    for name, radii in (("Simple", [500.0]), ("Spiral", [(500.0, 100.0, 100.0)])):
        alignment = ifcopenshell.api.alignment.create_by_pi_method(
            ifc, name, [(0.0, 0.0), (1000.0, 0.0), (1000.0, 1000.0)], radii
        )
        ifcopenshell.api.alignment.add_stationing_referent(ifc, "start", alignment, 0.0, 0.0)
        tool.Alignment.create_object_for_alignment(alignment)
        tool.Alignment.refresh_alignment_representation_object(alignment)
        dump[name] = segment_data(alignment)
        for seg in dump[name]:
            print(name, seg)

    out = os.environ.get("CURVE_DATA_OUT")
    if out:
        with open(out, "w") as f:
            json.dump({k: [{x: y for x, y in s.items() if x not in ("curve_props", "pi_station")} for s in v] for k, v in dump.items()}, f, indent=1)

    if dump["Simple"][1]["curve_props"] is not None:  # None on a decorator without curve data
        line, arc, _ = dump["Simple"]
        check(line["curve_props"] == [], f"straight should have no curve data: {line['curve_props']}")
        expected = [
            "R = 500.00 m",
            "T = 500.00 m",
            "Δ = 90°00'00.00\" Lt",
            f"L = {250.0 * math.pi:.2f} m",
            f"LC = {1000.0 * math.sin(math.pi / 4.0):.2f} m",
            f"E = {500.0 * (math.sqrt(2.0) - 1.0):.2f} m",
            f"M = {500.0 * (1.0 - math.sqrt(0.5)):.2f} m",
        ]
        check(arc["curve_props"] == expected, f"curve data {arc['curve_props']} != {expected}")
        # P.I. station = P.C. station + T
        check(abs(arc["pi_station"] - 1000.0) < 1e-6, f"P.I. station {arc['pi_station']} != 1000")
        spiral_in, spiral_arc = dump["Spiral"][1], dump["Spiral"][2]
        x, y, theta = ifcopenshell.api.alignment.compute_clothoid_end(100.0, 0.0, 1.0 / 500.0)
        expected = [
            f"T1 = {x - y / math.tan(theta):.2f} m",
            f"T2 = {y / math.sin(theta):.2f} m",
            "Δ = 5°43'46.48\" Lt",
            "L = 100.00 m",
            f"LC = {math.hypot(x, y):.2f} m",
        ]
        check(spiral_in["curve_props"] == expected, f"spiral data {spiral_in['curve_props']} != {expected}")
        check(spiral_arc["curve_props"][0] == "R = 500.00 m", f"arc data {spiral_arc['curve_props']}")
        # S.C. station + T for the arc between the spirals (pc_station is rounded to 4 places)
        expected_pi = spiral_arc["pc_station"] + 500.0 * math.tan((math.pi / 2.0 - 0.2) / 2.0)
        check(abs(spiral_arc["pi_station"] - expected_pi) < 1e-3, f"S.C.+T {spiral_arc['pi_station']} != {expected_pi}")

    # Curve data block placement: inward when clear, else around the anchor, never over a label
    def overlaps(a, b):
        return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])

    rect = _place_label_block((500, 400), (0, -1), 120, 90, [], 1000, 800)
    check(rect[3] <= 400 - 16 + 1e-6 and abs((rect[0] + rect[2]) / 2 - 500) < 1e-6, f"not placed inward: {rect}")
    blocked = [(400, 200, 600, 390)]
    rect = _place_label_block((500, 400), (0, -1), 120, 90, blocked, 1000, 800)
    check(not overlaps(rect, blocked[0]), f"overlaps a label: {rect}")
    rect = _place_label_block((990, 790), (1, 1), 120, 90, [], 1000, 800)
    check(rect[0] >= 0 and rect[1] >= 0 and rect[2] <= 1000 and rect[3] <= 800, f"off screen: {rect}")
    print("ALL OK")
except Exception:
    traceback.print_exc()
    raise
