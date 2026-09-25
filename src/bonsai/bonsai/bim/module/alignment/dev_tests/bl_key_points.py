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
import ifcopenshell.util.element


def check(cond, msg):
    if not cond:
        raise AssertionError(msg)


def select_only(obj):
    for o in bpy.context.selected_objects:
        o.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def kp_referents(alignment):
    nests = tool.Alignment.get_key_point_nests(alignment)
    return [r for n in nests for r in n.RelatedObjects]


def position_referents_in_file():
    return [r for r in tool.Ifc.get().by_type("IfcReferent") if r.PredefinedType == "POSITION"]


def kp_objects():
    return [o for o in bpy.data.objects if o.name.startswith("IfcReferent/") and "(" in o.name]


def summary(alignment):
    refs = kp_referents(alignment)
    return [
        (r.Name, round(ifcopenshell.util.element.get_pset(r, "Pset_Stationing", "Station"), 3)) for r in refs
    ]


def consistent(alignment, label):
    refs = kp_referents(alignment)
    nests = tool.Alignment.get_key_point_nests(alignment)
    in_file = position_referents_in_file()
    objs = kp_objects()
    print(f"[{label}] nests={len(nests)} referents={len(refs)} POSITION-in-file={len(in_file)} objects={len(objs)}")
    check(len(nests) <= 1, f"{label}: expected at most one key-point nest, got {len(nests)}")
    check(len(in_file) == len(refs), f"{label}: orphan POSITION referents ({len(in_file)} vs {len(refs)})")
    check(len(objs) == len(refs), f"{label}: Blender objects {len(objs)} != referents {len(refs)}")
    for r in refs:
        check(tool.Ifc.get_object(r) is not None, f"{label}: referent {r.Name} has no Blender object")


def create_alignment(name, with_key_points):
    ifc = tool.Ifc.get()
    alignment = ifcopenshell.api.alignment.create_by_pi_method(
        ifc, name,
        [(0.0, 0.0), (1000.0, 0.0), (1000.0, 1000.0)], [(300.0, 80.0, 80.0)],
        [(0.0, 0.0), (1000.0, 5.0), (1900.0, 0.0)], [400.0],
    )
    ifcopenshell.api.alignment.add_stationing_referent(ifc, "start", alignment, 0.0, 0.0)
    tool.Alignment.create_object_for_alignment(alignment)
    tool.Alignment.refresh_alignment_representation_object(alignment)
    select_only(tool.Ifc.get_object(alignment))
    if with_key_points:
        check(bpy.ops.align.generate_key_points() == {"FINISHED"}, "generate_key_points failed")
    return alignment


def edit_first_pi_radius(alignment, radius):
    from bonsai.bim.module.alignment.operator import _find_pi_markers, _is_interior_pi_marker

    select_only(tool.Ifc.get_object(alignment))
    check(bpy.ops.align.edit_horizontal_pis() == {"FINISHED"}, "edit_horizontal_pis failed")
    pis = [m for m in _find_pi_markers(alignment.id()) if _is_interior_pi_marker(m)]
    pis[0].bonsai_pi_curve_marker.radius = radius
    select_only(pis[0])
    check(bpy.ops.align.apply_pi_curve() == {"FINISHED"}, "apply_pi_curve failed")
    check(bpy.ops.align.finish_pi_editing() == {"FINISHED"}, "finish failed")
    select_only(tool.Ifc.get_object(alignment))


