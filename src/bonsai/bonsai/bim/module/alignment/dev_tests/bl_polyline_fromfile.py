# This file was generated with the assistance of an AI coding tool.
# Development test script for the alignment authoring work -- remove before the final PR (see README.md).

import os, sys, tempfile, traceback, bpy
import bonsai.bim.handler, bonsai.tool as tool
try:
    path = os.path.join(tempfile.gettempdir(), "polyline_alignments.ifc")
    bpy.ops.wm.read_homefile(app_template="")
    bpy.data.batch_remove(bpy.data.objects)
    bonsai.bim.handler.load_post(None)
    assert bpy.ops.bim.load_project(filepath=path, should_start_fresh_session=True) == {"FINISHED"}
    ifc = tool.Ifc.get()
    from bonsai.bim.module.alignment import operator as op_mod
    props = bpy.context.scene.CivilAlignmentProperties
    a = next(x for x in ifc.by_type("IfcAlignment") if x.Name == "Indexed3D")
    obj = tool.Ifc.get_object(a)
    for o in bpy.context.selected_objects: o.select_set(False)
    obj.select_set(True); bpy.context.view_layer.objects.active = obj
    print("polls:", bpy.ops.align.load_polyline_table.poll(), bpy.ops.align.edit_polyline_points.poll(), bpy.ops.align.draw_horizontal_alignment.poll())
    assert bpy.ops.align.load_polyline_table() == {"FINISHED"}
    print("rows:", [(r.x, r.y, r.z) for r in props.polyline_point_rows], props.editing_polyline_is_3d)
    props.active_polyline_point_row_index = 2
    bpy.ops.align.add_polyline_point_row()  # continues the last leg
    assert bpy.ops.align.apply_polyline_table() == {"FINISHED"}
    pts, dim = tool.Alignment.get_polyline_points(a)
    print("after:", pts, dim, tool.Alignment.get_polyline_curve(a).is_a(), "mesh verts:", len(tool.Ifc.get_object(a).data.vertices))
    assert len(pts) == 4 and pts[3] == (160.0, 30.0, 8.0) and tool.Alignment.get_polyline_curve(a).is_a("IfcIndexedPolyCurve")
    bpy.ops.align.finish_polyline_table()
    # save and reload: the edit round-trips
    out = os.path.join(tempfile.gettempdir(), "polyline_alignments_edited.ifc")
    ifc.write(out)
    bpy.ops.wm.read_homefile(app_template=""); bpy.data.batch_remove(bpy.data.objects); bonsai.bim.handler.load_post(None)
    bpy.ops.bim.load_project(filepath=out, should_start_fresh_session=True)
    a = next(x for x in tool.Ifc.get().by_type("IfcAlignment") if x.Name == "Indexed3D")
    print("reloaded:", tool.Alignment.get_polyline_points(a)[0][3], len(tool.Ifc.get_object(a).data.vertices))
    # and markers on a loaded one
    obj = tool.Ifc.get_object(a)
    for o in bpy.context.selected_objects: o.select_set(False)
    obj.select_set(True); bpy.context.view_layer.objects.active = obj
    assert bpy.ops.align.edit_polyline_points() == {"FINISHED"}
    ms = op_mod._find_pi_markers(a.id())
    print("marker locations:", [tuple(round(v, 3) for v in m.location) for m in ms])
    assert tuple(round(v, 3) for v in ms[3].location) == (160.0, 30.0, 8.0)
    print("FROMFILE_OK")
except Exception:
    traceback.print_exc(); print("FROMFILE_FAILED")
sys.stdout.flush()
