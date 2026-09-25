# This file was generated with the assistance of an AI coding tool.
# Development test script for the alignment authoring work -- remove before the final PR (see README.md).

import sys
import traceback

import bpy

import bonsai.bim.handler
import bonsai.tool as tool
import ifcopenshell.api.alignment


def check(cond, msg):
    if not cond:
        raise AssertionError(msg)


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
    A = tool.Alignment
    from bonsai.bim.module.alignment import operator as op_mod
    from bonsai.bim.module.model.polyline import PolylineOperator

    props = bpy.context.scene.CivilAlignmentProperties

    # ---- Add Alignment (Polyline) -> a bare alignment
    check(bpy.ops.align.add_alignment(alignment_name="Survey", definition="POLYLINE") == {"FINISHED"}, "add")
    a = next(x for x in ifc.by_type("IfcAlignment") if x.Name == "Survey")
    check(A.is_bare_alignment(a) and tool.Alignment.get_active_alignment() == a, "not bare/active")
    print("polls on bare: draw polyline", bpy.ops.align.draw_polyline_alignment.poll(),
          "| draw PI", bpy.ops.align.draw_horizontal_alignment.poll())
    check(bpy.ops.align.draw_polyline_alignment.poll(), "draw polyline disabled on bare")

    # ---- the draw tool: 2D/3D modes and finish (modal can't run headless; drive its pieces)
    Op = op_mod.ALIGN_OT_draw_polyline_alignment

    class Fake(op_mod._CivilAngleInput, PolylineOperator):
        pass

    for name in ("_set_mode", "_finish"):
        setattr(Fake, name, op_mod._DrawPolylineAlignment.__dict__[name])
    op = Fake()
    PolylineOperator.__init__(op)
    reports = []
    op.report = lambda level, msg: reports.append(msg)
    op._set_mode(True)
    check(op.input_ui.input_options == ["D", "A", "X", "Y", "Z"] and op.tool_state.plane_method is None
          and op.input_ui.get_number_value("Z") == 0.0, "3D mode setup")
    op._set_mode(False)
    check(op.input_ui.input_options == ["D", "A", "X", "Y"] and op.tool_state.plane_method == "XY"
          and op.input_ui.get_number_value("Z") is None, "2D mode setup")

    def draw(points_world, is_3d):
        tool.Polyline.clear_polyline()
        data = tool.Model.get_polyline_props().insertion_polyline.add()
        for x, y, z in points_world:
            p = data.polyline_points.add()
            p.x, p.y, p.z = x, y, z
        op._is_3d = is_3d
        op._finish(bpy.context)
        tool.Polyline.clear_polyline()

    draw([(0, 0, 0), (100, 0, 0), (150, 80, 0)], False)
    pts, dim = A.get_polyline_points(a)
    print("drew 2D:", pts, dim, reports[-1])
    check(dim == 2 and pts == [(0.0, 0.0), (100.0, 0.0), (150.0, 80.0)], "2D draw")
    check(a.ObjectPlacement.RelativePlacement.is_a("IfcAxis2Placement2D"), "2D placement")
    check(A.is_polyline_alignment(a), "not polyline after draw")
    print("polls on polyline: draw PI", bpy.ops.align.draw_horizontal_alignment.poll(),
          "| edit PIs", bpy.ops.align.edit_horizontal_pis.poll(),
          "| edit points", bpy.ops.align.edit_polyline_points.poll(),
          "| key points", bpy.ops.align.generate_key_points.poll())
    check(not bpy.ops.align.draw_horizontal_alignment.poll(), "PI draw allowed on a polyline alignment")
    check(bpy.ops.align.edit_polyline_points.poll() and bpy.ops.align.load_polyline_table.poll(), "edit disabled")

    # ---- point markers: drag, apply, finish
    check(bpy.ops.align.edit_polyline_points() == {"FINISHED"}, "edit points")
    ms = op_mod._find_pi_markers(a.id())
    check([m.bonsai_pi_curve_marker.role for m in ms] == ["VERTEX"] * 3 and ms[0].lock_location[2], "markers")
    ms[1].location = (110.0, 20.0, 0.0)
    select(ms[1])
    check(bpy.ops.align.move_pi_marker.poll(), "Move with Distance/Angle unavailable on a point marker")
    check(bpy.ops.align.apply_pi_curve() == {"FINISHED"}, "apply markers")
    check(A.get_polyline_points(a)[0][1] == (110.0, 20.0), f"marker apply: {A.get_polyline_points(a)}")
    check(bpy.ops.align.finish_pi_editing() == {"FINISHED"} and not op_mod._find_pi_markers(a.id()), "finish")

    # ---- table: insert a point after row 1, remove the last, apply
    select(tool.Ifc.get_object(a))
    check(bpy.ops.align.load_polyline_table() == {"FINISHED"} and len(props.polyline_point_rows) == 3, "load table")
    props.active_polyline_point_row_index = 0
    bpy.ops.align.add_polyline_point_row()
    rows = [(r.x, r.y) for r in props.polyline_point_rows]
    print("after add:", rows)
    check(rows[1] == (55.0, 10.0), "midpoint insert")
    props.polyline_point_rows[3].x = 200.0
    check(bpy.ops.align.apply_polyline_table() == {"FINISHED"}, "apply table")
    pts = A.get_polyline_points(a)[0]
    check(len(pts) == 4 and pts[1] == (55.0, 10.0) and pts[3][0] == 200.0, f"table apply: {pts}")
    props.active_polyline_point_row_index = 3
    bpy.ops.align.remove_polyline_point_row()
    bpy.ops.align.apply_polyline_table()
    check(len(A.get_polyline_points(a)[0]) == 3, "remove row")
    bpy.ops.align.finish_polyline_table()
    check(not props.polyline_point_rows, "table finish")

    # ---- 3D: redraw in 3D, markers free in Z, table has elevations
    select(tool.Ifc.get_object(a))
    draw([(0, 0, 10), (100, 0, 12), (150, 80, 11)], True)
    pts, dim = A.get_polyline_points(a)
    print("drew 3D:", pts, dim)
    check(dim == 3 and pts[1] == (100.0, 0.0, 12.0), "3D draw")
    check(a.Representation.Representations[0].RepresentationType == "Curve3D", "Curve3D")
    check(a.ObjectPlacement.RelativePlacement.is_a("IfcAxis2Placement3D"), "placement not 3D after 3D redraw")
    bpy.ops.align.edit_polyline_points()
    ms = op_mod._find_pi_markers(a.id())
    check(not ms[1].lock_location[2], "3D marker Z locked")
    ms[1].location = (100.0, 0.0, 15.0)
    select(ms[1])
    bpy.ops.align.apply_pi_curve()
    check(A.get_polyline_points(a)[0][1] == (100.0, 0.0, 15.0), "3D marker Z not applied")
    bpy.ops.align.finish_pi_editing()
    select(tool.Ifc.get_object(a))
    bpy.ops.align.load_polyline_table()
    check(props.editing_polyline_is_3d and props.polyline_point_rows[1].z == 15.0, "3D table")
    props.polyline_point_rows[2].z = 20.0
    bpy.ops.align.apply_polyline_table()
    check(A.get_polyline_points(a)[0][2][2] == 20.0, "3D table apply")
    bpy.ops.align.finish_polyline_table()

    # ---- a layout-based alignment is unaffected; deleting the polyline alignment is clean
    check(bpy.ops.align.remove_alignment() == {"FINISHED"}, "remove")
    check(not [x for x in ifc.by_type("IfcAlignment") if x.Name == "Survey"], "not removed")
    print("POLYLINE_FLOW_OK")
except Exception:
    traceback.print_exc()
    print("POLYLINE_FLOW_FAILED")
sys.stdout.flush()