try:
    bpy.ops.wm.read_homefile(app_template="")
    bpy.data.batch_remove(bpy.data.objects)
    bonsai.bim.handler.load_post(None)
    tool.Project.get_project_props().export_schema = "IFC4X3_ADD2"
    bpy.ops.bim.create_project()

    # ---- 1. generate ----
    a = create_alignment("KP", with_key_points=True)
    s1 = summary(a)
    print("generated:", s1)
    labels = " ".join(n for n, _ in s1)
    for tag in ("P.O.B.", "T.S.", "S.C.", "C.S.", "S.T.", "P.V.C.", "P.O.E."):
        check(tag in labels, f"missing {tag}")
    check(tool.Alignment.get_key_point_nests(a)[0].RelatingObject == a, "nest not on the alignment")
    consistent(a, "generate")

    # ---- 2. regenerate button is idempotent ----
    check(bpy.ops.align.generate_key_points() == {"FINISHED"}, "regenerate failed")
    check(summary(a) == s1, "regenerate changed the result")
    consistent(a, "regenerate")

    # ---- 3. horizontal PI edit regenerates automatically ----
    edit_first_pi_radius(a, 450.0)
    s2 = summary(a)
    print("after radius edit:", s2)
    check(len(s2) == len(s1) and s2 != s1, "key points not regenerated after horizontal edit")
    consistent(a, "h edit")

    # ---- 4. start station change regenerates ----
    check(bpy.ops.align.set_start_station(station="1000") == {"FINISHED"}, "set_start_station failed")
    s3 = summary(a)
    print("after start station 1000:", s3[:2])
    check(all(abs(b[1] - (x[1] + 1000.0)) < 1e-6 for x, b in zip(s2, s3)), "stations not shifted by 1000")
    consistent(a, "station")

    # ---- 5. cant layout adds cant key points ----
    check(bpy.ops.align.generate_cant_layout(cant_value=0.1) == {"FINISHED"}, "generate cant failed")
    s4 = summary(a)
    print("after cant:", len(s3), "->", len(s4))
    check(len(s4) > len(s3), "cant key points not added")
    consistent(a, "cant")

    # ---- 6. an alignment without key points never gets any ----
    b = create_alignment("NoKP", with_key_points=False)
    edit_first_pi_radius(b, 350.0)
    check(not tool.Alignment.has_key_point_referents(b), "key points appeared unasked")

    # ---- 7. save, reload: detected from IFC alone, and still auto-updates ----
    path = os.path.join(tempfile.gettempdir(), "kp_reload_test.ifc")
    tool.Ifc.get().write(path)
    bpy.ops.wm.read_homefile(app_template="")
    bpy.data.batch_remove(bpy.data.objects)
    bonsai.bim.handler.load_post(None)
    check(bpy.ops.bim.load_project(filepath=path, should_start_fresh_session=True) == {"FINISHED"}, "load failed")
    ifc = tool.Ifc.get()
    a = next(x for x in ifc.by_type("IfcAlignment") if x.Name == "KP")
    b = next(x for x in ifc.by_type("IfcAlignment") if x.Name == "NoKP")
    print("reloaded: KP has key points:", tool.Alignment.has_key_point_referents(a),
          "| NoKP:", tool.Alignment.has_key_point_referents(b))
    check(tool.Alignment.has_key_point_referents(a), "key points not detected after reload")
    check(not tool.Alignment.has_key_point_referents(b), "false positive after reload")
    check(summary(a) == s4, "reloaded key points differ")
    consistent(a, "reload")
    edit_first_pi_radius(a, 500.0)
    s5 = summary(a)
    check(len(s5) == len(s4) and s5 != s4, "loaded key points not auto-updated")
    consistent(a, "reload + edit")

    # ---- 8. removing layouts regenerates / removes ----
    select_only(tool.Ifc.get_object(a))
    cant = tool.Alignment.get_all_cant_layouts(a)[0]
    check(bpy.ops.align.remove_cant_layout(layout_id=cant.id()) == {"FINISHED"}, "remove cant failed")
    s6 = summary(a)
    print("after remove cant:", len(s6))
    check(len(s6) == len(s3), "cant key points not removed with cant layout")
    consistent(a, "remove cant")
    vert = tool.Alignment.get_all_vertical_layouts(a)[0]
    check(bpy.ops.align.remove_vertical_layout(layout_id=vert.id()) == {"FINISHED"}, "remove vertical failed")
    s7 = summary(a)
    print("after remove vertical:", s7)
    check(not any("P.V" in n for n, _ in s7), "vertical key points left behind")
    consistent(a, "remove vertical")
    check(bpy.ops.align.remove_horizontal_layout() == {"FINISHED"}, "remove horizontal failed")
    check(not tool.Alignment.has_key_point_referents(a), "key points left after horizontal removed")
    consistent(a, "remove horizontal")

    # ---- 9. remove button, and deleting the whole alignment ----
    select_only(tool.Ifc.get_object(b))
    check(bpy.ops.align.generate_key_points() == {"FINISHED"}, "generate on NoKP failed")
    check(bpy.ops.align.remove_key_points() == {"FINISHED"}, "remove_key_points failed")
    check(not tool.Alignment.has_key_point_referents(b) and not position_referents_in_file(), "remove button left some")
    check(bpy.ops.align.generate_key_points() == {"FINISHED"}, "generate again failed")
    check(bpy.ops.align.remove_alignment() == {"FINISHED"}, "remove_alignment failed")
    check(not position_referents_in_file(), "orphan key points after deleting alignment")
    check(not kp_objects(), "orphan key-point objects after deleting alignment")

    print("KEY_POINTS_TEST_OK")
except Exception:
    traceback.print_exc()
    print("KEY_POINTS_TEST_FAILED")
sys.stdout.flush()
