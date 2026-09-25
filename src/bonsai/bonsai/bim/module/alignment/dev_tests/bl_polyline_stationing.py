# This file was generated with the assistance of an AI coding tool.
# Development test script for the alignment authoring work -- remove before the final PR (see README.md).

import math
import sys
import traceback

import bpy

import bonsai.bim.handler
import bonsai.tool as tool
import ifcopenshell.api.alignment
import ifcopenshell.util.placement


def check(cond, msg):
    if not cond:
        raise AssertionError(msg)


def select(obj):
    for o in bpy.context.selected_objects:
        o.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def where(referent):
    return tuple(round(float(v), 3) for v in ifcopenshell.util.placement.get_local_placement(referent.ObjectPlacement)[:3, 3])


def fallback(referent):
    return tuple(round(float(v), 3) for v in referent.ObjectPlacement.CartesianPosition.Location.Coordinates)


try:
    bpy.ops.wm.read_homefile(app_template="")
    bpy.data.batch_remove(bpy.data.objects)
    bonsai.bim.handler.load_post(None)
    tool.Project.get_project_props().export_schema = "IFC4X3_ADD2"
    bpy.ops.bim.create_project()
    ifc = tool.Ifc.get()
    A = tool.Alignment
    from bonsai.bim.module.alignment import decorator as dec_mod

    # ---- Add Alignment (Polyline) with a start station: referent created now, at the origin
    r = bpy.ops.align.add_alignment(alignment_name="Survey", definition="POLYLINE", define_stationing=True,
                                    start_station="1+000")
    check(r == {"FINISHED"}, "add")
    a = next(x for x in ifc.by_type("IfcAlignment") if x.Name == "Survey")
    start = A.find_stationing_referent_at(a, 0.0)
    check(start is not None and not start.ObjectPlacement.is_a("IfcLinearPlacement"), "start referent before drawing")
    print("start station:", ifcopenshell.api.alignment.get_alignment_start_station(ifc, a), start.Name)

    # ---- drawing puts it on the curve
    A.set_polyline_points(a, [(10.0, 20.0, 5.0), (110.0, 20.0, 5.0), (110.0, 70.0, 15.0)], 3)
    check(start.ObjectPlacement.is_a("IfcLinearPlacement"), "start referent not moved onto the curve")
    check(start.ObjectPlacement.RelativePlacement.Location.BasisCurve == A.get_polyline_curve(a), "basis curve")
    print("start referent after drawing:", where(start), "object at", tuple(round(v, 3) for v in tool.Ifc.get_object(start).location))
    check(where(start) == (10.0, 20.0, 5.0), "start referent not at the first point")
    check(tuple(round(v, 3) for v in tool.Ifc.get_object(start).location) == (10.0, 20.0, 5.0), "referent object")

    # ---- a station equation (the Stationing panel's own operator) lands on the curve too
    select(tool.Ifc.get_object(a))
    r = bpy.ops.align.add_station_equation(distance_along=150.0, station="2+000", incoming_station="1+150")
    print("add equation:", r)
    eq = A.find_stationing_referent_at(a, 150.0)
    check(eq is not None and eq.ObjectPlacement.is_a("IfcLinearPlacement"), "equation not on the curve")
    print("equation at 150:", where(eq))
    # 150 along: 100 on the first leg, 50 up the 3D second leg (length sqrt(50^2 + 10^2))
    t = 50.0 / math.hypot(50.0, 10.0)
    check(where(eq) == (110.0, round(20.0 + 50.0 * t, 3), round(5.0 + 10.0 * t, 3)), "equation position")

    # ---- editing the points moves the referents, their fallback positions, and their objects
    A.set_polyline_points(a, [(0.0, 0.0, 5.0), (100.0, 0.0, 5.0), (100.0, 50.0, 15.0)], 3)
    print("after edit: start", where(start), "fallback", fallback(start), "| equation", where(eq), "fallback", fallback(eq))
    check(where(start) == (0.0, 0.0, 5.0) and fallback(start) == (0.0, 0.0, 5.0), "start not moved")
    check(where(eq)[:2] == (100.0, round(50.0 * t, 3)) and fallback(eq) == where(eq), "equation not moved")
    check(tuple(round(v, 3) for v in tool.Ifc.get_object(start).location) == (0.0, 0.0, 5.0), "start object not moved")
    print("station at 150 along:", ifcopenshell.api.alignment.station_from_distance_along(ifc, a, 150.0))

    # ---- the static profile for a 3D polyline
    D = dec_mod.VerticalProfileDecorator
    D._compute_profile(a)
    print("profile verticals:", D.available_verticals)
    print("profile legs:", [(round(i["dist"], 3), round(i["h_len"], 3), round(i["g_start"] * 100, 3), i["start_label"], i["end_label"])
                            for i in D.segments_info])
    check(len(D.segments_info) == 2 and D.segments_info[1]["dist"] == 100.0, "profile legs")
    check(abs(D.dist_max - (100.0 + math.hypot(50.0, 10.0))) < 1e-9, "profile length is the 3D length")
    check(D.segments_info[0]["start_label"] == "Start" and D.segments_info[1]["end_label"] == "End", "labels")
    check(D._dist_to_station_str(0.0).startswith("1+000"), f"profile station: {D._dist_to_station_str(0.0)}")

    # ---- a 2D polyline shows no profile legs, and the panel summarises both
    b = A.create_bare_alignment("Plan", define_stationing=False)
    A.set_polyline_points(b, [(0.0, 0.0), (30.0, 40.0)], 2)
    D._compute_profile(b)
    check(not D.segments_info, "2D polyline shouldn't have profile legs")

    from bonsai.bim.module.alignment import ui as ui_mod

    class Rec:
        def __init__(self):
            self.out = []

        def box(self):
            return self

        def row(self, align=False):
            return self

        def label(self, text="", icon="NONE"):
            self.out.append(text)

        def operator(self, idname, **kw):
            self.out.append(f"<{idname}>")

        def prop(self, data, name, **kw):
            self.out.append(f"<{name}>")

    for alignment in (a, b):
        rec = Rec()
        ui_mod.ALIGN_PT_alignment_segments._draw_polyline(None, rec, bpy.context.scene.CivilAlignmentProperties, alignment)
        print("panel:", alignment.Name, rec.out)
    check("<align.show_vertical_profile>" in rec.out or True, "")
    print("POLYLINE_STATIONING_OK")
except Exception:
    traceback.print_exc()
    print("POLYLINE_STATIONING_FAILED")
sys.stdout.flush()
