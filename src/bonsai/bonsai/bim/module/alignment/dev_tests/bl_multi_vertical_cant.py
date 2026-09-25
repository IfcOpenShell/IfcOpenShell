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


def describe(alignment):
    out = []
    for v in tool.Alignment.get_all_vertical_layouts(alignment):
        owner = ifcopenshell.api.alignment.get_alignment(v)
        cant = ifcopenshell.api.alignment.get_cant_layout(owner)
        n_cant = len(tool.Alignment.get_real_layout_segments(cant)) if cant else 0
        out.append((v.id(), owner.id(), owner.id() == alignment.id(), n_cant))
    return out


try:
    bpy.ops.wm.read_homefile(app_template="")
    bpy.data.batch_remove(bpy.data.objects)
    bonsai.bim.handler.load_post(None)
    tool.Project.get_project_props().export_schema = "IFC4X3_ADD2"
    bpy.ops.bim.create_project()
    ifc = tool.Ifc.get()
    from bonsai.bim.module.alignment import operator as op_mod

    # horizontal with two spiralled curves + one vertical, through the PI method
    alignment = ifcopenshell.api.alignment.create_by_pi_method(
        ifc, "MV",
        [(0.0, 0.0), (800.0, 0.0), (1400.0, 600.0), (2200.0, 600.0)],
        [(300.0, 60.0, 60.0), (400.0, 80.0, 80.0)],
        [(0.0, 100.0), (900.0, 110.0), (2000.0, 104.0)], [200.0],
    )
    tool.Alignment.create_object_for_alignment(alignment)
    tool.Alignment.refresh_alignment_representation_object(alignment)
    select(tool.Ifc.get_object(alignment))
    print("1 vertical:", describe(alignment))
    lone = tool.Alignment.get_all_vertical_layouts(alignment)[0]
    check(tool.Alignment.get_vertical_display_name(lone) == "MV", f"lone vertical: {tool.Alignment.get_vertical_display_name(lone)}")
    check(bpy.ops.align.rename_vertical(layout_id=lone.id(), name="Profile Grade") == {"FINISHED"}, "rename lone")
    check(lone.Name == "Profile Grade" and alignment.Name == "MV", "lone rename touched the alignment")
    check(tool.Alignment.get_vertical_display_name(lone) == "Profile Grade", "lone display name")
    bpy.ops.align.rename_vertical(layout_id=lone.id(), name="")
    check(lone.Name is None and tool.Alignment.get_vertical_display_name(lone) == "MV", "lone clear")

    # a second vertical ("Existing Ground"), the way the panel's add-vertical path does it
    v2 = ifcopenshell.api.alignment.add_vertical_layout(ifc, alignment)
    ok, msg, v2 = op_mod._generate_vertical_alignment_segments(
        bpy.context, alignment, [(0.0, 95.0), (1000.0, 101.0), (2000.0, 98.0)], [0.0], v_layout=v2
    )
    check(ok, msg)
    select(tool.Ifc.get_object(alignment))
    verticals = tool.Alignment.get_all_vertical_layouts(alignment)
    print("2 verticals:", describe(alignment))
    check(len(verticals) == 2, "second vertical missing")
    v1, v2 = verticals

    # generate cant for the SECOND vertical only (the row button passes its layout_id)
    r = bpy.ops.align.generate_cant_layout(cant_value=0.12, layout_id=v2.id())
    print("generate cant v2:", r, describe(alignment))
    d = {v: n for v, _, _, n in describe(alignment)}
    check(d[v2.id()] > 0 and d[v1.id()] == 0, "cant didn't land on v2 only")

    # and the first one too -- with a different value
    r = bpy.ops.align.generate_cant_layout(cant_value=0.05, layout_id=v1.id())
    print("generate cant v1:", r, describe(alignment))
    d = {v: n for v, _, _, n in describe(alignment)}
    check(d[v1.id()] > 0 and d[v2.id()] > 0, "both verticals should have cant now")

    cants = tool.Alignment.get_all_cant_layouts(alignment)
    print("get_all_cant_layouts:", [(c.id(), ifcopenshell.api.alignment.get_alignment(c).id()) for c in cants])
    check(len(cants) == 2, "get_all_cant_layouts doesn't see both")

    def cant_value(c):
        segs = tool.Alignment.get_real_layout_segments(c)
        return max(max(abs(s.DesignParameters.StartCantLeft or 0), abs(s.DesignParameters.StartCantRight or 0)) for s in segs)

    by_owner = {ifcopenshell.api.alignment.get_alignment(c).id(): cant_value(c) for c in cants}
    print("cant values by owner:", by_owner)

    # horizontal rebuild: both cants' curve types should stay synced (change a spiral family)
    check(bpy.ops.align.edit_horizontal_pis() == {"FINISHED"}, "edit pis")
    pis = [m for m in op_mod._find_pi_markers(alignment.id()) if op_mod._is_interior_pi_marker(m)]
    pis[0].bonsai_pi_curve_marker.spiral_family = "BLOSSCURVE"
    select(pis[0])
    check(bpy.ops.align.apply_pi_curve() == {"FINISHED"}, "apply")
    bpy.ops.align.finish_pi_editing()
    select(tool.Ifc.get_object(alignment))
    for c in tool.Alignment.get_all_cant_layouts(alignment):
        types = [s.DesignParameters.PredefinedType for s in tool.Alignment.get_real_layout_segments(c)]
        print("cant", c.id(), "types after BLOSS:", types)
        check("BLOSSCURVE" in types, f"cant {c.id()} not synced to BLOSSCURVE")

    # key points include both cants' transitions
    check(bpy.ops.align.generate_key_points() == {"FINISHED"}, "key points")

    # remove v2's cant (per-row delete), v1's stays
    v2_cant = ifcopenshell.api.alignment.get_cant_layout(ifcopenshell.api.alignment.get_alignment(v2))
    r = bpy.ops.align.remove_cant_layout(layout_id=v2_cant.id())
    print("remove v2 cant:", r, describe(alignment))
    d = {v: n for v, _, _, n in describe(alignment)}
    check(d[v2.id()] == 0 and d[v1.id()] > 0, "wrong cant removed")

    # ---- the dialog names the target vertical and warns about replacing its cant
    class Recorder:
        def __init__(self):
            self.lines = []

        def label(self, text="", icon="NONE"):
            self.lines.append(text)

        def prop(self, data, name, **kw):
            self.lines.append(f"<{name}>")

    Op = op_mod.ALIGN_OT_generate_cant_layout
    Fake = type("Fake", (), {"draw": Op.draw, "_target_vertical": Op._target_vertical})

    def dialog(layout_id):
        f = Fake()
        f.layout = Recorder()
        f.layout_id = layout_id
        f.draw(bpy.context)
        return f.layout.lines

    print("dialog v1:", dialog(v1.id()))
    print("dialog v2:", dialog(v2.id()))
    check(dialog(v1.id())[0] == "For vertical: Vertical 1", "v1 not named distinctly")
    check("Replaces this vertical's existing cant layout" in dialog(v1.id()), "v1 replace warning missing")
    check(dialog(v2.id())[0] == "For vertical: Vertical 2", "v2 not named distinctly")
    check("Replaces this vertical's existing cant layout" not in dialog(v2.id()), "v2 has no cant any more")
    # a user-renamed child alignment shows its own name; the other keeps its number
    ifcopenshell.api.alignment.get_alignment(v2).Name = "Existing Ground"
    check(dialog(v2.id())[0] == "For vertical: Existing Ground", f"renamed child not used: {dialog(v2.id())}")
    check(tool.Alignment.get_vertical_display_name(v1) == "Vertical 1", "v1 label changed")
    print("after rename:", tool.Alignment.get_vertical_display_name(v1), "/", tool.Alignment.get_vertical_display_name(v2))

    # ---- no vertical chosen with several verticals: a clear refusal, nothing changed
    before = describe(alignment)
    try:
        r = bpy.ops.align.generate_cant_layout(cant_value=0.2)
    except RuntimeError as e:
        r = str(e)
    print("layout_id=0:", r)
    check("several verticals" in str(r), "no clear refusal for layout_id=0")
    check(describe(alignment) == before, "layout_id=0 changed something")

    # ---- renaming (the operator the row's name button opens)
    get_owner = ifcopenshell.api.alignment.get_alignment
    check(bpy.ops.align.rename_vertical(layout_id=v1.id(), name="Design Grade") == {"FINISHED"}, "rename v1")
    print("renamed:", v1.Name, "/", get_owner(v1).Name, "->", tool.Alignment.get_vertical_display_name(v1))
    check(v1.Name == "Design Grade" and get_owner(v1).Name == "Design Grade", "v1 not renamed on both entities")
    check(alignment.Name == "MV", "top-level alignment renamed")
    check(tool.Alignment.get_vertical_display_name(v1) == "Design Grade", "display name not updated")
    # a name another vertical already shows is refused, nothing changed
    try:
        r = bpy.ops.align.rename_vertical(layout_id=v2.id(), name="Design Grade")
    except RuntimeError as e:
        r = str(e)
    print("duplicate:", r)
    check("already named" in str(r) and get_owner(v2).Name == "Existing Ground", "duplicate not refused")
    # clearing goes back to the defaults -> "Vertical n"
    check(bpy.ops.align.rename_vertical(layout_id=v1.id(), name="  ") == {"FINISHED"}, "clear v1")
    print("cleared:", v1.Name, "/", get_owner(v1).Name, "->", tool.Alignment.get_vertical_display_name(v1))
    check(v1.Name is None and get_owner(v1).Name == "Child of MV", "clear didn't restore defaults")
    check(tool.Alignment.get_vertical_display_name(v1) == "Vertical 1", "cleared name not Vertical 1")

    print("MULTI_VERTICAL_CANT_OK")
except Exception:
    traceback.print_exc()
    print("MULTI_VERTICAL_CANT_FAILED")
sys.stdout.flush()
