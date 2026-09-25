# This file was generated with the assistance of an AI coding tool.
# Development test script for the alignment authoring work -- remove before the final PR (see README.md).

import os
import sys
import tempfile
import traceback

import bpy

import bonsai.bim.handler
import bonsai.tool as tool
import ifcopenshell
import ifcopenshell.api.alignment
import ifcopenshell.api.geometry

try:
    bpy.ops.wm.read_homefile(app_template="")
    bpy.data.batch_remove(bpy.data.objects)
    bonsai.bim.handler.load_post(None)
    tool.Project.get_project_props().export_schema = "IFC4X3_ADD2"
    bpy.ops.bim.create_project()
    ifc = tool.Ifc.get()

    pts2 = [ifc.createIfcCartesianPoint((x, y)) for x, y in [(0.0, 0.0), (100.0, 0.0), (150.0, 80.0)]]
    a2 = ifcopenshell.api.alignment.create_as_polyline(ifc, "Poly2D", pts2, start_station=0.0)
    pts3 = [ifc.createIfcCartesianPoint(p) for p in [(0.0, 50.0, 10.0), (100.0, 50.0, 12.0), (160.0, 120.0, 11.0)]]
    a3 = ifcopenshell.api.alignment.create_as_polyline(ifc, "Poly3D", pts3)

    # an IfcIndexedPolyCurve one, by hand (the API only writes IfcPolyline)
    a4 = ifc.createIfcAlignment(GlobalId=ifcopenshell.guid.new(), Name="Indexed3D")
    plist = ifc.createIfcCartesianPointList3D(((0.0, -50.0, 5.0), (80.0, -50.0, 6.0), (120.0, -10.0, 7.0)))
    curve = ifc.createIfcIndexedPolyCurve(Points=plist, Segments=None, SelfIntersect=False)
    rep = ifc.createIfcShapeRepresentation(
        ContextOfItems=ifcopenshell.api.alignment.get_axis_subcontext(ifc),
        RepresentationIdentifier="Axis", RepresentationType="Curve3D", Items=(curve,),
    )
    a4.ObjectPlacement = ifc.createIfcLocalPlacement(
        RelativePlacement=ifc.createIfcAxis2Placement3D(Location=ifc.createIfcCartesianPoint((0.0, 0.0, 0.0)))
    )
    ifcopenshell.api.geometry.assign_representation(ifc, a4, rep)
    ifcopenshell.api.aggregate.assign_object(ifc, products=[a4], relating_object=ifc.by_type("IfcProject")[0])

    path = os.path.join(tempfile.gettempdir(), "polyline_alignments.ifc")
    ifc.write(path)

    bpy.ops.wm.read_homefile(app_template="")
    bpy.data.batch_remove(bpy.data.objects)
    bonsai.bim.handler.load_post(None)
    print("load:", bpy.ops.bim.load_project(filepath=path, should_start_fresh_session=True))
    ifc = tool.Ifc.get()
    for a in ifc.by_type("IfcAlignment"):
        obj = tool.Ifc.get_object(a)
        rep_items = [
            (r.RepresentationIdentifier, r.RepresentationType, [i.is_a() for i in r.Items])
            for r in (a.Representation.Representations if a.Representation else [])
        ]
        info = None
        if obj is not None:
            info = (obj.name, obj.type, len(obj.data.vertices) if obj.type == "MESH" else None,
                    len(obj.data.edges) if obj.type == "MESH" else None)
        print(a.Name, "| reps:", rep_items, "| obj:", info,
              "| h layout:", ifcopenshell.api.alignment.get_horizontal_layout(a),
              "| curve:", (ifcopenshell.api.alignment.get_curve(a).is_a() if ifcopenshell.api.alignment.get_curve(a) else None))
        if obj is not None:
            for o in bpy.context.selected_objects:
                o.select_set(False)
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            active = tool.Alignment.get_active_alignment()
            print("   active alignment:", active.Name if active else None,
                  "| stationing:", tool.Alignment.get_stationing_referents(a)[:1])
            for opname in ("draw_horizontal_alignment", "edit_horizontal_pis", "generate_key_points", "draw_vertical_alignment"):
                op = getattr(bpy.ops.align, opname)
                print(f"   poll {opname}:", op.poll())
    print("PROBE_DONE")
except Exception:
    traceback.print_exc()
sys.stdout.flush()
