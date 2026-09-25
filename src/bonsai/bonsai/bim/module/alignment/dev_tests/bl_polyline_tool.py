# This file was generated with the assistance of an AI coding tool.
# Development test script for the alignment authoring work -- remove before the final PR (see README.md).

import sys
import traceback

import bpy

import bonsai.bim.handler
import bonsai.tool as tool
import ifcopenshell
import ifcopenshell.api.alignment
import ifcopenshell.api.geometry


def check(cond, msg):
    if not cond:
        raise AssertionError(msg)


try:
    bpy.ops.wm.read_homefile(app_template="")
    bpy.data.batch_remove(bpy.data.objects)
    bonsai.bim.handler.load_post(None)
    tool.Project.get_project_props().export_schema = "IFC4X3_ADD2"
    bpy.ops.bim.create_project()
    ifc = tool.Ifc.get()
    A = tool.Alignment

    # a bare polyline alignment, then its first points
    a = A.create_bare_alignment("P2")
    check(A.is_bare_alignment(a) and not A.is_polyline_alignment(a), "new alignment should be bare")
    check(a.Decomposes and a.Decomposes[0].RelatingObject.is_a("IfcProject"), "not aggregated to project")
    A.set_polyline_points(a, [(0, 0), (100, 0), (150, 80)], 2)
    check(A.is_polyline_alignment(a) and not A.is_bare_alignment(a), "not a polyline alignment after drawing")
    pts, dim = A.get_polyline_points(a)
    print("P2:", pts, dim, A.get_polyline_curve(a).is_a())
    check(pts == [(0.0, 0.0), (100.0, 0.0), (150.0, 80.0)] and dim == 2, "points not written")
    obj = tool.Ifc.get_object(a)
    check(obj is not None and obj.type == "MESH" and len(obj.data.vertices) == 3, "mesh not built")
    rep = a.Representation.Representations[0]
    check((rep.RepresentationIdentifier, rep.RepresentationType) == ("Axis", "Curve2D"), "wrong representation")

    # update in place: same curve entity, old points cleaned up, mesh refreshed
    curve_id = A.get_polyline_curve(a).id()
    n_points_before = len(ifc.by_type("IfcCartesianPoint"))
    A.set_polyline_points(a, [(0, 0), (100, 10), (150, 80), (220, 90)], 2)
    check(A.get_polyline_curve(a).id() == curve_id, "curve entity replaced instead of updated")
    check(A.get_polyline_points(a)[0][3] == (220.0, 90.0), "update lost")
    check(len(ifc.by_type("IfcCartesianPoint")) == n_points_before + 1, "orphaned points left behind")
    check(len(tool.Ifc.get_object(a).data.vertices) == 4, "mesh not refreshed")

    # 3D from scratch
    b = A.create_bare_alignment("P3")
    A.set_polyline_points(b, [(0, 50, 10), (100, 50, 12), (160, 120, 11)], 3)
    pts, dim = A.get_polyline_points(b)
    rep = b.Representation.Representations[0]
    print("P3:", pts, dim, rep.RepresentationType)
    check(dim == 3 and pts[1] == (100.0, 50.0, 12.0) and rep.RepresentationType == "Curve3D", "3D wrong")

    # an IfcIndexedPolyCurve from a file keeps its type through an edit
    c = ifc.createIfcAlignment(GlobalId=ifcopenshell.guid.new(), Name="Idx")
    plist = ifc.createIfcCartesianPointList3D(((0.0, -50.0, 5.0), (80.0, -50.0, 6.0), (120.0, -10.0, 7.0)))
    curve = ifc.createIfcIndexedPolyCurve(Points=plist, Segments=None, SelfIntersect=False)
    rep = ifc.createIfcShapeRepresentation(
        ContextOfItems=ifcopenshell.api.alignment.get_axis_subcontext(ifc),
        RepresentationIdentifier="Axis", RepresentationType="Curve3D", Items=(curve,),
    )
    c.ObjectPlacement = ifc.createIfcLocalPlacement(
        RelativePlacement=ifc.createIfcAxis2Placement3D(Location=ifc.createIfcCartesianPoint((0.0, 0.0, 0.0)))
    )
    ifcopenshell.api.geometry.assign_representation(ifc, c, rep)
    check(A.get_polyline_points(c)[0][2] == (120.0, -10.0, 7.0), "indexed read")
    A.set_polyline_points(c, [(0, -50, 5), (80, -60, 6), (120, -10, 9), (150, 0, 9)], 3)
    check(A.get_polyline_curve(c).is_a("IfcIndexedPolyCurve"), "indexed curve type not kept")
    check(A.get_polyline_points(c)[0][3] == (150.0, 0.0, 9.0), "indexed update")
    check(plist.id() not in [e.id() for e in ifc.by_type("IfcCartesianPointList3D")], "old point list not removed")

    # line-index segments are read in order; arc segments are refused
    d = ifc.createIfcAlignment(GlobalId=ifcopenshell.guid.new(), Name="Seg")
    pl = ifc.createIfcCartesianPointList2D(((0.0, 0.0), (10.0, 0.0), (20.0, 5.0)))
    seg_curve = ifc.createIfcIndexedPolyCurve(Points=pl, Segments=[ifc.createIfcLineIndex((1, 2, 3))], SelfIntersect=False)
    ifcopenshell.api.geometry.assign_representation(ifc, d, ifc.createIfcShapeRepresentation(
        ContextOfItems=ifcopenshell.api.alignment.get_axis_subcontext(ifc),
        RepresentationIdentifier="Axis", RepresentationType="Curve2D", Items=(seg_curve,)))
    check(A.get_polyline_points(d)[0] == [(0.0, 0.0), (10.0, 0.0), (20.0, 5.0)], "line index read")
    seg_curve.Segments = [ifc.createIfcArcIndex((1, 2, 3))]
    try:
        A.get_polyline_points(d)
        raise AssertionError("arcs not refused")
    except ValueError as e:
        print("arcs refused:", e)

    # a layout-based alignment is not a polyline alignment
    e = ifcopenshell.api.alignment.create_by_pi_method(ifc, "L", [(0.0, 0.0), (100.0, 0.0)], [], [], [])
    check(not A.is_polyline_alignment(e) and not A.is_bare_alignment(e), "layout alignment misclassified")
    print("POLYLINE_TOOL_OK")
except Exception:
    traceback.print_exc()
    print("POLYLINE_TOOL_FAILED")
sys.stdout.flush()
