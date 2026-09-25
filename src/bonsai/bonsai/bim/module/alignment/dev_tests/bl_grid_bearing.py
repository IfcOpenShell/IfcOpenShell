# This file was generated with the assistance of an AI coding tool.
# Development test script for the alignment authoring work -- remove before the final PR (see README.md).

import math
import sys
import traceback
from types import SimpleNamespace

import bpy
from mathutils import Vector

import bonsai.bim.handler
import bonsai.tool as tool
import ifcopenshell.api.georeference


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

    from bonsai.bim.module.alignment import operator as op_mod
    from bonsai.bim.module.alignment import ui as ui_mod
    from bonsai.bim.module.model.polyline import PolylineOperator

    # no georeferencing: grid north is +Y
    check(abs(op_mod._grid_rotation_deg(True)) < 1e-9 and abs(op_mod._grid_rotation_deg(False)) < 1e-9, "rotation w/o georef")

    # georeference with the project's +X pointing 30 degrees anticlockwise of grid east
    ifcopenshell.api.georeference.add_georeferencing(ifc)
    t = math.radians(30.0)
    ifcopenshell.api.georeference.edit_georeferencing(
        ifc,
        projected_crs={"Name": "EPSG:26915"},
        coordinate_operation={
            "Eastings": 500000.0, "Northings": 4000000.0, "OrthogonalHeight": 0.0,
            "XAxisAbscissa": math.cos(t), "XAxisOrdinate": math.sin(t), "Scale": 1.0,
        },
    )
    rw, rl = op_mod._grid_rotation_deg(True), op_mod._grid_rotation_deg(False)
    print("grid rotation (world, local):", round(rw, 6), round(rl, 6))
    check(abs(rw - 30.0) < 1e-6 and abs(rl - 30.0) < 1e-6, "grid rotation not 30")

    # the Bearing readout: a leg along world +X is grid N 60 E
    hud = op_mod._bearing_string(0.0 + op_mod._grid_rotation_deg())
    print("readout for world +X:", hud)
    check(hud == "N 60°00'00.00\" E", hud)

    # the segment table: StartDirection 0 (project +X) is also N 60 E
    table = ui_mod._rad_to_bearing(0.0 + math.radians(op_mod._grid_rotation_deg(from_blender_world=False)))
    print("table for StartDirection 0:", table)
    check(table == "N 60°00'00.00\" E", table)

    # typing that grid bearing draws along world +X
    class Fake(op_mod._CivilAngleInput, PolylineOperator):
        pass

    op = Fake()
    PolylineOperator.__init__(op)
    op.report = lambda level, msg: print("report:", msg)
    op.snapping_points = [{"type": "Mouse"}]
    props = tool.Model.get_polyline_props()
    if not props.snap_mouse_point:
        props.snap_mouse_point.add()
    op.tool_state.use_default_container = False
    op.tool_state.plane_method = "XY"
    op.tool_state.is_input_on = False
    op_mod.ALIGN_OT_move_pi_marker._seed_anchor_points(op, bpy.context, [Vector((10.0, 20.0, 0.0))])
    mp = props.snap_mouse_point[0]
    mp.x, mp.y, mp.z = 3.0, -7.0, 0.0
    tool.Polyline.calculate_distance_and_angle(bpy.context, op.input_ui, op.tool_state)
    op.tool_state.is_input_on = True
    op.tool_state.mode = "Select"
    op.input_ui.set_value("D", 100)
    op.input_type = op.tool_state.input_type = "A"
    op.number_input = []
    for ch in "N 60 E":
        op.handle_keyboard_input(bpy.context, SimpleNamespace(value="PRESS", type=ch.upper(), ascii=ch))
    check(op.recalculate_inputs(bpy.context), "recalc failed")
    tool.Polyline.insert_polyline_point(op.input_ui, op.tool_state)
    p = op_mod.ALIGN_OT_move_pi_marker._polyline_points(op)[-1]
    print("typed N 60 E placed at:", (round(p.x, 4), round(p.y, 4)))
    check(abs(p.x - 110.0) < 1e-3 and abs(p.y - 20.0) < 1e-3, "grid bearing not converted back to world")

    print("GRID_BEARING_TEST_OK")
except Exception:
    traceback.print_exc()
    print("GRID_BEARING_TEST_FAILED")
sys.stdout.flush()
