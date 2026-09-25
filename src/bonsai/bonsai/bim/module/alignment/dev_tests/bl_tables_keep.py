# This file was generated with the assistance of an AI coding tool.
# Development test script for the alignment authoring work -- remove before the final PR (see README.md).

"""Segment table Apply keeps the GlobalIds of rows that came from existing segments."""

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


def guids(layout):
    return [s.GlobalId for s in tool.Alignment.get_real_layout_segments(layout)]


def terminator(layout):
    return ifcopenshell.api.alignment.get_layout_segments(layout)[-1]


def no_orphans(ifc):
    used = sum(len(c.Segments or ()) for c in ifc.by_type("IfcCompositeCurve"))
    check(len(ifc.by_type("IfcCurveSegment")) == used, f"orphan curve segments {len(ifc.by_type('IfcCurveSegment'))} vs {used}")


try:
    bpy.ops.wm.read_homefile(app_template="")
    bpy.data.batch_remove(bpy.data.objects)
    bonsai.bim.handler.load_post(None)
    tool.Project.get_project_props().export_schema = "IFC4X3_ADD2"
    bpy.ops.bim.create_project()
    ifc = tool.Ifc.get()
    props = bpy.context.scene.CivilAlignmentProperties

    alignment = ifcopenshell.api.alignment.create_by_pi_method(
        ifc, "T",
        [(0.0, 0.0), (800.0, 0.0), (1400.0, 600.0), (2200.0, 600.0)],
        [(300.0, 60.0, 60.0), (400.0, 80.0, 80.0)],
        [(0.0, 100.0), (900.0, 110.0), (2000.0, 104.0)], [200.0],
    )
    tool.Alignment.create_object_for_alignment(alignment)
    tool.Alignment.refresh_alignment_representation_object(alignment)
    select(tool.Ifc.get_object(alignment))
    h = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
    v = ifcopenshell.api.alignment.get_vertical_layout(alignment)

    # ---- horizontal: a radius change keeps every GlobalId
    before = guids(h)
    check(bpy.ops.align.enable_editing_h_segments(layout_id=h.id()) == {"FINISHED"}, "enable h")
    arc = next(i for i, r in enumerate(props.h_segment_rows) if r.predefined_type == "CIRCULARARC")
    props.h_segment_rows[arc].start_radius = 350.0
    check(bpy.ops.align.apply_h_segments() == {"FINISHED"}, "apply h")
    check(guids(h) == before, f"h guids changed: {before} -> {guids(h)}")
    check(abs(tool.Alignment.get_real_layout_segments(h)[arc].DesignParameters.StartRadiusOfCurvature - 350.0) < 1e-9, "radius")
    # the terminator sits at the end of the last real segment
    last = tool.Alignment.get_real_layout_segments(h)[-1]
    from ifcopenshell.api.alignment._get_segment_endpoint import _get_segment_endpoint
    end = _get_segment_endpoint(ifc, last)
    tdp = terminator(h).DesignParameters
    check(abs(tdp.StartPoint.Coordinates[0] - end[0, 3]) < 1e-6 and abs(tdp.StartPoint.Coordinates[1] - end[1, 3]) < 1e-6, "terminator position")
    no_orphans(ifc)
    print("h change ok", len(before))

    # ---- horizontal: remove a middle row, add a new row -> only the new row gets a new GlobalId
    check(bpy.ops.align.enable_editing_h_segments(layout_id=h.id()) == {"FINISHED"}, "enable h 2")
    props.active_h_segment_row_index = 1
    removed_guid = before[1]
    bpy.ops.align.remove_segment_row(kind="HORIZONTAL")
    props.active_h_segment_row_index = len(props.h_segment_rows) - 1
    bpy.ops.align.add_segment_row(kind="HORIZONTAL")
    check(bpy.ops.align.apply_h_segments() == {"FINISHED"}, "apply h 2")
    after = guids(h)
    expected_kept = [g for g in before if g != removed_guid]
    check(after[:-1] == expected_kept, f"kept order {after[:-1]} vs {expected_kept}")
    check(after[-1] not in before, "new row reused a guid")
    check(not ifc.by_guid(removed_guid) if False else all(s.GlobalId != removed_guid for s in ifc.by_type("IfcAlignmentSegment")), "removed segment survives")
    no_orphans(ifc)
    print("h delete/insert ok")

    # ---- vertical: a length change keeps GlobalIds
    vbefore = guids(v)
    check(bpy.ops.align.enable_editing_v_segments(layout_id=v.id()) == {"FINISHED"}, "enable v")
    props.v_segment_rows[0].h_length = props.v_segment_rows[0].h_length + 5.0
    check(bpy.ops.align.apply_v_segments() == {"FINISHED"}, "apply v")
    check(guids(v) == vbefore, "v guids changed")
    no_orphans(ifc)
    print("v ok", len(vbefore))

    # ---- cant: a value change keeps GlobalIds
    check(bpy.ops.align.generate_cant_layout(cant_value=0.1, layout_id=v.id()) == {"FINISHED"}, "gen cant")
    c = ifcopenshell.api.alignment.get_cant_layout(alignment)
    cbefore = guids(c)
    check(bpy.ops.align.enable_editing_cant_segments(layout_id=c.id()) == {"FINISHED"}, "enable c")
    r = next(r for r in props.cant_segment_rows if r.predefined_type == "CONSTANTCANT")
    r.start_cant_right = r.end_cant_right = r.start_cant_right + 0.01
    check(bpy.ops.align.apply_cant_segments() == {"FINISHED"}, "apply c")
    check(guids(c) == cbefore, "cant guids changed")
    no_orphans(ifc)
    print("cant ok", len(cbefore))
    print("ALL OK")
except Exception:
    traceback.print_exc()
    sys.exit(1)
sys.exit(0)
