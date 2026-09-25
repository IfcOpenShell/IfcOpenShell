# This file was generated with the assistance of an AI coding tool.
# Development test script for the alignment authoring work -- remove before the final PR (see README.md).

"""PI-method regeneration keeps the GlobalIds of corresponding segments."""

import sys
import traceback

import bpy

import bonsai.bim.handler
import bonsai.tool as tool
import ifcopenshell.api.alignment


def check(cond, msg):
    if not cond:
        raise AssertionError(msg)


def real(layout):
    return tool.Alignment.get_real_layout_segments(layout)


def sig(layout):
    return [(s.GlobalId, s.DesignParameters.PredefinedType) for s in real(layout)]


def no_orphans(ifc):
    used = sum(len(c.Segments or ()) for c in ifc.by_type("IfcCompositeCurve"))
    check(len(ifc.by_type("IfcCurveSegment")) == used, "orphan curve segments")


try:
    bpy.ops.wm.read_homefile(app_template="")
    bpy.data.batch_remove(bpy.data.objects)
    bonsai.bim.handler.load_post(None)
    tool.Project.get_project_props().export_schema = "IFC4X3_ADD2"
    bpy.ops.bim.create_project()
    ifc = tool.Ifc.get()
    from bonsai.bim.module.alignment import operator as op_mod

    H = [(0.0, 0.0), (800.0, 0.0), (1400.0, 600.0), (2200.0, 600.0), (3000.0, 0.0)]
    R = [(300.0, 60.0, 60.0), (400.0, 80.0, 80.0), (350.0, 0.0, 0.0)]
    V = [(0.0, 100.0), (900.0, 110.0), (2000.0, 104.0), (3000.0, 108.0)]
    L = [200.0, 150.0]
    alignment = ifcopenshell.api.alignment.create_by_pi_method(ifc, "T", H, R, V, L)
    tool.Alignment.create_object_for_alignment(alignment)
    tool.Alignment.refresh_alignment_representation_object(alignment)
    h = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
    v = ifcopenshell.api.alignment.get_vertical_layout(alignment)
    ctx = bpy.context

    s0 = sig(h)
    print("h:", [t for _, t in s0])

    # 1. move a PI and change radius/spirals: every GlobalId kept
    H1 = [H[0], H[1], (1450.0, 650.0), H[3], H[4]]
    R1 = [(320.0, 70.0, 50.0), (400.0, 80.0, 80.0), (350.0, 0.0, 0.0)]
    ok, msg = op_mod._generate_alignment_segments(ctx, alignment, H1, R1)
    check(ok, msg)
    check([g for g, _ in sig(h)] == [g for g, _ in s0], "move/radius changed guids")
    no_orphans(ifc)
    print("1 ok")

    # 2. delete PI 2 (index 1): only its back tangent + spiral/arc/spiral go
    H2 = [H1[0], H1[1], H1[3], H1[4]]
    R2 = [R1[0], R1[2]]
    ok, msg = op_mod._generate_alignment_segments(ctx, alignment, H2, R2)
    check(ok, msg)
    s2 = sig(h)
    print("after delete:", [t for _, t in s2])
    # groups before: PI1 = [0..3] (LINE, CLOTHOID, ARC, CLOTHOID), PI2 = [4..7], PI3 = [8, 9], END = [10]
    expected = [g for g, _ in s0[:4]] + [g for g, _ in s0[8:]]
    check([g for g, _ in s2] == expected, f"delete: {[g for g,_ in s2]} vs {expected}")
    no_orphans(ifc)
    print("2 ok")

    # 3. insert a PI back: only the new PI's segments are new
    ok, msg = op_mod._generate_alignment_segments(ctx, alignment, H1, R1)
    check(ok, msg)
    s3 = sig(h)
    g3 = [g for g, _ in s3]
    check(g3[:4] == expected[:4] and g3[8:] == expected[4:], "insert kept")
    check(not set(g3[4:8]) & {g for g, _ in s0}, "insert reused a guid")
    no_orphans(ifc)
    print("3 ok")

    # 4. drop the spirals at PI 1: the tangent and arc keep theirs, the spirals go
    R4 = [(320.0, 0.0, 0.0), R1[1], R1[2]]
    ok, msg = op_mod._generate_alignment_segments(ctx, alignment, H1, R4)
    check(ok, msg)
    g4 = [g for g, _ in sig(h)]
    check(g4[0] == g3[0] and g4[1] == g3[2] and g4[2:] == g3[4:], "spirals dropped")
    print("4 ok")

    # 5. vertical: move a VPI + curve length; then delete, then insert
    vs0 = [g for g, _ in sig(v)]
    print("v:", [t for _, t in sig(v)])
    V1 = [V[0], (950.0, 111.0), V[2], V[3]]
    ok, msg, _ = op_mod._generate_vertical_alignment_segments(ctx, alignment, V1, [220.0, 150.0])
    check(ok, msg)
    check([g for g, _ in sig(v)] == vs0, "v move changed guids")
    ok, msg, _ = op_mod._generate_vertical_alignment_segments(ctx, alignment, [V1[0], V1[2], V1[3]], [150.0])
    check(ok, msg)
    # VPI1 = [grade, arc], VPI2 = [grade, arc], END = [grade]: deleting VPI1 keeps VPI2 and END
    check([g for g, _ in sig(v)] == vs0[2:], f"v delete {[g for g,_ in sig(v)]} vs {vs0[2:]}")
    ok, msg, _ = op_mod._generate_vertical_alignment_segments(ctx, alignment, V1, [220.0, 150.0])
    check(ok, msg)
    gv = [g for g, _ in sig(v)]
    check(gv[2:] == vs0[2:] and not set(gv[:2]) & set(vs0), "v insert")
    no_orphans(ifc)
    print("5 ok")

    # (a spiral-less curve next to a spiralled one gives a constant-cant LINEARTRANSITION, which the
    # library's cant mapper can't handle -- a separate, pre-existing issue)
    ok, msg = op_mod._generate_alignment_segments(ctx, alignment, H1, R1)
    check(ok, msg)
    obj = tool.Ifc.get_object(alignment)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    # 6. regenerating cant with a new value keeps its GlobalIds
    check(bpy.ops.align.generate_cant_layout(cant_value=0.1, layout_id=v.id()) == {"FINISHED"}, "cant 1")
    c = ifcopenshell.api.alignment.get_cant_layout(alignment)
    cg = [g for g, _ in sig(c)]
    check(bpy.ops.align.generate_cant_layout(cant_value=0.12, layout_id=v.id()) == {"FINISHED"}, "cant 2")
    check([g for g, _ in sig(c)] == cg, "cant regen changed guids")
    no_orphans(ifc)
    print("6 ok")
    print("ALL OK")
except Exception:
    traceback.print_exc()
    sys.exit(1)
sys.exit(0)
