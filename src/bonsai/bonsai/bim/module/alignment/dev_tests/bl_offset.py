# This file was generated with the assistance of an AI coding tool.
# Development test script for the alignment authoring work -- remove before the final PR (see README.md).

import os
import sys
import tempfile
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


def first_vertex(alignment):
    obj = tool.Ifc.get_object(alignment)
    v = obj.matrix_world @ obj.data.vertices[0].co
    return tuple(round(c, 3) for c in v)


try:
    bpy.ops.wm.read_homefile(app_template="")
    bpy.data.batch_remove(bpy.data.objects)
    bonsai.bim.handler.load_post(None)
    tool.Project.get_project_props().export_schema = "IFC4X3_ADD2"
    bpy.ops.bim.create_project()
    ifc = tool.Ifc.get()
    A = tool.Alignment
    from bonsai.bim.module.alignment import operator as op_mod

    props = bpy.context.scene.CivilAlignmentProperties
    base = ifcopenshell.api.alignment.create_by_pi_method(
        ifc, "Main", [(0.0, 0.0), (100.0, 0.0), (200.0, 100.0)], [50.0], [(0.0, 10.0), (80.0, 12.0), (200.0, 10.0)], [0.0]
    )
    A.create_object_for_alignment(base)
    A.refresh_alignment_representation_object(base)

    # ---- Add Alignment (Offset Curve): created complete, from the chosen curve
    cands = A.get_offset_basis_candidates(None)
    print("candidates:", [(c.is_a(), label, dim) for c, label, dim in cands])
    check([dim for _, _, dim in cands] == [2, 3], "expected the horizontal (2D) and the vertical (3D)")
    grad = next(c for c, _, dim in cands if dim == 3)
    r = bpy.ops.align.add_alignment(alignment_name="Lane", definition="OFFSET", define_stationing=True,
                                    offset_from=str(grad.id()), offset_lateral=3.5, offset_vertical=0.2)
    check(r == {"FINISHED"}, "add")
    lane = next(x for x in ifc.by_type("IfcAlignment") if x.Name == "Lane")
    select(tool.Ifc.get_object(lane))
    bpy.ops.align.load_offset_table()
    basis, rows = A.get_offset_values(lane)
    rep = lane.Representation.Representations[0]
    print("lane:", basis.is_a(), rows, rep.RepresentationIdentifier, rep.RepresentationType, lane.ObjectPlacement.RelativePlacement.is_a())
    check(A.is_offset_alignment(lane) and basis == grad and len(rows) == 1 and rows[0][:2] == (0.0, 3.5)
          and abs(rows[0][2] - 0.2) < 1e-6 and rows[0][3] is None, "lane offsets")
    check(rep.RepresentationType == "Curve3D" and lane.ObjectPlacement.RelativePlacement.is_a("IfcAxis2Placement3D"), "3D rep")
    check(not ifcopenshell.api.alignment.get_alignment_layouts(lane), "offset alignment must have no layouts")
    obj = tool.Ifc.get_object(lane)
    check(obj is not None and obj.type == "MESH" and len(obj.data.vertices) > 10, "no mesh")
    print("lane first vertex:", first_vertex(lane))
    select(obj)
    check(not bpy.ops.align.draw_horizontal_alignment.poll(), "PI draw allowed on an offset alignment")
    bpy.ops.align.finish_offset_table()

    # ---- an offset of the offset: 3D (its lowest basis is a gradient curve); no circular choices
    lane_curve = A.get_offset_curve(lane)
    check(bpy.ops.align.add_alignment(alignment_name="Edge", definition="OFFSET", define_stationing=False,
                                      offset_from=str(lane_curve.id()), offset_lateral=2.0) == {"FINISHED"}, "add edge")
    edge = next(x for x in ifc.by_type("IfcAlignment") if x.Name == "Edge")
    select(tool.Ifc.get_object(edge))
    bpy.ops.align.load_offset_table()
    check(any(c == lane_curve for c, _, _ in A.get_offset_basis_candidates(edge)), "lane not offered")
    bpy.ops.align.add_offset_value_row()
    props.offset_value_rows[1].distance_along, props.offset_value_rows[1].lateral = 100.0, 4.0
    check(bpy.ops.align.apply_offset_table() == {"FINISHED"}, "apply edge")
    basis, rows = A.get_offset_values(edge)
    print("edge:", basis.is_a(), [tuple(round(v, 3) if v is not None else None for v in r) for r in rows], "dim", A.get_offset_dimension(basis))
    check(basis == lane_curve and len(rows) == 2 and A.get_offset_dimension(basis) == 3, "edge")
    bpy.ops.align.finish_offset_table()
    edge_curve = A.get_offset_curve(edge)
    check(not any(c == edge_curve for c, _, _ in A.get_offset_basis_candidates(lane)), "circular choice offered")

    # ---- switching the lane to the horizontal makes it 2D and drops the vertical offset
    select(tool.Ifc.get_object(lane))
    bpy.ops.align.load_offset_table()
    comp = next(c for c, _, dim in A.get_offset_basis_candidates(lane) if dim == 2)
    props.offset_basis_curve = str(comp.id())
    bpy.ops.align.apply_offset_table()
    basis, rows = A.get_offset_values(lane)
    rep = lane.Representation.Representations[0]
    print("lane now:", basis.is_a(), rows, rep.RepresentationType, lane.ObjectPlacement.RelativePlacement.is_a())
    check(basis == comp and rows[0][2] is None and rep.RepresentationType == "Curve2D", "2D switch")
    check(lane.ObjectPlacement.RelativePlacement.is_a("IfcAxis2Placement2D"), "placement 2D")
    check(A.get_offset_dimension(A.get_offset_curve(edge).BasisCurve) == 2, "edge dimension should follow its base")

    # ---- distances must increase; nothing changed on refusal
    bpy.ops.align.add_offset_value_row()
    props.offset_value_rows[1].distance_along = 0.0
    before = A.get_offset_values(lane)[1]
    bpy.ops.align.apply_offset_table()
    check(A.get_offset_values(lane)[1] == before, "out-of-order offsets applied")
    bpy.ops.align.finish_offset_table()

    # ---- rebuilding the reference moves the offset alignments' meshes (curve entities stay the same)
    comp_id = comp.id()
    before_lane, before_edge = first_vertex(lane), first_vertex(edge)
    ok, msg = op_mod._generate_alignment_segments(bpy.context, base, [(0.0, 20.0), (100.0, 20.0), (200.0, 120.0)], [50.0])
    check(ok, msg)
    check(A.get_offset_curve(lane).BasisCurve.id() == comp_id, "reference curve entity replaced")
    print("after moving the reference 20 north: lane", before_lane, "->", first_vertex(lane), "| edge", before_edge, "->", first_vertex(edge))
    check(abs(first_vertex(lane)[1] - before_lane[1] - 20.0) < 1e-3, "lane mesh didn't follow")
    check(abs(first_vertex(edge)[1] - before_edge[1] - 20.0) < 1e-3, "edge (offset of offset) mesh didn't follow")

    # ---- a longitudinal offset already in the file is carried through an edit
    A.get_offset_curve(lane).OffsetValues[0].OffsetLongitudinal = 1.25
    select(tool.Ifc.get_object(lane))
    bpy.ops.align.load_offset_table()
    props.offset_value_rows[0].lateral = 6.0
    bpy.ops.align.apply_offset_table()
    bpy.ops.align.finish_offset_table()
    check(A.get_offset_values(lane)[1][0] == (0.0, 6.0, None, 1.25), f"longitudinal lost: {A.get_offset_values(lane)[1]}")

    # ---- save and reload
    path = os.path.join(tempfile.gettempdir(), "offset_alignments.ifc")
    ifc.write(path)
    bpy.ops.wm.read_homefile(app_template="")
    bpy.data.batch_remove(bpy.data.objects)
    bonsai.bim.handler.load_post(None)
    check(bpy.ops.bim.load_project(filepath=path, should_start_fresh_session=True) == {"FINISHED"}, "reload")
    ifc = tool.Ifc.get()
    edge = next(x for x in ifc.by_type("IfcAlignment") if x.Name == "Edge")
    check(A.is_offset_alignment(edge) and tool.Ifc.get_object(edge).type == "MESH", "reloaded edge")
    print("reloaded edge offsets:", A.get_offset_values(edge)[1])
    print("OFFSET_TEST_OK")
except Exception:
    traceback.print_exc()
    print("OFFSET_TEST_FAILED")
sys.stdout.flush()
